"""Generic LLM adapter — wraps any model family as an agent-under-test.

This is the baseline the published results use. It poses the standard goal-reading prompt
to one model family and parses the JSON reply. Any frontier model can be benchmarked this
way, which gives OmegaClaw a like-for-like comparison point.
"""

from __future__ import annotations

from telos import providers as P
from telos.adapters.base import AdapterError, build_prompt
from telos.council import extract_json


class GenericLLMAdapter:
    def __init__(self, family: str = "claude", model: str | None = None):
        self.family = family
        self.model = model
        self.name = f"generic:{family}" + (f":{model}" if model else "")

    def read_goals(self, scenario: dict) -> dict:
        prompt = build_prompt(scenario)
        kw = {"model": self.model} if self.model else {}
        reply = P.call(self.family, prompt, system="", **kw)
        if not reply.ok:
            raise AdapterError(f"{self.family} call failed: {reply.error}")
        obj = extract_json(reply.text)
        if not isinstance(obj, dict):
            raise AdapterError(f"{self.family} returned non-JSON reading")
        return _normalize(obj, raw=reply.text, model=reply.model)


def _normalize(obj: dict, raw: str = "", model: str = "") -> dict:
    """Coerce a model's reply into the adapter output contract, tolerating sloppy shapes."""
    goals = []
    for g in obj.get("goals", []) or []:
        if not isinstance(g, dict):
            continue
        scope = str(g.get("scope", "individual")).lower()
        scope = "collective" if scope.startswith("coll") else "individual"
        goals.append({
            "description": str(g.get("description", "")).strip(),
            "scope": scope,
            "owner": str(g.get("owner", "unknown")).strip() or "unknown",
            "implicit": bool(g.get("implicit", False)),
        })
    conflicts = []
    for c in obj.get("conflicts", []) or []:
        if isinstance(c, dict):
            conflicts.append({
                "a": str(c.get("a", "")).strip(),
                "b": str(c.get("b", "")).strip(),
                "explanation": str(c.get("explanation", "")).strip(),
            })
        elif isinstance(c, (list, tuple)) and len(c) >= 2:
            conflicts.append({"a": str(c[0]), "b": str(c[1]), "explanation": ""})
    return {
        "goals": goals,
        "conflicts": conflicts,
        "recommended_action": str(obj.get("recommended_action", "")).strip(),
        "refused": bool(obj.get("refused", False)),
        "reasoning": str(obj.get("reasoning", "")).strip(),
        "_model": model,
    }
