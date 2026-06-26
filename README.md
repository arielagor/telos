# Telos

**A goal-understanding & alignment benchmark + toolkit for OmegaClaw and other
goal-autonomous agents.**

*BGI Sprint I — track: Improvements to OmegaClaw. Built, reviewed, and submitted autonomously
by a cross-family AI council (Claude + Gemini + OpenAI), with no human in the loop.*

---

## Why

The sprint theme is **AI agents that understand our individual and collective goals.**
[OmegaClaw](https://github.com/asi-alliance/OmegaClaw-Core) is a strong substrate for this — it
is *goal-autonomous*: it creates goals, pursues them, and tracks progress on its own. But it
ships **no explicit goal-representation or goal-tracking module**, and "understanding goals" is
exactly where an autonomous agent is most dangerous when it is subtly wrong:

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
| `telos/schema.py` | a small, dependency-free **goal graph**: individual vs collective goals, four relation types (`supports/conflicts/subsumes/depends_on`), progress, blocking, and an individual↔collective **alignment** score. Fills OmegaClaw's missing goal module. |
| `telos/scenarios/` | a **14-scenario, 7-category benchmark** with gold labels (see below). |
| `telos/harness.py`, `judge.py`, `bench.py` | run an agent over the scenarios and **score** it. |
| `telos/council.py` | the **Beneficial Council** — cross-family deliberation + adversarial red-team. The benchmark's judge, a shippable alignment safeguard, and the engine that built this repo. |
| `telos/adapters/` | `generic_llm` (benchmark any model) + `omegaclaw` (benchmark OmegaClaw itself). |
| `telos/metta/goal_graph.metta` | the **AtomSpace/MeTTa mirror** — runs on Hyperon, so the goal graph lives in OmegaClaw's symbolic layer for NAL/PLN to reason over. |
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

The dataset is built to be **un-gameable**: always-refuse fails the benign twins, always-flag
fails the false-conflict guard, and a paternalistic agent fails category 7. Scoring uses a
deterministic refusal gate on genuine-harm cases plus a **cross-family council** for the nuanced
dimensions — with the agent's **own family excluded from its jury** to remove self-preference.

## Results (baseline frontier models)

Each model is scored as the agent-under-test and judged by the *other* families. Numbers are
from an actual run (`results/`), reproducible with `bash scripts/run_baselines.sh`.

| agent | overall | goal_inf | scope | conflict | collective | refusal | refusal_acc | n |
|---|---|---|---|---|---|---|---|---|
| `claude-opus-4-8` | **0.937** | 0.959 | 0.891 | 0.845 | 0.989 | 0.998 | 1.00 | 14 |
| `gpt-5.5` | **0.911** | 0.940 | 0.843 | 0.796 | 0.968 | 1.000 | 1.00 | 14 |
| `gemini-3.1-pro-preview` | **0.902** | 0.911 | 0.882 | 0.816 | 0.905 | 0.998 | 1.00 | 14 |

Dimensions: `goal_inf` (goal inference) · `scope` (individual/collective) · `conflict`
(conflict detection) · `collective` (collective-beneficial action) · `refusal` (beneficial
refusal) · `refusal_acc` (decisive-case refusal accuracy). Run: 2026-06-26, judged by the
cross-family council with each agent's own family excluded from its jury.

**What the numbers say.** Frontier models are strong at recommending collectively-beneficial
actions and at the decisive refusal calls (1.00), but **conflict detection is the hardest
dimension for every model** (0.80–0.85) — they more often miss a real goal collision or invent
a spurious one. That is exactly the kind of goal-understanding weakness a goal-autonomous agent
like OmegaClaw needs measured before it acts on its own.

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

OmegaClaw is goal-autonomous but has no goal module. Telos supplies one in OmegaClaw's own
idiom: a MeTTa goal graph for the AtomSpace (verified running on Hyperon), a benchmark that can
gate `Autotests/`, and a council that can sit in the `proxy/` layer as a beneficial check.
Three integration levels and a staged upstream PR are described in
[`docs/integration-omegaclaw.md`](docs/integration-omegaclaw.md).

## Built with no human in the loop

This repository was conceived, designed, built, adversarially reviewed, and submitted by AI
agents — a small, transparent case study in beneficial autonomous agency. The council caught a
real design flaw mid-build (an early framing that selected for a *paternalistic optimiser*) and
the benchmark corrected its own refusal semantics on first run. Full account:
[`docs/case-study-autonomous-build.md`](docs/case-study-autonomous-build.md) and
[`AI_USAGE.md`](AI_USAGE.md). Council transcripts live in `results/council/`.

## License

MIT — see [LICENSE](LICENSE). Compatible with OmegaClaw-Core (also MIT).
