"""Langfuse, the parts beyond traces: scores, sessions, datasets and experiments, prompt management.

    from ledgerline.course.obs import lf
    c = lf.client()                                    # keys from LANGFUSE_PUBLIC_KEY / SECRET_KEY / BASE_URL
    tmpl, version = lf.system_prompt(c)                # Ask Northbridge's system prompt, label "production"
    c.create_score(trace_id=..., name="erp_check", value=1, data_type="BOOLEAN", comment="...")
    lf.fetch_trace(c, trace_id)                        # the trace as Langfuse stored it (observations, scores)

Everything here needs a Langfuse key. The notebook runs without one: it reads what these functions returned in our
run, saved in lectures/L10-observability-evals/experiments/logs/.
"""
from __future__ import annotations

import json
import os
import time

PROMPT_NAME = "ask-northbridge-system"


def client(**kw):
    from langfuse import Langfuse
    return Langfuse(public_key=os.environ["LANGFUSE_PUBLIC_KEY"], secret_key=os.environ["LANGFUSE_SECRET_KEY"],
                    base_url=os.environ.get("LANGFUSE_BASE_URL") or os.environ.get("LANGFUSE_HOST"), **kw)


def ensure_prompt_versions(c, versions: list[tuple[str, list[str], str]]) -> list[dict]:
    """versions: [(template, labels, commit_message)], oldest first. Creates a version only if its text is new."""
    out = []
    existing = {}
    try:
        for v in range(1, 50):
            p = c.get_prompt(PROMPT_NAME, version=v, cache_ttl_seconds=0)
            existing[p.prompt] = p.version
    except Exception:  # noqa: BLE001  ran past the last version
        pass
    for text, labels, msg in versions:
        if text in existing:
            out.append({"version": existing[text], "labels": labels, "created": False})
            continue
        p = c.create_prompt(name=PROMPT_NAME, prompt=text, labels=labels, type="text", commit_message=msg,
                            tags=["ask-northbridge", "L10"])
        out.append({"version": p.version, "labels": labels, "created": True})
    return out


def system_prompt(c, label: str = "production"):
    """The template and its version, as Ask Northbridge would fetch it at start-up (cached by the SDK)."""
    p = c.get_prompt(PROMPT_NAME, label=label, cache_ttl_seconds=0)
    return p.prompt, p.version


def _plain(o):
    if hasattr(o, "dict"):
        try:
            return o.dict()
        except Exception:  # noqa: BLE001
            pass
    if hasattr(o, "model_dump"):
        return o.model_dump()
    return o


FIELDS = "core,basic,io,usage,model,prompt,metrics,trace_context,metadata"


def _window(around_iso: str | None = None, hours: int = 6):
    import datetime as dt
    now = dt.datetime.now(dt.timezone.utc)
    return now - dt.timedelta(hours=hours), now + dt.timedelta(minutes=5)


def fetch_trace(c, trace_id: str, tries: int = 12, hours: int = 6) -> dict | None:
    """Every observation of one trace, as Langfuse stored it (GET /api/public/v2/observations, filtered by traceId).
    Organisations created after 16 Sep 2026 have no legacy GET /traces endpoint; the v2 observations API replaces it.
    Ingestion is asynchronous: poll until the observations are there."""
    frm, to = _window(hours=hours)
    for _ in range(tries):
        try:
            r = c.api.observations.get_many(trace_id=trace_id, fields=FIELDS, from_start_time=frm, to_start_time=to,
                                            limit=100, expand_metadata="true")
            obs = json.loads(json.dumps(_plain(r), default=str)).get("data", [])
            if obs and any(o.get("isRootObservation") or not o.get("parentObservationId") for o in obs):
                obs.sort(key=lambda o: o.get("startTime") or "")
                return {"id": trace_id, "observations": obs}
        except Exception as e:  # noqa: BLE001
            last = repr(e)[:300]
        time.sleep(5)
    return None


def fetch_scores(c, trace_id: str | None = None, session_id: str | None = None) -> list[dict]:
    """Scores (GET /api/public/v3/scores)."""
    kw = {k: v for k, v in (("trace_id", trace_id), ("session_id", session_id)) if v}
    try:
        r = c.api.scores_v3.get_many_v3(limit=100, **kw)
    except TypeError:
        r = c.api.scores_v3.get_many_v3(**kw)
    return json.loads(json.dumps(_plain(r), default=str)).get("data", [])


def metrics(c, query: dict) -> dict:
    """The metrics API (GET /api/public/v2/metrics): a dashboard is a query over observations and scores."""
    r = c.api.metrics.metrics(query=json.dumps(query))
    return json.loads(json.dumps(_plain(r), default=str))
