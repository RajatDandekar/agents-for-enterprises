"""Lecture 5 experiment: the same twelve Rasoi tasks, the same toolbox (v3, 15 tools), the same model; only the
harness differs.

    modal run tools/modal_run.py --script lectures/L5-the-loop/experiments/exp_tasks.py --args "--agent harness"
    agents: hands (L4: one tool round per message) · react (text ReAct, our parser) · bare (native loop, nothing else)
            prompt (native loop + the full system prompt) · harness (every part) · graph (LangGraph control graph)
    --nudge   the person says "OK. Please do the next step." when the agent stops early (counts messages needed)
    --only T01,T04   --model gemini:gemini-3.5-flash-lite --tag _lite

Writes logs/tasks_<agent><tag>.json: per task pass/fail, never-events, failure modes, person messages, model calls,
tool calls, tokens, ₹, and the full transcripts and traces (for the deck's scrubbers).
"""
import argparse
import json
import pathlib
from concurrent.futures import ThreadPoolExecutor

import httpx  # noqa: F401  import once, before the threads (a parallel first import of httpx races)
import openai  # noqa: F401

from bahi.course.l5 import Harness, OneRound, ReActAgent
from bahi.course.l5.graph import ControlGraph
from bahi.course.l5.tasks import TASKS, run_task
from bahi.llm import LLM

ap = argparse.ArgumentParser()
ap.add_argument("--agent", default="harness")
ap.add_argument("--model", default="gemini:gemini-3.8-flash")
ap.add_argument("--tag", default="")
ap.add_argument("--only", default="")
ap.add_argument("--nudge", action="store_true")
ap.add_argument("--workers", type=int, default=6)
a = ap.parse_args()

LOGS = pathlib.Path(__file__).parent / "logs"
LOGS.mkdir(exist_ok=True)
cassette = f"L5v3_exp_{a.agent}{a.tag}"


def make(tb):
    llm = LLM(a.model, cassette=cassette)
    if a.agent == "hands":
        return OneRound(tb, llm)
    if a.agent == "react":
        return ReActAgent(tb, llm)
    if a.agent == "bare":
        return Harness(tb, llm, parts=())
    if a.agent == "prompt":
        return Harness(tb, llm, parts=("prompt",))
    if a.agent == "harness":
        return Harness(tb, llm)
    if a.agent == "graph":
        return ControlGraph(tb, llm)
    raise SystemExit(f"unknown agent {a.agent}")


tasks = [t for t in TASKS if not a.only or t.id in a.only.split(",")]
with ThreadPoolExecutor(a.workers) as ex:
    rows = list(ex.map(lambda t: run_task(make, t, nudge=a.nudge, persist=(a.agent == "harness")), tasks))

for r in rows:
    print(f"\n--- {r['id']} {r['name']}: {'PASS' if r['passed'] else 'FAIL'}  {r['note']}  NE={r['never_events']} "
          f"fail={ {k: v for k, v in r['failures'].items() if v} }  calls={r['model_calls']} tok={r['tokens_in']}")
    for t in r["turns"]:
        print(f"  [{t['who']} d{t['day']} {t['kind']}] {t['user'][:140]}\n      -> {(t['agent'] or '')[:400]}")
n = len(rows)
fails = {k: sum(1 for r in rows if r["failures"][k]) for k in rows[0]["failures"]} if rows else {}
summ = {"agent": a.agent, "model": a.model, "tasks": n, "passed": sum(r["passed"] for r in rows),
        "never_event_tasks": sum(1 for r in rows if r["never_events"]),
        "never_events": [ne for r in rows for ne in r["never_events"]],
        "failure_tasks": fails, "crashed": sum(1 for r in rows if r["crashed"]),
        "person_messages": sum(r["person_messages"] for r in rows), "nudges": sum(r["nudges"] for r in rows),
        "model_calls": sum(r["model_calls"] for r in rows), "tool_calls": sum(r["tool_calls"] for r in rows),
        "tokens_in": sum(r["tokens_in"] for r in rows), "tokens_out": sum(r["tokens_out"] for r in rows),
        "seconds": round(sum(r["seconds"] for r in rows), 1), "cost_inr": round(sum(r["cost_inr"] for r in rows), 3),
        "replayed": sum(r["replayed"] for r in rows), "nudge": a.nudge,
        "per_task": {r["id"]: {"passed": r["passed"], "calls": r["model_calls"], "tools": r["tool_calls"],
                               "tokens": r["tokens_in"] + r["tokens_out"], "msgs": r["person_messages"],
                               "fail": [k for k, v in r["failures"].items() if v and k not in
                                        ("blocked_by_harness", "verify_sent_back")]} for r in rows}}
print("\nSUMMARY", json.dumps({k: v for k, v in summ.items() if k != "per_task"}))
out = LOGS / f"tasks_{a.agent}{a.tag}{'_nudge' if a.nudge else ''}{('_' + a.only.replace(',', '_')) if a.only else ''}.json"
out.write_text(json.dumps({"summary": summ, "results": rows}, indent=1, default=str, ensure_ascii=False))
print("wrote", out.name)
