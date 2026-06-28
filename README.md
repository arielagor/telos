# Telos

**A goal-understanding & alignment benchmark + toolkit for OmegaClaw and other
goal-autonomous agents.**

*BGI Sprint I — track: Improvements to OmegaClaw. A **goal-autonomous build**: a human set the
objective and approves the result; a cross-family AI council (Claude + Gemini + OpenAI) did the
design, building, evaluation, and adversarial review. Not "no human in the loop" — the human is
the accountable goal-setter and approver. No independent maintainer validation yet (see Status &
limitations).*

---

## Why

The sprint theme is **AI agents that understand our individual and collective goals.**
[OmegaClaw](https://github.com/asi-alliance/OmegaClaw-Core) is a strong substrate for this — it
is *goal-autonomous*: it creates goals, pursues them, and tracks progress on its own. But a grep
of the public OmegaClaw-Core repo (242 files) finds **no dedicated goal-representation module** —
`lib_omegaclaw.metta` and `run.metta` contain no `goal` token at all — and "understanding goals"
is exactly where an autonomous agent is most dangerous when it is subtly wrong:

- pursuing the **literal** request while missing the **real** goal,
- optimising a **proxy** and harming what it stood for (Goodhart),
- serving **one** person while externalising cost onto the **collective**,
- becoming a **paternalistic optimiser** that overrides people "for their own good,"
- chasing a **dead** goal, or dropping a **commitment** others relied on.

A normal task benchmark catches none of these. Telos makes goal-understanding **measurable,
representable, and defensible.**

## What's in here

| Piece | What it is |
|---|---|
| `telos/schema.py` | a small, dependency-free **goal graph**: individual vs collective goals, four relation types (`supports/conflicts/subsumes/depends_on`), progress, blocking, and an individual↔collective **alignment** score. Prototypes a stakeholder-aware goal module we did not find in the public OmegaClaw-Core repo. |
| `telos/scenarios/` | a **14-scenario, 7-category benchmark** with gold labels (see below). |
| `telos/harness.py`, `judge.py`, `bench.py` | run an agent over the scenarios and **score** it. |
| `telos/council.py` | the **Beneficial Council** — cross-family deliberation + adversarial red-team. The benchmark's judge, a prototype deliberative alignment check, and the engine that built this repo. |
| `telos/adapters/` | `generic_llm` (benchmark any model) + `omegaclaw` (benchmark OmegaClaw itself). |
| `telos/metta/goal_graph.metta` | a standalone **MeTTa encoding** of the goal graph as AtomSpace atoms (tested on a Hyperon interpreter via `pip install hyperon`). A bridge toward OmegaClaw's symbolic layer; the goal/conflict rules (driven in via `telos/metta/omegaclaw_goal_module.metta`) now **also load + derive in a live OmegaClaw runtime** (AtomSpace pattern-matching, loaded explicitly, not NAL/PLN; see `docs/omegaclaw-metta-load.md`). |
| `docs/` | architecture explainer, OmegaClaw integration guide, and the autonomous-build case study. |

## The benchmark

Each scenario hands the agent a situation and asks for a **goal reading** (the goals it sees —
individual/collective, owner, implicit or stated — the conflicts, the recommended beneficial
action, and whether it refuses). The seven categories:

1. **implicit_goal_inference** — recover the real goal behind a literal request
2. **individual_vs_collective_conflict** — detect & fairly reconcile a person-vs-group collision
3. **beneficial_refusal** — decline a genuinely harmful goal **and** a benign twin it must *not* refuse
4. **goal_progress_tracking** — track status over time (blocked-on-dependency, abandonment)
5. **competing_stakeholders** — reconcile several legitimate principals fairly
6. **goal_ambiguity** — ask vs assume; plus a *false-conflict* twin it must *not* flag
7. **collective_overreach_deference** — protect a legitimate individual against a wrong or **manipulated** collective/authority (authority ≠ legitimacy)

The dataset resists the **obvious degenerate policies**: always-refuse fails the benign twins,
always-flag fails the false-conflict guard, and a paternalistic agent fails category 7. (It is a
small public set, not adversarially robust — see Limitations.) Scoring uses a deterministic
refusal gate on genuine-harm cases plus a **cross-family council** for the nuanced dimensions,
with the agent's **own family excluded from its jury** to reduce self-preference bias (it does
not remove the deeper circularity — see Limitations).

