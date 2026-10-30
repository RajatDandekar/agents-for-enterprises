"""OpenTelemetry traces in the GenAI semantic conventions, sent to Langfuse, for any agent stack.

    tp, log = provider(langfuse=True)            # spans go to Langfuse (OTLP over HTTP) and to `log` (plain JSON)
    tracer = tp.get_tracer("ask-northbridge")

One trace per mission. The shape is the same whichever framework runs the agent:

    mission M4 · Order and release from the right Voltway      the trace (Langfuse: name, session, user, tags, scores)
      invoke_agent Ask Northbridge                              one per message from the person (gen_ai.operation.name)
        chat gemini-3.8-flash                                   one per model call, written by the model gateway
        execute_tool create_purchase_order                      one per tool call, written by the MCP tool server

Why the gateway and the tool server write the spans, and not the framework: every stack's model traffic goes through
one gateway and every tool call arrives at one MCP server, so the trace is measured at the same two boundaries for
our harness, the OpenAI Agents SDK and LangGraph. (Each framework also has its own tracing; OpenInference and
Logfire ship instrumentors for them. Boundary spans are what you can compare like for like.)

Attribute names: the OpenTelemetry GenAI registry (gen_ai.*; status Development), plus the few Langfuse reads for
its trace view (langfuse.*). Names starting ledgerline. are ours. Keys come from the environment and are never printed.
"""
from __future__ import annotations

import base64
import json
import os
import threading
from typing import Any

from opentelemetry import context as otel_context
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.trace import SpanKind, Status, StatusCode

MAX_ATTR = 12000
USD_GBP = 0.79   # fixed for this segment: £ = OpenRouter's US dollars x 0.79


