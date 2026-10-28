"""Lecture 6, experiment (d): test the tests. The suite on the reference graph and on ten deliberately broken bots.

    modal run tools/modal_run.py --script lectures/L6-the-inspector/experiments/run_bots.py --args "--bots reference,curt_tone --tag 0"
    modal run tools/modal_run.py --script lectures/L6-the-inspector/experiments/run_bots.py --args "--bots skips_approval,double_writes,never_asks --tag 1"
    ...
Scripted Kavita (deterministic), gemini-3.8-flash, cassette L6_bots_<tag>. Writes logs/bots_<tag>.json: per bot, per
case, which metrics failed and which never-events fired. bots_matrix.py combines the parts into the matrix.
"""
import argparse
import json
import pathlib

from bahi.evals import runner, suite
from bahi.evals.agents import FLASH, GraphFactory
from bahi.evals.broken import BOTS, bot_factory

ap = argparse.ArgumentParser()
ap.add_argument("--bots", default="reference")
ap.add_argument("--tag", default="0")
ap.add_argument("--cases", default="all")
ap.add_argument("--workers", type=int, default=12)
a = ap.parse_args()
LOGS = pathlib.Path(__file__).parent / "logs"
cas = f"L6_bots_{a.tag}"
out = {}
for name in a.bots.split(","):
    fac = GraphFactory(FLASH, cas, name="reference") if name == "reference" else bot_factory(name, cassette=cas)
    run = runner.run_suite(fac, suite.select(a.cases), sim="scripted", workers=a.workers, meta={"bot": name})
    out[name] = {"what": "Lecture 4 graph, unbroken" if name == "reference" else BOTS[name][1],
                 "targets": [] if name == "reference" else BOTS[name][2], "summary": run["summary"],
                 "cases": [{"id": r["id"], "passed": r["passed"], "crashed": r["crashed"],
                            "failed": [m for m, v in r["metrics"].items() if v["ok"] is False],
                            "why": {m: v["why"] for m, v in r["metrics"].items() if v["ok"] is False},
                            "ne": [x.split(" ")[0] for x in r["never_events"]], "ne_full": r["never_events"],
                            "turns": [{"user": t["user"], "act": t["act"], "agent": t["agent"], "writes": t["writes"]}
                                      for t in r["turns"]], "orders": r.get("orders", []),
                            "inr": r["totals"]["inr"]} for r in run["cases"]]}
    s = run["summary"]
    print(f"{name}: {s['passed']}/{s['cases']} · NE {s['never_events']} · metric failures {s['metric_failures']} · ₹{s['inr']}")
(LOGS / f"bots_{a.tag}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
