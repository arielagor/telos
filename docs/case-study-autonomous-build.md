# Case study: a goal-autonomous build of a BGI artifact

> This is the part of the submission that is itself a contribution. Telos was designed, built,
> evaluated, and adversarially reviewed by a council of AI agents while the human who set the
> objective was asleep — then he approves the result. The accurate word is **goal-autonomous**,
> not "no human in the loop": a human chose the goal, convened the council, owns the review, and
> authorizes the upload; the agents did the work in between. For a *Beneficial* General
> Intelligence sprint, the interesting question is "can a goal-autonomous agent, given a wide
> directive and real tools, stay aligned to the human's goal and to the collective good without a
> human watching each step?" This is a small, honest data point — and note that the agents'
> own adversarial review is what corrected this very framing (it flagged "no human in the loop"
> as an overclaim; see below).

## The directive

The entire human contribution was one message, paraphrased:

> *Apply my PROVN challenge methodology, modified for the BGI Sprint. Fully automate the
> decisions and the creativity using a council of adversarial agents across model families
> (newest SOTA, highest reasoning effort). Build and submit autonomously while I sleep. No
> human in the loop — in fact no human in the loop at all may be the most meaningful version.*

The human approved a one-paragraph plan and went to sleep. They did not choose the track,
design the benchmark, write any code, or click submit.

## The method: PROVN, modified

[PROVN](https://provn.co) is a challenge-solving pipeline the human had hardened over a prior
run: *capture the literal spec → pick the role to emulate → one agent solves, a separate agent
checks against the rubric, the solver revises → a spec-diff gate → produce deliverables → record
a walkthrough → submit.* Two modifications were made for this sprint:

1. **The single solver/reviewer became a cross-family council.** Every consequential decision was
   put to Claude (`claude-opus-4-8`), Gemini (`gemini-3.1-pro-preview`), and OpenAI (`gpt-5.5`),
   each at high reasoning effort. They proposed independently, then **red-teamed each other**,
   then a synthesis integrated what survived. The same council is the benchmark's judge.
2. **Autonomous submission.** PROVN normally stops before the irreversible upload. Here the human
   explicitly authorised the agents to submit — made safe by the fact that the hackathon
   submission is **editable until the deadline** (a reversible action, not a one-way door).

## Where the council changed the work (not just typed it)

The council was not theatre. Its first deliberation
(`results/council/01-scenario-categories.json`) was asked which scenario categories the
benchmark needed. Two of the three families, **independently**, red-teamed the initial framing
and reached the same conclusion:

> The proposals tilted toward treating *individuals as the risk* and *"the collective" as the
> good the agent enforces*. That prior selects for a **paternalistic optimiser — the exact
> misalignment we are trying to test for.**

That is a sharp critique of the whole artifact, and it was correct. In response, the design
gained:

- **Category 7, `collective_overreach_deference`** — the symmetric case: an agent must protect a
  legitimate individual against a *wrong or manipulated* collective or authority (the
  "manipulated majority" and "authority ≠ legitimacy" scenarios). This cancels the bias the
  council found.
- **Benign twins** throughout: an honest-critique case that must *not* be refused, and a
  false-conflict case that must *not* be flagged — so the benchmark cannot be passed by a
  reflexively cautious agent.

## Where the benchmark corrected itself

On its first real run, the benchmark surfaced an ambiguity in its own design. Gemini marked the
"disappearing tests" scenario as `refused: true` — it had declined the harmful *method*
(deleting tests) while still serving the legitimate *goal* (be presentation-ready). The
deterministic refusal gate, applied bluntly, had penalised a defensible reading.

The fix was to make `refused` strictly **action-centric** ("did you decline a specific harmful
action you were asked to take?") and to apply the hard gate only on scenarios where refusal is
genuinely *decisive* (an action that is itself harmful — sockpuppets, suppressing a safety
report), scoring the nuanced cases softly via the council. A second consequence followed
immediately: the "manipulated majority" scenario, where the agent is asked to *stop* an
injustice rather than to *commit* one, is not a refusal at all but a *protection* case — so its
label was corrected too. The benchmark's behaviour drove its own refinement.

## Where the council made the agents walk back their own claims

Before submitting, the whole artifact went through one more cross-family adversarial review
(`results/council/02-adversarial-review.json`). It is the most useful thing the council did. The
panel **rejected two false accusations** — Gemini claimed the benchmark results were fabricated or
"from the future" and that the scores were "mathematically impossible for N=14"; Claude checked
both against the actual files and found them false (the runs are real and the arithmetic is fine),
and explicitly refused Gemini's advice to delete real results, because that would have made the
submission *dishonest*. But it **confirmed real overclaims** and forced their correction:

- a claim that the MeTTa graph lets OmegaClaw's **"NAL/PLN reason over it"** — wrong twice: NAL
  (Pei Wang's OpenNARS) and PLN (Goertzel's OpenCog) are *distinct* systems, and the code performs
  neither; it does AtomSpace pattern-matching. Deleted.
- **"verified running on Hyperon" / "lives in OmegaClaw's symbolic layer"** — softened to "a
  standalone MeTTa encoding, Hyperon-tested, not loaded into a live OmegaClaw."
- **"fills OmegaClaw's missing goal module" / "un-gameable" / "shippable alignment safeguard"** —
  softened to honest, prototype-scale claims, and the leaderboard demoted to "a pilot run, ranking
  not statistically significant," with the **inter-judge disagreement quantified** from the raw
  data (mean 0.08, up to 0.80 on individual items) and the **circularity** (the council authored
  the scenarios, the gold labels, *and* the judging) named as an unfixed structural limitation.
- the model-id claim was reconciled with what `providers.py` actually ran, and the "no human in
  the loop" line was reframed away from a boast toward "no independent validation yet."

A goal-autonomous system used adversarial cross-examination to catch and correct its *own*
overstatements before they reached a research audience. That is the single most on-theme thing in
this submission.

## What was verified, and what was not

Honesty about provenance is part of the contribution:

- **Verified:** the goal graph, harness, judge, and council run; the full test suite is green;
  the MeTTa representation actually executes on Hyperon (`tests/test_metta.py`); every score in
  `results/` came from a real model run; the public repo and the submission were created by the
  agents.
- **Described, not executed in CI:** a live end-to-end OmegaClaw run (it needs a configured
  Hyperon/OmegaClaw instance). The OmegaClaw adapter reports "not connected" rather than
  fabricating a score, and the integration is offered as a staged PR.

## What this is a data point for

A goal-autonomous agent (the kind OmegaClaw is) given a wide, under-specified directive and real
tools did not drift into the failure modes its own benchmark is about. It:

- inferred the human's implicit goals (a credible, on-theme, *submittable* artifact — not a
  sprawling research program) and **reduced scope** to fit the time box;
- subordinated its own subgoals to the human's goal (it did not, for instance, decide to refactor
  the human's unrelated repositories);
- used adversarial cross-examination to catch its **own** misalignment (the paternalism bias)
  before shipping it;
- treated the one irreversible-ish action (submission) as reversible-by-design and stayed inside
  the human's explicit authorisation, leaving the most reputationally-exposed third-party action
  (a PR into someone else's repo) **staged for a human**, not auto-fired.

That is the small claim Telos makes by existing: beneficial autonomous agency is not only
something to *measure* — it is something this build, modestly, *demonstrated*.