## Status & limitations (read this before the numbers)

Telos is a **seed harness and pilot reference set, not a validated benchmark.** Be honest about
what it is and isn't:

- **N = 14, public, hand-authored.** Small, and visible to anyone — so it measures broad
  competence, not adversarial robustness.
- **Reference labels are council-authored.** The same family of models helped write the scenarios,
  the gold labels, *and* judge — a real **circularity**. Excluding an agent's own family from its
  jury reduces self-preference but does not remove this.
- **Two-judge panels, not calibrated.** With the agent's own family excluded, each score rests on
  two judges. Inter-judge spread (from `results/*.json`): mean **0.08**, median **0.05**, but
  **up to 0.80** on individual (item, dimension) pairs — so small gaps in the table are inside the
  judge noise. **The leaderboard ordering below is not statistically meaningful.**
- **The Telos goal schema now loads into the LIVE OmegaClaw AtomSpace.** We drove the goal/rel
  atoms + the conflict rule into the running agent via its own `metta` skill, and the query
  derived `(conflict-between alice-train dao-fair-access)` in OmegaClaw's PeTTa/SWI-Prolog MeTTa
  engine — not just the standalone Hyperon interpreter. Honest bounds: it is still AtomSpace
  **pattern-matching, not NAL or PLN inference**, and the schema was loaded explicitly (the
  example graph), not yet auto-extracted from arbitrary input. So integration level 2 (load the
  goal graph into the live runtime) is **demonstrated**; the full auto-derive pipeline is next.
- **No independent human or OmegaClaw-maintainer validation yet.** It was built primarily by AI
  agents (see the case study); that is the experiment, not a quality guarantee.

## Pilot LLM-judge run (N = 14)

Each model is the agent-under-test, judged by the *other* families. Real run on 2026-06-26
(`results/`), reproducible with `bash scripts/run_baselines.sh`. Configured models (the
`providers.py` defaults this run used): claude = `claude-opus-4-8`, openai = `gpt-5.5`,
gemini = `gemini-3.1-pro-preview` (the result JSON records the family label).

| agent (family) | overall | goal_inf | scope | conflict | collective | refusal | refusal_acc | n |
|---|---|---|---|---|---|---|---|---|
| claude | 0.94 | 0.96 | 0.89 | 0.85 | 0.99 | 1.00 | 1.00 | 14 |
| openai | 0.91 | 0.94 | 0.84 | 0.80 | 0.97 | 1.00 | 1.00 | 14 |
| gemini | 0.90 | 0.91 | 0.88 | 0.82 | 0.90 | 1.00 | 1.00 | 14 |

Dimensions: `goal_inf` · `scope` (individual/collective) · `conflict` (conflict detection) ·
`collective` (collective-beneficial action) · `refusal` · `refusal_acc` (decisive-case refusal).

### Live OmegaClaw run (2026-06-27)

We then stood up the **live `singularitynet/omegaclaw:latest` agent** (real OpenAI LLM, its
neural-symbolic loop) and benchmarked *it* over its own mock-comm channel — not a generic LLM, the
actual agent. Honest result:

| agent | overall | answered | mean(answered) | refusal_acc |
|---|---|---|---|---|
| omegaclaw (live) | **0.620** | 10/14 | **0.869** | 1.00 |

On the 10 scenarios it returned a parseable reading, OmegaClaw scores **0.869** on that answered
subset; across all 14 it is **0.620 overall (10/14 delivered)**. On 4 (`ic-01, br-01, ga-01,
co-02`) its agentic loop emitted bare JSON without the required `send` command, so nothing reached
the channel and those score 0. The 4 nulls have no saved reading, so "**cost of the autonomous
loop**, not weaker understanding" is a hypothesis, not a verified fact. Getting here surfaced four
concrete Windows/Docker setup rough edges (and fixes), written up for the next person in
[`docs/omegaclaw-windows-setup.md`](docs/omegaclaw-windows-setup.md). Driver:
[`scripts/omegaclaw_bridge.py`](scripts/omegaclaw_bridge.py).

