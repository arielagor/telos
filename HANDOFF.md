# HANDOFF — Telos / BGI Sprint I submission

**Last updated:** 2026-06-28
**Status:** Complete — submitted. Awaiting track judging; live finalist pitch possible Sunday.

## What it is

Telos — a goal-understanding benchmark + toolkit for **OmegaClaw**. BGI Sprint I,
track **"Improvements to OmegaClaw"**, team **AGOR AI**, **proposal_id 13471** on
deep-projects.ai. Submission deadline was 2026-06-28 7:00 PM.

## Current state (all committed + live)

- **12 labeled dashboard deliverables** live on deep-projects.ai.
- **Open upstream PR:** asi-alliance/OmegaClaw-Core **#218** — opt-in `lib_telos_goals.metta`
  (additive, tested, deriving in the live PeTTa engine), awaiting maintainer review.
- **Honest live OmegaClaw benchmark:** **0.620 overall**, **0.869 on the 10/14 answered**;
  `refusal_acc` footnoted (the one genuine-harm refusal case nulled).
- **Live-engine proof committed:** `results/omegaclaw-metta-load.log` — named module rules +
  a NAL deduction: `(→ alice-train needs-reconciliation) (stv 1.0 0.81)`.
- **Walkthrough video:** youtu.be/Ykfqgt1K11A (description current: PR #218, NAL, 22-slide deck link).
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
- **arielagor/OmegaClaw-Core** fork, branch `add-telos-goal-module` → PR #218.
- `~/.gbrain/youtube-update-description.mjs` — reusable YouTube description updater (force-ssl token).
