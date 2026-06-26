# Spec-diff gate — BGI Sprint requirements vs. Telos deliverables

The PROVN methodology requires grepping every stated requirement against the deliverables
before submission. **Any miss is a blocker.** Requirements are quoted from the BGI Sprint I
hackathon page.

## Hard rules

| # | Requirement (verbatim / paraphrased from the page) | Satisfied by | Status |
|---|---|---|---|
| 1 | "Every team must produce a **concrete artifact**. Discussion alone is not a valid final submission." | A runnable Python package + benchmark + council + MeTTa module + docs, public at `github.com/arielagor/telos`. | ✅ |
| 2 | Contribution must fit a **track**. | Track: **Improvements to OmegaClaw** — the artifact is a goal-tracking mechanism + benchmark + evaluation/validation framework (three of the track's named example areas). | ✅ |
| 3 | "Clearly **define the problem** being solved." | README "Why" + `docs/architecture.md` "The problem" — the five goal-understanding failure modes. | ✅ |
| 4 | "Explain how the improvement **fits into OmegaClaw**." | `docs/integration-omegaclaw.md` (three integration levels, mapped to OmegaClaw's actual modules) + a verified MeTTa AtomSpace mirror. | ✅ |
| 5 | "Provide **acceptance criteria or evidence** that the contribution works." | This gate + green `pytest` suite + real benchmark numbers in `results/` + the MeTTa file executing on Hyperon. | ✅ |
| 6 | "Useful, **maintainable**" / "does not risk the core architecture." | Zero-runtime-dependency core; optional, plugin-style extension; touches nothing in OmegaClaw's core loop. | ✅ |
| 7 | Submit deliverable links before **Jun 28, 7:00 PM** (editable until then). | Submitted via the dashboard (Track + repo + docs links). | ⏳ at submit step |

## Track-fit detail (Improvements to OmegaClaw example areas)

| Track example area | Telos component |
|---|---|
| "Goal-setting or goal-tracking mechanisms" | `telos/schema.py` goal graph + `telos/metta/goal_graph.metta` |
| "Benchmarking and evaluation tools" | `telos/scenarios/` + `harness.py` + `bench.py` |
| "Tests, metrics, or validation frameworks" | `judge.py` (5 metrics) + `tests/` (pytest) |
| "Flaw detection and correction workflows" | the Beneficial Council's adversarial red-team (`council.py`) |
| "Plugin-like extensions that do not risk the core architecture" | optional package; core untouched (see integration doc) |

## "What success looks like" (track rubric, verbatim)

> "A contribution improves OmegaClaw in a concrete and measurable way, while remaining safe,
> understandable, and maintainable for the core team and future community contributors."

- **Concrete & measurable** — a benchmark that outputs numbers; baseline results included.
- **Safe** — adds an alignment safeguard (beneficial-refusal + the council); core untouched.
- **Understandable** — `docs/architecture.md` is a from-scratch explainer (also serves the
  onboarding track).
- **Maintainable** — zero deps, tested, MIT-licensed, small surface.

## Honesty ledger (claims vs. evidence)

| Claim | Evidence | Verified? |
|---|---|---|
| Goal graph works | `tests/test_schema.py` | ✅ green |
| Benchmark runs & scores | `results/generic-*.json`, `results/LEADERBOARD.md` | ✅ real run |
| Council deliberates across 3 families | `results/council/*.json` | ✅ transcripts |
| MeTTa representation runs in OmegaClaw's symbolic layer | `tests/test_metta.py` on Hyperon | ✅ executes |
| Live end-to-end OmegaClaw integration | needs a configured Hyperon/OmegaClaw instance | ⚠️ described, adapter reports "not connected" rather than faking a score |

No requirement is currently a miss. The only open item is the submission action itself.
