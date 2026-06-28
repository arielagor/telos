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

## What this proves (and what it doesn't)

- **Proves:** the Telos goal representation + a derivation rule are valid in OmegaClaw's *live*
  MeTTa runtime, not just the reference Hyperon interpreter. The schema "lives" in the agent's
  AtomSpace and the rule fires there. That is integration level 2 from
  `docs/integration-omegaclaw.md` ("load the goal graph into the live runtime").
- **Honest bounds:** this is AtomSpace **pattern-matching, not NAL or PLN inference**, and the
  goal atoms were asserted explicitly (the example graph) rather than auto-extracted from arbitrary
  input by the agent. Closing that last loop — the agent reading free text and materialising its own
  goal atoms for these rules to fire on — is the next step.

## Reproduce

```bash
# 1) start the agent (see docs/omegaclaw-windows-setup.md for the full recipe)
# 2) over the mock-comm bridge, send the four `metta` lines above
# 3) read the agent log: docker logs omegaclaw 2>&1 | grep conflict-between
```
