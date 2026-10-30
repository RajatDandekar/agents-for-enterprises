"""The model gateway: one OpenAI-compatible endpoint on localhost that every stack talks to.

    gw = Gateway(tracer).start()
    url = gw.base_url(tag="ours-gemini-3.8-flash-r1-M4", cassette="L1v4_prod_ours_gemini-3.8-flash_r1")
    # give `url` to any SDK as its OpenAI base_url; set gw.parent[tag] = the current turn's span
    gw.records(tag)        # one row per model call: tokens, seconds, US dollars billed, upstream provider, replayed

For each request it (1) forwards it to OpenRouter (https://openrouter.ai/api/v1), the one API in front of every model
in the ablation, (2) records the reply in a cassette, ledgerline/cassettes/<cassette>.jsonl, so the run replays with no
key (LEDGER_LLM_MODE=replay; auto = replay what is recorded, call live for the rest), (3) writes a GenAI `chat` span
under the turn that sent it, and (4) keeps the cost OpenRouter billed (usage.cost, US dollars).

In production this box is OpenRouter itself, LiteLLM's proxy, Portkey or a cloud AI gateway. Here it is ~150 lines,
because a gateway is the one place that sees every model call of every framework the same way.
A spend cap (budget_usd) refuses new live calls once the run has spent it: an agent that loops cannot run up a bill.
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from ....llm import LLM, ReplayMiss, Reply, ToolCall
from . import tracing as T

OPENROUTER = "https://openrouter.ai/api/v1"


class BudgetExceeded(RuntimeError):
    pass


class RecordedModel(LLM):
    """ledgerline.llm.LLM (same cassette format and request hashing) for OpenRouter, keeping the billed cost."""

    def _live(self, messages, tools, response_format, **kw) -> Reply:
        from openai import OpenAI
        if self._client is None:
            self._client = OpenAI(base_url=OPENROUTER, api_key=os.environ.get("OPENROUTER_API_KEY", ""),
                                  max_retries=4, timeout=240)
        args = {"model": self.model_id, "messages": messages, "temperature": self.temperature,
                "max_tokens": self.max_tokens, "extra_body": {"usage": {"include": True}}, **kw}
        if tools:
            args["tools"] = tools
        t0 = time.perf_counter()
        try:
            resp = self._client.chat.completions.create(**args)
        except Exception as e:  # noqa: BLE001
            body = getattr(getattr(e, "response", None), "text", "")
            raise RuntimeError(f"{self.model}: {e} {body[:400]}") from e
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
            calls.append(ToolCall(tc.id or f"call_{i}", tc.function.name, a if isinstance(a, dict) else {"_value": a}))
        u = resp.usage
        r = Reply(msg.content, calls, getattr(u, "prompt_tokens", 0) or 0, getattr(u, "completion_tokens", 0) or 0,
                  round(secs, 3), self.model)
        r.raw = {"cost_usd": (getattr(u, "model_extra", None) or {}).get("cost") if u is not None else None,
                 "provider": getattr(resp, "provider", None) or (resp.model_extra or {}).get("provider"),
                 "finish": resp.choices[0].finish_reason}
        return r

    def _store(self, key, r: Reply):
        p = self._path()
        p.parent.mkdir(parents=True, exist_ok=True)
        if self._lookup(key) is not None:
            return
        d = {"key": key, "model": r.model, "content": r.content,
             "tool_calls": [{"id": t.id, "name": t.name, "arguments": t.arguments, "extra": t.extra} for t in r.tool_calls],
             "tokens_in": r.tokens_in, "tokens_out": r.tokens_out, "seconds": r.seconds, **(r.raw or {})}
        from ....llm import _lock
        with _lock, p.open("a") as f:
            f.write(json.dumps(d) + "\n")

    @staticmethod
    def _from_record(d, replayed) -> Reply:
        r = Reply(d["content"], [ToolCall(**t) for t in d["tool_calls"]], d["tokens_in"], d["tokens_out"],
                  d["seconds"], d["model"], replayed=replayed)
        r.raw = {k: d.get(k) for k in ("cost_usd", "provider", "finish")}
        return r


def normalise(messages: list[dict]) -> list[dict]:
    """The parts of a request that decide the reply, in one shape: SDKs differ in empty strings, content-part lists
    and argument spacing, none of which the model sees differently (from Lecture 8's meter)."""
    def text(c):
        if c is None or isinstance(c, str):
            return c
        if isinstance(c, list):
            return "".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in c)
        return str(c)

    out = []
    for m in messages:
        role = m.get("role")
        n = {"role": "system" if role == "developer" else role}
        c = text(m.get("content"))
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
                                        "function": {"name": f.get("name"), "arguments": json.dumps(args, sort_keys=True)}})
        else:
            n["content"] = c if c is not None else ""
        if role == "tool":
            n["tool_call_id"] = m.get("tool_call_id")
        out.append(n)
    return out


