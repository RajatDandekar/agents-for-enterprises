"""Lecture 10, Part 3: online evaluation and a dashboard, from what Langfuse stored (not from our memory of the run).

    tools/mrun.sh lectures/L10-observability-evals/experiments/l10_modal.py --script lectures/L10-observability-evals/experiments/online_evals.py

An online evaluator is a small job that runs after the fact, on production traces:
  1. pull the latest traces tagged L10 from Langfuse's public API (no access to Bahi: only what the trace holds)
  2. score each one with checks that need only the trace:
       claims_match_receipts  the reply says released/placed only if a release tool span in the same trace returned RL
       tool_errors            how many tool spans ended with ok=false
       turn_seconds, cost     from the agent span and the generation spans
  3. a sample (every second trace) also gets the words-only judge, as teams do to keep judge cost down
  4. write the scores back to Langfuse (name online_*), then read every score back and build the dashboard numbers
Writes logs/online_evals.json. Cassette IND10_online_judge.
"""
import json
import pathlib
import re
import statistics
import time

from bahi.course.l7.evals import JUDGE
from bahi.course.obs import lf as LF
from bahi.llm import LLM

HERE = pathlib.Path(__file__).parent
sess = json.loads((HERE / "logs" / "obs_sessions.json").read_text())
RUN = sess["run"]  # argv[1] = a log suffix (e.g. _r2) to read obs_sessions_r2.json instead
c = LF.client()
judge = LLM("openrouter:google/gemini-3.8-flash", cassette="IND10_online_judge")
CLAIM = re.compile(r"\b(released|placed|sent to (?:the )?supplier|has been ordered)\b", re.I)
NOT = re.compile(r"\bnot (?:yet )?(?:been )?(?:released|placed|sent)\b|draft|pending|waiting", re.I)

# ---- 1. pull: every observation of every trace of this run (GET /api/public/v2/observations)
SUF = __import__("sys").argv[1] if len(__import__("sys").argv) > 1 else ""
if SUF:
    sess = json.loads((HERE / "logs" / f"obs_sessions{SUF}.json").read_text())
    RUN = sess["run"]
tids = [t for s in sess["sessions"] for t in s["trace_ids"]]
traces = []
for tid in tids:
    t = LF.fetch_trace(c, tid, tries=8, hours=12)
    if t:
        traces.append(t)
print("pulled", len(traces), "of", len(tids), "traces from Langfuse")


def txt(x):
    return x if isinstance(x, str) else json.dumps(x or "", ensure_ascii=False)


rows = []
for i, t in enumerate(traces):
    obs = t["observations"]
    root = next((o for o in obs if not o.get("parentObservationId")), obs[0])
    reply = txt(root.get("output"))
    tools = [o for o in obs if (o.get("type") or "").upper() == "TOOL"]
    gens = [o for o in obs if (o.get("type") or "").upper() == "GENERATION"]
    released = [o for o in tools if "release_purchase_order" in (o.get("name") or "")
                and re.search(r"RL|RELEASED", txt(o.get("output")))]
    errors = sum(1 for o in tools if (o.get("level") or "") == "ERROR")
    claims = bool(CLAIM.search(reply)) and not NOT.search(reply)
    honest = (not claims) or bool(released)
    cost_usd = sum(float(o.get("totalCost") or 0) for o in gens)
    tok_in = sum(int((o.get("usageDetails") or {}).get("input", 0) or 0) for o in gens)
    tok_out = sum(int((o.get("usageDetails") or {}).get("output", 0) or 0) for o in gens)
    row = {"trace_id": t["id"], "session_id": next((x["session_id"] for x in sess["sessions"] if t["id"] in x["trace_ids"]), None),
           "root": root.get("name"), "latency_s": root.get("latency"), "tools": len(tools), "generations": len(gens),
           "tool_errors": errors, "tool_error_messages": [o.get("statusMessage") for o in tools if o.get("level") == "ERROR"],
           "claims_release": claims, "release_in_trace": bool(released), "claims_match_receipts": honest,
           "cost_usd_langfuse": round(cost_usd, 6), "tokens_in": tok_in, "tokens_out": tok_out,
           "prompt": [(o.get("promptName"), o.get("promptVersion")) for o in gens][:1]}
    c.create_score(trace_id=t["id"], name="online_claims_match_receipts", value=1 if honest else 0, data_type="BOOLEAN",
                   comment="reply claims a release only if a release span returned RL")
    c.create_score(trace_id=t["id"], name="online_tool_errors", value=errors, data_type="NUMERIC")
    if i % 2 == 0:  # the sampled judge
        user = txt(root.get("input"))
        r = judge.chat([{"role": "system", "content": JUDGE},
                        {"role": "user", "content": f"KAVITA: {user}\nASK RASOI: {reply}"}])
        jt = (r.content or "").strip()
        try:
            v = json.loads(jt[jt.find("{"):jt.rfind("}") + 1])
        except Exception:  # noqa: BLE001
            v = {"pass": None}
        row["judge_sampled"] = v.get("pass")
        row["judge_reason"] = v.get("reason")
        row["judge_cost_inr"] = r.cost_inr
        if v.get("pass") is not None:
            c.create_score(trace_id=t["id"], name="online_judge_sampled", value=1 if v["pass"] else 0,
                           data_type="BOOLEAN", comment=v.get("reason"))
    rows.append(row)
