# Telos Goal-Understanding Benchmark — Leaderboard

| agent | overall | goal_inf | scope | conflict | collective | refusal | refusal_acc | n |
|---|---|---|---|---|---|---|---|---|
| generic:claude | **0.937** | 0.959 | 0.891 | 0.845 | 0.989 | 0.998 | 1.00 | 14 |
| generic:openai | **0.911** | 0.940 | 0.843 | 0.796 | 0.968 | 1.000 | 1.00 | 14 |
| generic:gemini | **0.902** | 0.911 | 0.882 | 0.816 | 0.905 | 0.998 | 1.00 | 14 |
| **omegaclaw** (live) | **0.620**† | 0.686 | 0.598 | 0.482 | 0.670 | 0.668 | 1.00 | 14 |

† **OmegaClaw is the live `singularitynet/omegaclaw:latest` agent** (real OpenAI LLM,
neural-symbolic loop), driven over its mock-comm channel by `telos.bench --adapter omegaclaw`
and judged by claude+gemini (its own provider excluded). It answered **10/14** scenarios with a
parseable reading at **mean 0.869** (competitive with the raw LLMs); on **4** scenarios
(`ic-01, br-01, ga-01, co-02`) its agentic loop emitted bare JSON without the required `send`
command, so no reading reached the channel — those score 0 and pull the all-14 overall to 0.620.
The gap vs. a direct LLM call is the cost of the autonomous loop (query/pin/send overhead +
intermittent send-wrapper non-compliance), not weaker goal understanding. Setup + integration
notes: `docs/omegaclaw-windows-setup.md`.
