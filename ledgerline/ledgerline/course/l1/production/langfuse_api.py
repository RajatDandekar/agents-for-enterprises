"""The few Langfuse calls this segment needs, over its public REST API (no SDK magic, so students see the wire).

    post_score(trace_id, "erp_check", 1, "BOOLEAN", comment)   # POST /api/public/scores
    observations(trace_id)                                      # GET  /api/public/v2/observations (the current read API)
    trace_url(trace_id)                                         # https://<host>/project/<id>/traces/<trace id>
    make_public(tracer, trace_id, root_span_id)                 # a late OTel span that sets langfuse.trace.public

Traces are written with OpenTelemetry only (POST /api/public/otel/v1/traces, see tracing.py). The legacy read API
(GET /api/public/traces/<id>) answers 410 Gone for this project, and the old ingestion API refuses trace events, so a
trace is made public the OpenTelemetry way: one more span in the same trace carrying the trace attribute.
Keys come from LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY / LANGFUSE_BASE_URL and are never printed.
"""
from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request

_PROJECT: list = []


def _base() -> str:
    return (os.environ.get("LANGFUSE_BASE_URL") or os.environ.get("LANGFUSE_HOST") or "https://cloud.langfuse.com").rstrip("/")


def api(method: str, path: str, body=None, timeout: float = 60):
    auth = base64.b64encode(f"{os.environ['LANGFUSE_PUBLIC_KEY']}:{os.environ['LANGFUSE_SECRET_KEY']}".encode()).decode()
    req = urllib.request.Request(_base() + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:600].decode(errors="replace")


def project_id() -> str:
    if not _PROJECT:
        code, d = api("GET", "/api/public/projects")
        _PROJECT.append(d["data"][0]["id"] if code == 200 else "")
    return _PROJECT[0]


def trace_url(trace_id: str) -> str:
    return f"{_base()}/project/{project_id()}/traces/{trace_id}"


def post_score(trace_id: str, name: str, value: float, data_type: str = "NUMERIC", comment: str = ""):
    return api("POST", "/api/public/scores", {"traceId": trace_id, "name": name, "value": value, "dataType": data_type,
                                               "comment": comment[:1000]})


def observations(trace_id: str, fields: str = "core,basic,usage,model,metrics", limit: int = 200):
    q = urllib.parse.urlencode({"traceId": trace_id, "fields": fields, "limit": limit})
    return api("GET", f"/api/public/v2/observations?{q}")


def make_public(tracer, trace_id: str, root_span_id: str, at_ns: int | None = None, name: str = "publish trace"):
    """Langfuse reads trace attributes from any span of the trace, so a short child of the root sets public=true."""
    from opentelemetry import trace
    from opentelemetry.trace import NonRecordingSpan, SpanContext, TraceFlags
    parent = SpanContext(trace_id=int(trace_id, 16), span_id=int(root_span_id, 16), is_remote=True,
                         trace_flags=TraceFlags(TraceFlags.SAMPLED))
    sp = tracer.start_span(name, context=trace.set_span_in_context(NonRecordingSpan(parent)), start_time=at_ns)
    sp.set_attribute("langfuse.trace.public", True)
    sp.set_attribute("langfuse.observation.type", "event")
    sp.set_attribute("ledgerline.note", "made public for the Lecture 1 deck; all data is fictional")
    sp.end(end_time=at_ns)
