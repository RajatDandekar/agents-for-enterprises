"""Lecture 4 experiment: free tool loop vs control graph on 40 multi-step cases (gemini-3.8-flash).

    modal run tools/modal_run.py --script lectures/L4-the-route/experiments/exp40.py --args "--agent graph"
    modal run tools/modal_run.py --script lectures/L4-the-route/experiments/exp40.py --args "--agent loop"

Same model, same Lecture 3 intent tools (CORE + EXTRA), same policy search. Only the control differs.
Writes logs/forty_<agent>.json: per case pass/fail, never-events, transcript, model calls, tool calls, ERP services,
tokens, model seconds and ₹; and a summary.
"""
import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from cases40 import CASES  # noqa: E402
from l4lib import MODEL, dump, make_graph, make_loop, run_many  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--agent", default="graph")
ap.add_argument("--only", default="")
ap.add_argument("--workers", type=int, default=8)
ap.add_argument("--model", default=MODEL)
ap.add_argument("--tag", default="", help="suffix for the log and cassette, e.g. _lite")
a = ap.parse_args()
LOGS = pathlib.Path(__file__).parent / "logs"
LOGS.mkdir(exist_ok=True)
cases = [c for c in CASES if not a.only or c.id in a.only.split(",")]
make = (make_graph("L4_graph40" + a.tag, a.model) if a.agent == "graph" else make_loop("L4_loop40" + a.tag, a.model))
rows = run_many(make, cases, workers=a.workers)
for r in rows:
    print(f"\n--- {r['id']} {r['name']}: {'PASS' if r['passed'] else 'FAIL'} {r['never_events']} {r['note']} {r['crashed']}")
    for t in r["turns"]:
        print(f"K: {t['user']}\nA: {t['agent'][:700]}\n   writes: {t['writes']}")
    if r.get("path"):
        print("PATH:", " > ".join(r["path"]))
n = len(rows)
summ = {"agent": a.agent, "model": a.model, "cases": n, "passed": sum(r["passed"] for r in rows),
        "never_event_cases": sum(1 for r in rows if r["never_events"]),
        "never_events": sorted({ne.split()[0] for r in rows for ne in r["never_events"]}),
        "never_event_count": {k: sum(1 for r in rows for ne in r["never_events"] if ne.startswith(k))
                              for k in ("NE1", "NE2", "NE3", "NE4", "NE5")},
        "crashed": sum(1 for r in rows if r["crashed"]),
        "model_calls": sum(r["model_calls"] for r in rows), "tool_calls": sum(r["tool_calls"] for r in rows),
        "services": sum(r["services"] for r in rows), "turns": sum(len(r["turns"]) for r in rows),
        "tokens_in": sum(r["tokens_in"] for r in rows), "tokens_out": sum(r["tokens_out"] for r in rows),
        "seconds": round(sum(r["seconds"] for r in rows), 1), "cost_inr": round(sum(r["cost_inr"] for r in rows), 3),
        "by_family": {}}
for fam in dict.fromkeys(r["family"] for r in rows):
    fr = [r for r in rows if r["family"] == fam]
    summ["by_family"][fam] = {"cases": len(fr), "passed": sum(r["passed"] for r in fr)}
print("\nSUMMARY", summ)
dump(LOGS / f"forty_{a.agent}{a.tag}.json", {"summary": summ, "results": rows})
