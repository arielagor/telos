"""Thin, dependency-free adapters for three model families.

Each ``call_*`` function takes a system + user prompt and returns a :class:`ModelReply`.
Calls degrade gracefully: a missing key or a transport error yields ``ok=False`` with the
error captured, so the council can proceed with whichever families answered.

Families
--------
- **Claude** (Anthropic) — invoked through the local ``claude`` CLI in headless mode
  (``claude -p``). On Ariel's machine this bills against the Max plan ($0), so we never
  need ``ANTHROPIC_API_KEY`` (and we strip it from the child env to be sure).
- **Gemini** (Google) — REST ``generateContent`` with Gemini-3 ``thinkingLevel: high``.
- **OpenAI** — REST ``/v1/responses`` with ``reasoning.effort: high``.

Only the stdlib is used (``urllib``, ``subprocess``) so the package installs with zero
third-party dependencies.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Optional

# Newest SOTA model per family, resolved at import from env overrides (so the toolkit
# tracks "newest available" without a code change). Defaults verified live 2026-06-26.
CLAUDE_MODEL = os.environ.get("TELOS_CLAUDE_MODEL", "claude-opus-4-8")
GEMINI_MODEL = os.environ.get("TELOS_GEMINI_MODEL", "gemini-3.1-pro-preview")
OPENAI_MODEL = os.environ.get("TELOS_OPENAI_MODEL", "gpt-5.5")

DEFAULT_TIMEOUT = int(os.environ.get("TELOS_TIMEOUT", "240"))


@dataclass
class ModelReply:
    family: str
    model: str
    text: str = ""
    ok: bool = True
    error: str = ""
    latency_s: float = 0.0
    raw: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = {
            "family": self.family,
            "model": self.model,
            "text": self.text,
            "ok": self.ok,
            "error": self.error,
            "latency_s": round(self.latency_s, 2),
        }
        return d


# --------------------------------------------------------------------------------------
# transport helper
# --------------------------------------------------------------------------------------
def _post_json(url: str, payload: dict, headers: dict, timeout: int) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (trusted endpoints)
        return json.loads(resp.read().decode("utf-8"))


# --------------------------------------------------------------------------------------
# Claude — local CLI, Max-plan billing
# --------------------------------------------------------------------------------------
def call_claude(
    prompt: str,
    system: str = "",
    model: Optional[str] = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> ModelReply:
    model = model or CLAUDE_MODEL
    if shutil.which("claude") is None:
        return ModelReply("claude", model, ok=False, error="claude CLI not found on PATH")

    # Strip ANTHROPIC_API_KEY so the child routes through the Max-plan OAuth, not the
    # paid API (per Ariel's standing cost rule). The prompt is piped via STDIN rather than
    # passed as an argv element: long prompts blow past the Windows command-line length
    # limit (WinError 206), and stdin has no such cap.
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    cmd = ["claude", "-p", "--model", model, "--output-format", "json"]
    if system:
        cmd += ["--append-system-prompt", system]
    # Belt and braces: never let the headless child touch the filesystem or shell.
    cmd += ["--disallowedTools", "Bash,Edit,Write,NotebookEdit"]

    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd,
            env=env,
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",        # Windows defaults stdin to cp1252, which chokes on
            errors="replace",        # non-Latin-1 chars (e.g. arrows/em-dashes) in prompts
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return ModelReply("claude", model, ok=False, error=f"timeout after {timeout}s",
                          latency_s=time.time() - t0)
    if proc.returncode != 0:
        return ModelReply("claude", model, ok=False,
                          error=f"exit {proc.returncode}: {proc.stderr.strip()[:300]}",
                          latency_s=time.time() - t0)

    text = _extract_claude_text(proc.stdout)
    return ModelReply("claude", model, text=text, ok=bool(text), latency_s=time.time() - t0,
                      error="" if text else "empty result")


def _extract_claude_text(stdout: str) -> str:
    """``claude -p --output-format json`` emits a result envelope; tolerate format drift."""
    stdout = stdout.strip()
    if not stdout:
        return ""
    try:
        obj = json.loads(stdout)
        if isinstance(obj, dict):
            for key in ("result", "text", "content", "response"):
                v = obj.get(key)
                if isinstance(v, str) and v.strip():
                    return v.strip()
        if isinstance(obj, str):
            return obj.strip()
    except json.JSONDecodeError:
        pass
    return stdout  # last resort: the raw stdout is the answer


# --------------------------------------------------------------------------------------
# Gemini — REST generateContent
# --------------------------------------------------------------------------------------
def call_gemini(
    prompt: str,
    system: str = "",
    model: Optional[str] = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> ModelReply:
    model = model or GEMINI_MODEL
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        return ModelReply("gemini", model, ok=False, error="GEMINI_API_KEY unset")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 8192,
                             "thinkingConfig": {"thinkingLevel": "high"}},
    }
    if system:
        payload["systemInstruction"] = {"parts": [{"text": system}]}

    t0 = time.time()
    try:
        data = _post_json(url, payload, headers={}, timeout=timeout)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")[:300]
        # Older models reject thinkingConfig; retry once without it.
        if "thinking" in body.lower() or e.code == 400:
            payload["generationConfig"].pop("thinkingConfig", None)
            try:
                data = _post_json(url, payload, headers={}, timeout=timeout)
            except Exception as e2:  # noqa: BLE001
                return ModelReply("gemini", model, ok=False, error=f"{e.code}: {e2}",
                                  latency_s=time.time() - t0)
        else:
            return ModelReply("gemini", model, ok=False, error=f"HTTP {e.code}: {body}",
                              latency_s=time.time() - t0)
    except Exception as e:  # noqa: BLE001
        return ModelReply("gemini", model, ok=False, error=str(e), latency_s=time.time() - t0)

    text = _extract_gemini_text(data)
    return ModelReply("gemini", model, text=text, ok=bool(text), latency_s=time.time() - t0,
                      error="" if text else "empty result")


def _extract_gemini_text(data: dict) -> str:
    out = []
    for cand in data.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            if part.get("thought"):  # skip thinking traces
                continue
            if isinstance(part.get("text"), str):
                out.append(part["text"])
    return "".join(out).strip()


# --------------------------------------------------------------------------------------
# OpenAI — REST Responses API
# --------------------------------------------------------------------------------------
def call_openai(
    prompt: str,
    system: str = "",
    model: Optional[str] = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> ModelReply:
    model = model or OPENAI_MODEL
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return ModelReply("openai", model, ok=False, error="OPENAI_API_KEY unset")

    url = "https://api.openai.com/v1/responses"
    inputs = []
    if system:
        inputs.append({"role": "system", "content": system})
    inputs.append({"role": "user", "content": prompt})
    payload = {
        "model": model,
        "input": inputs,
        "reasoning": {"effort": "high"},
        "max_output_tokens": 8192,
    }
    headers = {"Authorization": f"Bearer {key}"}

    t0 = time.time()
    try:
        data = _post_json(url, payload, headers=headers, timeout=timeout)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")[:300]
        return ModelReply("openai", model, ok=False, error=f"HTTP {e.code}: {body}",
                          latency_s=time.time() - t0)
    except Exception as e:  # noqa: BLE001
        return ModelReply("openai", model, ok=False, error=str(e), latency_s=time.time() - t0)

    text = _extract_openai_text(data)
    return ModelReply("openai", model, text=text, ok=bool(text), latency_s=time.time() - t0,
                      error="" if text else "empty result")


def _extract_openai_text(data: dict) -> str:
    # Convenience field first (some SDK-compatible responses include it).
    if isinstance(data.get("output_text"), str) and data["output_text"].strip():
        return data["output_text"].strip()
    out = []
    for item in data.get("output", []):
        if item.get("type") == "message":
            for c in item.get("content", []):
                if c.get("type") in ("output_text", "text") and isinstance(c.get("text"), str):
                    out.append(c["text"])
    return "".join(out).strip()


# --------------------------------------------------------------------------------------
# registry
# --------------------------------------------------------------------------------------
PROVIDERS = {
    "claude": call_claude,
    "gemini": call_gemini,
    "openai": call_openai,
}


def call(family: str, prompt: str, system: str = "", **kw) -> ModelReply:
    fn = PROVIDERS.get(family)
    if fn is None:
        return ModelReply(family, "?", ok=False, error=f"unknown family {family!r}")
    return fn(prompt, system=system, **kw)


def available_families() -> list[str]:
    """Which families are usable right now (key present / CLI installed)."""
    fams = []
    if shutil.which("claude"):
        fams.append("claude")
    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        fams.append("gemini")
    if os.environ.get("OPENAI_API_KEY"):
        fams.append("openai")
    return fams
