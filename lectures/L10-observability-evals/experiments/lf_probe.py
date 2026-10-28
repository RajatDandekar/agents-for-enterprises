"""Probe Langfuse's v2 read API in SDK 4.17 (observations, metrics, scores). No keys printed."""
import inspect, json, pathlib, traceback, datetime as dt
from bahi.course.obs import lf as LF
c = LF.client()
out = {}
for path in ("observations.get_many", "metrics.metrics", "sessions.get", "scores.get_many", "scores_v3", "unstable"):
    o = c.api
    try:
        for p in path.split("."):
            o = getattr(o, p)
        out["sig " + path] = str(inspect.signature(o)) if callable(o) else [m for m in dir(o) if not m.startswith("_")]
        out["doc " + path] = (inspect.getdoc(o) or "")[:1500]
    except Exception as e:
        out["sig " + path] = repr(e)
tid = "ca6160020430f3e9a22100d65f625764"
frm, to = "2026-10-28T10:40:00Z", "2026-10-28T11:30:00Z"
tries = {
  "obs_by_trace": lambda: c.api.observations.get_many(trace_id=tid, from_start_time=dt.datetime.fromisoformat(frm[:-1]+"+00:00"), to_start_time=dt.datetime.fromisoformat(to[:-1]+"+00:00")),
  "obs_window": lambda: c.api.observations.get_many(from_start_time=dt.datetime.fromisoformat(frm[:-1]+"+00:00"), to_start_time=dt.datetime.fromisoformat(to[:-1]+"+00:00"), limit=5),
  "scores": lambda: c.api.scores.get_many(limit=5),
  "session": lambda: c.api.sessions.get("l10-1028-1051-s2"),
  "metrics": lambda: c.api.metrics.metrics(query=json.dumps({"view": "traces", "metrics": [{"measure": "count", "aggregation": "count"}], "dimensions": [{"field": "name"}], "filters": [], "fromTimestamp": frm, "toTimestamp": to})),
}
for k, f in tries.items():
    try:
        r = f()
        out["ok " + k] = json.loads(json.dumps(LF._plain(r), default=str))
    except Exception:
        out["err " + k] = traceback.format_exc()[-1200:]
(pathlib.Path(__file__).parent / "logs" / "_lf_probe2.json").write_text(json.dumps(out, indent=1, default=str))
