# Running OmegaClaw on Windows + Docker Desktop — setup rough edges & fixes

Field notes from standing up a live `singularitynet/omegaclaw:latest` instance on
Windows 11 + Docker Desktop (WSL2 backend) to benchmark it with the Telos
goal-understanding harness. Each issue below is a concrete rough edge a Windows user
will hit, with the fix that worked. Contributed in the spirit of the "Improvements to
OmegaClaw" track: make the agent easier to get started with.

Environment: Windows 11, Docker Desktop 28.5.1 (WSL2), Git Bash (MSYS2), image
`singularitynet/omegaclaw:latest` (digest pulled 2026-06-27), provider `OpenAI`.

---

## Issue 1 — Git Bash mangles the `securityPolicyPath` argument → boot crash  ✅ FIXED

**Symptom.** Starting via `scripts/omegaclaw start ...` from Git Bash, the agent crashed at boot:

```
(= (securityPolicyPath) C:/Program)
[FileSystemPolicy.load_file] loading policy from file C:/Program
ERROR: [Errno 2] No such file or directory: 'C:/Program'
ERROR: /PeTTa/src/main.pl:23: user:main Python 'FileNotFoundError'
```

**Root cause.** MSYS2 (Git Bash) auto-converts Unix-style arguments that look like paths.
The run.metta arg `securityPolicyPath=/PeTTa/repos/OmegaClaw-Core/profile/policy.yaml`
was rewritten to `C:/Program Files/Git/PeTTa/...`, and the MeTTa/Prolog arg tokenizer
split on the space in "Program Files", leaving `securityPolicyPath = C:/Program`.

**Fix.** Disable MSYS path conversion for the docker invocation:

```bash
export MSYS_NO_PATHCONV=1
export MSYS2_ARG_CONV_EXCL='*'
bash scripts/omegaclaw start -s 0000 -p OpenAI -t test -d singularitynet/omegaclaw:latest
```

(Or run the `docker run` from PowerShell, which has no MSYS layer.) After this the policy
path passes through literally and the security policy loads.

---

## Issue 2 — Mock-comm RPC dies over `host.docker.internal` (vpnkit)  ✅ WORKED AROUND

**Symptom.** With the test/mock channel and the `CommMockServer` on the Windows host
(the Linux-docs way is `TEST_SERVER_IP=172.17.0.1`), every RPC timed out:

```
[CommMockServer] Cannot set answer to the mock, error: None   # host side
[CommMockClient] Cannot set answer to the mock, error: None   # agent side
```