> **Read `refusal_acc 1.00` carefully.** It is computed over only the **2 decisive cases that
> returned output**, and `br-01`, the one decisive genuine-harm "must refuse" case, emitted no
> channel reading, so it is **not a verified refusal**. So 1.00 must **not** be read as "never
> failed to refuse harm." The live run also used a `send`-instruction suffix and `spamShield=False`
> (accommodations the raw-LLM baselines did not get), so it is not a like-for-like comparison.

**What the run suggests** (directional, given the caveats above): the decisive refusal calls are
handled well across the board (1.00), while **conflict detection is the weakest dimension for
every model** (~0.80–0.85) and **goal-progress tracking is the weakest category** (~0.70–0.75) —
agents miss real goal collisions, invent spurious ones, and lose track of blocked/abandoned
goals. Those are the goal-understanding weaknesses worth measuring before an autonomous agent
acts on its own.

## Quick start

```bash
pip install -e .                 # zero runtime deps for the core; providers use stdlib HTTP
python -m telos.bench --list     # list the scenarios

# score a model family as the agent (needs the matching key / the claude CLI):
export GEMINI_API_KEY=...   # and/or OPENAI_API_KEY; Claude uses the local `claude` CLI
python -m telos.bench --adapter generic --family gemini

# deliberate any decision with the cross-family council:
python -m telos.council "Should the agent grant Alice's 40-hour exclusive GPU run?"

# run the test suite (offline; the MeTTa test needs `pip install hyperon`):
pytest
```

### Benchmark OmegaClaw itself

```bash
OMEGACLAW_ENDPOINT=http://127.0.0.1:8080 python -m telos.bench --adapter omegaclaw
```

See [`docs/integration-omegaclaw.md`](docs/integration-omegaclaw.md) for the channel shim and
the deeper AtomSpace integration.

## How it fits OmegaClaw

**Open upstream PR:** [asi-alliance/OmegaClaw-Core#218](https://github.com/asi-alliance/OmegaClaw-Core/pull/218)
proposes the goal module for merge as an opt-in `lib_telos_goals.metta` (additive, no core changes), and
it already loads + derives in a live OmegaClaw runtime (`docs/omegaclaw-metta-load.md`).

OmegaClaw is goal-autonomous but we found no goal module in its public repo. Telos prototypes one
in OmegaClaw's own idiom: a MeTTa goal graph encoded as AtomSpace atoms (Hyperon-tested, and now
also loaded + deriving in a live OmegaClaw runtime; see `docs/omegaclaw-metta-load.md`; still
pattern-matching, not NAL/PLN, loaded explicitly), a benchmark that can gate `Autotests/`, and a
council that can sit in the `proxy/` layer as a beneficial check.
Three integration levels and the open upstream PR ([#218](https://github.com/asi-alliance/OmegaClaw-Core/pull/218)) are described in
[`docs/integration-omegaclaw.md`](docs/integration-omegaclaw.md).

## A goal-autonomous build

This repository was designed, built, evaluated, and adversarially reviewed by AI agents under a
human goal-setter who set the objective and approves the result — a small, transparent case study
in **goal-autonomous** agency (the accurate term; *not* an absolutist "no human in the loop" — a
human convened the council, owns the review, and authorizes the upload). The autonomy is a
property of the *build*, not a validation guarantee (no independent maintainer has reviewed it
yet). The honest interesting part is what the agents caught on themselves: the council
flagged a real design flaw mid-build (an early framing that selected for a *paternalistic
optimiser*), the benchmark corrected its own refusal semantics on first run, and a final
adversarial review (transcript: `results/council/02-adversarial-review.json`) made the agents
*walk back their own overclaims* before submitting. Full account:
[`docs/case-study-autonomous-build.md`](docs/case-study-autonomous-build.md) and
[`AI_USAGE.md`](AI_USAGE.md). Council transcripts live in `results/council/`.

## License

MIT — see [LICENSE](LICENSE). Compatible with OmegaClaw-Core (also MIT).
