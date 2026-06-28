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


# The reusable, parameterized module — the exact file offered upstream as lib_telos_goals.metta
# (PR asi-alliance/OmegaClaw-Core#218). Covers each NAMED rule, not a hard-coded example, so a
# maintainer who imports the module gets the same derivations we claim.
MODULE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                           "telos", "metta", "omegaclaw_goal_module.metta")

_DRIVER = """
(goal alice-train individual alice active)
(goal dao-fair-access collective dao active)
(rel conflicts alice-train dao-fair-access)
(goal gpu-quota collective dao proposed)
(rel depends-on dao-fair-access gpu-quota)
!(telos-conflicts)
!(telos-collective-goals)
!(telos-blocked)
"""


def test_omegaclaw_goal_module_named_rules_derive():
    """Load the upstream module and exercise each named rule (telos-conflicts /
    telos-collective-goals / telos-blocked, incl. the nested match+if), so PR #218 is
    proven to run, not just to parse. Mirrors results/omegaclaw-metta-load.log."""
    from hyperon import MeTTa

    src = open(MODULE_FILE, encoding="utf-8").read() + "\n" + _DRIVER
    results = MeTTa().run(src)
    flat = [str(a) for group in results for a in group]
    assert any("conflict-between alice-train dao-fair-access" in s for s in flat)
    assert any("collective-goal dao-fair-access dao" in s for s in flat)
    # telos-blocked nests a match inside a match with an if-guard; this is the rule most
    # likely to error on a maintainer's interpreter, so assert it derives.
    assert any("blocked dao-fair-access on gpu-quota" in s for s in flat)
