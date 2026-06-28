# Telos — finalist pitch (spoken, ~3 minutes, no slides)

Here is the problem we set out to measure.

OmegaClaw is goal-autonomous. It creates goals, pursues them, and tracks progress on its
own. That is exactly the property that makes it powerful, and exactly the property that
makes a quiet misunderstanding dangerous. An agent that pursues the literal request while
missing the real goal, or optimizes a proxy and harms the thing it stood for, or serves
one person while pushing the cost onto everyone else, will do all of that confidently. A
normal task benchmark catches none of it. So we built Telos to make goal-understanding
measurable, and then we did the unglamorous work of actually testing it against your agent.

First, we stood up the live OmegaClaw agent. The real neural-symbolic loop, not a stand-in
LLM, benchmarked over its own channel. It scored 0.620 overall. On the 10 of 14 scenarios
where it returned a clean reading, it scored 0.869, right in the range of the frontier
models we tested. The four it missed were not misunderstandings. Its agentic loop produced
the answer but never issued the send command, so nothing reached the channel. That gap is
the cost of the autonomous loop, and it is worth knowing about before the agent acts on its
own. We are honest that the four nulls have no saved reading, so "loop cost, not weaker
understanding" is our hypothesis, not a proven fact.

Second, we did not just describe the integration. We loaded the goal module into OmegaClaw's
own MeTTa engine and ran its named rules there. The conflict rule, the collective-goal rule,
and the nested blocked-dependency rule all derive correctly in the running PeTTa engine, and
we went one step past pattern-matching: a Non-Axiomatic Logic deduction over goal terms
returns a real truth value, confidence 0.81. The transcript is committed. And we opened a
real pull request, OmegaClaw-Core number 218, adding an opt-in lib_telos_goals.metta.
Additive, no core changes, tested, there for you to review.

Now the honest part, because it is the whole thesis. Goal misunderstanding is a safety
property, so a benchmark that flatters itself is worse than useless. This was built by a
cross-family council, Claude, Gemini, and OpenAI, and before we submitted, that council
red-teamed its own work and made us walk back our own overclaims. The set is 14 scenarios,
public and hand-authored. The labels were council-authored, which is a real circularity.
The leaderboard ordering sits inside the judge noise, so it is not statistically
meaningful. The conflict rules are pattern-matching and the NAL step is one hand-built
inference, not the full pipeline yet. We would rather tell you that than oversell it.

What is next is the obvious list. Wire the conflict and alignment checks into NAL and PLN so
inference is automatic, not one hand-built deduction. Grow the scenario set past 14 and
harden it. Auto-extract goal atoms from free text so the loaded rules fire on real input.
And the one thing we cannot do ourselves: your review, as the maintainers, on whether 218
is the right shape. That is the ask.
