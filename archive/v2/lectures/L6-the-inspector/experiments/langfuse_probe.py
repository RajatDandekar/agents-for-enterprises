"""Probe the Langfuse v2 read API with one exported trace (scenario 2). Status codes and server messages only; no keys."""
import json
import pathlib
import time

from bahi.evals.trace import _iso, _lf, export_langfuse, langfuse_host

LOGS = pathlib.Path(__file__).parent / "logs"
d = json.loads((LOGS / "suite_graph.json").read_text())
rec = [r for r in d["cases"] if r["id"] == "S2"]
t0 = time.time() - 7200
e = export_langfuse(rec, d["meta"], t0=t0)
print("host", langfuse_host(), "export", {k: v for k, v in e.items() if k != "trace_ids"})
tid = e["trace_ids"]["S2"]
time.sleep(45)
frm, to = _iso(t0 - 60), _iso(t0 + 600)
for params in [{"fromStartTime": frm, "toStartTime": to, "limit": 5}, {"fromStartTime": frm, "toStartTime": to, "traceId": tid, "limit": 100},
               {"fromStartTime": frm, "toStartTime": to, "traceId": tid, "limit": 100, "fields": "core,basic,usage,io,metadata,model"}]:
    c, r = _lf("GET", "/api/public/v2/observations", params=params)
    data = r.get("data") or []
    print("v2/observations", sorted(params), c, "n", len(data), "meta", r.get("meta"), "keys", sorted(data[0].keys()) if data else str(r)[:400])
    if data:
        print("  sample", json.dumps(data[0], default=str)[:900])
    time.sleep(3)
for q in [{"view": "observations", "metrics": [{"measure": "count", "aggregation": "count"}], "dimensions": [{"field": "type"}],
           "filters": [], "fromTimestamp": frm, "toTimestamp": to},
          {"view": "observations", "metrics": [{"measure": "count", "aggregation": "count"}, {"measure": "totalCost", "aggregation": "sum"},
                                               {"measure": "latency", "aggregation": "p95"}, {"measure": "inputTokens", "aggregation": "sum"},
                                               {"measure": "outputTokens", "aggregation": "sum"}],
           "dimensions": [{"field": "type"}], "filters": [{"column": "traceTags", "operator": "any of", "value": ["L6-suite"], "type": "arrayOptions"}],
           "fromTimestamp": frm, "toTimestamp": to},
          {"view": "observations", "metrics": [{"measure": "traceId", "aggregation": "uniq"}], "dimensions": [],
           "filters": [{"column": "tags", "operator": "any of", "value": ["L6-suite"], "type": "arrayOptions"}], "fromTimestamp": frm, "toTimestamp": to}]:
    c, r = _lf("GET", "/api/public/v2/metrics", params={"query": json.dumps(q)})
    print("v2/metrics", c, json.dumps(r, default=str)[:900])
    time.sleep(3)
c, r = _lf("GET", "/api/public/scores", params={"traceId": tid})
print("scores", c, json.dumps(r, default=str)[:600])
