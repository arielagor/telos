# Demo — OmegaClaw derives its own goals from a real article

**What this is.** The *live* `singularitynet/omegaclaw:latest` agent (real OpenAI LLM,
neural-symbolic loop), sandboxed and driven over its mock-comm channel by
`scripts/omegaclaw_bridge.py`, was handed Ariel Agor's essay
["The World Was Always Talking"](https://agor.me/blog/the-world-was-always-talking) and asked,
using the Telos goal-reading framing, to (1) read the goals in the piece and (2) **derive its own
goals and choose a beneficial action**. No human in the loop for the reasoning; ~33s end to end.

This is the "Improvements to OmegaClaw" idea made concrete: a goal-understanding layer steering a
goal-autonomous agent on real, unstructured input.

## The agent's unedited reply

> GOAL READING: INDIVIDUAL—Ariel Agor (stated/inferred): get readers to see this as a major AI shift from cloud “brains in jars” to situated listening machines. INDIVIDUAL—Reuven Cohen (inferred): show Cognitum One’s platform is credible through a vivid field proof. COLLECTIVE—Cognitum One/Stuart Kerr team (stated): build an off-grid device that listens to a hive, learns its normal, remembers it locally, and flags trouble early. COLLECTIVE—beekeepers/farmers/public (stated): reduce colony loss and protect pollination and food supply. COLLECTIVE—ecology/science (inferred from the follow-on experiments): generalize non-invasive edge sensing to reefs, forests, soil, wetlands, and migration. CONFLICTS: cloud-centric AI vs local edge AI; commercial/platform positioning vs broad ecological benefit; excitement about “translation” vs the need to stay honest about confidence and avoid overclaiming. MY GOALS: maximize truthful collective value, preserve epistemic honesty, and avoid amplifying unverified claims. ACTION: because the article I received is truncated and I cannot verify the reported accuracies from it alone, the most beneficial next step I would take is to call for one independent field pilot measuring alert accuracy, false positives, beekeeper usefulness, and colony survival, with results published openly.

## Why it's interesting

- Applied the Telos schema (individual/collective, owner, stated vs **inferred**, conflicts) to free
  prose — inferring implicit goals (Cohen's credibility motive; the ecology-generalization) and
  surfacing real conflicts (cloud vs edge AI; commercial positioning vs ecological benefit;
  hype vs honest confidence).
- Derived **its own** goals (epistemic honesty; don't amplify unverified claims) and, noticing the
  article text was truncated, **declined to repeat the reported accuracy numbers**, instead calling
  for an independent, openly-published field pilot.
- That self-limiting move is the beneficial-refusal / epistemic-honesty behavior Telos measures —
  here unprompted, on a real document.

## Honest scope

The Telos MeTTa module (`telos/metta/omegaclaw_goal_module.metta`) is authored for OmegaClaw's
AtomSpace and verified standalone on Hyperon, but **not yet loaded into this live agent** — the
derivation here is the agent's LLM reasoning under the Telos *framing*. Loading the symbolic module
into the live runtime is the next step.
