"""OpenTelemetry for Ask Northbridge (Lecture 6): every turn a trace, GenAI semantic conventions, to any back end.

    tr = Tracing.from_env(public=True)          # every back end whose key is in the environment, none if there is none
    a = Agent("thursday", tracing=tr)
    a.turn("Order the usual, please.")     # one trace:
        invoke_agent Ask Northbridge             #   the turn            gen_ai.operation.name = invoke_agent
          chat claude-sonnet-5-5                 #   each model call     gen_ai.operation.name = chat
          execute_tool create_purchase_request   #   each tool call      gen_ai.operation.name = execute_tool
    tr.flush(); tr.log.tree()                    # the spans as plain JSON, parents before children
    tr.links(trace_id)                           # {"langfuse": url, "langsmith": url, "sentry": url} for what is configured

Back ends (each switches on when its key is present, and is skipped silently when it is not):
    Langfuse   LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST         OTLP  {host}/api/public/otel/v1/traces
    LangSmith  LANGSMITH_API_KEY, LANGSMITH_ENDPOINT (default US), LANGSMITH_PROJECT   OTLP  {endpoint}/otel/v1/traces
    Sentry     SENTRY_DSN (SENTRY_ORG for links)                               OTLP  https://{dsn host}/api/{project}/integration/otlp/v1/traces

One span, read by all three. The attribute names follow each tool's OTLP mapping docs (read 16 Nov 2026):
    input / output   langfuse.observation.input|output (Langfuse, JSON strings; in Langfuse v4 the trace's input is the
                     ROOT observation's input), input.value|output.value (LangSmith and Langfuse both read these),
                     gen_ai.input.messages|gen_ai.output.messages and gen_ai.tool.call.arguments|result (Sentry, GenAI names)
    kind             langfuse.observation.type (agent|generation|tool), langsmith.span.kind (chain|llm|tool),
                     sentry.op (gen_ai.invoke_agent|gen_ai.chat|gen_ai.execute_tool), gen_ai.operation.name
    who / which chat session.id, user.id (Langfuse; on every span, as v4 asks), langsmith.metadata.thread_id|user_id,
                     gen_ai.conversation.id (Sentry)
    tokens           gen_ai.usage.input_tokens|output_tokens|total_tokens (all three)
Content (messages, tool arguments, results) is opt-in in the conventions; here content=True, and redact (a function on
text, e.g. Presidio) is applied to every content attribute before it leaves the process. ledgerline.* names are ours.
"""
from __future__ import annotations

import base64
import contextlib
import json
import os
import time

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
from opentelemetry.trace import SpanKind, Status, StatusCode

from ..obs.otel import PROVIDER_NAMES, SpanLog, to_semconv_messages

MAX_ATTR = 12000
LF_PROJECT = os.environ.get("LANGFUSE_PROJECT_ID", "")


