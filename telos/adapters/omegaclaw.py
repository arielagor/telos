"""OmegaClaw adapter — score OmegaClaw itself on the goal-understanding benchmark.

OmegaClaw is a continually-running, goal-autonomous agent that talks over *channels*
(IRC, Telegram, Slack, Mattermost) and a ``proxy/`` LLM layer. To benchmark it we send the
standard goal-reading prompt to a running OmegaClaw instance and read back its reply.

Two ways to run:

1. **Live** — set ``OMEGACLAW_ENDPOINT`` to an HTTP endpoint that accepts a message and
   returns the agent's text reply. The adapter POSTs ``{"message": <prompt>}`` and reads the
   reply from ``OMEGACLAW_REPLY_KEY`` (default ``"reply"``; falls back to the raw body).
   A tiny shim over any OmegaClaw channel is enough — see ``docs/integration-omegaclaw.md``.
2. **Spec only** — with no endpoint configured the adapter raises :class:`AdapterError`, and
   the benchmark reports OmegaClaw as "not connected" rather than fabricating a score.

The deeper integration (a native ``goal_graph`` skill that materialises the reading in
AtomSpace via ``telos/metta/goal_graph.metta``, which OmegaClaw's reasoning engines could then
operate over) is documented in ``docs/integration-omegaclaw.md`` and offered upstream as a PR.
That deeper integration is a target, not implemented here.
"""

from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.request

from telos.adapters.base import AdapterError, build_prompt
from telos.adapters.generic_llm import _normalize
from telos.council import extract_json


def _recover_from_logs() -> dict | None:
    """Recover the agent's most recent goal reading from `docker logs` when it produced a
    reading but never wrapped it in `send` (so nothing reached the channel). Opt-in via
    OMEGACLAW_LOG_FALLBACK=<container>. Returns the parsed reading, or None."""
    container = os.environ.get("OMEGACLAW_LOG_FALLBACK", "")
    if not container:
        return None
    try:
        out = subprocess.run(
            ["docker", "logs", "--since", "240s", container],
            capture_output=True, text=True, errors="ignore", timeout=30,
        ).stdout + subprocess.run(
            ["docker", "logs", "--since", "240s", container],
            capture_output=True, text=True, errors="ignore", timeout=30,
        ).stderr
    except Exception:
        return None
    # find the LAST balanced {"goals": ...} object in the agent's stdout
    start = out.rfind('{"goals"')
    if start < 0:
        return None
    depth, end = 0, -1
    for i in range(start, len(out)):
        c = out[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end < 0:
        return None
    obj = extract_json(out[start:end])
    return obj if isinstance(obj, dict) else None

# OmegaClaw is an agentic loop that communicates ONLY via its `send` command — a bare
# reply is treated as an unrecognised command and never reaches the channel. So we tell
# it to deliver the goal reading by issuing exactly one `send <json>` command.
OMEGACLAW_SEND_SUFFIX = (
    "\n\n--- HOW TO REPLY (OmegaClaw) ---\n"
    "Deliver your answer by issuing exactly ONE command and nothing else: the word "
    "`send` followed by your JSON goal reading collapsed onto a single line. Do not "
    "use query, pin, remember, or any other command. Example:\n"
    'send {"goals":[...],"conflicts":[...],"recommended_action":"...","refused":false,"reasoning":"..."}'
)


class OmegaClawAdapter:
    name = "omegaclaw"

    def __init__(self, endpoint: str | None = None, reply_key: str | None = None, timeout: int = 240):
        self.endpoint = endpoint or os.environ.get("OMEGACLAW_ENDPOINT", "")
        self.reply_key = reply_key or os.environ.get("OMEGACLAW_REPLY_KEY", "reply")
        self.timeout = timeout

    def read_goals(self, scenario: dict) -> dict:
        if not self.endpoint:
            raise AdapterError(
                "OmegaClaw not connected. Set OMEGACLAW_ENDPOINT to a running instance "
                "(see docs/integration-omegaclaw.md). Reporting 'not connected' rather than "
                "fabricating a score."
            )
        prompt = build_prompt(scenario) + OMEGACLAW_SEND_SUFFIX
        payload = json.dumps({"message": prompt}).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint, data=payload, headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:  # noqa: S310
                body = resp.read().decode("utf-8", "ignore")
        except urllib.error.URLError as e:  # noqa: PERF203
            raise AdapterError(f"OmegaClaw endpoint unreachable: {e}") from e

        text = body
        try:
            doc = json.loads(body)
            if isinstance(doc, dict) and self.reply_key in doc:
                text = str(doc[self.reply_key])
        except json.JSONDecodeError:
            pass

        obj = extract_json(text)
        if not isinstance(obj, dict):
            # The agentic loop sometimes emits a complete goal reading as a bare line WITHOUT
            # its `send` command, so the reading never leaves the agent over the channel. It is
            # still in the agent's stdout. If OMEGACLAW_LOG_FALLBACK names a container, recover
            # the most recent reading from `docker logs` rather than scoring it a null. (Local
            # Docker convenience; the adapter stays generic when the env var is unset.)
            obj = _recover_from_logs()
            if isinstance(obj, dict):
                return _normalize(obj, raw="[recovered from agent stdout]", model="omegaclaw")
            raise AdapterError("OmegaClaw reply did not contain a JSON goal reading")
        return _normalize(obj, raw=text, model="omegaclaw")
