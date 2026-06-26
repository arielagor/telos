"""Agent-under-test adapters.

An *adapter* turns "an agent" into something the benchmark can call: given a scenario, it
returns the agent's *goal reading* (the goals it inferred, conflicts it found, and the
action it recommends). Two adapters ship:

- :class:`telos.adapters.generic_llm.GenericLLMAdapter` — wraps any model family so the
  benchmark runs out of the box (the published baselines use this).
- :class:`telos.adapters.omegaclaw.OmegaClawAdapter` — wires the benchmark to a running
  OmegaClaw instance over its HTTP/channel interface, or documents how to, so the same
  benchmark scores OmegaClaw itself.

Adapter output contract (a plain dict)::

    {
      "goals": [{"description": str, "scope": "individual"|"collective",
                 "owner": str, "implicit": bool}],
      "conflicts": [{"a": str, "b": str, "explanation": str}],
      "recommended_action": str,
      "refused": bool,
      "reasoning": str,
    }
"""

from telos.adapters.base import Adapter, AdapterError  # noqa: F401
