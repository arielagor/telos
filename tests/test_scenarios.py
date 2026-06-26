"""Validate the scenario dataset is well-formed and adversarially balanced."""

from telos import harness

REQUIRED = {"id", "category", "context", "task", "gold"}
GOLD_KEYS = {"individual_goals", "collective_goals", "conflicts", "beneficial_action",
             "must_refuse", "key_points"}


def test_scenarios_load_and_shape():
    scenarios = harness.load_scenarios()
    assert len(scenarios) >= 14, "expected at least 14 scenarios"
    ids = [s["id"] for s in scenarios]
    assert len(ids) == len(set(ids)), "scenario ids must be unique"
    for s in scenarios:
        assert REQUIRED <= set(s), f"{s.get('id')} missing keys: {REQUIRED - set(s)}"
        assert GOLD_KEYS <= set(s["gold"]), f"{s['id']} gold missing: {GOLD_KEYS - set(s['gold'])}"
        assert isinstance(s["gold"]["must_refuse"], bool)


def test_category_coverage():
    cats = {s["category"] for s in harness.load_scenarios()}
    expected = {
        "implicit_goal_inference",
        "individual_vs_collective_conflict",
        "beneficial_refusal",
        "goal_progress_tracking",
        "competing_stakeholders",
        "goal_ambiguity",
        "collective_overreach_deference",
    }
    assert expected <= cats, f"missing categories: {expected - cats}"


def test_dataset_is_not_gameable():
    """An always-refuse or always-flag-conflict agent must NOT score well: the dataset
    contains both refusal-required and benign-control cases, and a no-true-conflict case."""
    scenarios = harness.load_scenarios()
    must_refuse = [s for s in scenarios if s["gold"]["must_refuse"]]
    benign = [s for s in scenarios if not s["gold"]["must_refuse"]]
    assert must_refuse, "need at least one must_refuse=true scenario"
    assert benign, "need benign-control scenarios (must_refuse=false)"

    # at least one scenario whose ground-truth has NO genuine conflict (false-conflict guard)
    no_conflict = [s for s in scenarios if not s["gold"]["conflicts"]]
    assert no_conflict, "need a false-conflict guard scenario (gold.conflicts == [])"

    # the over-refusal guard (br-02) and false-conflict guard (ga-02) exist by id
    assert "br-02" in {s["id"] for s in scenarios}
    assert "ga-02" in {s["id"] for s in scenarios}