gas = next((s for s in sess["sessions"] if s["scenario"] == 2 and s["passed"]), None) or \
    next(s for s in sess["sessions"] if s["scenario"] == 2)
(HERE / "logs" / f"langfuse_gasket{SUF}.json").write_text(json.dumps(
    {"session_id": gas["session_id"], "trace_ids": gas["trace_ids"],
     "traces": [t for t in traces if t["id"] in gas["trace_ids"]]}, indent=1, ensure_ascii=False, default=str))
c.flush()
time.sleep(20)

# ---- 4. read the scores back (GET /api/public/v3/scores) and ask the metrics API: a dashboard is a query
back = []
for tid in tids:
    try:
        back += LF.fetch_scores(c, trace_id=tid)
    except Exception as e:  # noqa: BLE001
        back.append({"error": repr(e)[:300]})
import datetime as _dt  # noqa: E402
now = _dt.datetime.now(_dt.timezone.utc)
frm = (now - _dt.timedelta(hours=12)).strftime("%Y-%m-%dT%H:%M:%SZ")
to = (now + _dt.timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
mq = {}
for name, q in {
    "by_type": {"view": "observations", "metrics": [{"measure": "count", "aggregation": "count"},
                                                    {"measure": "latency", "aggregation": "p95"},
                                                    {"measure": "totalCost", "aggregation": "sum"}],
                "dimensions": [{"field": "type"}], "filters": [], "fromTimestamp": frm, "toTimestamp": to},
    "by_name": {"view": "observations", "metrics": [{"measure": "count", "aggregation": "count"},
                                                    {"measure": "latency", "aggregation": "p50"}],
                "dimensions": [{"field": "name"}], "filters": [], "fromTimestamp": frm, "toTimestamp": to},
    "scores": {"view": "scores-boolean", "metrics": [{"measure": "count", "aggregation": "count"},
                                                    {"measure": "value", "aggregation": "avg"}],
               "dimensions": [{"field": "name"}], "filters": [], "fromTimestamp": frm, "toTimestamp": to},
}.items():
    try:
        mq[name] = LF.metrics(c, q)
    except Exception as e:  # noqa: BLE001
        mq[name] = {"error": repr(e)[-600:]}
lat = [r["latency_s"] for r in rows if r["latency_s"] is not None]


def pct(xs, p):
    xs = sorted(xs)
    return round(xs[min(len(xs) - 1, int(round(p * (len(xs) - 1))))], 2) if xs else None


dash = {"traces": len(rows), "sessions": len({r["session_id"] for r in rows}),
        "latency_p50_s": pct(lat, .5), "latency_p95_s": pct(lat, .95),
        "claims_match_receipts": sum(r["claims_match_receipts"] for r in rows),
        "tool_errors_total": sum(r["tool_errors"] for r in rows),
        "traces_with_tool_errors": sum(1 for r in rows if r["tool_errors"]),
        "judge_sampled_n": sum(1 for r in rows if "judge_sampled" in r),
        "judge_sampled_pass": sum(1 for r in rows if r.get("judge_sampled") is True),
        "tokens_in_total": sum(r["tokens_in"] for r in rows), "tokens_out_total": sum(r["tokens_out"] for r in rows),
        "cost_usd_langfuse_total": round(sum(r["cost_usd_langfuse"] or 0 for r in rows), 5),
        "erp_check_sessions_passed": sum(s["passed"] for s in sess["sessions"]),
        "erp_check_sessions": len(sess["sessions"]),
        "cost_inr_ours_total": round(sum(s["cost_inr"] for s in sess["sessions"]), 3)}
out = {"date": time.strftime("%Y-%m-%d %H:%M"), "run": RUN, "dashboard": dash, "rows": rows, "metrics_api": mq,
       "scores_read_back": back[:400], "n_scores_read_back": len(back)}
(HERE / "logs" / f"online_evals{SUF}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
print(json.dumps(dash, indent=1))
