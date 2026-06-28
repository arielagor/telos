#!/usr/bin/env python3
"""Live bridge: telos.bench  <->  a running OmegaClaw container.

OmegaClaw is a continually-running, goal-autonomous agent that talks over a *channel*.
For the benchmark we run it on the in-process **test (mock) comm channel**: the agent
(inside the container) connects out to a CommMockServer on the host (TCP :9766), and we
push the goal-reading prompt to it and read its reply back over the same RPC.

This script exposes a tiny HTTP endpoint (POST {"message": ...} -> {"reply": ...}) so the
existing ``telos.adapters.omegaclaw`` adapter can drive a real OmegaClaw with no changes:

    OMEGACLAW_ENDPOINT=http://127.0.0.1:8099 python -m telos.bench --adapter omegaclaw

Because the agent is autonomous (it may emit several lines, or take its time), each POST:
  1. drains any stale/proactive chatter,
  2. sends the prompt,
  3. collects every line the agent emits until it goes quiet for QUIET_S (or HARD_TIMEOUT_S),
  4. returns the concatenation as ``reply`` (the adapter's extract_json pulls the goal JSON).

Env:
  OMEGACLAW_MOCK_DIR  path to OmegaClaw-Core/Autotests/mock (has comm.py + rpc.py)
  BRIDGE_PORT         host HTTP port (default 8099)
  COMM_PORT           mock-comm server port (default 9766; must match TEST_SERVER_IP target)
"""
from __future__ import annotations

import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MOCK_DIR = os.environ.get(
    "OMEGACLAW_MOCK_DIR",
    r"C:\Users\ariel\.claude\projects\OmegaClaw-Core\Autotests\mock",
)
sys.path.insert(0, MOCK_DIR)

from comm import CommMockServer  # noqa: E402  (from the OmegaClaw mock package)

COMM_PORT = int(os.environ.get("COMM_PORT", "9766"))
BRIDGE_PORT = int(os.environ.get("BRIDGE_PORT", "8099"))
HTTP_HOST = os.environ.get("HTTP_HOST", "127.0.0.1")  # 0.0.0.0 when run in a container w/ published port

# Collection tuning for the autonomous agent. (Configurable via env so a benchmark run
# can fail empty scenarios fast instead of waiting the full window.)
FIRST_TOKEN_TIMEOUT_S = int(os.environ.get("FIRST_TOKEN_TIMEOUT_S", "90"))   # wait for agent's FIRST line
QUIET_S = int(os.environ.get("QUIET_S", "4"))                                # silence after first line = done
HARD_TIMEOUT_S = int(os.environ.get("HARD_TIMEOUT_S", "150"))               # absolute cap per prompt
POLL_S = 0.4

_server: CommMockServer | None = None


def _drain():
    """Throw away any messages already queued (proactive chatter, prior turn spill)."""
    n = 0
    while True:
        m = _server.getLastMessage()
        if not m:
            break
        n += 1
    if n:
        print(f"[bridge] drained {n} stale message(s)", flush=True)


def ask(prompt: str) -> str:
    _drain()
    ok = _server.send_message(prompt, timeout=15)
    print(f"[bridge] sent prompt ({len(prompt)} chars), ack={ok}", flush=True)
    collected: list[str] = []
    start = time.time()
    last_msg_at = None
    while True:
        now = time.time()
        if now - start > HARD_TIMEOUT_S:
            break
        if last_msg_at is None and now - start > FIRST_TOKEN_TIMEOUT_S:
            break
        if last_msg_at is not None and now - last_msg_at > QUIET_S:
            break
        m = _server.getLastMessage()
        if m:
            collected.append(m)
            last_msg_at = time.time()
            preview = m if len(m) < 160 else m[:160] + "..."
            print(f"[bridge] <- agent: {preview}", flush=True)
        else:
            time.sleep(POLL_S)
    reply = "\n".join(collected)
    print(f"[bridge] reply assembled: {len(reply)} chars from {len(collected)} message(s)", flush=True)
    return reply


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet the default access log
        pass

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8", "ignore")
        try:
            msg = json.loads(body).get("message", "")
        except json.JSONDecodeError:
            msg = body
        reply = ask(msg)
        out = json.dumps({"reply": reply}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)


def main():
    global _server
    print(f"[bridge] starting CommMockServer on 0.0.0.0:{COMM_PORT}", flush=True)
    _server = CommMockServer(("0.0.0.0", COMM_PORT))
    print(f"[bridge] HTTP endpoint on http://{HTTP_HOST}:{BRIDGE_PORT}  (POST message->reply)", flush=True)
    print("[bridge] waiting for the OmegaClaw agent to connect on the comm channel...", flush=True)
    httpd = ThreadingHTTPServer((HTTP_HOST, BRIDGE_PORT), Handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        _server.stop(5)


if __name__ == "__main__":
    main()
