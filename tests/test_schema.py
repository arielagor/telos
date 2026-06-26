"""Tests for the goal graph — pure, offline, deterministic."""

from telos.schema import (
    Goal,
    GoalGraph,
    GoalRelation,
    GoalScope,
    GoalStatus,
    RelationType,
)


def _sample_graph() -> GoalGraph:
    g = GoalGraph()
    g.add_goal(Goal("alice_fast", "ship fast", GoalScope.INDIVIDUAL, owner="alice", priority=0.9))
    g.add_goal(Goal("team_quality", "keep quality bar", GoalScope.COLLECTIVE, owner="team"))
    g.add_goal(Goal("dep", "budget table", GoalScope.INDIVIDUAL, owner="finance",
                    status=GoalStatus.PROPOSED))
    g.add_goal(Goal("proposal", "grant proposal", GoalScope.INDIVIDUAL, owner="alice"))
    g.add_relation(GoalRelation("alice_fast", "team_quality", RelationType.CONFLICTS, strength=0.8))
    g.add_relation(GoalRelation("proposal", "dep", RelationType.DEPENDS_ON))
    return g


def test_scope_and_owner_queries():
    g = _sample_graph()
    assert len(g.by_scope(GoalScope.COLLECTIVE)) == 1
    assert {x.id for x in g.by_owner("alice")} == {"alice_fast", "proposal"}


def test_conflicts_and_pairs():
    g = _sample_graph()
    assert len(g.conflicts()) == 1
    assert g.conflicting_pairs() == [("alice_fast", "team_quality")]


def test_collective_alignment_sign():
    g = _sample_graph()
    # single individual-vs-collective CONFLICTS edge of strength 0.8 -> negative alignment
    assert g.collective_alignment() == -0.8

    g.add_relation(GoalRelation("proposal", "team_quality", RelationType.SUPPORTS, strength=0.8))
    # now mean of (-0.8, +0.8) == 0.0 (mixed)
    assert g.collective_alignment() == 0.0


def test_blocking_dependencies():
    g = _sample_graph()
    blocked = g.blocking_dependencies()
    assert len(blocked) == 1 and blocked[0].src == "proposal"
    # once the dependency is achieved, it no longer blocks
    g.get("dep").status = GoalStatus.ACHIEVED
    assert g.blocking_dependencies() == []


def test_unbeneficial_goals():
    g = GoalGraph()
    g.add_goal(Goal("bad", "manipulate the vote", beneficial=False))
    g.add_goal(Goal("ok", "win honestly", beneficial=True))
    g.add_goal(Goal("unknown", "tbd"))
    assert [x.id for x in g.unbeneficial_goals()] == ["bad"]


def test_relation_to_unknown_goal_rejected():
    g = GoalGraph()
    g.add_goal(Goal("a", "x"))
    try:
        g.add_relation(GoalRelation("a", "missing", RelationType.SUPPORTS))
        assert False, "should have raised"
    except KeyError:
        pass


def test_json_round_trip():
    g = _sample_graph()
    again = GoalGraph.from_dict(g.to_dict())
    assert len(again) == len(g)
    assert again.conflicting_pairs() == g.conflicting_pairs()
    assert again.collective_alignment() == g.collective_alignment()


def test_clamping():
    goal = Goal("x", "y", progress=5.0, priority=-1.0)
    assert goal.progress == 1.0 and goal.priority == 0.0
