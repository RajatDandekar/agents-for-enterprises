"""One small client for every chat model the course uses, with a replay mode.

    from bahi.llm import LLM
    llm = LLM("gemini:gemini-3.8-flash", cassette="nb1")
    r = llm.chat([{"role": "user", "content": "hi"}], tools=[...])
    r.content, r.tool_calls, r.tokens_in, r.tokens_out, r.seconds, r.cost_inr

Every provider is reached through the OpenAI-compatible chat-completions API, so one code path serves
Gemini, OpenRouter (GPT, Claude, Llama ...), OpenAI and Anthropic.

Replay. Each request is hashed (model, messages, tools, settings). In "record" mode the reply is stored in
bahi/cassettes/<cassette>.jsonl; in "replay" mode it is read back, with the original token counts and
seconds, so a notebook runs top to bottom without a key and shows the numbers of the recorded run.
Mode comes from BAHI_LLM_MODE: auto (default: replay if recorded, else call live if a key is set),
replay, record, live.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import threading
import time
from dataclasses import dataclass, field

USD_INR = 88.0  # fixed for the course so costs are comparable across runs

_CLIENT_LOCK = threading.Lock()

PROVIDERS = {
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai/", ["GEMINI_API_KEY", "GOOGLE_API_KEY"]),
    "openrouter": ("https://openrouter.ai/api/v1", ["OPENROUTER_API_KEY"]),
    "openai": ("https://api.openai.com/v1", ["OPENAI_API_KEY"]),
    "anthropic": ("https://api.anthropic.com/v1/", ["ANTHROPIC_API_KEY"]),
}

# USD per million tokens (input, output). Edit when prices change; the course reports ₹ from these.
PRICES = {  # assumed list prices for the course's three Gemini tiers; edit when your provider's prices differ
    "gemini-3.5-flash-lite": (0.10, 0.40),
    "gemini-3.1-flash-lite": (0.10, 0.40),
    "gemini-3-flash-preview": (0.50, 3.00),
    "gemini-3.8-flash": (0.50, 3.00),
    "gemini-3.1-pro-preview": (2.00, 12.0),
    "gemini-pro-latest": (2.00, 12.0),
    "gpt-6.1-terra": (1.00, 5.00),        # OpenRouter list price, 27 Oct 2026 (openai/gpt-6.1-terra)
    "claude-sonnet-5.5": (2.00, 10.0),    # OpenRouter list price, 27 Oct 2026 (anthropic/claude-sonnet-5.5)
}

CASSETTE_DIR = pathlib.Path(os.environ.get("BAHI_CASSETTES", pathlib.Path(__file__).parent / "cassettes"))
_lock = threading.Lock()


def load_env_file(path: str | None = None):
    """Read KEY=VALUE lines from a .env file into os.environ (does not overwrite what is already set)."""
    path = path or os.environ.get("BAHI_ENV_FILE")
    if not path or not os.path.exists(path):
        return
    for line in open(path):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict
    extra: dict | None = None  # provider data to echo back (Gemini 3 needs its thought signature returned)


@dataclass
class Reply:
    content: str | None
    tool_calls: list[ToolCall]
    tokens_in: int
    tokens_out: int
    seconds: float
    model: str
    replayed: bool = False
    raw: dict = field(default_factory=dict)

    @property
    def cost_inr(self) -> float:
        p = PRICES.get(self.model.split(":", 1)[-1].split("/")[-1])
        if not p:
            return 0.0
        return round((self.tokens_in * p[0] + self.tokens_out * p[1]) / 1e6 * USD_INR, 4)

    def message(self) -> dict:
        """The assistant message to append to the conversation."""
        m = {"role": "assistant", "content": self.content}
        if self.tool_calls:
            m["tool_calls"] = [{"id": t.id, "type": "function",
                                "function": {"name": t.name, "arguments": json.dumps(t.arguments)},
                                **({"extra_content": t.extra} if t.extra else {})}
                               for t in self.tool_calls]
        return m


class ReplayMiss(RuntimeError):
    pass


class LLM:
    def __init__(self, model: str | None = None, cassette: str = "default", mode: str | None = None,
                 temperature: float = 0.0, max_tokens: int = 2048):
        load_env_file()
        self.model = model or os.environ.get("BAHI_MODEL", "gemini:gemini-3.8-flash")
        if ":" not in self.model:
            self.model = "gemini:" + self.model
        self.provider, self.model_id = self.model.split(":", 1)
        self.cassette = cassette
        self.mode = (mode or os.environ.get("BAHI_LLM_MODE", "auto")).lower()
        self.temperature, self.max_tokens = temperature, max_tokens
        self.log: list[Reply] = []
        self._client = None

    # ------------------------------------------------------------------ public
    def chat(self, messages: list[dict], tools: list[dict] | None = None, response_format: dict | None = None,
             **kw) -> Reply:
        req = {"model": self.model, "messages": messages, "tools": tools or None, "temperature": self.temperature,
               "response_format": response_format, **kw}
        key = hashlib.sha256(json.dumps(req, sort_keys=True, default=str).encode()).hexdigest()[:24]
        rec = None if self.mode in ("live", "record") else self._lookup(key)
        if rec is not None:
            r = self._from_record(rec, replayed=True)
        elif self.mode == "replay" or (self.mode == "auto" and not self._has_key()):
            raise ReplayMiss(
                f"No recorded reply for this request in cassette '{self.cassette}' and no live key. "
                f"Set {PROVIDERS[self.provider][1][0]} (and BAHI_LLM_MODE=live) to call {self.model} for real.")
        else:
            r = self._live(messages, tools, response_format, **kw)
            if self.mode in ("record", "auto"):
                self._store(key, r)
        self.log.append(r)
        return r

    def totals(self) -> dict:
        return {"calls": len(self.log), "tokens_in": sum(r.tokens_in for r in self.log),
                "tokens_out": sum(r.tokens_out for r in self.log),
                "seconds": round(sum(r.seconds for r in self.log), 2),
                "cost_inr": round(sum(r.cost_inr for r in self.log), 4)}

    # ------------------------------------------------------------------ live
    def _has_key(self) -> bool:
        return any(os.environ.get(k) for k in PROVIDERS[self.provider][1])

    def _live(self, messages, tools, response_format, **kw) -> Reply:
        with _CLIENT_LOCK:  # importing openai lazily from several threads at once raced (L4 experiment, 2026-10-28)
            from openai import OpenAI

        if self._client is None:
            base, keys = PROVIDERS[self.provider]
            api_key = next((os.environ[k] for k in keys if os.environ.get(k)), None)
            self._client = OpenAI(base_url=base, api_key=api_key, max_retries=4, timeout=120)
        args = {"model": self.model_id, "messages": messages, "temperature": self.temperature,
                "max_tokens": self.max_tokens, **kw}
        if tools:
            args["tools"] = tools
        if response_format:
            args["response_format"] = response_format
        t0 = time.perf_counter()
        try:
            resp = self._client.chat.completions.create(**args)
        except Exception as e:  # show the provider's reason, not just the status code
            body = getattr(getattr(e, "response", None), "text", "")
            raise RuntimeError(f"{self.model}: {e} {body[:600]}") from e
        secs = time.perf_counter() - t0
        msg = resp.choices[0].message
        calls = []
        for i, tc in enumerate(msg.tool_calls or []):
            try:
                a = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                a = {"_unparsed": tc.function.arguments}
            extra = (tc.model_extra or {}).get("extra_content")
            calls.append(ToolCall(tc.id or f"call_{i}", tc.function.name, a, extra))
        u = resp.usage
        return Reply(msg.content, calls, getattr(u, "prompt_tokens", 0) or 0, getattr(u, "completion_tokens", 0) or 0,
                     round(secs, 3), self.model)

    # ------------------------------------------------------------------ cassette
    def _path(self) -> pathlib.Path:
        return CASSETTE_DIR / f"{self.cassette}.jsonl"

    def _lookup(self, key):
        p = self._path()
        if not p.exists():
            return None
        if getattr(self, "_cache_for", None) != (p, p.stat().st_mtime):
            self._cache = {}
            for line in p.open():
                if line.strip():
                    d = json.loads(line)
                    self._cache[d["key"]] = d
            self._cache_for = (p, p.stat().st_mtime)
        return self._cache.get(key)

    def _store(self, key, r: Reply):
        p = self._path()
        p.parent.mkdir(parents=True, exist_ok=True)
        if self._lookup(key) is not None:  # parallel threads recorded the same request: the first one wins
            return
        d = {"key": key, "model": r.model, "content": r.content,
             "tool_calls": [{"id": t.id, "name": t.name, "arguments": t.arguments, "extra": t.extra}
                            for t in r.tool_calls],
             "tokens_in": r.tokens_in, "tokens_out": r.tokens_out, "seconds": r.seconds}
        with _lock, p.open("a") as f:
            f.write(json.dumps(d) + "\n")

    @staticmethod
    def _from_record(d, replayed) -> Reply:
        return Reply(d["content"], [ToolCall(**t) for t in d["tool_calls"]], d["tokens_in"], d["tokens_out"],
                     d["seconds"], d["model"], replayed=replayed)


def tool_schema(name: str, description: str, properties: dict, required: list[str] | None = None) -> dict:
    """An OpenAI-style function tool definition."""
    return {"type": "function", "function": {"name": name, "description": description,
                                             "parameters": {"type": "object", "properties": properties,
                                                            "required": required or []}}}
