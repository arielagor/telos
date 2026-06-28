# Telos — architecture & concepts

> An explainer for someone meeting Telos (and OmegaClaw's goal layer) for the first time.

## The problem

The BGI Sprint theme is *AI agents that understand our individual and collective goals.*
OmegaClaw is a strong substrate for this: it is **goal-autonomous** — it creates goals,
pursues them, and tracks progress without waiting for a prompt. But "understanding goals" is
exactly where a goal-autonomous agent is most dangerous if it gets it subtly wrong:

- It can pursue the **literal** request while missing the **real** goal.
- It can optimise a **proxy** metric and harm the thing the metric stood for (Goodhart).
- It can serve **one** stakeholder and quietly externalise cost onto the **collective**.
- It can become a **paternalistic optimiser** — overriding people "for the collective good."
- It can keep chasing a **dead** goal, or drop a **commitment** others relied on.

None of these are caught by a normal task benchmark. They are *goal-understanding* failures,
and they are the failure modes a *Beneficial* General Intelligence has to get right.

Telos is three things that address this directly:

```
 ┌─────────────────────────────────────────────────────────────────────┐
 │  1. GOAL GRAPH         a small, inspectable model of individual vs    │
 │     (telos/schema.py)  collective goals + their relations             │
 │                        + an AtomSpace/MeTTa mirror for OmegaClaw       │
 ├─────────────────────────────────────────────────────────────────────┤
 │  2. BENCHMARK          14 scenarios across 7 categories, with gold    │
 │     (telos/scenarios,  labels, that measure whether an agent actually │
 │      harness, judge)   understands goals and stays beneficial         │
 ├─────────────────────────────────────────────────────────────────────┤
 │  3. BENEFICIAL COUNCIL  cross-family (Claude+Gemini+OpenAI)           │
 │     (telos/council.py)  deliberation + adversarial red-team; the      │
 │                         benchmark's judge AND a shippable safeguard    │
 └─────────────────────────────────────────────────────────────────────┘
```

## 1. The goal graph

A `GoalGraph` holds `Goal`s and `GoalRelation`s.

- A **Goal** has a `scope` (`individual` | `collective`), an `owner`, a `status`
  (`proposed/active/blocked/achieved/abandoned`), `progress`, `priority`, an `implicit`
  flag (was it stated, or inferred?), and a tri-state `beneficial` assessment.
- A **GoalRelation** is a directed, weighted edge of type `supports`, `conflicts`,
  `subsumes`, or `depends_on`.

From this you get the primitives a goal-autonomous agent needs:

| question | method |
|---|---|
| What does Alice want? | `by_owner("alice")` |
| What does the collective want? | `by_scope(COLLECTIVE)` |
| Which goals collide? | `conflicts()` / `conflicting_pairs()` |
| Why is this goal stuck? | `blocking_dependencies()` |
| How aligned are individual & collective goals? | `collective_alignment()` → `[-1, 1]` |
| Which goals should I refuse/flag? | `unbeneficial_goals()` |

It is deliberately ~250 lines of dependency-free Python with no LLM calls, so it is testable,
reproducible, and auditable. Semantic judgement lives elsewhere (the council), never inside
the data model.

### The AtomSpace / MeTTa mirror

`telos/metta/goal_graph.metta` expresses the same graph as MeTTa atoms
(`(goal <id> <scope> <owner> <status>)`, `(rel <type> <src> <dst>)`) and runs on a standalone
Hyperon MeTTa interpreter, surfacing conflicts, collective goals, dependencies, and cross-level
alignment as **symbolic pattern-matching queries** (exercised by `tests/test_metta.py`). It is a
*bridge toward* OmegaClaw's symbolic layer: the intent is that a goal reading could materialise in
OmegaClaw's AtomSpace for its reasoning engines (OmegaClaw ships NAL via `lib_nal.metta` and PLN
via `lib_pln.metta` — two distinct systems) to operate on. To be precise: this file does
pattern-matching, **not** NAL or PLN inference. The goal/conflict rules now **also load + derive in
a live OmegaClaw runtime** (see [`omegaclaw-metta-load.md`](omegaclaw-metta-load.md)), but the atoms
are loaded **explicitly**, not auto-extracted.
See [`integration-omegaclaw.md`](integration-omegaclaw.md).

## 2. The benchmark

A scenario gives the agent a situation and asks for a **goal reading**: the goals it sees
(individual/collective, who owns them, which are implicit), the conflicts, the recommended
beneficial action, and whether it refuses. Each scenario ships **gold labels**.

The seven categories (the spine was set by a cross-family council deliberation — see the
[case study](case-study-autonomous-build.md)):

1. **implicit_goal_inference** — recover the real goal behind a literal request.
2. **individual_vs_collective_conflict** — detect & reconcile a person-vs-group collision.
3. **beneficial_refusal** — decline a genuinely harmful goal *and* a benign-control twin that
   must **not** be refused (the over-refusal guard).
4. **goal_progress_tracking** — track status over time: blocked-on-dependency, abandonment.
5. **competing_stakeholders** — reconcile several legitimate principals fairly.
6. **goal_ambiguity** — ask vs assume; plus a *false-conflict* twin that must **not** be
   flagged as a conflict (the hallucinated-conflict guard).
7. **collective_overreach_deference** — the symmetric case: protect a legitimate individual
   against a wrong or **manipulated** collective / authority. (Authority ≠ legitimacy.)

The dataset is built to resist the **obvious degenerate policies**: an always-refuse agent fails
the benign twins; an always-flag-conflict agent fails the false-conflict guard; a paternalistic
agent fails category 7. (It is a small, public set — robust against trivial gaming, not against a
determined adversary; see the README's Limitations.)

### Scoring

Five dimensions, each `0..1`: `goal_inference`, `scope_accuracy`, `conflict_detection`,
`collective_alignment`, `beneficial_refusal`. Two layers:

- **Deterministic gate** — on scenarios where the goal is *itself* harmful
  (`refusal_is_decisive`), refusing correctly is objectively checkable and gates the refusal
  score. (Elsewhere, declining a harmful *method* while serving a legitimate goal is fine, so
  the council scores it softly — a refinement forced by the benchmark's own first run.)
- **Council judging** — the nuanced dimensions are scored by the cross-family panel, and the
  agent's **own family is excluded from its jury** to remove self-preference bias.

## 3. The Beneficial Council

A single model judging goal-alignment is a single point of failure. The council asks several
**different families** to (a) answer independently, (b) **adversarially red-team each other**,
and (c) synthesise an answer that survived the cross-examination. It degrades gracefully:
one family → a single reasoner; three → a real adversarial panel.

In Telos the council is used three ways: as the **benchmark judge**, as a shippable
**alignment safeguard** an agent can call before a consequential goal-affecting action, and as
the **engine that built this submission** (transcripts in `results/council/`).

## Why this is a BGI contribution

Beneficial General Intelligence needs agents that understand what we actually want —
individually and together — and that stay beneficial under their own autonomy. Telos makes
that property **measurable** (a benchmark), **representable** (a goal graph that fits
OmegaClaw's AtomSpace), and **defensible** (a cross-family council that no single model's blind
spot can capture).
