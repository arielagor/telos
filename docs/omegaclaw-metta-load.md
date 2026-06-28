# Proof — the Telos goal module loads and derives in the LIVE OmegaClaw AtomSpace

This is the concrete evidence behind the claim "integration level 2 demonstrated." The Telos
goal schema + a derivation rule were driven into the **running** `singularitynet/omegaclaw:latest`
agent (its PeTTa / SWI-Prolog MeTTa engine), and the query derived the conflict **in the live
AtomSpace** — not the standalone Hyperon interpreter the unit test uses.

## How it was done

The live agent was driven over its own mock-comm channel (see `scripts/omegaclaw_bridge.py`) and
asked to run these through its built-in **`metta`** skill, one per line:

```
metta (goal alice-train individual alice active)
metta (goal dao-fair-access collective dao active)
metta (rel conflicts alice-train dao-fair-access)
metta !(match &self (rel conflicts $a $b) (conflict-between $a $b))
```

The first three assert goal/rel atoms into the agent's `&self` AtomSpace; the fourth is the Telos
conflict-detection rule (the same one in `telos/metta/omegaclaw_goal_module.metta`).

## Result (from the live agent's log)

```
metta (goal alice-train individual alice active)
metta (goal dao-fair-access collective dao active)
metta (rel conflicts alice-train dao-fair-access)
metta !(match &self (rel conflicts $a $b) (conflict-between $a $b))
-> conflict-between alice-train dao-fair-access
```

The agent's running engine returned **`conflict-between alice-train dao-fair-access`** — the
individual-vs-collective conflict, derived symbolically inside OmegaClaw at runtime.

## The named module rules + a NAL deduction (committed log)

The line above drove *inline* atoms + a `match` query. To show the **named rules** the upstream
PR ships (`lib_telos_goals.metta` = `telos/metta/omegaclaw_goal_module.metta`) actually run — and
to go one step past pattern-matching — we ran them, plus a Non-Axiomatic Logic deduction, directly
in OmegaClaw's PeTTa engine (`cd /PeTTa && sh run.sh`). Full transcript:
[`results/omegaclaw-metta-load.log`](../results/omegaclaw-metta-load.log). The derived results:

```
(conflict-between alice-train dao-fair-access)            ; telos-conflicts
(collective-goal dao-fair-access dao)                    ; telos-collective-goals
(collective-goal gpu-quota dao)                          ; telos-collective-goals
(blocked dao-fair-access on gpu-quota)                   ; telos-blocked  (nested match + if)
((--> alice-train needs-reconciliation) (stv 1.0 0.81)) ; NAL deduction (lib_nal Truth_Deduction)
```

The last line is a real **NAL inference** over goal terms: chaining "alice-train is a conflicted
goal" with "conflicted goals need reconciliation" through `lib_nal`'s deduction rule yields the
conclusion with a computed non-axiomatic truth value (confidence 0.9 * 0.9 = **0.81**), not a
boolean match. `tests/test_metta.py::test_omegaclaw_goal_module_named_rules_derive` pins the three
named rules on Hyperon so the PR can't regress.

## What this proves (and what it doesn't)

- **Proves:** the Telos goal representation, the **named module rules** (incl. the nested
  `telos-blocked`), and a NAL deduction over goal terms all run in OmegaClaw's MeTTa runtime, not
  just the reference Hyperon interpreter. That is integration level 2 from
  `docs/integration-omegaclaw.md` ("load the goal graph into the live runtime").
- **Honest bounds:** the conflict/collective/blocked rules are AtomSpace **pattern-matching**; the
  NAL step is **one hand-built deduction**, not yet wired into the module's pipeline. And the goal
  atoms were asserted explicitly (the example graph) rather than auto-extracted from arbitrary
  input. Closing those loops — the agent reading free text, materialising its own goal atoms, and
  routing conflicts through NAL/PLN automatically — is the next step.

## Reproduce

```bash
# 1) start the agent (see docs/omegaclaw-windows-setup.md for the full recipe)
# 2) over the mock-comm bridge, send the four `metta` lines above
# 3) read the agent log: docker logs omegaclaw 2>&1 | grep conflict-between
```
