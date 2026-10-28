"""Lecture 11 experiment 6: cost per order, from token counts measured in this course's own runs.

    tools/mrun.sh tools/modal_run.py --script lectures/L11-production/experiments/cost_model.py

No model is called. It reads the logs below, prices every run at OpenRouter list prices (bahi/course/production/cost.py)
and writes logs/cost_model.json + bahi/course/production/fixtures/cost_runs.json.
  L5  lectures/L5-the-loop/experiments/logs/tasks_harness_or{,_lite}.json     12 tasks, the harness, over days
  L7  lectures/L7-trust/experiments/logs/six_{flash,lite}.json                 six scenarios x set-ups x runs
  L11 lectures/L11-production/experiments/logs/injection_eval.json             order from an approved PR
  L11 lectures/L11-production/experiments/logs/guard_eval.json                 guard tokens per message
  L11 lectures/L11-production/experiments/logs/durable_order.json              the durable drill (calls per worker)
"""
import json
import pathlib
import statistics

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parents[2]
LOGS = HERE / "logs"
import bahi.course.production as P
from bahi.course.production import cost as C

FIX = pathlib.Path(P.__file__).parent / "fixtures"
runs = []


def tier_model(m):
    return "gemini-3.5-flash-lite" if "lite" in m else "gemini-3.8-flash"


for f in ("tasks_harness_or.json", "tasks_harness_or_lite.json"):
    p = ROOT / "lectures/L5-the-loop/experiments/logs" / f
    d = json.loads(p.read_text())
    m = tier_model(d["summary"]["model"])
    for r in d["results"]:
        runs.append({"source": f"L5 {f}", "task": f"{r['id']} {r['name']}", "model": m, "tokens_in": r["tokens_in"],
                     "tokens_out": r["tokens_out"], "model_calls": r["model_calls"], "person_messages": r.get("person_messages"),
                     "passed": r["passed"], "inr": round(C.inr(r["tokens_in"], r["tokens_out"], m), 4)})
for f in ("six_flash.json", "six_lite.json"):
    d = json.loads((ROOT / "lectures/L7-trust/experiments/logs" / f).read_text())
    m = tier_model(d["model"])
    for r in d["results"]:
        runs.append({"source": f"L7 {f}", "task": f"S{r['scenario']} {r['name']} [{r['config']}] run {r['rep']}", "model": m,
                     "tokens_in": r["tokens_in"], "tokens_out": r["tokens_out"], "model_calls": r["model_calls"],
                     "person_messages": len(r.get("turns") or []), "passed": r["passed"],
                     "inr": round(C.inr(r["tokens_in"], r["tokens_out"], m), 4)})
inj = json.loads((LOGS / "injection_eval.json").read_text())
for r in inj["rows"]:
    m = tier_model(r["tier"])
    runs.append({"source": "L11 injection_eval.json", "task": f"PO from approved PR, {r['cond']} w{r['w']}", "model": m,
                 "tokens_in": r["tokens_in"], "tokens_out": r["tokens_out"], "model_calls": r["model_calls"],
                 "person_messages": len(r["turns"]), "passed": not r["ne3"], "inr": round(C.inr(r["tokens_in"], r["tokens_out"], m), 4)})

# the headline: Kavita's whole order, PR -> Rohit -> PO -> release -> GRN, from L5 T01 (the harness, both models)
whole = [r for r in runs if r["task"].startswith("T01 ")]
l7s2 = [r for r in runs if r["source"].startswith("L7") and r["task"].startswith("S2 ") and "[trust]" in r["task"]]
summ = {}
for name, rows in (("whole_order_L5_T01", whole), ("reorder_above_limit_L7_S2_trust", l7s2)):
    for m in ("gemini-3.8-flash", "gemini-3.5-flash-lite"):
        rs = [r for r in rows if r["model"] == m]
        if rs:
            summ[f"{name}|{m}"] = {"n": len(rs), "tokens_in_mean": round(statistics.mean(r["tokens_in"] for r in rs)),
                                   "tokens_out_mean": round(statistics.mean(r["tokens_out"] for r in rs)),
                                   "calls_mean": round(statistics.mean(r["model_calls"] for r in rs), 1),
                                   "inr_mean": round(statistics.mean(r["inr"] for r in rs), 3),
                                   "inr_min": min(r["inr"] for r in rs), "inr_max": max(r["inr"] for r in rs)}
by_model = {}
for m in ("gemini-3.8-flash", "gemini-3.5-flash-lite"):
    rs = [r for r in runs if r["model"] == m]
    by_model[m] = {"runs": len(rs), "tokens_in_per_call": round(sum(r["tokens_in"] for r in rs) / sum(r["model_calls"] for r in rs)),
                   "tokens_out_per_call": round(sum(r["tokens_out"] for r in rs) / sum(r["model_calls"] for r in rs)),
                   "out_share_of_cost": round(sum(C.inr(0, r["tokens_out"], m) for r in rs) / sum(r["inr"] for r in rs), 3)}

guard = {}
gp = LOGS / "guard_eval.json"
if gp.exists():
    g = json.loads(gp.read_text())
    for name in ("llamaguard", "safeguard", "nemo_input", "nemo_topic"):
        s = g["guards"].get(name, {})
        guard[name] = {"usd_per_message": s.get("usd_per_message"), "inr_per_message": round((s.get("usd_per_message") or 0) * C.USD_INR, 5),
                       "latency_ms_p50": s.get("latency_ms_p50")}
durable = {}
dp = LOGS / "durable_order.json"
if dp.exists():
    d = json.loads(dp.read_text())
    durable = {"model_calls": d.get("model_calls"), "activities": len(d.get("history", {}).get("activities", [])),
               "events": d.get("history", {}).get("events")}

out = {"date": "2026-10-28", "usd_inr": C.USD_INR, "prices_usd_per_m": C.PRICE, "summary": summ, "by_model": by_model,
       "guard_per_message": guard, "durable": durable, "runs": runs,
       "note": "prices are OpenRouter list prices on 2026-10-28; token counts are from our recorded runs"}
(LOGS / "cost_model.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
(FIX / "cost_runs.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({"summary": summ, "by_model": by_model, "guard": guard, "durable": durable}, indent=1))
