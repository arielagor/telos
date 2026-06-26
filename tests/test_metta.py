"""Validate the MeTTa AtomSpace representation actually runs on Hyperon.

Skipped automatically when hyperon is not installed (so CI stays light), but run in the
authoring environment to keep the OmegaClaw-fit claim honest.
"""

import os

import pytest

hyperon = pytest.importorskip("hyperon")

METTA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                          "telos", "metta", "goal_graph.metta")


def test_goal_graph_metta_runs_and_finds_conflict():
    from hyperon import MeTTa

    src = open(METTA_FILE, encoding="utf-8").read()
    results = MeTTa().run(src)
    flat = [str(a) for group in results for a in group]
    # conflict detection query must surface the individual-vs-collective conflict
    assert any("conflict-between alice-train dao-fair-access" in s for s in flat)
    # collective-goal query must surface a collective goal
    assert any("collective-goal" in s for s in flat)
    # dependency query must surface the blocked grant proposal's dependency
    assert any("depends grant-proposal on budget-table" in s for s in flat)
