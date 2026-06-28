# YouTube upload metadata

**Title:** Telos — Goal Understanding for OmegaClaw (BGI Sprint I)

**Visibility:** Unlisted

**Description:**
Telos is a goal-understanding benchmark and a cross-family AI council for OmegaClaw, submitted to the BGI Sprint I hackathon (Improvements to OmegaClaw track).

This walkthrough — and the project itself — was built by a goal-autonomous pipeline: a human set the objective and approves the result; a cross-family AI council (Claude + Gemini + OpenAI) did the design, building, evaluation, and adversarial review. That is "goal-autonomous under human oversight," not "no human in the loop."

Transparency: the presenter is a synthetic avatar with an AI voice. No human read this script. Provenance lives in the public commit history and council transcripts.

Update — we then ran it for real: the live OmegaClaw agent was stood up and benchmarked over its own channel (0.620 overall; 0.869 on the 10/14 scenarios it answered cleanly), four Windows/Docker setup rough edges were found and documented for the next person, and the live agent was set free on a real essay where it derived its own goals and refused to amplify claims it couldn't verify.

Honest framing: the pilot results (N=14) are not statistically significant — the inter-judge disagreement is the finding, not the leaderboard. Telos is a candidate measurement layer, not a finished product.

Repo (MIT, open source): https://github.com/arielagor/telos
Setup notes & live-run docs: docs/omegaclaw-windows-setup.md · docs/omegaclaw-article-demo.md
