"""Lecture 6, experiments (a), (b) and (e): run the 60-case suite on one agent and log everything.

    modal run tools/modal_run.py --script lectures/L6-the-inspector/experiments/run_suite.py --args "--agent graph --tag graph"
    ... --args "--agent loop --tag loop"
    ... --args "--agent naive --tag naive"
    ... --args "--agent graph --words gemini:gemini-3.1-pro-preview --route gemini:gemini-3.1-pro-preview --fill gemini:gemini-3.1-pro-preview --tag tier_pro"
    ... --args "--agent graph --words gemini:gemini-3.1-pro-preview --route gemini:gemini-3.5-flash-lite --fill gemini:gemini-3.5-flash-lite --tag tier_mix"

Writes logs/suite_<tag>.json (summary + every case: transcript, metrics, never-events, ERP orders, spans, totals)
and logs/traces_<tag>.jsonl (the local trace store). Cassettes: L6_<tag> for the agent, L6_sim_<tag> for Kavita
(L6_sim for the main graph run), so parallel Modal jobs never write the same cassette.
"""
import argparse
import json
import os
import pathlib
import time

from bahi.evals import runner, suite
from bahi.evals.agents import FLASH, GraphFactory, LoopFactory, NaiveFactory
from bahi.evals.trace import TraceStore, export_langfuse, langfuse_ready

ap = argparse.ArgumentParser()
ap.add_argument("--agent", default="graph")
ap.add_argument("--model", default=FLASH)
ap.add_argument("--words", default="")
ap.add_argument("--route", default="")
ap.add_argument("--fill", default="")
ap.add_argument("--tag", default="graph")
ap.add_argument("--cases", default="all")
ap.add_argument("--sim", default="llm")
ap.add_argument("--sim-cassette", default="")
ap.add_argument("--cassette", default="")
ap.add_argument("--workers", type=int, default=8)
a = ap.parse_args()

LOGS = pathlib.Path(__file__).parent / "logs"
LOGS.mkdir(exist_ok=True)
cas = a.cassette or ("L6_" + a.tag)
simcas = a.sim_cassette or ("L6_sim" if a.tag == "graph" else "L6_sim_" + a.tag)
if a.agent == "graph":
    fac = GraphFactory(a.model, cas, words=a.words or None, route=a.route or None, fill=a.fill or None)
elif a.agent == "loop":
    fac = LoopFactory(a.model, cas)
else:
    fac = NaiveFactory(a.model, cas)
cases = suite.select(a.cases)
t0 = time.time()
run = runner.run_suite(fac, cases, sim=a.sim, sim_cassette=simcas, workers=a.workers,
                       meta={"tag": a.tag, "mode": os.environ.get("BAHI_LLM_MODE", "auto")})
run["meta"]["wall_seconds"] = round(time.time() - t0, 1)
ok, why = langfuse_ready()
run["meta"]["langfuse"] = export_langfuse(run["cases"], run["meta"]) if ok else {"exported": 0, "reason": why}
out = runner.slim(run)
(LOGS / f"suite_{a.tag}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
TraceStore(LOGS / f"traces_{a.tag}.jsonl").write(run["meta"], out["cases"])

for r in out["cases"]:
    bad = {k: v["why"] for k, v in r["metrics"].items() if v["ok"] is False}
    print(f"\n--- {r['id']} {r['name']}: {'PASS' if r['passed'] else 'FAIL'} {r['never_events']} {bad} {r['crashed']}")
    for t in r["turns"]:
        print(f"K[{t['act']}]: {t['user'][:300]}\nA: {t['agent'][:600]}\n   writes: {t['writes']}")
s = out["summary"]
print("\nSUMMARY", json.dumps({k: v for k, v in s.items() if k != "by"}, default=str))
print("BY", json.dumps(s["by"]))
print("LANGFUSE", run["meta"]["langfuse"])
