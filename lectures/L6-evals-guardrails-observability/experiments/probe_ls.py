"""Probe: what LangSmith holds for the project, and how its ids relate to the OpenTelemetry ids. Prints no key."""
import json, os, httpx
from _common import LOGS
LS = (os.environ.get("LANGSMITH_ENDPOINT") or "https://api.smith.langchain.com").rstrip("/")
c = httpx.Client(base_url=LS, headers={"x-api-key": os.environ["LANGSMITH_API_KEY"]}, timeout=60)
r = c.get("/api/v1/sessions", params={"limit": 20})
print("sessions", r.status_code, [(s.get("name"), s.get("id"), s.get("run_count")) for s in (r.json() if r.status_code < 300 else [])][:20])
proj = next((s for s in r.json() if s.get("name") == os.environ.get("LANGSMITH_PROJECT", "ask-northbridge")), None) or (r.json() or [None])[0]
print("project used:", proj and proj.get("name"))
tv = json.loads((LOGS / "traces_v2.json").read_text())
want = {t["trace_id"]: (n, i) for n, rr in tv["rows"].items() for i, t in enumerate(rr["turns"], 1)}
sel = ["ID", "NAME", "RUN_TYPE", "IS_ROOT", "TRACE_ID", "START_TIME", "TOTAL_TOKENS", "TOTAL_COST", "METADATA", "THREAD_ID"]
q = c.post("/api/v2/runs/query", json={"project_ids": [proj["id"]], "is_root": True, "selects": sel, "page_size": 30})
print("v2 query", q.status_code, q.text[:300] if q.status_code >= 300 else "")
if q.status_code < 300:
    for x in q.json().get("items", []):
        md = x.get("metadata") or {}
        print(x.get("id"), x.get("trace_id"), x.get("name"), x.get("start_time"), x.get("total_tokens"), x.get("total_cost"), x.get("thread_id"),
              {k: v for k, v in md.items() if "trace" in k.lower() or "otel" in k.lower() or k in ("thread_id", "ls_model_name")})
    print("selects available keys on first:", sorted((q.json().get("items") or [{}])[0].keys()))
q1 = c.post("/api/v1/runs/query", json={"session": [proj["id"]], "is_root": True, "limit": 5})
print("v1 query", q1.status_code, q1.text[:200] if q1.status_code >= 300 else [(x.get("id"), x.get("trace_id"), x.get("name")) for x in q1.json().get("runs", [])])
print("our otel trace ids:", want)
