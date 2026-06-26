"""Goal representation for goal-autonomous agents.

This module is the heart of Telos: a small, inspectable, dependency-free model of
*individual* and *collective* goals and the relations between them. It is designed to
slot into OmegaClaw's symbolic layer (see ``telos/metta/goal_graph.metta`` for the
AtomSpace mirror) while also being usable standalone by any Python agent.

Design principles
-----------------
1. **Inspectable.** Every goal and relation is a plain dataclass that round-trips to
   JSON. Nothing hides behind a model weight.
2. **Individual vs collective is first-class.** A goal-autonomous system that serves
   people must distinguish "what this one person wants" from "what the group needs",
   and reason about where they reinforce or fight each other.
3. **Beneficial by construction.** Each goal carries a ``beneficial`` assessment so an
   agent can refuse or flag a goal that harms the collective — the BGI safety property.
4. **Deterministic.** No semantic matching or LLM calls live here; scoring against gold
   labels lives in ``telos.judge`` so the data model stays testable and reproducible.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Iterable, Optional


class GoalScope(str, Enum):
    """Whose goal this is."""

    INDIVIDUAL = "individual"  # belongs to one stakeholder
    COLLECTIVE = "collective"  # belongs to a group / community / the commons


class GoalStatus(str, Enum):
    """Lifecycle state of a goal — lets an agent *track progress*, not just store goals."""

    PROPOSED = "proposed"    # surfaced but not yet committed to
    ACTIVE = "active"        # currently being pursued
    BLOCKED = "blocked"      # cannot progress until a dependency clears
    ACHIEVED = "achieved"    # done
    ABANDONED = "abandoned"  # dropped (superseded, infeasible, or no longer wanted)


class RelationType(str, Enum):
    """How two goals relate. The four relations OmegaClaw goal-tracking needs."""

    SUPPORTS = "supports"        # achieving src advances dst
    CONFLICTS = "conflicts"      # achieving src harms / blocks dst (the alignment hotspot)
    SUBSUMES = "subsumes"        # src is a broader goal that contains dst
    DEPENDS_ON = "depends_on"    # src cannot progress until dst is achieved


@dataclass
class Goal:
    """A single goal held by a stakeholder or by the collective.

    Attributes
    ----------
    id:           stable identifier (e.g. ``"g_alice_ship_fast"``).
    description:  natural-language statement of the goal.
    scope:        INDIVIDUAL or COLLECTIVE.
    owner:        stakeholder id for individual goals; a group id (or ``"collective"``)
                  for collective goals.
    status:       lifecycle state (see :class:`GoalStatus`).
    progress:     0.0..1.0 estimate of completion.
    priority:     0.0..1.0 importance to its owner (used to weight conflicts/trade-offs).
    implicit:     ``True`` if the goal was *inferred* rather than explicitly stated.
                  Understanding implicit goals is a core competency the benchmark tests.
    beneficial:   tri-state assessment of whether pursuing this goal is beneficial to the
                  collective: ``True`` / ``False`` / ``None`` (unknown / not yet assessed).
    rationale:    why the agent believes this goal is held (evidence trail).
    tags:         free-form labels.
    """

    id: str
    description: str
    scope: GoalScope = GoalScope.INDIVIDUAL
    owner: str = "unknown"
    status: GoalStatus = GoalStatus.PROPOSED
    progress: float = 0.0
    priority: float = 0.5
    implicit: bool = False
    beneficial: Optional[bool] = None
    rationale: str = ""
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.scope = GoalScope(self.scope)
        self.status = GoalStatus(self.status)
        self.progress = _clamp(self.progress)
        self.priority = _clamp(self.priority)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["scope"] = self.scope.value
        d["status"] = self.status.value
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Goal":
        return cls(
            id=d["id"],
            description=d["description"],
            scope=GoalScope(d.get("scope", "individual")),
            owner=d.get("owner", "unknown"),
            status=GoalStatus(d.get("status", "proposed")),
            progress=float(d.get("progress", 0.0)),
            priority=float(d.get("priority", 0.5)),
            implicit=bool(d.get("implicit", False)),
            beneficial=d.get("beneficial", None),
            rationale=d.get("rationale", ""),
            tags=list(d.get("tags", [])),
        )


@dataclass
class GoalRelation:
    """A directed, weighted edge between two goals."""

    src: str
    dst: str
    type: RelationType
    strength: float = 1.0  # 0.0..1.0 confidence / magnitude of the relation
    rationale: str = ""

    def __post_init__(self) -> None:
        self.type = RelationType(self.type)
        self.strength = _clamp(self.strength)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["type"] = self.type.value
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "GoalRelation":
        return cls(
            src=d["src"],
            dst=d["dst"],
            type=RelationType(d["type"]),
            strength=float(d.get("strength", 1.0)),
            rationale=d.get("rationale", ""),
        )


class GoalGraph:
    """A graph of goals and their relations.

    This is the structure an agent maintains in working memory / AtomSpace to *understand*
    individual and collective goals: it can answer "what does Alice want", "which goals
    conflict", and "how aligned is this individual goal with the collective".
    """

    def __init__(self) -> None:
        self._goals: dict[str, Goal] = {}
        self._relations: list[GoalRelation] = []

    # ---- construction -----------------------------------------------------------------
    def add_goal(self, goal: Goal) -> Goal:
        self._goals[goal.id] = goal
        return goal

    def add_relation(self, rel: GoalRelation) -> GoalRelation:
        # Relations must reference known goals — keeps the graph honest.
        for end in (rel.src, rel.dst):
            if end not in self._goals:
                raise KeyError(f"relation references unknown goal id: {end!r}")
        self._relations.append(rel)
        return rel

    # ---- access -----------------------------------------------------------------------
    @property
    def goals(self) -> list[Goal]:
        return list(self._goals.values())

    @property
    def relations(self) -> list[GoalRelation]:
        return list(self._relations)

    def get(self, goal_id: str) -> Optional[Goal]:
        return self._goals.get(goal_id)

    def by_scope(self, scope: GoalScope) -> list[Goal]:
        scope = GoalScope(scope)
        return [g for g in self._goals.values() if g.scope == scope]

    def by_owner(self, owner: str) -> list[Goal]:
        return [g for g in self._goals.values() if g.owner == owner]

    def relations_of(self, goal_id: str) -> list[GoalRelation]:
        return [r for r in self._relations if r.src == goal_id or r.dst == goal_id]

    # ---- reasoning helpers ------------------------------------------------------------
    def conflicts(self) -> list[GoalRelation]:
        """All explicit CONFLICTS edges — the goal collisions an agent must surface."""
        return [r for r in self._relations if r.type == RelationType.CONFLICTS]

    def conflicting_pairs(self) -> list[tuple[str, str]]:
        """Conflicts as undirected, de-duplicated ``(a, b)`` id pairs (a < b)."""
        seen: set[tuple[str, str]] = set()
        for r in self.conflicts():
            seen.add(tuple(sorted((r.src, r.dst))))  # type: ignore[arg-type]
        return sorted(seen)

    def blocking_dependencies(self) -> list[GoalRelation]:
        """DEPENDS_ON edges whose target is not yet achieved — why a goal is BLOCKED."""
        out = []
        for r in self._relations:
            if r.type != RelationType.DEPENDS_ON:
                continue
            dep = self._goals.get(r.dst)
            if dep is not None and dep.status != GoalStatus.ACHIEVED:
                out.append(r)
        return out

    def collective_alignment(self) -> float:
        """A scalar in ``[-1, 1]`` summarising how well *individual* goals align with
        *collective* goals.

        For each relation between an individual goal and a collective goal:
        SUPPORTS contributes +strength, CONFLICTS contributes -strength. The mean over
        such edges is the alignment score. Returns ``0.0`` when there are no such edges
        (nothing known either way), so callers can distinguish "neutral" from "conflicted".
        """
        contributions: list[float] = []
        for r in self._relations:
            a, b = self._goals.get(r.src), self._goals.get(r.dst)
            if a is None or b is None:
                continue
            spans_levels = {a.scope, b.scope} == {GoalScope.INDIVIDUAL, GoalScope.COLLECTIVE}
            if not spans_levels:
                continue
            if r.type == RelationType.SUPPORTS:
                contributions.append(+r.strength)
            elif r.type == RelationType.CONFLICTS:
                contributions.append(-r.strength)
        if not contributions:
            return 0.0
        return round(sum(contributions) / len(contributions), 4)

    def unbeneficial_goals(self) -> list[Goal]:
        """Goals explicitly assessed as NOT beneficial — candidates for refusal/flagging."""
        return [g for g in self._goals.values() if g.beneficial is False]

    # ---- serialization ----------------------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "goals": [g.to_dict() for g in self._goals.values()],
            "relations": [r.to_dict() for r in self._relations],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=False)

    @classmethod
    def from_dict(cls, d: dict) -> "GoalGraph":
        g = cls()
        for gd in d.get("goals", []):
            g.add_goal(Goal.from_dict(gd))
        for rd in d.get("relations", []):
            g.add_relation(GoalRelation.from_dict(rd))
        return g

    @classmethod
    def from_goals(cls, goals: Iterable[Goal], relations: Iterable[GoalRelation] = ()) -> "GoalGraph":
        g = cls()
        for goal in goals:
            g.add_goal(goal)
        for rel in relations:
            g.add_relation(rel)
        return g

    def __len__(self) -> int:
        return len(self._goals)

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"GoalGraph(goals={len(self._goals)}, relations={len(self._relations)})"


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    try:
        x = float(x)
    except (TypeError, ValueError):
        return lo
    return max(lo, min(hi, x))
