"""Make a public LangSmith link for each trace id given on the command line (anyone with the link can read that one
trace, no account). Used for the Lecture 7 deck: the Aegis demo turns. The traces are sandbox turns on made-up data.

    tools/mrun.sh .../l6_modal.py --script share_trace.py --args "<trace id> <trace id> ..."

Writes logs/share_trace.json. Nothing here prints a key or a header.
"""
import os
import sys

import httpx

from _common import LOGS, now, write

LS = (os.environ.get("LANGSMITH_ENDPOINT") or "https://api.smith.langchain.com").rstrip("/")
c = httpx.Client(base_url=LS, headers={"x-api-key": os.environ["LANGSMITH_API_KEY"]}, timeout=60)
r = c.get("/api/v1/sessions", params={"name": os.environ.get("LANGSMITH_PROJECT", "ask-northbridge")})
project = (r.json() or [None])[0]["id"]

# LangSmith keeps the OpenTelemetry trace id in a root run's metadata: find the root runs once, newest first
roots, cursor = {}, None
for _ in range(5):
    body = {"project_ids": [project], "is_root": True, "page_size": 200, "selects": ["ID", "NAME", "METADATA", "START_TIME"]}
    if cursor:
        body["cursor"] = cursor
    q = c.post("/api/v2/runs/query", json=body)
    q.raise_for_status()
    d = q.json()
    for x in d.get("items", []):
        roots.setdefault((x.get("metadata") or {}).get("OTEL_TRACE_ID"), x)
    cursor = (d.get("cursors") or {}).get("next") or d.get("next_cursor")
    if not cursor or all(t in roots for t in sys.argv[1:]):
        break

out = {"at": now(), "traces": {}}
for tid in sys.argv[1:]:
    root = roots.get(tid)
    if not root:
        out["traces"][tid] = {"arrived": False}
        print(tid, "no root run found")
        continue
    s = c.post(f"/api/v2/runs/{root['id']}/share", json={"session_id": project, "trace_id": root["id"]})
    tok = (s.json() or {}).get("share_token") if s.status_code < 300 else None
    out["traces"][tid] = {"arrived": True, "run_id": root["id"], "share_status": s.status_code,
                          "public_url": f"https://smith.langchain.com/public/{tok}/r" if tok else None}
    print(tid, s.status_code, out["traces"][tid]["public_url"])
write("share_trace.json", out)
