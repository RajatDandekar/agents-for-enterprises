"""Lecture 6, experiment (e): run to run. The same 15 cases, three more times, on the graph and on the tool loop.

    modal run tools/modal_run.py --script lectures/L6-the-inspector/experiments/variance.py

Each repeat has its own cassettes (L6_var_<agent>_r<k>, and L6_var_sim_<agent>_r<k> for Kavita), so every model call
is made fresh; repeat 0 is the main run (logs/suite_<agent>.json). Writes logs/variance.json.
"""
import json
import pathlib

from bahi.evals import runner, suite
from bahi.evals.agents import FLASH, GraphFactory, LoopFactory

IDS = ["S1", "S2", "S3", "S4", "S5", "S6", "G03", "G10", "G15", "V04", "V10", "A01", "A03", "M03", "M05"]
LOGS = pathlib.Path(__file__).parent / "logs"
cases = [suite.BY_ID[i] for i in IDS]
out = {"cases": IDS, "agents": {}}
for agent in ("graph", "loop"):
    main = json.loads((LOGS / f"suite_{agent}.json").read_text())
    by = {r["id"]: r for r in main["cases"]}
    runs = [{i: {"passed": by[i]["passed"], "failed": [m for m, v in by[i]["metrics"].items() if v["ok"] is False],
                 "ne": by[i]["never_events"], "inr": by[i]["totals"]["inr"], "seconds": by[i]["totals"]["seconds"]} for i in IDS}]
    for k in (1, 2, 3):
        fac = (GraphFactory(FLASH, f"L6_var_{agent}_r{k}") if agent == "graph" else LoopFactory(FLASH, f"L6_var_{agent}_r{k}"))
        run = runner.run_suite(fac, cases, sim="llm", sim_cassette=f"L6_var_sim_{agent}_r{k}", workers=15)
        runs.append({r["id"]: {"passed": r["passed"], "failed": [m for m, v in r["metrics"].items() if v["ok"] is False],
                               "ne": r["never_events"], "inr": r["totals"]["inr"], "seconds": r["totals"]["seconds"],
                               "last": r["turns"][-1]["agent"][:400] if r["turns"] else ""} for r in run["cases"]})
        print(agent, "repeat", k, run["summary"]["passed"], "/", len(IDS), "₹", run["summary"]["inr"])
    per_case = {i: [r[i]["passed"] for r in runs] for i in IDS}
    flipped = [i for i, v in per_case.items() if len(set(v)) > 1]
    out["agents"][agent] = {"runs": runs, "per_case": per_case, "passes_per_run": [sum(r[i]["passed"] for i in IDS) for r in runs],
                            "flipped": flipped, "inr": round(sum(r[i]["inr"] for r in runs[1:] for i in IDS), 3)}
    print(agent, "passes per run", out["agents"][agent]["passes_per_run"], "flipped", flipped)
(LOGS / "variance.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
