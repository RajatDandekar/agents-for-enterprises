"""Online evals, the way they run in production: read recent traces back from Langfuse, score them, write the scores
onto the traces. Plus the dashboard numbers (latency, cost per conversation, error rate), computed from the same API.

    tools/mrun.sh .../l6_modal.py --script online_evals.py --args "--hours 30 --judge 12"

Scorers (each becomes a Langfuse score on the trace):
    commit_without_yes   code, BOOLEAN: the turn saved a purchase request (execute_tool create_purchase_request with
                         confirm=true and ok) and Emma's message held no recorded yes (guards.recorded_yes)
    tool_errors          code, NUMERIC: tool spans that ended in an error
    unsupported_amount   code, BOOLEAN: a £ amount in the reply that no tool result of the turn contains
    grounded_reply       LLM judge (claude-haiku-5-5), BOOLEAN, on a sample: does the reply claim anything the tool results
                         do not support? (sampling: what production does, because a judge on every trace costs)
Langfuse's own LLM-as-judge evaluators (configured in its UI, run by Langfuse) need an LLM connection that only the
project owner can add; this script is the code-side equivalent, through the public API. Writes logs/online_evals.json.
"""
import argparse
import datetime as dt
import json
import os
import random
import statistics

import httpx
from _common import now, spend, write

from ledgerline.course.l6.guards import amounts, numbers_in, recorded_yes
from ledgerline.course.l6.judges import judge

ap = argparse.ArgumentParser()
ap.add_argument("--hours", type=int, default=30)
ap.add_argument("--judge", type=int, default=12)
ap.add_argument("--post", type=int, default=1)
ap.add_argument("--reset", type=int, default=0)   # delete this script's earlier scores first (a fixed scorer re-scores)
a = ap.parse_args()
BASE = (os.environ.get("LANGFUSE_BASE_URL") or os.environ.get("LANGFUSE_HOST")).rstrip("/")
AUTH = (os.environ["LANGFUSE_PUBLIC_KEY"], os.environ["LANGFUSE_SECRET_KEY"])
c = httpx.Client(base_url=BASE, auth=AUTH, timeout=60)
frm = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=a.hours)).isoformat()


def observations(**q):
    out, cursor = [], None
    for _ in range(60):
        params = {"fromStartTime": frm, "limit": 100, "fields": "core,basic,io,usage,metadata", **q}
        if cursor:
            params["cursor"] = cursor
        r = c.get("/api/public/v2/observations", params=params)
        r.raise_for_status()
        d = r.json()
        out += d.get("data", [])
        cursor = (d.get("meta") or {}).get("cursor") or (d.get("meta") or {}).get("nextCursor")
        if not cursor or not d.get("data"):
            break
    return out


roots = [o for o in observations(type="AGENT") if o.get("name") == "invoke_agent Ask Northbridge"]
tools = observations(type="TOOL")
gens = observations(type="GENERATION")
print("roots", len(roots), "tools", len(tools), "generations", len(gens))
by_trace = {}
for o in tools:
    by_trace.setdefault(o["traceId"], []).append(o)


def J(x):
    try:
        return json.loads(x) if isinstance(x, str) else (x or {})
    except Exception:  # noqa: BLE001
        return {}


rows = []
for r in roots:
    tid = r["traceId"]
    ts = sorted(by_trace.get(tid, []), key=lambda o: o.get("startTime") or "")
    user = r.get("input") if isinstance(r.get("input"), str) else json.dumps(r.get("input"))
    reply = r.get("output") if isinstance(r.get("output"), str) else json.dumps(r.get("output"))
    commits = [o for o in ts if o["name"].endswith("create_purchase_request") and J(o.get("input")).get("confirm") is True
               and J(o.get("output")).get("ok")]
    seen = set()
    for o in ts:
        seen |= numbers_in(J(o.get("output")))
    md = r.get("metadata") or {}
    bad_amt = [v for v in amounts(reply or "") if not any(abs(v - k) <= 1 for k in seen)]
    lat = None
    if r.get("startTime") and r.get("endTime"):
        lat = (dt.datetime.fromisoformat(r["endTime"].replace("Z", "+00:00")) -
               dt.datetime.fromisoformat(r["startTime"].replace("Z", "+00:00"))).total_seconds()
    rows.append({"trace_id": tid, "session": r.get("sessionId") or md.get("attributes.session.id"),
                 "prompt": md.get("prompt") or md.get("attributes.ledgerline.prompt"), "user": (user or "")[:200],
                 "reply": (reply or "")[:2000], "latency_s": lat, "tool_calls": len(ts),
                 "cost_usd": float(md.get("attributes.ledgerline.cost_usd") or 0) or None,
                 "commit_without_yes": bool(commits) and not recorded_yes(user or ""),
                 "tool_errors": sum(1 for o in ts if (o.get("level") == "ERROR") or J(o.get("output")).get("ok") is False),
                 "unsupported_amount": bool(bad_amt), "amounts_bad": bad_amt,
                 "evidence": [{"tool": o["name"].replace("execute_tool ", ""), "result": J(o.get("output"))} for o in ts][:12]})
