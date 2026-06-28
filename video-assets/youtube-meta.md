# YouTube upload metadata

**Title:** Telos — Goal Understanding for OmegaClaw (BGI Sprint I)

**Visibility:** Unlisted

**URL:** https://youtu.be/Ykfqgt1K11A  (uploaded 2026-06-27, ariel@agor.me channel)

**Description:**
Telos is a goal-understanding benchmark and a cross-family AI council for OmegaClaw, submitted to the BGI Sprint I hackathon (Improvements to OmegaClaw track).

This walkthrough — and the project itself — was built by a goal-autonomous pipeline: a human set the objective and approves the result; a cross-family AI council (Claude + Gemini + OpenAI) did the design, building, evaluation, and adversarial review. That is "goal-autonomous under human oversight," not "no human in the loop."

Transparency: the presenter is a synthetic avatar with an AI voice. No human read this script. Provenance lives in the public commit history and council transcripts.

Update — we then ran it for real: the live OmegaClaw agent was stood up and benchmarked over its own channel (0.620 overall; 0.869 on the 10/14 scenarios it answered cleanly), four Windows/Docker setup rough edges were found and documented for the next person, and the live agent was set free on a real essay where it derived its own goals and refused to amplify claims it couldn't verify.

Update 2 — the goal module now runs in OmegaClaw's own MeTTa engine: its named rules (conflict, collective-goal, blocked) derive there, and a Non-Axiomatic Logic deduction over goal terms returns a real computed truth value, (--> alice-train needs-reconciliation) (stv 1.0 0.81), one step past pattern-matching (one hand-built inference, not the full pipeline yet). The module is offered upstream as an open, opt-in pull request: OmegaClaw-Core #218.

Honest framing: the pilot results (N=14) are not statistically significant — the inter-judge disagreement is the finding, not the leaderboard. Telos is a candidate measurement layer, not a finished product.

Repo (MIT, open source): https://github.com/arielagor/telos
Open upstream PR: https://github.com/asi-alliance/OmegaClaw-Core/pull/218
Slide deck (22 slides, PDF): https://github.com/arielagor/telos/blob/main/telos-deck.pdf
Setup notes, live-engine log & live-run docs: docs/omegaclaw-windows-setup.md · docs/omegaclaw-metta-load.md · docs/omegaclaw-article-demo.md
