"""OpenTelemetry for Ask Northbridge, written by hand, following the GenAI semantic conventions (status: Development).

    from ledgerline.course.obs.otel import provider, instrument, SpanLog
    log = SpanLog()                                   # keeps every finished span as plain JSON (for plates, notebooks)
    tp = provider(log, langfuse=True, phoenix=False)   # the same spans can go to several back ends at once
    agent = AskNorthbridge(erp, "ECLARKE", llm=..., trust=True)
    instrument(agent, tp.get_tracer("ask-northbridge"), conversation_id="conv-s2", user="ECLARKE")
    agent.respond("Reorder 20,000 ...")                # one trace per user turn:
        invoke_agent Ask Northbridge                         #   the turn (gen_ai.operation.name = invoke_agent)
          chat gemini-3.8-flash                        #   each model call (operation chat)
          execute_tool create_purchase_request         #   each tool call (operation execute_tool)
            tools/call create_purchase_request         #     the MCP request the toolbox server answered
    tp.force_flush()

Why by hand: the course's LLM shim (ledgerline.llm) is our own code, so no auto-instrumentation library knows it. Writing
the twenty lines teaches what those libraries do: open a span, put standard attributes on it, close it.

Attribute names are the ones in the OpenTelemetry GenAI registry (docs/registry/attributes/gen-ai.md in
open-telemetry/semantic-conventions-genai, checked 2026-10-28). Names starting with ledgerline. are ours.
Langfuse reads the standard names (model, usage) plus a few of its own (langfuse.*), set here too where they help.
"""
from __future__ import annotations

import base64
import json
import os
import time
from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.trace import SpanKind, Status, StatusCode

PROVIDER_NAMES = {"gemini": "gcp.gemini", "openrouter": "openrouter", "openai": "openai", "anthropic": "anthropic"}
MAX_ATTR = 12000  # characters kept of one content attribute (messages, tool results)