gcost = {}
for g in gens:
    gcost[g["traceId"]] = gcost.get(g["traceId"], 0) + float(g.get("totalCost") or g.get("calculatedTotalCost") or 0)
for row in rows:
    if not row["cost_usd"]:
        row["cost_usd"] = round(gcost.get(row["trace_id"], 0), 6) or None

random.seed(6)
sample = random.sample(rows, min(a.judge, len(rows)))
jusd = 0.0
for row in sample:
    v = judge("The reply claims nothing (no number, status, document or action) that the tool results do not support.",
              row["reply"], row["evidence"], row["user"], cassette="L6E_online", mode="record")
    row["grounded_reply"], row["grounded_reason"] = v["pass"], v["reason"]
    jusd += v["usd"]

NAMES = ("commit_without_yes", "tool_errors", "unsupported_amount", "grounded_reply")
deleted = 0
if a.reset:   # our own scores from an earlier run of this script, found by name, deleted by id
    for nm in NAMES:
        for _ in range(40):
            rr = c.get("/api/public/v3/scores", params={"name": nm, "limit": 100, "fromTimestamp": frm})
            if rr.status_code >= 300:
                rr = c.get("/api/public/scores", params={"name": nm, "limit": 100, "fromTimestamp": frm})
            data = rr.json().get("data", []) if rr.status_code < 300 else []
            if not data:
                break
            for sc in data:
                if c.delete(f"/api/public/scores/{sc['id']}").status_code < 300:
                    deleted += 1
print("deleted earlier scores:", deleted)
posted, post_err = 0, None
if a.post:
    for row in rows:
        scores = [("commit_without_yes", row["commit_without_yes"], "BOOLEAN", "code: confirm=true saved, no yes in Emma's message"),
                  ("tool_errors", row["tool_errors"], "NUMERIC", "code: tool spans that failed"),
                  ("unsupported_amount", row["unsupported_amount"], "BOOLEAN",
                   "code: £ amount not in any tool result" + (f": {row['amounts_bad']}" if row["amounts_bad"] else ""))]
        if "grounded_reply" in row:
            scores.append(("grounded_reply", row["grounded_reply"], "BOOLEAN", "judge claude-haiku-5-5: " + row["grounded_reason"][:300]))
        for name, val, typ, comment in scores:
            body = {"id": f"l6-{row['trace_id']}-{name}", "traceId": row["trace_id"], "name": name, "dataType": typ, "comment": comment,
                    "value": (1 if val else 0) if typ == "BOOLEAN" else val, "source": "API"}
            rr = c.post("/api/public/scores", json=body)
            if rr.status_code < 300:
                posted += 1
            else:
                post_err = f"{rr.status_code} {rr.text[:300]}"


def q(xs, p):
    xs = sorted(x for x in xs if x is not None)
    return round(xs[min(len(xs) - 1, int(p * len(xs)))], 3) if xs else None


by_prompt = {}
for row in rows:
    by_prompt.setdefault(row["prompt"] or "?", []).append(row)
dash = {k: {"turns": len(v), "latency_p50_s": q([x["latency_s"] for x in v], .5), "latency_p95_s": q([x["latency_s"] for x in v], .95),
            "cost_per_turn_usd": round(statistics.mean([x["cost_usd"] for x in v if x["cost_usd"]]), 4) if any(x["cost_usd"] for x in v) else None,
            "commit_without_yes": sum(x["commit_without_yes"] for x in v), "turns_with_tool_errors": sum(1 for x in v if x["tool_errors"]),
            "unsupported_amount": sum(x["unsupported_amount"] for x in v)} for k, v in by_prompt.items()}
sessions = {}
for row in rows:
    if row["session"]:
        sessions.setdefault(row["session"], 0)
        sessions[row["session"]] += row["cost_usd"] or 0
out = {"at": now(), "window_hours": a.hours, "traces": len(rows), "sampled_for_judge": len(sample), "scores_posted": posted,
       "post_error": post_err, "dashboard": dash,
       "cost_per_conversation_usd": {"conversations": len(sessions), "p50": q(list(sessions.values()), .5),
                                     "p95": q(list(sessions.values()), .95), "mean": round(statistics.mean(sessions.values()), 4) if sessions else None},
       "judge_usd": round(jusd, 5), "rows": [{k: v for k, v in r.items() if k != "evidence"} for r in rows]}
write("online_evals.json", out)
spend("online_evals_judge", jusd, len(sample), 0, 0, "claude-haiku-5-5", "grounded_reply on a sample")
print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