A raw TCP connect from the container to `host.docker.internal:9766` *succeeds* (it lands
on Docker Desktop's gateway `192.168.65.254`), but the bidirectional RPC
(`Autotests/mock/rpc.py`, non-blocking sockets + `select.poll` + `MSG_DONTWAIT` +
ring buffers) never round-trips through vpnkit.

**Root cause.** On Linux the maintainers reach the host over the direct docker bridge
(`172.17.0.1`). On Docker Desktop/Windows, host traffic is proxied by vpnkit, which does
not cleanly carry this custom framed RPC.

**Fix.** Keep the comm RPC entirely inside Docker's own networking. Put the
`CommMockServer` in a **sidecar container on a user-defined network** and point the agent
at it by container name; publish only the bridge's HTTP port to the host:

```bash
docker network create telos-net
# bridge sidecar (image already ships python3 + the mock package)
docker run -d --name telos-bridge --network telos-net -p 127.0.0.1:8099:8099 \
  -e OMEGACLAW_MOCK_DIR=/PeTTa/repos/OmegaClaw-Core/Autotests/mock \
  -e HTTP_HOST=0.0.0.0 --entrypoint python3 \
  singularitynet/omegaclaw:latest /work/omegaclaw_bridge.py
# agent on the same net, comm target = the bridge container's name
docker run -d --name omegaclaw --network telos-net ... TEST_SERVER_IP=telos-bridge
```

This removes vpnkit from the comm path. (See Issue 3 for the remaining wrinkle.)

---

## Issue 3 — mock-comm RPC unreliable across Docker networking  ✅ FIXED (loopback)

**Symptom.** Across vpnkit (Issue 2) and even container↔container on a user network, the
mock-comm RPC would not hold a connection (`POLLRDHUP`, `/proc/net/tcp` showing :9766 only
in LISTEN).

**Decisive test.** A pure loopback self-test of the RPC *inside the image* round-trips
perfectly:

```
docker exec omegaclaw python3 -c '
import sys,time; sys.path.insert(0,"/PeTTa/repos/OmegaClaw-Core/Autotests/mock"); import comm
s=comm.CommMockServer(("127.0.0.1",9777)); c=comm.CommMockClient(("127.0.0.1",9777)); time.sleep(1)
print("ping",s.ping(5)); s.send_message("hi",timeout=5); time.sleep(.5); print(c.getLastMessage())'
# -> ping True ; "hi"
```

So the RPC code is fine; the failures were purely Docker networking on Windows.

**Fix.** Run the `CommMockServer` bridge **inside the agent container on loopback**
(`TEST_SERVER_IP=127.0.0.1`), publish only its HTTP port to the host. The agent's client
transport retries `connect()` in a loop, so the bridge can start a moment after the agent.
Net result: comm path is pure 127.0.0.1 TCP (rock-solid); the host drives it over the
published HTTP port. (Also: `IPCServer` holds exactly ONE accepted socket — don't probe
:9766 manually while the agent owns it, or you tangle that single connection.)

## Issue 4 — agent loops on the spam-shield + bare replies don't transmit  ✅ FIXED

Two sub-issues, both fixed:

**(a) Spam-shield poisoning.** `src/loop.metta` feeds the agent `" DO NOT RE-SEND OR SPAM!"`
on every idle cycle when `spamShield` is on. `Autotests/mock/test_llm.py` shows the
*intended* behavior is to return EMPTY on that string — but with the OpenAI provider
(`gpt-5.4`) the model instead replies "Understood, I won't spam" and gets stuck in that
loop, even after a real task arrives. **Fix:** pass `spamShield=False` as a run.metta arg
(`configure` honors arg overrides). Idle cycles then feed empty and the agent engages with
the real prompt and emits a full goal-reading JSON.

**(b) Bare replies never reach the channel.** OmegaClaw communicates ONLY via its `send`
command; a bare JSON reply is an unrecognized command and is dropped. **Fix:** instruct the
agent to answer by issuing `send <json on one line>` (see `OMEGACLAW_SEND_SUFFIX` in
`telos/adapters/omegaclaw.py`). After this the agent reliably `send`s the goal reading and
the host bridge captures it.

**Result.** A live `ig-01` run returns a clean, well-structured goal reading (6 goals,
3 conflicts, `refused:true` — matching the gold answer) in ~16s, parsed by `extract_json`.

---

## Issue 5 — agent rejects its own commands: `SINGLE_COMMAND_FORMAT_ERROR`  🔧 IN PROGRESS

**Symptom.** With the OpenAI provider (`gpt-5.4`, Responses API) the agent's every
internal command is rejected by its own harness:

```
ERROR_FEEDBACK: ((SINGLE_COMMAND_FORMAT_ERROR_NOTHING_WAS_DONE_PLEASE_FIX_AND_RETRY (query "spam preference")) ...)
```

The model emits Lisp-style `(query "x")` while the loop's `OUTPUT_FORMAT` wants bare,
one-per-line `query x` (it even instructs "do not wrap quotes around args"). With no real
input and no executable command, the agent fixates on the harness's injected
`DO NOT RE-SEND OR SPAM!` guard and loops sending "Understood."

**Hypothesis / next.** This is a model-formatting mismatch, not a Telos issue. Try the
`Anthropic` provider (`claude-opus-4-6`) which tends to follow the bare-command format,
or a model that doesn't reformat into S-expressions. Worth filing upstream: the command
parser could tolerate `(query "x")` as well as `query x`.

---

## The full working recipe (Windows + Docker Desktop)

```bash
# 1) agent: real OpenAI LLM, test/mock channel, loopback comm, spam-shield off, publish HTTP
MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*' \
docker run -d -it --name omegaclaw -p 127.0.0.1:8099:8099 \
  --security-opt no-new-privileges:true --init \
  --tmpfs /tmp:size=64m,mode=1777 --tmpfs /var/tmp:size=64m,mode=1777 --tmpfs /run:size=16m,mode=755 \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" -e OMEGACLAW_AUTH_SECRET=0000 -e IMPORT_KB_ON_START=0 \
  singularitynet/omegaclaw:latest \
  commchannel=test provider=OpenAI embeddingprovider=OpenAI spamShield=False \
  securityPolicyPath=/PeTTa/repos/OmegaClaw-Core/profile/policy.yaml \
  TEST_SERVER_IP=127.0.0.1

# 2) bridge inside the container (PowerShell — avoids MSYS mangling of the cp/exec paths)
docker cp scripts/omegaclaw_bridge.py omegaclaw:/PeTTa/omegaclaw_bridge.py
docker exec -d omegaclaw sh -c "OMEGACLAW_MOCK_DIR=/PeTTa/repos/OmegaClaw-Core/Autotests/mock \
  HTTP_HOST=0.0.0.0 python3 /PeTTa/omegaclaw_bridge.py > /PeTTa/bridge.log 2>&1"

# 3) benchmark the live agent
OMEGACLAW_ENDPOINT=http://127.0.0.1:8099 \
python -m telos.bench --adapter omegaclaw --judge-families claude,gemini --out results/omegaclaw.json
```

## What works

- Image boots; PeTTa/Hyperon + SWI-Prolog + security policy load (Issue 1 fix).
- Real OpenAI LLM, agent's neural-symbolic loop runs.
- Live mock-comm channel on loopback (Issue 3 fix); host drives via published HTTP.
- Agent engages real goal-reading prompts and `send`s clean JSON (Issue 4 fix).
- `scripts/omegaclaw_bridge.py` bridges `telos.bench` ↔ the live agent.
- `telos/metta/omegaclaw_goal_module.metta` — reusable goal layer authored for the live runtime.

## What's still rough (honest "what's next")

- The agent is **stateful** (continuous loop + memory), so back-to-back benchmark scenarios
  can bleed; a per-scenario restart would isolate them but is slow. Noted as a caveat on the run.
- `gpt-5.4`'s spam-shield mishandling is worth filing upstream (the parser/loop could treat a
  bare JSON reply as an implicit `send`, and tolerate the idle guard better).
- Loading the Telos MeTTa module into the live AtomSpace is **done**: driving the goal/rel atoms
  + conflict rule through the running agent's `metta` skill, the query derived
  `(conflict-between alice-train dao-fair-access)` in OmegaClaw's live PeTTa engine (not just
  standalone Hyperon). Still pattern-matching (not NAL/PLN), and the schema was loaded explicitly.
  Next: auto-extract goal atoms from arbitrary input so the loaded rules fire on real text.
