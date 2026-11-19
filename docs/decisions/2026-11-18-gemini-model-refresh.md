# 2026-11-18 — Gemini council/judge default: gemini-3.1-pro-preview -> gemini-4-neon

Ariel asked (2026-11-18) to move every Gemini call to the best-value model for its role.

- `telos/providers.py` `GEMINI_MODEL` default: `gemini-3.1-pro-preview` -> `gemini-4-neon`. `TELOS_GEMINI_MODEL` still overrides it.
- Why: the Gemini family is a judge and council member (agent-under-test judged by the other families). Neon is the top Gemini on AA v5.0.1 (61) at $3/$15 per 1M and accepts `thinkingLevel: high`.
- Reproducibility: the 2026-06-26 pilot in `results/` ran on 3.1-pro-preview. README says how to reproduce it (`TELOS_GEMINI_MODEL=gemini-3.1-pro-preview`). Results, AI_USAGE.md and the case study describe that build and are left as written.
- `maxOutputTokens: 8192` includes thinking tokens; unchanged.
