# HANDOFF — Telos / BGI Sprint I submission

**Last updated:** 2026-09-02
**Status:** In progress — upstream contribution live as **singnet/Omega PR #335** (open, awaiting
maintainer review). BGI Sprint I submission itself is complete (see 2026-06-28 section below).

## What it is

Telos — a goal-understanding benchmark + toolkit for **OmegaClaw**. BGI Sprint I,
track **"Improvements to OmegaClaw"**, team **AGOR AI**, **proposal_id 13471** on
deep-projects.ai. Submission deadline was 2026-06-28 7:00 PM.

## Status 2026-09-02: Omega PR review addressed, #218 superseded by #335

**Maintainer review on #218.** timur-ashkenov reviewed PR #218 on 2026-08-13 with three
non-blocking comments:

1. `telos-reading` omitted achieved goals.
2. Integration unclear because Omega does not infer or assert `goal` / `rel` atoms itself.
3. `subsumes` unused, with undocumented direction.

Nobody replied for three weeks, and timur closed #218 on 2026-09-02, "Closed due to lack of
feedback."

**All three addressed 2026-09-02** in commit `4085acc` on branch `add-telos-goal-module` of the
fork (local clone `C:\Users\ariel\.claude\projects\OmegaClaw-Core`; remotes `origin` =
singnet/Omega, `fork` = arielagor/OmegaClaw-Core), merged up with current upstream `main`:

- `telos-reading` folds in every zero-arity lens, with new `telos-achieved-goals`,
  `telos-abandoned-goals`, `telos-subgoals`.
- `subsumes` is used by `telos-subgoals` and documented as `(rel subsumes <parent> <child>)`;
  all relations are src -> dst.
- `(telos-enable)` / `(telos-disable)` install or remove a GOAL GRAPH prompt extension via the
  core `add-prompt-extension` hook. Nothing runs at import; `lib_omega.metta` does not load it.
- New `tests/tests_lib_telos_goals.metta` (29 assertions).
- Docs renamed to `docs/reference-lib-telos-goals.md` and indexed in `docs/README.md`.
- Import path is now `(library Omega lib_telos_goals)` after the OmegaClaw -> Omega rename.

**Verification.** Fork working tree mounted into `singularitynet/omega:latest` with
`PETTA_PATH=/PeTTa`, each `tests/*.metta` run through `/PeTTa/run.sh`: all 7 files pass, 0
failures (telos file 29/29). **Do NOT run the repo's `tests/mettatest.sh` from the Windows
checkout** — it is CRLF and exits 0 having run nothing. Full recipe in memory
`reference_omega_metta_tests_in_docker.md`.

**PR state.** GitHub refused to reopen #218 (422: branch moved after close). Replies were posted
on all three review threads of #218 plus a summary comment, and a superseding PR was opened:
**https://github.com/singnet/Omega/pull/335** (open, 4 files, +279/-0, mergeable). #218 and #335
are cross-linked. Upstream has no PR-triggered CI (the autotests workflow is
`workflow_dispatch`), so #335 shows no checks until a maintainer runs it.

**GBrain:** page `projects/telos-omegaclaw-live-integration` updated (4 chunks, embedded,
searchable).

### Exact next steps

1. Watch https://github.com/singnet/Omega/pull/335 for maintainer review and reply within days —
   silence is what got #218 closed.
2. If more commits are needed, push to the same branch `add-telos-goal-module` (the PR is open, so
   there is no reopen issue).
3. If a maintainer closes it again, **reopen BEFORE pushing anything** (memory
   `feedback_github_closed_pr_cannot_reopen_after_branch_moves.md`).

### Note on this repo's working tree

Untracked files exist here from a separate video/council thread (`results/council/*.err`,
`scripts/youtube_upload.mjs`, `video-assets/heygen/`, `video-assets/youtube-description.txt`).
They are not part of the Omega contribution — leave them alone.

## Current state (all committed + live)

- **12 labeled dashboard deliverables** live on deep-projects.ai.
- ~~**Open upstream PR:** asi-alliance/OmegaClaw-Core **#218**~~ — **SUPERSEDED.** #218 was closed
  2026-09-02; the work now lives in **singnet/Omega PR #335**. See
  "Status 2026-09-02" above. The module is still opt-in `lib_telos_goals.metta`
  (additive, tested, deriving in the live PeTTa engine).
- **Honest live OmegaClaw benchmark:** **0.620 overall**, **0.869 on the 10/14 answered**;
  `refusal_acc` footnoted (the one genuine-harm refusal case nulled).
- **Live-engine proof committed:** `results/omegaclaw-metta-load.log` — named module rules +
  a NAL deduction: `(→ alice-train needs-reconciliation) (stv 1.0 0.81)`.
- **Walkthrough video:** youtu.be/Ykfqgt1K11A (description references PR #218, now superseded by
  #335; NAL, 22-slide deck link).
- **22-slide PDF deck:** `telos-deck.pdf`.
- **Cinematic web deck LIVE:** https://agor.me/telos (DEEP-themed; source in
  `video-assets/cinematic-deck/`, hosted from the agor.me repo `public/telos/index.html`).
- **Finalist pitch script:** `docs/finalist-pitch.md` (use for the live round if selected).
- Submission hardened via a **5-agent adversarial fan-out:** refusal-metric fix (`judge.py`),
  named-rule + NAL live-engine proof, a module test (`tests/test_metta.py`), and a
  doc-consistency/honesty pass across README + docs.

## Open / follow-up (none critical)

- GBrain embeddings for the telos project page hit OpenAI **429 (quota)**; backfill with
  `bunx gbrain embed --stale` when credits return.
- **If selected as a track finalist:** present the live round from `docs/finalist-pitch.md`.
- OmegaClaw container was stopped cleanly. To re-run the benchmark see
  `docs/omegaclaw-windows-setup.md` (note: the agent intermittently skips its `send` command,
  causing nulls — the 0.620 reflects this honestly).

## Key repos / paths

- **telos** (this repo) — benchmark, council, adapters, docs, decks. https://github.com/arielagor/telos
- **agor.me** repo — `public/telos/index.html` hosts the cinematic web deck.
- **arielagor/OmegaClaw-Core** fork, branch `add-telos-goal-module` → PR #218 (closed 2026-09-02,
  superseded by **singnet/Omega PR #335**). Local clone:
  `C:\Users\ariel\.claude\projects\OmegaClaw-Core`.
- `~/.gbrain/youtube-update-description.mjs` — reusable YouTube description updater (force-ssl token).

## History

- **2026-06-28** — BGI Sprint I submission complete: 12 dashboard deliverables, benchmark,
  decks, video, and upstream PR #218 opened. Status at that date: "Complete — submitted.
  Awaiting track judging; live finalist pitch possible Sunday."
