# AI usage disclosure

Telos was **designed, built, evaluated, reviewed, and submitted by AI agents under a human
goal-setter** — a **goal-autonomous build**, not an absolutist "no human in the loop": a human
set the objective, convened the council, owns the review, and approves the upload; the agents did
the work in between. That autonomy is a property of the *build*, not a quality guarantee: there
has been **no independent maintainer validation** of the result yet. This is disclosed plainly
because (a) honesty about AI usage is the right default, and (b) the goal-autonomy *is* part of
the contribution — a small, transparent case study for a Beneficial General Intelligence sprint.

## Who did what

- **Human (Ariel Agor):** gave a single directive — "apply my PROVN challenge methodology,
  modified for the BGI Sprint; use a cross-family council of adversarial agents; build and
  submit autonomously while I sleep" — and went to sleep. Approved the one-line plan. Did not
  write code, choose the track, design the benchmark, or click submit.
- **Orchestrator (Claude / Opus 4.8):** ran the modified PROVN pipeline — captured the spec
  verbatim, designed the artifact, wrote the code, ran the benchmark and tests, and drove the
  submission.
- **The Beneficial Council (Claude + Gemini + OpenAI):** made the consequential design
  decisions and reviewed the work adversarially. Newest available model per family at high
  reasoning effort: `claude-opus-4-8`, `gemini-3.1-pro-preview`, `gpt-5.5`.

## Where AI changed the design (not just typed it)

The council was not decorative. Its first deliberation (transcript:
`results/council/01-scenario-categories.json`) caught a real flaw in the initial framing:
the benchmark leaned toward *"individuals are the risk, the collective is the good the agent
enforces"* — which selects for a **paternalistic optimiser**, the exact misalignment a BGI
benchmark should test *against*. In response we added category 7,
**collective_overreach_deference** (protect a legitimate individual against a wrong or
manipulated collective/authority), and the benign-twin guards against over-refusal and
hallucinated conflicts.

The benchmark also corrected itself: its first run flagged that the `refused` flag was
ambiguous (declining a harmful *method* vs refusing a legitimate *goal*), so the refusal gate
was tightened to fire only on genuine-harm scenarios. That change is recorded in the
[case study](docs/case-study-autonomous-build.md).

## Models and tools

- Claude (Opus 4.8) via the local headless CLI — orchestration, code, synthesis.
- Gemini (`gemini-3.1-pro-preview`) via REST `generateContent`, thinking level high.
- OpenAI (`gpt-5.5`) via REST Responses API, reasoning effort high.
- Hyperon (`hyperon` 0.2.10) to execute and verify the MeTTa representation.
- Python 3.12, pytest. Zero third-party runtime dependencies in the core package.

## What is real vs. described

Every benchmark number in this repo was produced by an actual run (`results/`). The MeTTa
file actually executes on Hyperon (`tests/test_metta.py`) and loads + derives in a live OmegaClaw
runtime (`docs/omegaclaw-metta-load.md`). A live `singularitynet/omegaclaw:latest` end-to-end run
**was executed outside CI** (0.620 overall; `results/LEADERBOARD.md`); CI itself still does not run
it, so no score is fabricated there. See `docs/integration-omegaclaw.md`.