def _j(x: Any, n: int = MAX_ATTR) -> str:
    s = x if isinstance(x, str) else json.dumps(x, default=str, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + " …(cut)"


OI = True  # also write OpenInference attribute names (Arize Phoenix's own convention) on every span


def _oi(sp, kind: str, **kv):
    """OpenInference names: openinference.span.kind, input.value, output.value, llm.model_name, llm.token_count.*"""
    if not OI:
        return
    sp.set_attribute("openinference.span.kind", kind)
    for k, v in kv.items():
        if v is not None:
            sp.set_attribute(k, v)


def to_semconv_messages(messages: list[dict]) -> list[dict]:
    """OpenAI-style chat messages -> the GenAI convention's shape: {role, parts: [{type, content | name, arguments}]}."""
    out = []
    for m in messages:
        parts = []
        if m.get("content"):
            if m["role"] == "tool":
                parts.append({"type": "tool_call_response", "id": m.get("tool_call_id"), "response": m["content"]})
            else:
                parts.append({"type": "text", "content": m["content"]})
        for tc in m.get("tool_calls") or []:
            f = tc.get("function", {})
            args = f.get("arguments")
            try:
                args = json.loads(args) if isinstance(args, str) else args
            except Exception:  # noqa: BLE001
                pass
            parts.append({"type": "tool_call", "id": tc.get("id"), "name": f.get("name"), "arguments": args})
        out.append({"role": m["role"], "parts": parts})
    return out


# ------------------------------------------------------------------------------------------------ exporters
class SpanLog(SpanExporter):
    """An exporter that keeps every finished span as a plain dict, in the order they ended."""

    def __init__(self):
        self.spans: list[dict] = []

    def export(self, spans):
        for s in spans:
            self.spans.append(json.loads(s.to_json()))
        return SpanExportResult.SUCCESS

    def shutdown(self):
        pass

    def tree(self, trace_id: str | None = None) -> list[dict]:
        """Spans of one trace (default: the last one), parents before children, each with a depth."""
        ss = [s for s in self.spans if trace_id is None or s["context"]["trace_id"] == trace_id]
        if trace_id is None and ss:
            tid = ss[-1]["context"]["trace_id"]
            ss = [s for s in ss if s["context"]["trace_id"] == tid]
        kids: dict = {}
        for s in ss:
            kids.setdefault(s.get("parent_id"), []).append(s)
        for v in kids.values():
            v.sort(key=lambda s: s["start_time"])
        out = []

        def walk(pid, d):
            for s in kids.get(pid, []):
                out.append({**s, "depth": d})
                walk(s["context"]["span_id"], d + 1)
        walk(None, 0)
        return out


def langfuse_exporter():
    """OTLP over HTTP to Langfuse's OpenTelemetry endpoint. Keys come from the environment and are never printed."""
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    base = (os.environ.get("LANGFUSE_BASE_URL") or os.environ.get("LANGFUSE_HOST") or "https://cloud.langfuse.com").rstrip("/")
    auth = base64.b64encode(f"{os.environ['LANGFUSE_PUBLIC_KEY']}:{os.environ['LANGFUSE_SECRET_KEY']}".encode()).decode()
    return OTLPSpanExporter(endpoint=f"{base}/api/public/otel/v1/traces", headers={"Authorization": f"Basic {auth}"})


def phoenix_exporter(url: str = "http://127.0.0.1:6006/v1/traces"):
    """OTLP over HTTP to a Phoenix server running on this machine (phoenix serve). No key."""
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    return OTLPSpanExporter(endpoint=url)


def provider(*exporters, langfuse: bool = False, phoenix: bool | str = False, service: str = "ask-northbridge",
             version: str = "l10") -> TracerProvider:
    """A TracerProvider whose spans go to every exporter given. Not installed globally: pass its tracer around."""
    tp = TracerProvider(resource=Resource.create({"service.name": service, "service.version": version,
                                                  "openinference.project.name": service,
                                                  "deployment.environment.name": os.environ.get("LEDGER_ENV", "course")}))
    exps = list(exporters)
    if langfuse:
        exps.append(langfuse_exporter())
    if phoenix:
        exps.append(phoenix_exporter(phoenix if isinstance(phoenix, str) else "http://127.0.0.1:6006/v1/traces"))
    for e in exps:
        tp.add_span_processor(SimpleSpanProcessor(e))
    return tp


# ------------------------------------------------------------------------------------------------ wrappers
class TracedLLM:
    """Wraps ledgerline.llm.LLM: every chat() becomes a span named 'chat <model>'."""

    def __init__(self, llm, tracer, content: bool = True):
        self._llm, self._tracer, self._content = llm, tracer, content
        self.last_calls: list = []
        self.prompt: tuple | None = None  # (name, version) when the system prompt came from Langfuse

    def __getattr__(self, k):  # .log, .totals(), .model ... come from the real LLM
        return getattr(self._llm, k)

    def chat(self, messages, tools=None, **kw):
        llm = self._llm
        with self._tracer.start_as_current_span(f"chat {llm.model_id}", kind=SpanKind.CLIENT) as sp:
            sp.set_attribute("gen_ai.operation.name", "chat")
            sp.set_attribute("gen_ai.provider.name", PROVIDER_NAMES.get(llm.provider, llm.provider))
            sp.set_attribute("gen_ai.request.model", llm.model_id)
            sp.set_attribute("gen_ai.request.temperature", llm.temperature)
            sp.set_attribute("gen_ai.request.max_tokens", llm.max_tokens)
            sp.set_attribute("langfuse.observation.type", "generation")
            sp.set_attribute("langfuse.observation.model.name", llm.model_id)
            if self.prompt:  # a prompt fetched from Langfuse prompt management: link the generation to its version
                sp.set_attribute("langfuse.observation.prompt.name", self.prompt[0])
                sp.set_attribute("langfuse.observation.prompt.version", self.prompt[1])
            if self._content:
                sp.set_attribute("gen_ai.input.messages", _j(to_semconv_messages(messages)))
                sp.set_attribute("langfuse.observation.input", _j(messages[-6:]))  # what Langfuse's UI shows
                if tools:
                    sp.set_attribute("gen_ai.tool.definitions", _j([t["function"]["name"] for t in tools]))
            try:
                r = llm.chat(messages, tools=tools, **kw)
            except Exception as e:
                sp.set_status(Status(StatusCode.ERROR, str(e)[:200]))
                sp.set_attribute("error.type", type(e).__name__)
                raise
            served = r.model.split(":", 1)[-1]
            sp.set_attribute("gen_ai.response.model", served)
            sp.set_attribute("gen_ai.usage.input_tokens", r.tokens_in)
            sp.set_attribute("gen_ai.usage.output_tokens", r.tokens_out)
            sp.set_attribute("gen_ai.response.finish_reasons", ["tool_calls" if r.tool_calls else "stop"])
            sp.set_attribute("ledgerline.cost_inr", r.cost_inr)
            sp.set_attribute("langfuse.observation.usage_details", json.dumps({"input": r.tokens_in, "output": r.tokens_out}))
            sp.set_attribute("langfuse.observation.cost_details", json.dumps({"total": round(r.cost_inr / 88.0, 6)}))  # USD
            sp.set_attribute("ledgerline.model_seconds", r.seconds)
            sp.set_attribute("ledgerline.replayed", bool(r.replayed))
            if self._content:
                sp.set_attribute("gen_ai.output.messages", _j(to_semconv_messages([r.message()])))
                sp.set_attribute("langfuse.observation.output", _j(r.message()))
            _oi(sp, "LLM", **{"llm.model_name": served, "llm.provider": llm.provider,
                              "llm.token_count.prompt": r.tokens_in, "llm.token_count.completion": r.tokens_out,
                              "llm.token_count.total": r.tokens_in + r.tokens_out,
                              "input.value": _j(messages[-1].get("content") or "") if self._content else None,
                              "output.value": _j(r.content or [t.name for t in r.tool_calls]) if self._content else None})
            self.last_calls = list(r.tool_calls)
            return r


class TracedTools:
    """Wraps a tool set (Toolbox, MCPClientTools or the L7 TrustLayer): every call() becomes 'execute_tool <name>'."""

    def __init__(self, tools, tracer, llm: TracedLLM | None = None, trust=None, content: bool = True):
        self._tools, self._tracer, self._llm, self._trust, self._content = tools, tracer, llm, trust, content

    def __getattr__(self, k):
        return getattr(self._tools, k)

    def schemas(self):
        return self._tools.schemas()

    def call(self, name, args):
        call_id = None
        if self._llm is not None:  # match the model's tool call, to carry its id
            for tc in self._llm.last_calls:
                if tc.name == name and tc.arguments == args:
                    call_id = tc.id
                    break
        with self._tracer.start_as_current_span(f"execute_tool {name}", kind=SpanKind.INTERNAL) as sp:
            sp.set_attribute("gen_ai.operation.name", "execute_tool")
            sp.set_attribute("gen_ai.tool.name", name)
            sp.set_attribute("gen_ai.tool.type", "function")
            sp.set_attribute("langfuse.observation.type", "tool")
            if call_id:
                sp.set_attribute("gen_ai.tool.call.id", call_id)
            if self._content:
                sp.set_attribute("gen_ai.tool.call.arguments", _j(args))
                sp.set_attribute("langfuse.observation.input", _j(args))
            n_ev = len(self._trust.events) if self._trust is not None else 0
            out = self._tools.call(name, args)
            d = out if isinstance(out, dict) else _as_dict(out)
            ok = d.get("ok")
            sp.set_attribute("ledgerline.ok", bool(ok))
            for k in ("request_no", "po_no", "status", "status_code"):
                if isinstance(d.get(k), (str, int)):
                    sp.set_attribute(f"ledgerline.receipt.{k}", d[k])
            if self._trust is not None:
                for ev in self._trust.events[n_ev:]:
                    sp.add_event(f"trust.{ev['decision'].replace(' ', '_')}",
                                 {k: (v if isinstance(v, (str, int, float, bool)) else _j(v, 500))
                                  for k, v in ev.items() if v is not None})
            if d.get("refused_by"):
                sp.set_attribute("ledgerline.refused_by", d["refused_by"])
                sp.set_attribute("ledgerline.rule", d.get("rule") or "")
            if ok is False:
                sp.set_status(Status(StatusCode.ERROR, (d.get("error") or "")[:200]))
                sp.set_attribute("error.type", "tool_refused" if d.get("refused_by") else "tool_error")
            if self._content:
                sp.set_attribute("gen_ai.tool.call.result", _j(d))
                sp.set_attribute("langfuse.observation.output", _j(d))
            _oi(sp, "TOOL", **{"tool.name": name, "input.value": _j(args) if self._content else None,
                               "output.value": _j(d) if self._content else None})
            return out


class TracedMCP:
    """Wraps MCPClientTools: the JSON-RPC request 'tools/call' to the toolbox server, as a client span."""

    def __init__(self, tools, tracer):
        self._tools, self._tracer = tools, tracer

    def __getattr__(self, k):
        return getattr(self._tools, k)

    def schemas(self):
        return self._tools.schemas()

    def call(self, name, args):
        with self._tracer.start_as_current_span(f"tools/call {name}", kind=SpanKind.CLIENT) as sp:
            sp.set_attribute("mcp.method.name", "tools/call")
            sp.set_attribute("rpc.system", "jsonrpc")
            sp.set_attribute("gen_ai.tool.name", name)
            sp.set_attribute("server.address", "northbridge-toolbox (in-process)")
            return self._tools.call(name, args)


def _as_dict(out):
    try:
        d = json.loads(out)
        return d if isinstance(d, dict) else {"value": d}
    except Exception:  # noqa: BLE001
        return {"text": str(out)}


def instrument(agent, tracer, conversation_id: str, user: str | None = None, tags: tuple = (), content: bool = True,
               public: bool = False, metadata: dict | None = None, prompt: tuple | None = None):
    """Trace an AskNorthbridge (ledgerline.course.l7) in place. Each respond() is one trace; the conversation id ties them."""
    tl = TracedLLM(agent.llm, tracer, content)
    tl.prompt = prompt
    agent.llm = tl
    trust = getattr(agent, "trust", None)
    if trust is not None:
        trust.tools = TracedMCP(trust.tools, tracer)
        agent.tools = TracedTools(trust, tracer, tl, trust, content)
    else:
        inner = TracedMCP(agent.tools, tracer) if type(agent.tools).__name__ == "MCPClientTools" else agent.tools
        agent.tools = TracedTools(inner, tracer, tl, None, content)
    plain = agent.respond
    who = user or getattr(agent, "user", None)

    def respond(text):
        with tracer.start_as_current_span("invoke_agent Ask Northbridge", kind=SpanKind.INTERNAL) as sp:
            sp.set_attribute("gen_ai.operation.name", "invoke_agent")
            sp.set_attribute("gen_ai.agent.name", "Ask Northbridge")
            sp.set_attribute("gen_ai.conversation.id", conversation_id)
            sp.set_attribute("gen_ai.provider.name", PROVIDER_NAMES.get(tl._llm.provider, tl._llm.provider))
            sp.set_attribute("gen_ai.request.model", tl._llm.model_id)
            sp.set_attribute("ledgerline.turn", getattr(agent, "turn", 0) + 1)
            sp.set_attribute("ledgerline.trust_layer", trust is not None)
            # trace-level fields as Langfuse reads them: session.id and user.id are OpenTelemetry's own names
            sp.set_attribute("langfuse.observation.type", "agent")
            sp.set_attribute("langfuse.trace.name", "Ask Northbridge")
            sp.set_attribute("session.id", conversation_id)
            if who:
                sp.set_attribute("user.id", who)
            if tags:
                sp.set_attribute("langfuse.trace.tags", list(tags))
            if public:
                sp.set_attribute("langfuse.trace.public", True)
            for k, v in (metadata or {}).items():
                sp.set_attribute(f"langfuse.trace.metadata.{k}", v if isinstance(v, (str, int, float, bool)) else _j(v, 500))
            sp.set_attribute("langfuse.trace.input", _j(text))
            sp.set_attribute("langfuse.observation.input", _j(text))
            sp.set_attribute("gen_ai.input.messages", _j([{"role": "user", "parts": [{"type": "text", "content": text}]}]))
            t0 = time.perf_counter()
            reply = plain(text)
            sp.set_attribute("langfuse.trace.output", _j(reply))
            sp.set_attribute("langfuse.observation.output", _j(reply))
            sp.set_attribute("gen_ai.output.messages", _j([{"role": "assistant", "parts": [{"type": "text", "content": reply}]}]))
            sp.set_attribute("ledgerline.turn_seconds", round(time.perf_counter() - t0, 3))
            _oi(sp, "AGENT", **{"input.value": text, "output.value": reply, "session.id": conversation_id})
            agent.last_trace_id = format(sp.get_span_context().trace_id, "032x")
            agent.trace_ids = getattr(agent, "trace_ids", []) + [agent.last_trace_id]
            return reply

    agent.respond = respond
    return agent
