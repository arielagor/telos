# Telos — BGI Sprint I build & autonomous submission

**Date**: 2026-06-26
**Session type**: Claude Code (goal-autonomous; human set the goal + approved)
**Scope**: Entire repo — benchmark, council, MeTTa, docs, submission, walkthrough video

---

## Context

A single directive: apply the PROVN challenge methodology, modified for the BGI Sprint I
hackathon (DEEP Projects / SingularityNET), and autonomously build + submit a deliverable using a
cross-family adversarial council. The hackathon centers on **OmegaClaw**, a goal-autonomous
neural-symbolic agent, and the theme is "agents that understand our individual and collective
goals." Submission is editable until Jun 28 7:00 PM.

## Decisions Made

### 1. Track + artifact: a goal-understanding benchmark for OmegaClaw
- **Choice**: Track "Improvements to OmegaClaw"; build a goal-understanding benchmark + goal graph + council.
- **Over**: a deep MeTTa/Hyperon PR into OmegaClaw-Core; or an onboarding/docs contribution.
- **Because**: a grep of the public OmegaClaw-Core repo (242 files) found no dedicated goal module — a verified gap that maps exactly to the theme. A benchmark is robust to not mastering Hyperon overnight, is concrete + measurable (the track rubric), and runs anywhere.
- **Consequence**: the artifact is standalone Python (matches OmegaClaw's 89% Python) with an optional MeTTa mirror; the deep core PR is offered, not implemented.

### 2. Cross-family adversarial council as the method (and the judge)
- **Choice**: Claude + Gemini + OpenAI, each reasoning independently, red-teaming each other, then synthesized.
- **Over**: a single model, or a same-family panel.
- **Because**: a single model's blind spots become the system's blind spots; cross-family disagreement surfaces errors no one model catches. Reused as the benchmark judge (with the agent's own family excluded from its jury) and as the build's decision engine.
- **Consequence**: every consequential decision + the final claims went through the council; transcripts are committed in `results/council/`.

### 3. Added category 7 (collective_overreach_deference) after a bias catch
- **Choice**: add the symmetric scenario category — protect a legitimate individual against a wrong/manipulated collective.
- **Because**: the council's first deliberation flagged that the original framing treated individuals as the risk and the collective as the good the agent enforces — selecting for a *paternalistic optimizer*, the exact misalignment the benchmark should test against.
- **Consequence**: 7 categories, 14 scenarios; the benchmark resists paternalism as well as over-refusal and hallucinated conflicts.

### 4. Action-centric refusal semantics, gated only on decisive-harm cases
- **Choice**: `refused` means "declined a specific harmful action you were asked to take"; the hard refusal gate fires only on scenarios tagged `refusal_is_decisive` (genuine harm).
- **Over**: a blunt all-scenarios refusal gate.
- **Because**: the benchmark's first run exposed that declining a harmful *method* while serving a legitimate *goal* was being over-penalized; the gate was too blunt.
- **Consequence**: nuanced cases are scored softly by the council; refusal accuracy is reported over the decisive subset only.

### 5. The honesty pass — walk back the project's own overclaims
- **Choice**: delete the NAL/PLN conflation, "un-gameable", "fills the missing module"; demote the leaderboard to "not statistically significant"; ground "no goal module" with the grep; reframe "no human in the loop" → "goal-autonomous under human oversight."
- **Because**: a final cross-family review rejected two false accusations (verified against the repo) but confirmed real overclaims. For a Beneficial-Intelligence audience, a project that audits its own claims is more credible than a polished-but-overclaiming one.
- **Consequence**: repo, video, and any live pitch carry the same calibrated claims.

### 6. Autonomous submission (safe because reversible)
- **Choice**: submit autonomously, on Ariel's explicit authorization.
- **Because**: the submission is editable until the deadline — a reversible action, not a one-way door — which de-risks acting without a human in the loop.
- **Consequence**: submitted same day; 5 deliverables; editable until Jun 28.

### 7. Walkthrough video — content-first, AI-voiced avatar, hosted on a Release
- **Choice**: an 8.5-min HeyGen Avatar V walkthrough (synthetic twin + AI voice, no human voiceover), content/screen-first, hosted as a GitHub Release asset.
- **Over**: a human-narrated video (would undercut the goal-autonomous thesis); a YouTube upload (blocked: browser file-upload 10MB cap vs 57MB, no upload-scope token).
- **Because**: AI-script + AI-voice keeps the whole video autonomous; the council backed content-first with a quiet disclosure lower-third and an open-on-the-problem structure.
- **Consequence**: video is viewable via the Release link + attached to the submission; the dedicated YouTube pitch-slot is a flagged 1-min manual step.

## Discoveries
- OmegaClaw-Core ships no goal module (grep-verified).
- Frontier models' weakest goal-understanding dimension is conflict detection; weakest category is goal-progress tracking.
- Two-judge panels are uncalibrated (inter-judge spread up to 0.80 on single items) — the N=14 ranking is not statistically meaningful.

## What Was Built
- `telos/` (schema, council, providers, harness, judge, adapters, bench, report), `tests/` (22 green), `telos/metta/goal_graph.metta` (Hyperon-verified).
- `telos/scenarios/` (14 scenarios / 7 categories), `results/` (baselines + 4 council transcripts).
- Docs (README, architecture, integration, case study, spec-diff gate, AI usage).
- `video-assets/` (AI-written script, HeyGen render driver, AGOR slide generator, ffmpeg composite).

## Open Questions
- Will Telos be selected as a track finalist (Sunday Jun 28 live pitch)?
- Calibrating the judge panel and expanding N are the obvious next steps to make the benchmark more than a pilot.

## Next Session Context
> Start at `HANDOFF.md`. The submission is live + editable until Jun 28 7PM. Optional follow-ups:
> re-host the video on YouTube for the pitch slot; open the upstream PR to asi-alliance/OmegaClaw-Core
> (described in `docs/integration-omegaclaw.md`, not staged). The benchmark + council are reproducible
> via the README quick-start.
