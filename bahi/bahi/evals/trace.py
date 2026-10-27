"""Lecture 6: traces. Every model call and every Bahi service call of a conversation, in order, with tokens,
seconds and ₹. Stored locally (JSON lines), and exported to Langfuse when LANGFUSE_* keys are set
(export_langfuse, then verify_langfuse reads it back through the Langfuse API).

    tracer = Tracer()
    llm = tracer.llm("gemini:gemini-3.8-flash", cassette="L6_graph")   # an LLM that records a span per call
    ... run the conversation; tracer.attach(erp) so service calls are read back from erp.calls ...
    spans = tracer.spans(erp)        # [{"seq", "kind": "llm"|"svc", "name", "node", "turn", "seconds", "tokens", "inr"}]

Seconds: a model span carries the seconds the provider took (recorded in the cassette, so a replay shows the
original run's seconds); a service span carries the sandbox's own milliseconds. The timeline lays the spans end to
end in the order they happened (the agents here call one thing at a time).
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

from ..llm import LLM, Reply
from .stats import percentile

PURPOSE = {"_say": "words", "_extract": "fill", "sample": "decide", "respond": "loop"}


def _where() -> tuple[str, str]:
    """Which graph node and which purpose made this model call (read off the call stack)."""
    f = sys._getframe(2)
    node = purpose = ""
    while f is not None:
        n = f.f_code.co_name
        if not purpose and n in PURPOSE:
            purpose = PURPOSE[n]
        if not node and n.startswith("n_"):
            node = n[2:]
        f = f.f_back
    return node, purpose


class TracedLLM(LLM):
    """An LLM that reports every reply to a Tracer. role: agent (counts towards the agent's bill) | sim | judge."""

    def __init__(self, model: str, cassette: str, tracer: "Tracer", role: str = "agent", **kw):
        super().__init__(model, cassette=cassette, **kw)
        self.tracer, self.role = tracer, role

    def chat(self, messages, tools=None, response_format=None, **kw) -> Reply:
        r = super().chat(messages, tools=tools, response_format=response_format, **kw)
        node, purpose = _where()
        self.tracer._llm_span(self, r, node, purpose)
        return r


class Tracer:
    def __init__(self):
        self._spans: list[dict] = []
        self.erp = None
        self.turn = 0
        self.llms: list[TracedLLM] = []

    def llm(self, model: str, cassette: str, role: str = "agent", **kw) -> TracedLLM:
        x = TracedLLM(model, cassette, self, role, **kw)
        self.llms.append(x)
        return x

    def attach(self, erp):
        self.erp = erp

    def _llm_span(self, llm: TracedLLM, r: Reply, node: str, purpose: str):
        self._spans.append({"kind": "llm", "role": llm.role, "name": r.model.split(":", 1)[-1], "node": node,
                            "purpose": purpose, "turn": self.turn, "erp_at": len(self.erp.calls) if self.erp else 0,
                            "tokens_in": r.tokens_in, "tokens_out": r.tokens_out, "seconds": r.seconds,
                            "inr": r.cost_inr, "replayed": r.replayed,
                            "tool_calls": [t.name for t in r.tool_calls]})

    def add_foreign(self, replies: list[Reply], role: str = "agent"):
        """For an agent built outside the tracer (a plain make_agent(erp, user)): add its llm.log afterwards."""
        for r in replies:
            self._spans.append({"kind": "llm", "role": role, "name": r.model.split(":", 1)[-1], "node": "",
                                "purpose": "", "turn": self.turn, "erp_at": len(self.erp.calls) if self.erp else 0,
                                "tokens_in": r.tokens_in, "tokens_out": r.tokens_out, "seconds": r.seconds,
                                "inr": r.cost_inr, "replayed": r.replayed, "tool_calls": []})

    def spans(self, erp=None, turn_ranges: list[tuple[int, int, int]] | None = None, start: int = 0) -> list[dict]:
        """Model spans and service spans merged in order. turn_ranges: [(turn, first_call, last_call)] of the agent's
        own service calls (calls made by the harness, like Rohit's approval, are left out)."""
        erp = erp or self.erp
        svc = []
        for t, a, b in turn_ranges or []:
            for c in erp.calls[a:b]:
                svc.append({"kind": "svc", "role": "agent", "name": c.svc, "node": c.screen or "", "purpose": "",
                            "turn": t, "erp_at": c.seq - 1, "user": c.user, "rc": c.rc, "err": c.err_cd,
                            "seconds": round(c.ms / 1000, 5), "tokens_in": 0, "tokens_out": 0, "inr": 0.0,
                            "timed_out": c.timed_out})
        llm = [s for s in self._spans if s["role"] == "agent"]
        merged = sorted(llm + svc, key=lambda s: (s["erp_at"], 0 if s["kind"] == "llm" else 1))
        # stable order: model spans keep their own order among themselves
        out, at = [], 0.0
        for i, s in enumerate(merged):
            s = dict(s, seq=i, start=round(at, 4))
            at += s["seconds"] or 0
            out.append(s)
        return out

    def role_totals(self, role: str) -> dict:
        xs = [s for s in self._spans if s["role"] == role]
        return {"calls": len(xs), "tokens_in": sum(s["tokens_in"] for s in xs), "tokens_out": sum(s["tokens_out"] for s in xs),
                "seconds": round(sum(s["seconds"] for s in xs), 3), "inr": round(sum(s["inr"] for s in xs), 4)}


# ----------------------------------------------------------------------------- the local store
class TraceStore:
    """One JSON line per conversation: run id, case, agent, versions, spans, totals. Plain files, easy to diff."""

    def __init__(self, path: str | os.PathLike):
        self.path = pathlib.Path(path)

    def write(self, run: dict, records: list[dict]):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w") as f:
            for r in records:
                f.write(json.dumps({"run": run.get("run_id"), "agent": run.get("agent"), "versions": run.get("versions"),
                                    "case": r["id"], "passed": r["passed"], "spans": r.get("spans", []),
                                    "turns": [{"seconds": t.get("seconds"), "inr": t.get("inr")} for t in r["turns"]]},
                                   default=str) + "\n")

    def load(self) -> list[dict]:
        if not self.path.exists():
            return []
        return [json.loads(l) for l in self.path.open() if l.strip()]


def turn_stats(records: list[dict]) -> dict:
    """Steps, tokens, seconds and ₹ per conversation and per turn, with p50/p95 (nearest rank)."""
    turns = [t["seconds"] for r in records for t in r["turns"] if t.get("seconds") is not None and t.get("agent_turn", True)]
    convo = [r["totals"]["seconds"] for r in records]
    steps = [r["totals"]["llm_calls"] + r["totals"]["services"] for r in records]
    return {"turns": len(turns), "turn_p50": round(percentile(turns, 50), 2), "turn_p95": round(percentile(turns, 95), 2),
            "turn_max": round(max(turns), 2) if turns else 0, "convo_p50": round(percentile(convo, 50), 2),
            "convo_p95": round(percentile(convo, 95), 2), "steps_p50": percentile(steps, 50),
            "steps_p95": percentile(steps, 95)}


# ----------------------------------------------------------------------------- Langfuse (when keys are set)
# We talk to Langfuse's public REST API directly (ingestion, then read-back), so the exporter does not depend on the
# SDK's version and every number can be checked against what the server holds. Keys come from the environment and are
# never printed or logged; only the host is.
LF_TAG = "L6-suite"


def langfuse_host() -> str:
    return (os.environ.get("LANGFUSE_BASE_URL") or os.environ.get("LANGFUSE_HOST") or "https://cloud.langfuse.com").rstrip("/")


def langfuse_ready() -> tuple[bool, str]:
    keys = [k for k in ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY") if not os.environ.get(k)]
    if keys:
        return False, "skipped: " + ", ".join(keys) + " not set here (traces stay in the local store)"
    return True, "ready"


def _lf(method: str, path: str, body: dict | None = None, params: dict | None = None, timeout: float = 60) -> tuple[int, dict]:
    import base64
    import urllib.parse
    import urllib.request
    url = langfuse_host() + path + (("?" + urllib.parse.urlencode(params, doseq=True)) if params else "")
    auth = base64.b64encode(f"{os.environ['LANGFUSE_PUBLIC_KEY']}:{os.environ['LANGFUSE_SECRET_KEY']}".encode()).decode()
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": "Basic " + auth, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:   # the server's reason, never the request headers
        try:
            return e.code, json.loads(e.read() or b"{}")
        except ValueError:
            return e.code, {"error": str(e)}


def _id(*parts) -> str:
    """Deterministic ids, so exporting the same run twice updates the same traces instead of adding new ones."""
    import hashlib
    return hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:32]


def _iso(t: float) -> str:
    import datetime as _dt
    return _dt.datetime.fromtimestamp(t, _dt.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _attr(k, v):
    if isinstance(v, bool):
        return {"key": k, "value": {"boolValue": v}}
    if isinstance(v, int):
        return {"key": k, "value": {"intValue": str(v)}}
    if isinstance(v, float):
        return {"key": k, "value": {"doubleValue": v}}
    if isinstance(v, (list, tuple)) and all(isinstance(x, str) for x in v):
        return {"key": k, "value": {"arrayValue": {"values": [{"stringValue": x} for x in v]}}}
    return {"key": k, "value": {"stringValue": v if isinstance(v, str) else json.dumps(v, ensure_ascii=False, default=str)}}


def otel_spans(rec: dict, run: dict, t0: float, tag: str = LF_TAG) -> tuple[str, list[dict], list[dict]]:
    """One conversation -> (trace id, OTLP spans, Langfuse scores). The trace: a root span for the conversation; a span
    per turn (Kavita's message in, the agent's reply out); under each turn a generation per model call (model, tokens,
    cost) and a span per Bahi service call. Scores: passed, and each code metric that applies. Times: the recorded
    seconds of our run, laid end to end from t0. Attribute names follow Langfuse's OpenTelemetry mapping."""
    from ..llm import PRICES, USD_INR
    rid = run.get("run_id", "")
    tid = _id(tag, rid, rec["id"])
    ns = lambda t: str(int(t * 1e9))  # noqa: E731
    spans_in = rec.get("spans") or []
    end_all = t0 + max([s["start"] + (s["seconds"] or 0) for s in spans_in] or [0.001])
    root = _id(tid, "root")[:16]
    failed = [m for m, v in rec["metrics"].items() if v["ok"] is False]
    model = (run.get("models") or {}).get("words", "").split(":")[-1]
    out = [{"traceId": tid, "spanId": root, "name": f"{rec['id']} · {rec['name']}", "kind": 1,
            "startTimeUnixNano": ns(t0), "endTimeUnixNano": ns(end_all), "attributes": [
                _attr("langfuse.trace.name", f"{rec['id']} · {rec['name']}"), _attr("langfuse.observation.type", "span"),
                _attr("user.id", "KJOSHI"), _attr("session.id", f"{tag} · {run.get('agent', '')}"),
                _attr("langfuse.trace.tags", [tag, run.get("kind") or "agent", model, "pass" if rec["passed"] else "fail", rec["kind"]]),
                _attr("langfuse.trace.input", rec["turns"][0]["user"] if rec["turns"] else ""),
                _attr("langfuse.trace.output", rec["turns"][-1]["agent"] if rec["turns"] else ""),
                _attr("langfuse.trace.metadata.case", rec["id"]), _attr("langfuse.trace.metadata.passed", rec["passed"]),
                _attr("langfuse.trace.metadata.never_events", rec["never_events"]),
                _attr("langfuse.trace.metadata.failed_metrics", failed),
                _attr("langfuse.trace.metadata.inr", rec["totals"]["inr"]),
                _attr("langfuse.trace.metadata.versions", {k: v for k, v in (run.get("versions") or {}).items()
                                                           if k in ("models", "tools", "suite")})]}]
    for ti, turn in enumerate(rec["turns"]):
        ts = [s for s in spans_in if s["turn"] == ti]
        a = t0 + (min(s["start"] for s in ts) if ts else 0)
        b = t0 + (max(s["start"] + (s["seconds"] or 0) for s in ts) if ts else 0)
        sid = _id(tid, "turn", ti)[:16]
        out.append({"traceId": tid, "spanId": sid, "parentSpanId": root, "name": f"turn {ti + 1} · {turn.get('act', '')}",
                    "kind": 1, "startTimeUnixNano": ns(a), "endTimeUnixNano": ns(max(a + 0.001, b)), "attributes": [
                        _attr("langfuse.observation.type", "span"), _attr("langfuse.observation.input", turn["user"]),
                        _attr("langfuse.observation.output", turn["agent"]),
                        _attr("langfuse.observation.metadata.writes", turn.get("writes") or []),
                        _attr("langfuse.observation.metadata.inr", float(turn.get("inr") or 0))]})
        for s in ts:
            st, en = t0 + s["start"], t0 + s["start"] + max(s["seconds"] or 0, 1e-6)
            oid = _id(tid, "obs", s["seq"])[:16]
            if s["kind"] == "llm":
                pr = PRICES.get(s["name"], (0, 0))
                attrs = [_attr("langfuse.observation.type", "generation"), _attr("gen_ai.request.model", s["name"]),
                         _attr("langfuse.observation.model.name", s["name"]),
                         _attr("gen_ai.usage.input_tokens", int(s["tokens_in"])), _attr("gen_ai.usage.output_tokens", int(s["tokens_out"])),
                         _attr("langfuse.observation.usage_details", {"input": s["tokens_in"], "output": s["tokens_out"]}),
                         _attr("langfuse.observation.cost_details", {"input": round(s["tokens_in"] * pr[0] / 1e6, 8),
                                                                     "output": round(s["tokens_out"] * pr[1] / 1e6, 8)}),
                         _attr("langfuse.observation.metadata.inr", float(s["inr"])), _attr("langfuse.observation.metadata.usd_inr", USD_INR),
                         _attr("langfuse.observation.metadata.node", s.get("node") or ""),
                         _attr("langfuse.observation.metadata.purpose", s.get("purpose") or "")]
                name = f"{s.get('node') or 'agent'} · {s.get('purpose') or 'call'}"
            else:
                attrs = [_attr("langfuse.observation.type", "span"), _attr("langfuse.observation.metadata.user", s.get("user") or ""),
                         _attr("langfuse.observation.metadata.rc", s.get("rc") or "")]
                if s.get("rc") == "E":
                    attrs += [_attr("langfuse.observation.level", "ERROR"), _attr("langfuse.observation.status_message", s.get("err") or "")]
                name = "bahi · " + s["name"]
            out.append({"traceId": tid, "spanId": oid, "parentSpanId": sid, "name": name, "kind": 1,
                        "startTimeUnixNano": ns(st), "endTimeUnixNano": ns(en), "attributes": attrs})
    scores = [{"id": _id(tid, "score", "passed"), "traceId": tid, "name": "passed", "value": 1 if rec["passed"] else 0,
               "dataType": "BOOLEAN", "comment": "; ".join(failed + rec["never_events"])[:500]}]
    scores += [{"id": _id(tid, "score", m), "traceId": tid, "name": m, "value": 1 if v["ok"] else 0, "dataType": "BOOLEAN",
                "comment": (v.get("why") or "")[:300]} for m, v in rec["metrics"].items() if v["ok"] is not None]
    return tid, out, scores


def export_langfuse(records: list[dict], run: dict, tag: str = LF_TAG, t0: float | None = None) -> dict:
    """Send every conversation of a suite run to Langfuse: spans over OpenTelemetry (POST /api/public/otel/v1/traces,
    one request per conversation), scores through the ingestion API (score events). Idempotent: deterministic ids, so
    the same run exported twice updates the same traces. Returns counts and trace ids, never keys."""
    import time as _time
    ok, why = langfuse_ready()
    if not ok:
        return {"exported": 0, "reason": why}
    t0 = t0 or _time.time() - 3600
    out = {"host": langfuse_host(), "tag": tag, "t0": _iso(t0), "exported": 0, "spans": 0, "generations": 0, "scores": 0,
           "errors": [], "trace_ids": {}}
    all_scores = []
    for i, rec in enumerate(records):
        tid, spans, scores = otel_spans(rec, run, t0 + i * 2, tag)
        body = {"resourceSpans": [{"resource": {"attributes": [_attr("service.name", "bahi-evals")]},
                                   "scopeSpans": [{"scope": {"name": "bahi.evals", "version": "1.0"}, "spans": spans}]}]}
        for attempt in range(4):
            code, resp = _lf("POST", "/api/public/otel/v1/traces", body)
            if code != 429:
                break
            _time.sleep(5 * (attempt + 1))
        if code < 300:
            out["exported"] += 1
        else:
            out["errors"].append({"case": rec["id"], "status": code, "error": str(resp)[:300]})
        gens = sum(1 for sp in spans if any(a["key"] == "langfuse.observation.type" and a["value"].get("stringValue") == "generation"
                                            for a in sp["attributes"]))
        out["generations"] += gens
        out["spans"] += len(spans) - gens
        out["trace_ids"][rec["id"]] = tid
        all_scores += scores
    for k in range(0, len(all_scores), 100):
        batch = [{"id": _id("score-ev", sc["id"]), "timestamp": _iso(t0), "type": "score-create", "body": sc}
                 for sc in all_scores[k:k + 100]]
        code, resp = _lf("POST", "/api/public/ingestion", {"batch": batch})
        bad = [e for e in (resp.get("errors") or [])]
        out["scores"] += len(batch) - len(bad)
        if code >= 300 or bad:
            out["errors"].append({"scores_from": k, "status": code, "error": str(bad[:2] or resp)[:300]})
    return out


def _metric(q: dict) -> tuple[int, dict]:
    return _lf("GET", "/api/public/v2/metrics", params={"query": json.dumps(q)})


def verify_langfuse(tag: str = LF_TAG, expect: int = 0, sample_trace: str | None = None, t0: str | None = None,
                    t1: str | None = None, wait: int = 300) -> dict:
    """Read back from Langfuse (v2 API) what it holds for this tag: how many traces and observations arrived, one
    trace's tree with its latency, tokens and cost, and totals by observation type and by model."""
    import time as _time
    ok, why = langfuse_ready()
    if not ok:
        return {"verified": False, "reason": why}
    flt = [{"column": "tags", "operator": "any of", "value": [tag], "type": "arrayOptions"}]
    win = {"fromTimestamp": t0, "toTimestamp": t1}
    deadline, n = _time.time() + wait, 0
    while True:
        code, r = _metric({"view": "observations", "metrics": [{"measure": "traceId", "aggregation": "uniq"}],
                           "dimensions": [], "filters": flt, **win})
        n = int(((r.get("data") or [{}])[0] or {}).get("uniq_traceId") or 0)
        if n >= expect or _time.time() > deadline:
            break
        _time.sleep(15)
    out = {"verified": expect > 0 and n >= expect, "host": langfuse_host(), "tag": tag, "traces_found": n, "expected": expect,
           "window": win, "by_type": {}, "by_model": [], "errors": [],
           "note": "trace count and conversation latency: filtered by tag (tags sit on each trace's root); totals by type "
                   "and model: every observation in the export's time window"}
    code, r = _metric({"view": "observations", "metrics": [{"measure": "count", "aggregation": "count"},
                                                           {"measure": "latency", "aggregation": "p95"},
                                                           {"measure": "latency", "aggregation": "p50"}],
                       "dimensions": [{"field": "type"}], "filters": [], **win})   # tags sit on the root only: use the window
    if code == 200:
        out["by_type"] = {d.get("type"): {k: v for k, v in d.items() if k != "type"} for d in r.get("data") or []}
    else:
        out["errors"].append({"query": "by_type", "status": code, "error": str(r)[:300]})
    for measures in ([("totalCost", "sum"), ("inputTokens", "sum"), ("outputTokens", "sum"), ("count", "count"),
                      ("latency", "p95")], [("totalCost", "sum"), ("count", "count")]):
        code, r = _metric({"view": "observations", "metrics": [{"measure": m, "aggregation": a} for m, a in measures],
                           "dimensions": [{"field": "providedModelName"}], "filters": [
                               {"column": "type", "operator": "=", "value": "GENERATION", "type": "string"}], **win})
        if code == 200:
            out["by_model"] = r.get("data") or []
            break
        out["errors"].append({"query": "by_model", "status": code, "error": str(r)[:300]})
    code, r = _metric({"view": "observations", "metrics": [{"measure": "count", "aggregation": "count"},
                                                           {"measure": "latency", "aggregation": "p50"},
                                                           {"measure": "latency", "aggregation": "p95"}],
                       "dimensions": [], "filters": flt + [{"column": "isRootObservation", "operator": "=", "value": True,
                                                            "type": "boolean"}], **win})
    if code == 200:
        out["conversations"] = (r.get("data") or [{}])[0]
    else:
        out["errors"].append({"query": "conversations", "status": code, "error": str(r)[:300]})
    code, r = _metric({"view": "scores-boolean", "metrics": [{"measure": "count", "aggregation": "count"}],
                       "dimensions": [{"field": "name"}], "filters": [], **win})
    if code == 200:
        out["scores"] = r.get("data") or []
    else:
        out["errors"].append({"query": "scores", "status": code, "error": str(r)[:300]})
    if sample_trace:
        code, r = _lf("GET", "/api/public/v2/observations", params={"traceId": sample_trace, "limit": 200, "fromStartTime": t0,
                                                                    "toStartTime": t1, "fields": "core,basic,usage,model"})
        obs = r.get("data") or []
        out["sample"] = {"status": code, "trace_id": sample_trace, "observations": [
            {"id": o.get("id"), "parent": o.get("parentObservationId"), "type": o.get("type"), "name": o.get("name"),
             "model": o.get("model") or o.get("providedModelName"), "start": o.get("startTime"), "end": o.get("endTime"),
             "latency": o.get("latency"), "usage": o.get("usageDetails"), "cost": o.get("totalCost"),
             "level": o.get("level")} for o in obs]}
    return out
