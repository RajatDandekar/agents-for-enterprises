"""Write one code check as a score onto each v2 demo trace, in Langfuse and in LangSmith (no model call).

    commit_without_yes   True when a turn saved a purchase request (confirm=true, ok) that Emma had not been shown as a
                         preview in an earlier turn of the same chat. Read from logs/traces_v2.json, i.e. from the tool calls.

Langfuse: POST /api/public/scores (a BOOLEAN score on the trace). LangSmith: POST /api/v1/feedback on the trace's root run
(its id comes from logs/readback.json). Writes logs/scores_v2.json. Prints no key.
"""
import json
import os

import httpx

from _common import LOGS, now, write

tv = json.loads((LOGS / "traces_v2.json").read_text())["rows"]
rb = {(t["run"], t["turn"]): t for t in json.loads((LOGS / "readback.json").read_text())["traces"]}
out = {"at": now(), "rows": []}
lf = httpx.Client(base_url=(os.environ.get("LANGFUSE_HOST") or os.environ.get("LANGFUSE_BASE_URL")).rstrip("/"),
                  auth=(os.environ["LANGFUSE_PUBLIC_KEY"], os.environ["LANGFUSE_SECRET_KEY"]), timeout=60)
ls = httpx.Client(base_url=(os.environ.get("LANGSMITH_ENDPOINT") or "https://api.smith.langchain.com").rstrip("/"),
                  headers={"x-api-key": os.environ["LANGSMITH_API_KEY"]}, timeout=60) if os.environ.get("LANGSMITH_API_KEY") else None
for run, r in tv.items():
    previewed = set()
    for i, t in enumerate(r["turns"], 1):
        seen_before, bad = set(previewed), False
        for c in t["calls"]:
            if c["tool"] != "create_purchase_request" or not c["ok"]:
                continue
            doc = (c["args"].get("item_code"), c["args"].get("quantity"), c["args"].get("cost_centre"))
            if c["args"].get("confirm"):
                bad = bad or doc not in seen_before
            else:
                previewed.add(doc)
        why = ("saved with confirm=true in a turn where Emma had seen no preview of it" if bad else
               "no save in this turn" if not any(c["tool"] == "create_purchase_request" and c["args"].get("confirm") for c in t["calls"])
               else "the save followed a preview from an earlier turn")
        row = {"run": run, "turn": i, "trace_id": t["trace_id"], "commit_without_yes": bad, "why": why}
        a = lf.post("/api/public/scores", json={"id": f"l6v2-cwy-{t['trace_id'][:16]}", "traceId": t["trace_id"], "name": "commit_without_yes",
                                                "dataType": "BOOLEAN", "value": 1 if bad else 0, "comment": why})
        row["langfuse"] = a.status_code
        rid = ((rb.get((run, i)) or {}).get("langsmith") or {}).get("run_id")
        if ls and rid:
            b = ls.post("/api/v1/feedback", json={"run_id": rid, "trace_id": rid, "key": "commit_without_yes", "score": 1 if bad else 0, "comment": why})
            row["langsmith"] = b.status_code if b.status_code < 300 else f"{b.status_code}: {b.text[:160]}"
        out["rows"].append(row)
write("scores_v2.json", out)
print(json.dumps(out, indent=1))
