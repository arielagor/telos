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
import urllib.error
import urllib.request

from telos.adapters.base import AdapterError, build_prompt
from telos.adapters.generic_llm import _normalize
from telos.council import extract_json


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
        prompt = build_prompt(scenario)
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
            raise AdapterError("OmegaClaw reply did not contain a JSON goal reading")
        return _normalize(obj, raw=text, model="omegaclaw")
