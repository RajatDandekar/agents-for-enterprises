"""Demo day: run a module's hidden demo-day test on an agent and print the 6 points it earns. On Modal:

    /Users/raj/.venv/bin/modal run tools/modal_run.py --script lectures/L8-your-module/experiments/grade_change.py \
        --args "--module hr_leave --agent py:student_pkg.agent:make_agent" --mode replay
    ... --args "--module hr_leave --agent reference"      # the scripted careful run (NEW): proves the grader itself works
    ... --args "--module all --agent reference"

--agent is a make_agent(erp, user) importable as py:package.module:function (the same spec bahi.evals.gate takes),
or 'reference' / 'friday' / 'naive' for the scripted runs in demo_change.py. Writes logs/grade_<module>_<agent>.json.
The other 4 points of the change (document in the corpus, rule named) are judged by hand from the transcript.
"""
from __future__ import annotations

import argparse
import importlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
COURSE = HERE.parents[2]
sys.path.insert(0, str(COURSE / "bahi"))
sys.path.insert(0, str(COURSE / "modules"))

from demo_day import load_change, run_change  # noqa: E402

from bahi.modules._kit import KITS, scripted  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--module", required=True)
ap.add_argument("--agent", default="reference")
a = ap.parse_args()


def make(ch, spec):
    if spec == "reference":
        return scripted(ch.NEW)
    if spec == "friday":
        return scripted(ch.OLD)
    if spec == "naive":
        return scripted(ch.NAIVE, getattr(ch, "NAIVE_RUN_AS", None))
    mod, fn = spec.removeprefix("py:").rsplit(":", 1)
    return getattr(importlib.import_module(mod), fn)


out = {}
for m in (KITS if a.module == "all" else a.module.split(",")):
    ch = load_change(m)
    r = run_change(make(ch, a.agent), m, ch)
    pts = 6 if r.passed else 0
    out[m] = {"change": ch.CHANGE["id"], "passed": r.passed, "points_hidden_test": pts, "never_events": r.never_events,
              "notes": r.notes, "tokens": r.tokens_in + r.tokens_out, "inr": r.cost_inr, "seconds": r.seconds,
              "turns": [{"user": t["user"], "agent": t["agent"], "writes": t["writes"], "as": t.get("users")} for t in r.turns]}
    print(f"{m:16s} {ch.CHANGE['id']:16s} {'PASS' if r.passed else 'FAIL'}  {pts}/6  {r.never_events} {r.notes}")
tag = a.agent.split(":")[-1]
(HERE / "logs").mkdir(exist_ok=True)
(HERE / "logs" / f"grade_{a.module.replace(',', '_')}_{tag}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
