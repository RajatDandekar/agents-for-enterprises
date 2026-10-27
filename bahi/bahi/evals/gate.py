"""Lecture 6: the regression gate. A change ships only if the suite says so.

    python -m bahi.evals.gate --agent graph --baseline lectures/L6-the-inspector/experiments/logs/baseline_graph.json
    python -m bahi.evals.gate --results candidate.json --baseline baseline.json        # gate a run you already have
    python -m bahi.evals.gate --agent graph --save baseline.json --min-pass 0.9         # record a new baseline

Rules (any one fails the gate, exit code 1):
    1. any never-event in any case
    2. pass rate below the baseline's, minus --tolerance (default 0: not one case fewer)
    3. pass rate below --min-pass (default 0)
    4. with --strict: any case that passed in the baseline and fails now
The report also lists what changed between the two runs' fingerprints: prompts, tools, models, route, suite.
In replay mode (BAHI_LLM_MODE=replay) the gate needs no key: every model reply comes from the cassettes.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

from . import versions


def evaluate(candidate: dict, baseline: dict | None = None, tolerance: float = 0.0, min_pass: float = 0.0,
             strict: bool = False) -> dict:
    cs = candidate["summary"]
    reasons = []
    ne_cases = [r["id"] + " " + "; ".join(x.split(" ")[0] for x in r["never_events"]) for r in candidate["cases"] if r["never_events"]]
    if ne_cases:
        reasons.append(f"never-event in {len(ne_cases)} case(s): " + ", ".join(ne_cases))
    if cs["pass_rate"] < min_pass:
        reasons.append(f"pass rate {cs['pass_rate']:.1%} is below the bar {min_pass:.0%}")
    newly_failing, newly_passing, changes = [], [], []
    if baseline:
        bs = baseline["summary"]
        if cs["pass_rate"] < bs["pass_rate"] - tolerance - 1e-9:
            reasons.append(f"pass rate dropped: {cs['passed']}/{cs['cases']} ({cs['pass_rate']:.1%}) against the baseline's "
                           f"{bs['passed']}/{bs['cases']} ({bs['pass_rate']:.1%})")
        b = {r["id"]: r["passed"] for r in baseline["cases"]}
        c = {r["id"]: r["passed"] for r in candidate["cases"]}
        newly_failing = sorted(i for i in c if b.get(i) and not c[i])
        newly_passing = sorted(i for i in c if b.get(i) is False and c[i])
        if strict and newly_failing:
            reasons.append("cases that passed before and fail now: " + ", ".join(newly_failing))
        bv, cv = dict(baseline["meta"].get("versions", {})), dict(candidate["meta"].get("versions", {}))
        if set(c) < set(b):            # a subset of the suite: its hash differs by construction
            bv.pop("suite", None), cv.pop("suite", None)
        changes = versions.diff(bv, cv)
    return {"passed": not reasons, "reasons": reasons, "candidate": {k: cs[k] for k in ("cases", "passed", "pass_rate", "ci95",
            "never_event_cases")}, "baseline": {k: baseline["summary"][k] for k in ("cases", "passed", "pass_rate", "ci95")}
            if baseline else None, "newly_failing": newly_failing, "newly_passing": newly_passing, "changes": changes}


def report(g: dict) -> str:
    c = g["candidate"]
    lines = [f"{'PASS' if g['passed'] else 'FAIL'} · candidate {c['passed']}/{c['cases']} = {c['pass_rate']:.1%} "
             f"(95% interval {c['ci95'][0]:.0%}–{c['ci95'][1]:.0%}) · cases with a never-event: {c['never_event_cases']}"]
    if g["baseline"]:
        b = g["baseline"]
        lines.append(f"       baseline  {b['passed']}/{b['cases']} = {b['pass_rate']:.1%}")
    for r in g["reasons"]:
        lines.append("  ✗ " + r)
    if g["newly_failing"]:
        lines.append("  newly failing: " + ", ".join(g["newly_failing"]))
    if g["newly_passing"]:
        lines.append("  newly passing: " + ", ".join(g["newly_passing"]))
    if g["changes"]:
        lines.append("  what changed since the baseline:")
        lines += ["    " + x for x in g["changes"][:20]]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m bahi.evals.gate", description="Run the Lecture 6 suite and gate a change.")
    ap.add_argument("--agent", default="graph", help="graph | loop | naive | graph:words=..,route=..,fill=.. | py:pkg.mod:make_agent")
    ap.add_argument("--model", default="gemini:gemini-3.8-flash")
    ap.add_argument("--cassette", default="", help="model cassette (default L6_graph / L6_loop / L6_naive)")
    ap.add_argument("--cases", default="all", help="all | a family (G V N S A M) | a kind | ids like S1,S2")
    ap.add_argument("--sim", default="llm", choices=["llm", "scripted"])
    ap.add_argument("--sim-cassette", default="L6_sim")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--results", default="", help="gate an existing results file instead of running")
    ap.add_argument("--baseline", default="")
    ap.add_argument("--save", default="", help="write the candidate run here")
    ap.add_argument("--tolerance", type=float, default=0.0)
    ap.add_argument("--min-pass", type=float, default=0.0)
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--json", default="", help="write the gate verdict here")
    a = ap.parse_args(argv)

    if a.results:
        cand = json.loads(pathlib.Path(a.results).read_text())
    else:
        from .agents import factory
        from .runner import run_suite, slim
        from .suite import select
        fac = factory(a.agent, a.cassette, a.model)
        cand = slim(run_suite(fac, select(a.cases), sim=a.sim, sim_cassette=a.sim_cassette, workers=a.workers,
                              meta={"mode": os.environ.get("BAHI_LLM_MODE", "auto")}), keep_spans=False)
    if a.save:
        pathlib.Path(a.save).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(a.save).write_text(json.dumps(cand, indent=1, ensure_ascii=False, default=str))
    base = json.loads(pathlib.Path(a.baseline).read_text()) if a.baseline else None
    if base and not a.results and a.cases != "all":
        ids = {r["id"] for r in cand["cases"]}
        base = {**base, "cases": [r for r in base["cases"] if r["id"] in ids]}
        from .runner import summarise
        base["summary"] = summarise(base["cases"]) if base["cases"] and "totals" in base["cases"][0] else base["summary"]
        # a subset of the suite has its own hash by construction: compare everything else
        base["meta"] = {**base["meta"], "versions": {k: v for k, v in base["meta"].get("versions", {}).items() if k != "suite"}}
        cand["meta"] = {**cand["meta"], "versions": {k: v for k, v in cand["meta"].get("versions", {}).items() if k != "suite"}}
    g = evaluate(cand, base, a.tolerance, a.min_pass, a.strict)
    print(report(g))
    if a.json:
        pathlib.Path(a.json).write_text(json.dumps(g, indent=1))
    sys.exit(0 if g["passed"] else 1)


if __name__ == "__main__":
    main()