class Gateway:
    def __init__(self, tracer=None, mode: str | None = None, max_tokens: int = 4096, budget_usd: float = 3.0):
        self.tracer, self.mode, self.max_tokens, self.budget_usd = tracer, mode, max_tokens, budget_usd
        self.cassettes: dict[str, str] = {}   # run tag -> cassette name
        self.parent: dict[str, object] = {}   # run tag -> the span new chat spans go under (the current turn)
        self.log: list[dict] = []
        self.spent_usd = 0.0
        self._models: dict[tuple, RecordedModel] = {}
        self._lock = threading.Lock()
        self.server = None

    def start(self) -> "Gateway":
        gw = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                self._send(200, {"object": "list", "data": []})

            def do_POST(self):
                n = int(self.headers.get("content-length") or 0)
                body = json.loads(self.rfile.read(n) or b"{}")
                tag = self.path.split("/run/", 1)[1].split("/", 1)[0] if "/run/" in self.path else "default"
                try:
                    resp = gw.complete(tag, body)
                except BudgetExceeded as e:
                    return self._send(402, {"error": {"message": str(e), "type": "budget"}})
                except ReplayMiss as e:
                    return self._send(404, {"error": {"message": str(e), "type": "replay_miss"}})
                except Exception as e:  # noqa: BLE001
                    return self._send(502, {"error": {"message": f"{type(e).__name__}: {str(e)[:600]}", "type": "upstream"}})
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
                base = {"id": resp["id"], "object": "chat.completion.chunk", "created": resp["created"], "model": resp["model"]}
                self.send_response(200)
                self.send_header("content-type", "text/event-stream")
                self.end_headers()
                for c in ({**base, "choices": [{"index": 0, "delta": delta, "finish_reason": None}]},
                          {**base, "choices": [{"index": 0, "delta": {}, "finish_reason": ch["finish_reason"]}],
                           "usage": resp["usage"]}):
                    self.wfile.write(f"data: {json.dumps(c)}\n\n".encode())
                self.wfile.write(b"data: [DONE]\n\n")

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.server.daemon_threads = True
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return self

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()

    def base_url(self, tag: str, cassette: str) -> str:
        self.cassettes[tag] = cassette
        return f"http://127.0.0.1:{self.server.server_address[1]}/run/{tag}/v1"

    def _model(self, model: str, cassette: str) -> RecordedModel:
        with self._lock:
            k = (model, cassette)
            if k not in self._models:
                self._models[k] = RecordedModel("openrouter:" + model, cassette=cassette, mode=self.mode,
                                                max_tokens=self.max_tokens)
            return self._models[k]

    def complete(self, tag: str, body: dict) -> dict:
        model = body.get("model") or ""
        msgs = normalise(body.get("messages") or [])
        tools = body.get("tools") or None
        kw = {}
        if body.get("tool_choice") and body["tool_choice"] != "auto" and tools:
            kw["tool_choice"] = body["tool_choice"]
        llm = self._model(model, self.cassettes.get(tag, "L1v4_prod_default"))
        if self.spent_usd >= self.budget_usd and llm.mode != "replay":
            key_req = {"model": llm.model, "messages": msgs, "tools": tools, "temperature": llm.temperature,
                       "response_format": None, **kw}
            key = hashlib.sha256(json.dumps(key_req, sort_keys=True, default=str).encode()).hexdigest()[:24]
            if llm._lookup(key) is None:
                raise BudgetExceeded(f"spend cap reached: ${self.spent_usd:.2f} of ${self.budget_usd:.2f}")
        sp = T.chat_span(self.tracer, self.parent.get(tag), model, msgs, tools,
                         {"temperature": llm.temperature, "max_tokens": llm.max_tokens}) if self.tracer else None
        t0 = time.perf_counter()
        try:
            r = llm.chat(msgs, tools=tools, **kw)
        except Exception as e:
            if sp is not None:
                T.finish_chat(sp, None, None, None, False, error=str(e))
            with self._lock:
                self.log.append({"run": tag, "model": model, "error": str(e)[:300]})
            raise
        wall = time.perf_counter() - t0
        cost = (r.raw or {}).get("cost_usd")
        if sp is not None:
            T.finish_chat(sp, r, cost, (r.raw or {}).get("provider"), r.replayed)
        with self._lock:
            if not r.replayed and cost:
                self.spent_usd += float(cost)
            self.log.append({"run": tag, "model": model, "tokens_in": r.tokens_in, "tokens_out": r.tokens_out,
                             "seconds": r.seconds, "wall_s": round(wall, 3), "cost_usd": cost,
                             "provider": (r.raw or {}).get("provider"), "replayed": r.replayed,
                             "calls": [t.name for t in r.tool_calls], "messages": len(msgs)})
        message = {"role": "assistant", "content": r.content}
        if r.tool_calls:
            message["tool_calls"] = [{"id": t.id, "type": "function",
                                      "function": {"name": t.name, "arguments": json.dumps(t.arguments)}}
                                     for t in r.tool_calls]
        rid = "chatcmpl-" + hashlib.sha256(json.dumps([msgs[-1:], r.content], default=str).encode()).hexdigest()[:20]
        return {"id": rid, "object": "chat.completion", "created": int(time.time()), "model": model,
                "choices": [{"index": 0, "message": message, "finish_reason": "tool_calls" if r.tool_calls else "stop"}],
                "usage": {"prompt_tokens": r.tokens_in, "completion_tokens": r.tokens_out,
                          "total_tokens": r.tokens_in + r.tokens_out}}

    def records(self, tag: str) -> list[dict]:
        return [r for r in self.log if r["run"] == tag]
