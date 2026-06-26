"""Telos — goal understanding & alignment for goal-autonomous agents.

Telos gives a goal-autonomous agent (such as OmegaClaw) an explicit, inspectable
representation of *individual* and *collective* goals, the relations between them,
and a benchmark + council that measure whether an agent actually understands those
goals and stays beneficial.

Submodules:
- ``telos.schema``    : the goal graph (Goal, GoalRelation, GoalGraph) — zero deps.
- ``telos.harness``   : runs an agent-under-test over scenarios.
- ``telos.judge``     : scores agent output against gold labels (deterministic + council).
- ``telos.council``   : cross-family (Claude/Gemini/OpenAI) deliberation + adversarial red-team.
- ``telos.providers`` : thin model-family REST/CLI adapters used by the council and baselines.
- ``telos.adapters``  : agent-under-test adapters (generic LLM baseline + OmegaClaw spec).
- ``telos.bench``     : the ``telos`` CLI.
"""

__version__ = "0.1.0"

from telos.schema import (  # noqa: F401
    Goal,
    GoalGraph,
    GoalRelation,
    GoalScope,
    GoalStatus,
    RelationType,
)