def _j(x, n: int = MAX_ATTR) -> str:
    s = x if isinstance(x, str) else json.dumps(x, default=str, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + " …(cut)"


def _otlp(endpoint: str, headers: dict):
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    return OTLPSpanExporter(endpoint=endpoint, headers=headers)


def langfuse_exporter():
    """OTLP over HTTP to Langfuse's OpenTelemetry endpoint. Keys from the environment, never printed."""
    base = (os.environ.get("LANGFUSE_BASE_URL") or os.environ.get("LANGFUSE_HOST") or "https://cloud.langfuse.com").rstrip("/")
    auth = base64.b64encode(f"{os.environ['LANGFUSE_PUBLIC_KEY']}:{os.environ['LANGFUSE_SECRET_KEY']}".encode()).decode()
    return _otlp(f"{base}/api/public/otel/v1/traces", {"Authorization": f"Basic {auth}", "x-langfuse-ingestion-version": "4"})


def langsmith_exporter():
    """OTLP to LangSmith: the API base (LANGSMITH_ENDPOINT, default the US one) + /otel/v1/traces; the key in x-api-key;
    the project in Langsmith-Project (docs.langchain.com/langsmith/trace-with-opentelemetry)."""
    base = (os.environ.get("LANGSMITH_ENDPOINT") or "https://api.smith.langchain.com").rstrip("/")
    return _otlp(f"{base}/otel/v1/traces", {"x-api-key": os.environ["LANGSMITH_API_KEY"],
                                             "Langsmith-Project": os.environ.get("LANGSMITH_PROJECT", "ask-northbridge")})


def sentry_otlp(dsn: str) -> tuple[str, dict]:
    """A Sentry DSN  https://<public key>@o<org id>.ingest.<region>.sentry.io/<project id>  ->  its OTLP traces endpoint
    and auth header (docs.sentry.io/concepts/otlp/direct/traces)."""
    from urllib.parse import urlparse
    u = urlparse(dsn)
    return (f"https://{u.hostname}/api/{u.path.strip('/')}/integration/otlp/v1/traces",
            {"x-sentry-auth": f"sentry sentry_key={u.username}"})


def sentry_exporter():
    return _otlp(*sentry_otlp(os.environ["SENTRY_DSN"]))


BACKENDS = {"langfuse": (("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"), langfuse_exporter),
            "langsmith": (("LANGSMITH_API_KEY",), langsmith_exporter),
            "sentry": (("SENTRY_DSN",), sentry_exporter)}


def configured() -> list[str]:
    """The back ends whose keys are in the environment."""
    return [n for n, (keys, _) in BACKENDS.items() if all(os.environ.get(k) for k in keys)]


def langfuse_project_id() -> str:
    """The project the keys belong to (GET /api/public/projects), for trace links."""
    global LF_PROJECT
    if LF_PROJECT:
        return LF_PROJECT
    import httpx
    base = (os.environ.get("LANGFUSE_BASE_URL") or os.environ.get("LANGFUSE_HOST") or "").rstrip("/")
    r = httpx.get(f"{base}/api/public/projects", auth=(os.environ["LANGFUSE_PUBLIC_KEY"], os.environ["LANGFUSE_SECRET_KEY"]),
                  timeout=20)
    r.raise_for_status()
    LF_PROJECT = r.json()["data"][0]["id"]
    return LF_PROJECT


def trace_url(trace_id: str) -> str:
    base = (os.environ.get("LANGFUSE_BASE_URL") or os.environ.get("LANGFUSE_HOST") or "").rstrip("/")
    return f"{base}/project/{langfuse_project_id()}/traces/{trace_id}"


_LS_PROJECT_URL: list = []
_ROOT_SPAN: dict = {}      # trace id -> the root span's id (hex), kept as each turn starts: LangSmith names a trace by its root run


def langsmith_run_id(span_id: str) -> str:
    """The run id LangSmith gives a span that arrived by OTLP: 00000000-0000-0000-<the 16 hex digits of the span id>.
    (Measured on our own traces, 16 Nov 2026; the OpenTelemetry ids are also kept in the run's metadata as OTEL_TRACE_ID
    and OTEL_SPAN_ID. A trace's id in LangSmith is its root run's id.)"""
    return f"00000000-0000-0000-{span_id[:4]}-{span_id[4:]}"


def langsmith_url(trace_id: str = "") -> str:
    """This trace in LangSmith when we saw its root span start in this process (…/trace/<root run>/run/<root run>, the form
    LangSmith's own API returns), else the project's page (newest traces first). The tenant and project ids come from its
    API once, with the key (never printed)."""
    if not _LS_PROJECT_URL:
        url = "https://smith.langchain.com"
        try:
            import httpx
            base = (os.environ.get("LANGSMITH_ENDPOINT") or "https://api.smith.langchain.com").rstrip("/")
            r = httpx.get(f"{base}/api/v1/sessions", params={"name": os.environ.get("LANGSMITH_PROJECT", "ask-northbridge")},
                          headers={"x-api-key": os.environ["LANGSMITH_API_KEY"]}, timeout=15)
            d = (r.json() or [None])[0] if r.status_code < 300 else None
            if d and d.get("tenant_id") and d.get("id"):
                url = f"https://smith.langchain.com/o/{d['tenant_id']}/projects/p/{d['id']}"
        except Exception:  # noqa: BLE001  the link is a convenience
            pass
        _LS_PROJECT_URL.append(url)
    root = _ROOT_SPAN.get(trace_id)
    if root and "/projects/p/" in _LS_PROJECT_URL[0]:
        rid = langsmith_run_id(root)
        return f"{_LS_PROJECT_URL[0]}/trace/{rid}/run/{rid}"
    return _LS_PROJECT_URL[0]


def sentry_url(trace_id: str) -> str | None:
    """Sentry's trace explorer for the organisation (SENTRY_ORG, the slug), filtered to this trace."""
    org = os.environ.get("SENTRY_ORG")
    return f"https://sentry.io/orgredirect/organizations/{org}/explore/traces/?query=trace%3A{trace_id}" if org else None


def links(trace_id: str) -> dict:
    """Where to open this trace, for every configured back end."""
    out = {}
    if not trace_id:
        return out
    on = configured()
    if "langfuse" in on:
        try:
            out["langfuse"] = trace_url(trace_id)
        except Exception:  # noqa: BLE001
            pass
    if "langsmith" in on:
        out["langsmith"] = langsmith_url(trace_id)
    if "sentry" in on and sentry_url(trace_id):
        out["sentry"] = sentry_url(trace_id)
    return out


class Tracing:
    def __init__(self, langfuse: bool = False, langsmith: bool = False, sentry: bool = False, phoenix: str | None = None,
                 public: bool = False, content: bool = True, redact=None, service: str = "ask-northbridge",
                 version: str = "l6", batch: bool = True, exporters=(), provider=None, log=None):
        self.log = log or SpanLog()
        self.public, self.content, self.redact = public, content, redact
        self.backends: list[str] = []
        if provider is not None:   # share one provider (and its exporters) across many conversations, e.g. in Argus
            self.tp = provider
            self.tracer = provider.get_tracer("ledgerline.course.l6")
            self.last_trace_id = None
            return
        self.tp = TracerProvider(resource=Resource.create({
            "service.name": service, "service.version": version, "openinference.project.name": service,
            "deployment.environment.name": os.environ.get("LEDGER_ENV", "course")}))
        self.tp.add_span_processor(SimpleSpanProcessor(self.log))
        Proc = BatchSpanProcessor if batch else SimpleSpanProcessor
        for name, want in (("langfuse", langfuse), ("langsmith", langsmith), ("sentry", sentry)):
            if want and name in configured():      # asked for AND its key is there; otherwise skipped silently
                self.tp.add_span_processor(Proc(BACKENDS[name][1]()))
                self.backends.append(name)
        if phoenix:
            self.tp.add_span_processor(Proc(_otlp(phoenix, {})))
        for e in exporters:
            self.tp.add_span_processor(Proc(e))
        self.tracer = self.tp.get_tracer("ledgerline.course.l6")
        self.last_trace_id: str | None = None

    @classmethod
    def from_env(cls, **kw):
        """Every back end whose key is in the environment (Langfuse, LangSmith, Sentry); none of them is required."""
        return cls(langfuse=True, langsmith=True, sentry=True, **kw)

    @staticmethod
    def links(trace_id: str) -> dict:
        return links(trace_id)

    def flush(self):
        self.tp.force_flush()

    def _c(self, x, n: int = MAX_ATTR) -> str:
        s = _j(x, n)
        return self.redact(s) if self.redact else s

    # ------------------------------------------------------------------ the turn
    @contextlib.contextmanager
    def agent_span(self, agent, text: str):
        with self.tracer.start_as_current_span("invoke_agent Ask Northbridge", kind=SpanKind.INTERNAL) as sp:
            sp.set_attribute("gen_ai.operation.name", "invoke_agent")
            sp.set_attribute("gen_ai.agent.name", "Ask Northbridge")
            sp.set_attribute("gen_ai.provider.name", PROVIDER_NAMES.get(agent.model.split(":")[0], "anthropic"))
            sp.set_attribute("gen_ai.request.model", agent.model.split(":", 1)[-1])
            sp.set_attribute("gen_ai.conversation.id", agent.conversation_id)
            sp.set_attribute("ledgerline.turn", len(agent.turns) + 1)
            sp.set_attribute("ledgerline.prompt", agent.prompt_name)
            sp.set_attribute("ledgerline.session_user", agent.session_user)
            sp.set_attribute("ledgerline.guards", ",".join(sorted(agent.guards.on)) if agent.guards else "")
            sp.set_attribute("langfuse.observation.type", "agent")
            sp.set_attribute("langsmith.span.kind", "chain")
            sp.set_attribute("sentry.op", "gen_ai.invoke_agent")
            sp.set_attribute("langfuse.trace.name", "Ask Northbridge")
            tags = list(agent.tags) + [f"prompt:{agent.prompt_name}"]
            self._who = {"session.id": agent.conversation_id, "user.id": agent.user_label,
                         "langsmith.metadata.thread_id": agent.conversation_id, "langsmith.metadata.user_id": agent.user_label,
                         "gen_ai.conversation.id": agent.conversation_id, "gen_ai.agent.name": "Ask Northbridge"}
            for k, v in self._who.items():           # who and which chat: on the root, and repeated on every child span
                sp.set_attribute(k, v)
            sp.set_attribute("langfuse.trace.tags", tags)
            sp.set_attribute("langsmith.span.tags", ",".join(tags))
            sp.set_attribute("langfuse.trace.metadata.prompt", agent.prompt_name)
            sp.set_attribute("langsmith.metadata.prompt", agent.prompt_name)
            sp.set_attribute("langfuse.trace.metadata.guards", ",".join(sorted(agent.guards.on)) if agent.guards else "none")
            if self.public:
                sp.set_attribute("langfuse.trace.public", True)
            # the turn's input: Emma's message, under each back end's name for it
            sp.set_attribute("langfuse.observation.input", json.dumps(self._c(text), ensure_ascii=False))
            sp.set_attribute("input.value", self._c(text))
            sp.set_attribute("gen_ai.input.messages", json.dumps([{"role": "user", "parts": [{"type": "text", "content": self._c(text)}]}],
                                                                 ensure_ascii=False))
            sp.set_attribute("openinference.span.kind", "AGENT")
            self.last_trace_id = format(sp.get_span_context().trace_id, "032x")
            _ROOT_SPAN[self.last_trace_id] = format(sp.get_span_context().span_id, "016x")
            if len(_ROOT_SPAN) > 5000:
                _ROOT_SPAN.pop(next(iter(_ROOT_SPAN)))
            yield sp

    def end_agent(self, sp, rec: dict):
        reply = rec.get("reply") or ""
        sp.set_attribute("langfuse.observation.output", json.dumps(self._c(reply), ensure_ascii=False))
        sp.set_attribute("output.value", self._c(reply))
        sp.set_attribute("gen_ai.output.messages", json.dumps([{"role": "assistant", "parts": [{"type": "text", "content": self._c(reply)}]}],
                                                              ensure_ascii=False))
        sp.set_attribute("gen_ai.usage.total_tokens", rec["tokens_in"] + rec["tokens_out"])
        sp.set_attribute("gen_ai.usage.input_tokens", rec["tokens_in"])
        sp.set_attribute("gen_ai.usage.output_tokens", rec["tokens_out"])
        sp.set_attribute("ledgerline.cost_usd", rec["usd"])
        sp.set_attribute("ledgerline.tool_calls", len(rec["calls"]))
        rec["trace_id"] = format(sp.get_span_context().trace_id, "032x")

    # ------------------------------------------------------------------ model calls
    def wrap_llm(self, llm):
        return _TracedLLM(llm, self)

    # ------------------------------------------------------------------ tool calls
    def tool_span(self, tc, args: dict, run, rec: dict) -> dict:
        n_ev = len(rec["guard_events"])
        with self.tracer.start_as_current_span(f"execute_tool {tc.name}", kind=SpanKind.INTERNAL) as sp:
            sp.set_attribute("gen_ai.operation.name", "execute_tool")
            sp.set_attribute("gen_ai.tool.name", tc.name)
            sp.set_attribute("gen_ai.tool.type", "function")
            sp.set_attribute("gen_ai.tool.call.id", tc.id or "")
            sp.set_attribute("langfuse.observation.type", "tool")
            sp.set_attribute("langsmith.span.kind", "tool")
            sp.set_attribute("sentry.op", "gen_ai.execute_tool")
            sp.set_attribute("openinference.span.kind", "TOOL")
            sp.set_attribute("tool.name", tc.name)
            for k, v in getattr(self, "_who", {}).items():
                sp.set_attribute(k, v)
            if "confirm" in args:
                sp.set_attribute("ledgerline.confirm", bool(args.get("confirm")))
            if self.content:
                sp.set_attribute("gen_ai.tool.call.arguments", self._c(args))
                sp.set_attribute("langfuse.observation.input", self._c(args))
                sp.set_attribute("input.value", self._c(args))
            out = run()
            for ev in rec["guard_events"][n_ev:]:
                self.guard_span(ev)
            ok = out.get("ok", True) if isinstance(out, dict) else True
            sp.set_attribute("ledgerline.ok", bool(ok))
            for k in ("request_no", "po_no", "status"):
                if isinstance(out.get(k), (str, int)):
                    sp.set_attribute(f"ledgerline.receipt.{k}", out[k])
            if "preview" in out:
                sp.set_attribute("ledgerline.preview_only", True)
            if out.get("refused_by"):
                sp.set_attribute("ledgerline.refused_by", out["refused_by"])
                sp.set_attribute("ledgerline.rule", out.get("rule") or "")
            if ok is False:
                sp.set_status(Status(StatusCode.ERROR, (out.get("error") or "")[:200]))
                sp.set_attribute("error.type", "guard_refused" if out.get("refused_by") else "tool_error")
            if self.content:
                sp.set_attribute("gen_ai.tool.call.result", self._c(out))
                sp.set_attribute("langfuse.observation.output", self._c(out))
                sp.set_attribute("output.value", self._c(out))
            return out

    def guard_span(self, ev: dict):
        """One guard decision as its own short span (Langfuse shows it as a 'guardrail' observation)."""
        with self.tracer.start_as_current_span(f"guardrail {ev['guard']}", kind=SpanKind.INTERNAL) as g:
            g.set_attribute("langfuse.observation.type", "guardrail")
            g.set_attribute("langsmith.span.kind", "chain")
            g.set_attribute("sentry.op", "guardrail")
            for k, v in getattr(self, "_who", {}).items():
                g.set_attribute(k, v)
            g.set_attribute("openinference.span.kind", "GUARDRAIL")
            g.set_attribute("ledgerline.guard", ev["guard"])
            g.set_attribute("ledgerline.guard.decision", ev["decision"])
            g.set_attribute("ledgerline.guard.where", ev.get("where", ""))
            g.set_attribute("ledgerline.guard.ms", float(ev.get("ms", 0)))
            g.set_attribute("langfuse.observation.output", self._c({k: v for k, v in ev.items() if k != "guard"}, 2000))
            g.set_attribute("output.value", self._c(ev.get("why", ev["decision"]), 2000))
            if ev["decision"] in ("refused", "blocked", "quarantined"):
                g.set_attribute("langfuse.observation.level", "WARNING")

    def guard_events_span(self, events: list[dict]):
        for ev in events:
            self.guard_span(ev)


class _TracedLLM:
    """The course LLM, with every chat() a 'chat <model>' span (inference span of the GenAI conventions)."""

    def __init__(self, llm, tr: Tracing):
        self._llm, self._tr = llm, tr

    def __getattr__(self, k):
        return getattr(self._llm, k)

    def chat(self, messages, tools=None, **kw):
        llm, tr = self._llm, self._tr
        with tr.tracer.start_as_current_span(f"chat {llm.model_id}", kind=SpanKind.CLIENT) as sp:
            sp.set_attribute("gen_ai.operation.name", "chat")
            sp.set_attribute("gen_ai.provider.name", PROVIDER_NAMES.get(llm.provider, llm.provider))
            sp.set_attribute("gen_ai.request.model", llm.model_id)
            sp.set_attribute("gen_ai.request.max_tokens", llm.max_tokens)
            sp.set_attribute("langfuse.observation.type", "generation")
            sp.set_attribute("langfuse.observation.model.name", llm.model_id)
            sp.set_attribute("langsmith.span.kind", "llm")
            sp.set_attribute("sentry.op", "gen_ai.chat")
            sp.set_attribute("gen_ai.system", PROVIDER_NAMES.get(llm.provider, llm.provider))
            sp.set_attribute("openinference.span.kind", "LLM")
            for k, v in getattr(tr, "_who", {}).items():
                sp.set_attribute(k, v)
            if tr.content:
                sp.set_attribute("gen_ai.input.messages", tr._c(to_semconv_messages(messages)))
                sp.set_attribute("langfuse.observation.input", tr._c(messages[-8:]))
                sp.set_attribute("input.value", tr._c(messages[-1].get("content") or ""))
                if tools:
                    sp.set_attribute("gen_ai.tool.definitions", _j([t["function"]["name"] for t in tools]))
            t0 = time.perf_counter()
            try:
                r = llm.chat(messages, tools=tools, **kw)
            except Exception as e:
                sp.set_status(Status(StatusCode.ERROR, str(e)[:200]))
                sp.set_attribute("error.type", type(e).__name__)
                raise
            served = r.model.split(":", 1)[-1]
            from .agent import usd
            cost = usd(served, r.tokens_in, r.tokens_out)
            sp.set_attribute("gen_ai.response.model", served)
            sp.set_attribute("gen_ai.usage.input_tokens", r.tokens_in)
            sp.set_attribute("gen_ai.usage.output_tokens", r.tokens_out)
            sp.set_attribute("gen_ai.usage.total_tokens", r.tokens_in + r.tokens_out)
            sp.set_attribute("gen_ai.response.finish_reasons", ["tool_calls" if r.tool_calls else "stop"])
            sp.set_attribute("langfuse.observation.usage_details", json.dumps({"input": r.tokens_in, "output": r.tokens_out}))
            sp.set_attribute("langfuse.observation.cost_details", json.dumps({"total": cost}))
            sp.set_attribute("ledgerline.cost_usd", cost)
            # Cost, said three ways. Langfuse: cost_details (above). Sentry: its gen_ai.cost.* extension, in US$; with a numeric
            # total it keeps ours instead of estimating from a price table that may not know the model. LangSmith documents no
            # OTLP cost attribute: it prices from its model table by metadata.ls_model_name / ls_provider, so we send those,
            # and our own figure as plain metadata so it can be read on the run either way.
            from ...llm import PRICES
            pin, pout = PRICES.get(served, (2.0, 10.0))[:2]           # the same table and default as agent.usd()
            sp.set_attribute("gen_ai.cost.input_tokens", round(r.tokens_in * pin / 1e6, 6))
            sp.set_attribute("gen_ai.cost.output_tokens", round(r.tokens_out * pout / 1e6, 6))
            sp.set_attribute("gen_ai.cost.total_tokens", cost)
            sp.set_attribute("langsmith.metadata.ls_model_name", served)
            sp.set_attribute("langsmith.metadata.ls_provider", PROVIDER_NAMES.get(llm.provider, llm.provider))
            sp.set_attribute("langsmith.metadata.cost_usd", cost)
            sp.set_attribute("ledgerline.model_seconds", round(time.perf_counter() - t0, 3))
            sp.set_attribute("llm.model_name", served)
            sp.set_attribute("llm.provider", llm.provider)
            sp.set_attribute("llm.token_count.prompt", r.tokens_in)
            sp.set_attribute("llm.token_count.completion", r.tokens_out)
            sp.set_attribute("llm.token_count.total", r.tokens_in + r.tokens_out)
            if tr.content:
                sp.set_attribute("gen_ai.output.messages", tr._c(to_semconv_messages([r.message()])))
                sp.set_attribute("langfuse.observation.output", tr._c(r.message()))
                sp.set_attribute("output.value", tr._c(r.content or [{"tool": t.name, "args": t.arguments} for t in r.tool_calls]))
            return r


# ------------------------------------------------------------------------------------------------ replay
def replay(spans: list[dict], exporter, service: str = "ask-northbridge", shift_to_now: bool = True) -> int:
    """Send recorded spans (SpanLog JSON) to another back end, unchanged: same ids, names, attributes, timings.
    shift_to_now moves the timestamps so the newest span ends now (a viewer's default time window is recent)."""
    import datetime as _dt

    from opentelemetry.sdk.trace import Event, ReadableSpan
    from opentelemetry.trace import SpanContext, TraceFlags
    from opentelemetry.trace.status import Status as _St

    def ns(s):
        return int(_dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() * 1e9)

    shift = 0
    if shift_to_now and spans:
        shift = int(time.time() * 1e9) - max(ns(s["end_time"]) for s in spans)
    res = Resource.create({**(spans[0].get("resource", {}).get("attributes", {}) if spans else {}), "service.name": service})
    out = []
    for s in spans:
        c = s["context"]
        ctx = SpanContext(int(c["trace_id"], 16), int(c["span_id"], 16), is_remote=False, trace_flags=TraceFlags(1))
        parent = SpanContext(int(c["trace_id"], 16), int(s["parent_id"], 16), is_remote=False, trace_flags=TraceFlags(1)) \
            if s.get("parent_id") else None
        kind = getattr(SpanKind, s.get("kind", "SpanKind.INTERNAL").split(".")[-1], SpanKind.INTERNAL)
        code = s.get("status", {}).get("status_code", "UNSET")
        st = _St(StatusCode[code], s.get("status", {}).get("description")) if code != "UNSET" else _St(StatusCode.UNSET)
        evs = [Event(e["name"], e.get("attributes") or {}, ns(e["timestamp"]) + shift) for e in s.get("events", [])]
        out.append(ReadableSpan(name=s["name"], context=ctx, parent=parent, resource=res, attributes=s.get("attributes") or {},
                                events=evs, kind=kind, status=st, start_time=ns(s["start_time"]) + shift,
                                end_time=ns(s["end_time"]) + shift))
    exporter.export(out)
    return len(out)
