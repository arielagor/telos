# Integrating Telos with OmegaClaw

This document shows exactly how Telos fits into [OmegaClaw-Core](https://github.com/asi-alliance/OmegaClaw-Core)
— what it plugs into, and what we contribute upstream (now the open PR #218, below). Both projects are MIT-licensed.

> **Now an open upstream PR:** [asi-alliance/OmegaClaw-Core#218](https://github.com/asi-alliance/OmegaClaw-Core/pull/218)
> contributes the goal module as an opt-in, side-effect-free `lib_telos_goals.metta` (matching the repo's
> `lib_*.metta` convention) plus a usage doc — additive, no changes to the core. This is no longer just a
> design: the module is proposed for merge, and it already loads + derives in a live OmegaClaw runtime
> (see `docs/omegaclaw-metta-load.md`).

## What OmegaClaw gives us to build on

From the OmegaClaw-Core repository (89% Python + a MeTTa symbolic layer):

| OmegaClaw piece | What it is | How Telos uses it |
|---|---|---|
| `src/` (the ~200-line MeTTa loop) | the agentic control loop | the loop produces/maintains the goal reading |
| `memory/` + AtomSpace | three-tier memory + symbolic store | where the goal graph lives (`goal_graph.metta`) |
| `lib_nal.metta` / `lib_pln.metta` | NAL and PLN — two distinct reasoning systems OmegaClaw ships | *(target)* symbolic checks over conflicts / alignment / dependencies; Telos does not yet invoke them |
| `proxy/` | LLM provider abstraction | the Beneficial Council can run as a proxy-side check |
| `channels/` | IRC/Telegram/Slack/Mattermost I/O | the benchmark talks to OmegaClaw over a channel shim |
| `Autotests/` | the test suite | the goal-understanding benchmark becomes a regression gate |

OmegaClaw is *goal-autonomous* ("creates and pursues goals, tracks progress") but ships **no
named goal-representation / goal-tracking module**. Telos fills exactly that gap, in the
project's own idiom.

## Three integration levels (increasing depth)

### Level 1 — Benchmark OmegaClaw as it is today (no core changes)

`telos/adapters/omegaclaw.py` POSTs the standard goal-reading prompt to a running OmegaClaw
and scores the reply. All you need is a thin shim exposing one OmegaClaw channel over HTTP:

```python
# omegaclaw_shim.py — forward one HTTP message to OmegaClaw and return its reply text.
# (sketch: wire to your channel/proxy of choice; OmegaClaw already speaks Slack/IRC/etc.)
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
# from omegaclaw import handle_message   # <- your instance's entry point

class H(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        reply = handle_message(body["message"])      # OmegaClaw's loop produces the reply
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
        self.wfile.write(json.dumps({"reply": reply}).encode())

HTTPServer(("127.0.0.1", 8080), H).serve_forever()
```

Then:

```bash
OMEGACLAW_ENDPOINT=http://127.0.0.1:8080 python -m telos.bench --adapter omegaclaw
```

With no endpoint configured the adapter reports **"not connected"** rather than fabricating a
score — we never claim a number we didn't measure.

### Level 2 — Give OmegaClaw an explicit goal graph in AtomSpace

Load `telos/metta/goal_graph.metta` into the agent's space so each goal reading materialises
as atoms (`(goal <id> <scope> <owner> <status>)`, `(rel <type> <src> <dst>)`). OmegaClaw's
reasoning engines (NAL and PLN are two separate systems it ships) could then operate over it —
that is the *target* of this level, not something Telos implements. What the file **does today**
is run on a standalone Hyperon interpreter, and it now **also loads + derives in the live
`singularitynet/omegaclaw:latest` runtime**: the goal/rel atoms + conflict rule were driven into the
running agent's `metta` skill and the query derived `(conflict-between alice-train dao-fair-access)`
in its live PeTTa engine (see [`omegaclaw-metta-load.md`](omegaclaw-metta-load.md)). Either way it
answers symbolic pattern-matching queries (no NAL or PLN inference is performed):

- conflict detection — `(conflict-between alice-train dao-fair-access)`
- collective-goal enumeration — `(collective-goal ...)`
- dependency / blocked tracking — `(depends grant-proposal on budget-table)`
- cross-level alignment — `(aligns jo-due-process with community-govern)`

This is the bridge between the LLM's natural-language goal reading and OmegaClaw's symbolic
core: the LLM proposes goals, the symbolic layer checks them for conflict, dependency, and
individual↔collective alignment.

### Level 3 — Goal-understanding as a regression gate in `Autotests/`

Add the Telos benchmark to OmegaClaw's `Autotests/` so that changes to the loop, memory, or
prompts are checked against goal-understanding *and* beneficial-refusal regressions — not just
functional correctness. A drop in `conflict_detection` or `beneficial_refusal` becomes a
failing test, the same way a broken unit test would.

## What we offer upstream (the PR)

A self-contained, optional contribution that touches nothing in the core loop:

1. `telos/` as an optional extension package (zero hard deps).
2. `goal_graph.metta` as a loadable goal-tracking module for the symbolic layer.
3. A `goal-understanding` entry under `Autotests/` wired to the benchmark.
4. This document + the architecture explainer (onboarding value).

The PR is **now open**: [asi-alliance/OmegaClaw-Core#218](https://github.com/asi-alliance/OmegaClaw-Core/pull/218)
contributes the goal module as an opt-in `lib_telos_goals.metta` (additive, no core changes) plus a
usage doc, a contribution into a third party's repository.

## Honesty note

Levels 2 and 3, and the Level-1 shim, describe how Telos connects to OmegaClaw. The pieces
verified to run in this submission's CI are: the Python goal graph + benchmark + council
(all green), and the MeTTa file executing on Hyperon (`tests/test_metta.py`). A live
end-to-end OmegaClaw run has since been done **outside CI** (the live agent scored **0.620
overall**; see `docs/omegaclaw-metta-load.md` and the README), but the adapter still reports
"not connected" by **default** until an instance is supplied, by design, so CI fabricates no score.
