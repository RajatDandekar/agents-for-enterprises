"""The meter: a small OpenAI-compatible model gateway on localhost, so every framework is measured the same way.

    from bahi.course.frameworks.meter import Meter
    m = Meter(cassette="IND8_demo").start()            # http://127.0.0.1:<port>
    url = m.base_url("T01-KJOSHI")                     # give this to any SDK as its OpenAI base_url
    ...                                               # run the framework
    m.records("T01-KJOSHI")                            # one row per model call: tokens, seconds, cost, replayed

Every framework in Lecture 8 speaks the OpenAI chat-completions API to some model. Point them all at this meter and
it (1) forwards each request to the real model through OpenRouter (or a local Ollama), (2) records the reply in a
cassette (bahi/cassettes/<cassette>.jsonl), (3) logs tokens, seconds and the cost OpenRouter billed, and (4) in
replay mode answers from the cassette with no key at all. The framework code runs for real either way: only the
model's replies are played back. This is LiteLLM-proxy / OpenRouter in sixty lines, for teaching.

The run tag in the URL path (/run/<tag>/v1/...) says which framework and task each call belongs to.
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from ...llm import LLM, PROVIDERS, USD_INR, ReplayMiss, Reply, ToolCall

UPSTREAMS = {  # provider prefix -> OpenAI-compatible base URL and key variable
    "openrouter": (PROVIDERS["openrouter"][0], "OPENROUTER_API_KEY"),
    "ollama": (os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1"), None),
}


class MeteredLLM(LLM):
    """bahi.llm.LLM, plus: the cost OpenRouter actually billed (usage.cost) is kept in the cassette, and a local
    Ollama model is a provider too ("ollama:qwen3:8b"). Same cassette format and request hashing as LLM."""

    def _has_key(self) -> bool:
        if self.provider == "ollama":
            return True
        return super()._has_key()

    def chat(self, messages, tools=None, response_format=None, **kw):
        try:
            return super().chat(messages, tools, response_format, **kw)
        except KeyError:  # an unknown provider on a replay miss
            raise ReplayMiss(f"No recorded reply in cassette '{self.cassette}' for {self.model}.")

    def _live(self, messages, tools, response_format, **kw) -> Reply:
        from openai import OpenAI
        base, keyvar = UPSTREAMS[self.provider] if self.provider in UPSTREAMS else (None, None)
        if base is None:
            return super()._live(messages, tools, response_format, **kw)
        if self._client is None:
            self._client = OpenAI(base_url=base, api_key=os.environ.get(keyvar, "") if keyvar else "ollama",
                                  max_retries=4, timeout=300)
        args = {"model": self.model_id, "messages": messages, "temperature": self.temperature,
                "max_tokens": self.max_tokens, **kw}
        if tools:
            args["tools"] = tools
        if response_format:
            args["response_format"] = response_format
        if self.provider == "openrouter":
            args["extra_body"] = {"usage": {"include": True}}
        t0 = time.perf_counter()
        try:
            resp = self._client.chat.completions.create(**args)
        except Exception as e:
            body = getattr(getattr(e, "response", None), "text", "")
            raise RuntimeError(f"{self.model}: {e} {body[:600]}") from e
        secs = time.perf_counter() - t0
        if not resp.choices:
            raise RuntimeError(f"{self.model}: empty choices {str(resp)[:300]}")
        msg = resp.choices[0].message
        calls = []
        for i, tc in enumerate(msg.tool_calls or []):
            try:
                a = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                a = {"_unparsed": tc.function.arguments}
            calls.append(ToolCall(tc.id or f"call_{i}", tc.function.name, a, (tc.model_extra or {}).get("extra_content")))
        u = resp.usage
        cost = (getattr(u, "model_extra", None) or {}).get("cost") if u is not None else None
        r = Reply(msg.content, calls, getattr(u, "prompt_tokens", 0) or 0, getattr(u, "completion_tokens", 0) or 0,
                  round(secs, 3), self.model)
        r.raw = {"cost_usd": cost, "provider": getattr(resp, "provider", None) or (resp.model_extra or {}).get("provider")}
        return r

    def _store(self, key, r: Reply):
        p = self._path()
        p.parent.mkdir(parents=True, exist_ok=True)
        if self._lookup(key) is not None:
            return
        d = {"key": key, "model": r.model, "content": r.content,
             "tool_calls": [{"id": t.id, "name": t.name, "arguments": t.arguments, "extra": t.extra} for t in r.tool_calls],
             "tokens_in": r.tokens_in, "tokens_out": r.tokens_out, "seconds": r.seconds,
             "cost_usd": (r.raw or {}).get("cost_usd"), "provider": (r.raw or {}).get("provider")}
        from ...llm import _lock
        with _lock, p.open("a") as f:
            f.write(json.dumps(d) + "\n")

    @staticmethod
    def _from_record(d, replayed) -> Reply:
        r = Reply(d["content"], [ToolCall(**t) for t in d["tool_calls"]], d["tokens_in"], d["tokens_out"],
                  d["seconds"], d["model"], replayed=replayed)
        r.raw = {"cost_usd": d.get("cost_usd"), "provider": d.get("provider")}
        return r


def billed_inr(r: Reply) -> float:
    """₹ for one reply: what OpenRouter billed when we recorded it, else the course's list-price table, else 0."""
    c = (r.raw or {}).get("cost_usd")
    return round(float(c) * USD_INR, 4) if c is not None else r.cost_inr