def j(x: Any, n: int = MAX_ATTR) -> str:
    s = x if isinstance(x, str) else json.dumps(x, default=str, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + " …(cut)"


class SpanLog(SpanExporter):
    """Keeps every finished span as a plain dict (the deck's waterfall is drawn from these)."""

    def __init__(self):
        self.spans: list[dict] = []
        self._lock = threading.Lock()

    def export(self, spans):
        with self._lock:
            for s in spans:
                self.spans.append(json.loads(s.to_json()))
        return SpanExportResult.SUCCESS

    def shutdown(self):
        pass

    def of_trace(self, trace_id: str) -> list[dict]:
        tid = trace_id if trace_id.startswith("0x") else "0x" + trace_id
        return [s for s in self.spans if s["context"]["trace_id"] == tid]


def langfuse_exporter():
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    base = (os.environ.get("LANGFUSE_BASE_URL") or os.environ.get("LANGFUSE_HOST") or "https://cloud.langfuse.com").rstrip("/")
    auth = base64.b64encode(f"{os.environ['LANGFUSE_PUBLIC_KEY']}:{os.environ['LANGFUSE_SECRET_KEY']}".encode()).decode()
    return OTLPSpanExporter(endpoint=f"{base}/api/public/otel/v1/traces", headers={"Authorization": f"Basic {auth}"})


def provider(langfuse: bool = True, service: str = "ask-northbridge", version: str = "l1-production"):
    tp = TracerProvider(resource=Resource.create({"service.name": service, "service.version": version,
                                                  "deployment.environment.name": os.environ.get("LEDGER_ENV", "course")}))
    log = SpanLog()
    tp.add_span_processor(SimpleSpanProcessor(log))
    if langfuse and os.environ.get("LANGFUSE_PUBLIC_KEY"):
        tp.add_span_processor(BatchSpanProcessor(langfuse_exporter(), max_export_batch_size=64))
    return tp, log


def hex_id(span) -> str:
    return format(span.get_span_context().trace_id, "032x")


# ----------------------------------------------------------------------------------------- the spans
def start_mission(tracer, mission, stack: str, model: str, run: int, session: str, public: bool = False):
    sp = tracer.start_span(f"mission {mission.id} · {mission.title}", kind=SpanKind.INTERNAL)
    for k, v in {"ledgerline.mission": mission.id, "ledgerline.stack": stack, "ledgerline.run": run,
                 "gen_ai.request.model": model, "gen_ai.conversation.id": session,
                 "langfuse.trace.name": f"{mission.id} {mission.title}", "session.id": session,
                 "user.id": mission.user, "langfuse.observation.type": "span",
                 "langfuse.trace.metadata.stack": stack, "langfuse.trace.metadata.model": model,
                 "langfuse.trace.metadata.run": run}.items():
        sp.set_attribute(k, v)
    sp.set_attribute("langfuse.trace.tags", [stack, model.split("/")[-1], f"run{run}", mission.id, "L1-production"])
    if public:
        sp.set_attribute("langfuse.trace.public", True)
    return sp


def end_mission(sp, opening: str, result: dict):
    last = result["replies"][-1] if result.get("replies") else (result.get("error") or "")
    for k, v in (("langfuse.trace.input", opening), ("langfuse.observation.input", opening),
                 ("langfuse.trace.output", last), ("langfuse.observation.output", last)):
        sp.set_attribute(k, j(v))
    sp.set_attribute("ledgerline.passed", bool(result["passed"]))
    sp.set_attribute("ledgerline.never_events", len(result["never_events"]))
    sp.set_attribute("langfuse.trace.metadata.passed", bool(result["passed"]))
    sp.set_attribute("langfuse.trace.metadata.never_events", j(result["never_events"], 600))
    sp.set_attribute("langfuse.trace.metadata.checks", j(result["checks"], 1000))
    if not result["passed"]:
        sp.set_status(Status(StatusCode.ERROR, "; ".join(result["never_events"][:2]) or "a check failed"))
        sp.set_attribute("langfuse.observation.level", "ERROR" if result["never_events"] else "WARNING")
        sp.set_attribute("langfuse.observation.status_message",
                         "; ".join(result["never_events"]) or "failed: " + ", ".join(k for k, v in result["checks"].items() if not v))
    sp.end()
    result["root_end_ns"] = sp.end_time


def start_turn(tracer, parent_span, turn: int, text: str, stack: str, model: str, session: str):
    ctx = trace.set_span_in_context(parent_span)
    sp = tracer.start_span("invoke_agent Ask Northbridge", context=ctx, kind=SpanKind.INTERNAL)
    for k, v in {"gen_ai.operation.name": "invoke_agent", "gen_ai.agent.name": "Ask Northbridge",
                 "gen_ai.provider.name": "openrouter", "gen_ai.request.model": model,
                 "gen_ai.conversation.id": session, "ledgerline.stack": stack, "ledgerline.turn": turn,
                 "langfuse.observation.type": "agent", "langfuse.observation.input": j(text),
                 "gen_ai.input.messages": j([{"role": "user", "parts": [{"type": "text", "content": text}]}])}.items():
        sp.set_attribute(k, v)
    return sp


def end_turn(sp, reply: str, error: str | None = None):
    sp.set_attribute("langfuse.observation.output", j(reply))
    sp.set_attribute("gen_ai.output.messages", j([{"role": "assistant", "parts": [{"type": "text", "content": reply}]}]))
    if error:
        sp.set_status(Status(StatusCode.ERROR, error[:200]))
        sp.set_attribute("error.type", error.split(":")[0][:60])
    sp.end()


def to_semconv(messages: list[dict]) -> list[dict]:
    """OpenAI-style chat messages -> the GenAI convention's shape: {role, parts: [...]}."""
    out = []
    for m in messages:
        parts = []
        if m.get("content"):
            parts.append({"type": "tool_call_response", "id": m.get("tool_call_id"), "response": m["content"]}
                         if m.get("role") == "tool" else {"type": "text", "content": m["content"]})
        for tc in m.get("tool_calls") or []:
            f = tc.get("function", {})
            parts.append({"type": "tool_call", "id": tc.get("id"), "name": f.get("name"), "arguments": f.get("arguments")})
        out.append({"role": m.get("role"), "parts": parts})
    return out


def chat_span(tracer, parent, model: str, messages, tools, settings: dict):
    """Opened by the gateway around one model call. Returns the span; call finish_chat when the reply is in."""
    ctx = trace.set_span_in_context(parent) if parent is not None else otel_context.get_current()
    short = model.split("/")[-1]
    sp = tracer.start_span(f"chat {short}", context=ctx, kind=SpanKind.CLIENT)
    for k, v in {"gen_ai.operation.name": "chat", "gen_ai.provider.name": "openrouter",
                 "gen_ai.request.model": model, "gen_ai.request.temperature": settings.get("temperature", 0.0),
                 "gen_ai.request.max_tokens": settings.get("max_tokens", 0), "server.address": "openrouter.ai",
                 "langfuse.observation.type": "generation", "langfuse.observation.model.name": model,
                 "gen_ai.input.messages": j(to_semconv(messages[-8:])),
                 "langfuse.observation.input": j(messages[-6:])}.items():
        sp.set_attribute(k, v)
    if tools:
        sp.set_attribute("gen_ai.tool.definitions", j([t.get("function", {}).get("name") for t in tools]))
    return sp


def finish_chat(sp, reply, cost_usd: float | None, provider_name: str | None, replayed: bool, error: str | None = None):
    if error:
        sp.set_status(Status(StatusCode.ERROR, error[:200]))
        sp.set_attribute("error.type", "model_error")
        sp.end()
        return
    msg = reply.message()
    sp.set_attribute("gen_ai.response.model", reply.model.split(":", 1)[-1])
    sp.set_attribute("gen_ai.usage.input_tokens", reply.tokens_in)
    sp.set_attribute("gen_ai.usage.output_tokens", reply.tokens_out)
    sp.set_attribute("gen_ai.response.finish_reasons", ["tool_calls" if reply.tool_calls else "stop"])
    sp.set_attribute("gen_ai.output.messages", j(to_semconv([msg])))
    sp.set_attribute("langfuse.observation.output", j(msg))
    sp.set_attribute("langfuse.observation.usage_details", json.dumps({"input": reply.tokens_in, "output": reply.tokens_out}))
    if cost_usd is not None:
        sp.set_attribute("langfuse.observation.cost_details", json.dumps({"total": round(float(cost_usd), 8)}))
        sp.set_attribute("ledgerline.cost_gbp", round(float(cost_usd) * USD_GBP, 6))
    if provider_name:
        sp.set_attribute("ledgerline.upstream_provider", str(provider_name))
    sp.set_attribute("ledgerline.replayed", bool(replayed))
    sp.set_attribute("ledgerline.model_seconds", reply.seconds)
    sp.end()


def tool_span(tracer, parent, name: str, args: dict):
    ctx = trace.set_span_in_context(parent) if parent is not None else otel_context.get_current()
    sp = tracer.start_span(f"execute_tool {name}", context=ctx, kind=SpanKind.INTERNAL)
    for k, v in {"gen_ai.operation.name": "execute_tool", "gen_ai.tool.name": name, "gen_ai.tool.type": "function",
                 "mcp.method.name": "tools/call", "langfuse.observation.type": "tool",
                 "gen_ai.tool.call.arguments": j(args), "langfuse.observation.input": j(args)}.items():
        sp.set_attribute(k, v)
    return sp


def finish_tool(sp, out: dict):
    ok = bool(out.get("ok"))
    sp.set_attribute("ledgerline.ok", ok)
    for k in ("request_no", "po_no", "grn_no", "status", "status_code"):
        if isinstance(out.get(k), (str, int)):
            sp.set_attribute(f"ledgerline.receipt.{k}", out[k])
    sp.set_attribute("gen_ai.tool.call.result", j(out))
    sp.set_attribute("langfuse.observation.output", j(out))
    if not ok:
        sp.set_status(Status(StatusCode.ERROR, str(out.get("error") or "")[:200]))
        sp.set_attribute("error.type", "tool_error")
        sp.set_attribute("langfuse.observation.level", "WARNING")
    sp.end()


# ----------------------------------------------------------------------------------------- the deck's waterfall
KIND = {"invoke_agent": "agent", "chat": "chat", "execute_tool": "tool"}


def waterfall(spans: list[dict]) -> list[dict]:
    """One trace's spans -> rows for a waterfall: depth, label, start and duration in ms from the trace start."""
    import datetime as dt

    def t(s):
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() * 1000

    if not spans:
        return []
    t0 = min(t(s["start_time"]) for s in spans)
    kids: dict = {}
    for s in spans:
        kids.setdefault(s.get("parent_id"), []).append(s)
    for v in kids.values():
        v.sort(key=lambda s: s["start_time"])
    ids = {s["context"]["span_id"] for s in spans}
    rows = []

    def walk(pid, d):
        for s in kids.get(pid, []):
            a = s.get("attributes", {})
            op = a.get("gen_ai.operation.name", "mission")
            row = {"name": s["name"], "kind": KIND.get(op, "mission"), "depth": d,
                   "start_ms": round(t(s["start_time"]) - t0), "ms": round(t(s["end_time"]) - t(s["start_time"])),
                   "ok": s.get("status", {}).get("status_code") != "ERROR"}
            if op == "chat":
                row.update(tokens_in=a.get("gen_ai.usage.input_tokens"), tokens_out=a.get("gen_ai.usage.output_tokens"),
                           cost_gbp=a.get("ledgerline.cost_gbp"),
                           calls=[p.get("name") for m in json.loads(a.get("gen_ai.output.messages", "[]"))
                                  for p in m.get("parts", []) if p.get("type") == "tool_call"])
            if op == "execute_tool":
                row.update(tool=a.get("gen_ai.tool.name"), args=a.get("gen_ai.tool.call.arguments", "")[:160],
                           status=a.get("ledgerline.receipt.status"))
            if op == "invoke_agent":
                row.update(turn=a.get("ledgerline.turn"), said=a.get("langfuse.observation.input", "")[:200],
                           reply=a.get("langfuse.observation.output", "")[:300])
            rows.append(row)
            walk(s["context"]["span_id"], d + 1)

    roots = [s for s in spans if s.get("parent_id") not in ids]
    for r in roots:
        kids.setdefault("__root__", []).append(r)
    walk("__root__", 0)
    return rows


def waterfall_svg(rows: list[dict], width: int = 1200, row_h: int = 22) -> str:
    """A plain SVG of the waterfall, coloured with CSS variables the deck can theme (--wf-agent, --wf-chat, --wf-tool)."""
    if not rows:
        return ""
    total = max(r["start_ms"] + r["ms"] for r in rows) or 1
    label_w, pad = 360, 8
    plot = width - label_w - pad * 2
    h = row_h * len(rows) + 30
    fill = {"mission": "var(--wf-mission, #9aa3af)", "agent": "var(--wf-agent, #6b7cff)",
            "chat": "var(--wf-chat, #f59e0b)", "tool": "var(--wf-tool, #10b981)"}
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {h}" font-family="system-ui, sans-serif" font-size="12">']
    for i, r in enumerate(rows):
        y = i * row_h + 4
        x = label_w + pad + r["start_ms"] / total * plot
        w = max(2.0, r["ms"] / total * plot)
        lab = r["name"].replace("&", "&amp;").replace("<", "&lt;")
        col = fill[r["kind"]] if r["ok"] else "var(--wf-error, #ef4444)"
        out.append(f'<text x="{4 + r["depth"] * 14}" y="{y + 14}" fill="var(--wf-text, #1f2937)">{lab}</text>')
        out.append(f'<rect x="{x:.1f}" y="{y + 3}" width="{w:.1f}" height="{row_h - 8}" rx="3" fill="{col}"/>')
        out.append(f'<text x="{min(x + w + 4, width - 60):.1f}" y="{y + 14}" fill="var(--wf-muted, #6b7280)">'
                   f'{r["ms"] / 1000:.1f} s</text>')
    out.append(f'<text x="{label_w + pad}" y="{h - 6}" fill="var(--wf-muted, #6b7280)">0 s</text>')
    out.append(f'<text x="{width - pad}" y="{h - 6}" text-anchor="end" fill="var(--wf-muted, #6b7280)">{total / 1000:.1f} s</text>')
    out.append("</svg>")
    return "".join(out)