# ----------------------------------------------------------------------------- request normalisation
def _text(content):
    if content is None or isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [p.get("text", "") if isinstance(p, dict) else str(p) for p in content]
        return "".join(parts)
    return str(content)


def normalise(messages: list[dict]) -> list[dict]:
    """The parts of a chat request that decide the reply, in one canonical shape: SDKs differ in empty strings,
    content-part lists and argument spacing, none of which the model sees differently."""
    out = []
    for m in messages:
        role = m.get("role")
        n = {"role": "system" if role == "developer" else role}
        c = _text(m.get("content"))
        if m.get("tool_calls"):
            n["content"] = c or None
            n["tool_calls"] = []
            for tc in m["tool_calls"]:
                f = tc.get("function", {})
                try:
                    args = json.loads(f.get("arguments") or "{}")
                except (json.JSONDecodeError, TypeError):
                    args = f.get("arguments")
                n["tool_calls"].append({"id": tc.get("id"), "type": "function",
                                        "function": {"name": f.get("name"),
                                                     "arguments": json.dumps(args, sort_keys=True)}})
        else:
            n["content"] = c if c is not None else ""
        if role == "tool":
            n["tool_call_id"] = m.get("tool_call_id")
        out.append(n)
    return out


# ----------------------------------------------------------------------------- the HTTP gateway
class Meter:
    def __init__(self, cassette: str = "IND8_meter", mode: str | None = None, default_model: str | None = None,
                 port: int = 0, max_tokens: int = 2048):
        self.cassette, self.mode, self.max_tokens = cassette, mode, max_tokens
        self.default_model = default_model or "openrouter:google/gemini-3.8-flash"
        self.port = port
        self._llms: dict[str, MeteredLLM] = {}
        self.log: list[dict] = []          # one row per model call, every run
        self.replies: dict[str, list] = {}  # run tag -> [Reply], for bahi.course.l5.tasks.run_task
        self.first: dict[str, dict] = {}    # run tag -> the first request it sent (what the framework puts on the wire)
        self._lock = threading.Lock()
        self.server = None

    # -------------------------------------------------------------- lifecycle
    def start(self) -> "Meter":
        meter = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):  # quiet
                pass

            def do_GET(self):
                self._send(200, {"object": "list", "data": [{"id": meter.default_model.split(":", 1)[1],
                                                             "object": "model"}]})

            def do_POST(self):
                n = int(self.headers.get("content-length") or 0)
                body = json.loads(self.rfile.read(n) or b"{}")
                path = self.path
                tag = path.split("/run/", 1)[1].split("/", 1)[0] if "/run/" in path else "default"
                try:
                    resp = meter.complete(tag, body)
                except ReplayMiss as e:
                    return self._send(404, {"error": {"message": str(e), "type": "replay_miss"}})
                except Exception as e:  # noqa: BLE001
                    return self._send(502, {"error": {"message": f"{type(e).__name__}: {str(e)[:800]}",
                                                      "type": "upstream"}})
                if body.get("stream"):
                    return self._stream(resp)
                self._send(200, resp)

            def _send(self, code, obj):
                data = json.dumps(obj).encode()
                self.send_response(code)
                self.send_header("content-type", "application/json")
                self.send_header("content-length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def _stream(self, resp):  # one chunk with the whole reply, then [DONE]
                ch = resp["choices"][0]
                delta = {"role": "assistant", "content": ch["message"].get("content")}
                if ch["message"].get("tool_calls"):
                    delta["tool_calls"] = [{"index": i, **tc} for i, tc in enumerate(ch["message"]["tool_calls"])]
                chunks = [{"id": resp["id"], "object": "chat.completion.chunk", "created": resp["created"],
                           "model": resp["model"], "choices": [{"index": 0, "delta": delta, "finish_reason": None}]},
                          {"id": resp["id"], "object": "chat.completion.chunk", "created": resp["created"],
                           "model": resp["model"], "choices": [{"index": 0, "delta": {},
                                                                "finish_reason": ch["finish_reason"]}],
                           "usage": resp["usage"]}]
                self.send_response(200)
                self.send_header("content-type", "text/event-stream")
                self.end_headers()
                for c in chunks:
                    self.wfile.write(f"data: {json.dumps(c)}\n\n".encode())
                self.wfile.write(b"data: [DONE]\n\n")

        self.server = ThreadingHTTPServer(("127.0.0.1", self.port), H)
        self.server.daemon_threads = True
        self.port = self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return self

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()

    def base_url(self, tag: str = "default") -> str:
        return f"http://127.0.0.1:{self.port}/run/{tag}/v1"

    # -------------------------------------------------------------- one request
    def _llm(self, model: str) -> MeteredLLM:
        with self._lock:
            if model not in self._llms:
                self._llms[model] = MeteredLLM(model, cassette=self.cassette, mode=self.mode, max_tokens=self.max_tokens)
            return self._llms[model]

    def complete(self, tag: str, body: dict) -> dict:
        req_model = body.get("model") or self.default_model.split(":", 1)[1]
        model = req_model if ":" in req_model and req_model.split(":", 1)[0] in UPSTREAMS else (
            ("ollama:" + req_model) if self.default_model.startswith("ollama:") else "openrouter:" + req_model)
        msgs = normalise(body.get("messages") or [])
        tools = body.get("tools") or None
        kw = {}
        tc = body.get("tool_choice")
        if tc and tc != "auto" and tools:
            kw["tool_choice"] = tc
        t0 = time.perf_counter()
        r = self._llm(model).chat(msgs, tools=tools, **kw)
        wall = time.perf_counter() - t0
        row = {"run": tag, "model": r.model, "tokens_in": r.tokens_in, "tokens_out": r.tokens_out,
               "seconds": r.seconds, "cost_inr": billed_inr(r), "replayed": r.replayed, "messages": len(msgs),
               "tools": len(tools or []), "tools_bytes": len(json.dumps(tools or [])),
               "system_bytes": sum(len(m.get("content") or "") for m in msgs if m["role"] == "system"),
               "calls": [t.name for t in r.tool_calls], "gateway_ms": round(wall * 1000, 1)}
        with self._lock:
            self.first.setdefault(tag, {"messages": msgs, "tools": tools, "tool_choice": tc})
            self.log.append(row)
            self.replies.setdefault(tag, []).append(r)
        rid = "chatcmpl-" + hashlib.sha256(json.dumps([msgs, r.content, [t.id for t in r.tool_calls]],
                                                      default=str).encode()).hexdigest()[:20]
        message = {"role": "assistant", "content": r.content}
        if r.tool_calls:
            message["tool_calls"] = [{"id": t.id, "type": "function",
                                      "function": {"name": t.name, "arguments": json.dumps(t.arguments)}}
                                     for t in r.tool_calls]
        return {"id": rid, "object": "chat.completion", "created": 1793000000, "model": req_model,
                "choices": [{"index": 0, "message": message,
                             "finish_reason": "tool_calls" if r.tool_calls else "stop"}],
                "usage": {"prompt_tokens": r.tokens_in, "completion_tokens": r.tokens_out,
                          "total_tokens": r.tokens_in + r.tokens_out}}

    # -------------------------------------------------------------- what we measured
    def records(self, prefix: str = "") -> list[dict]:
        return [r for r in self.log if r["run"].startswith(prefix)]

    def view(self, tag: str) -> "MeterView":
        return MeterView(self, tag)


class MeterView:
    """Looks like bahi.llm.LLM to bahi.course.l5.tasks.run_task: .log is the list of replies for one run tag."""

    def __init__(self, meter: Meter, tag: str):
        self.meter, self.tag = meter, tag

    @property
    def log(self):
        return [_Billed(r) for r in self.meter.replies.get(self.tag, [])]


class _Billed:
    """A Reply whose cost_inr is what OpenRouter billed."""

    def __init__(self, r: Reply):
        self._r = r

    def __getattr__(self, k):
        return getattr(self._r, k)

    @property
    def cost_inr(self):
        return billed_inr(self._r)
