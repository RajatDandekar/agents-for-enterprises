"""Lecture 4 experiment: raw services or one tool per business activity?

Two agents on the same 30 tasks (tasks.py, reused from v2 L3 with two lookups swapped), same model, same simple loop
(bahi.agent.loop.ToolLoopAgent: call tools until the model answers in words, max 20 steps; Lecture 5 builds this
loop properly), same system prompt, both in Kavita's own Bahi session:
  raw      Bahi's 41 raw services as tools, described as Bahi's service catalogue describes them
  toolbox  the 15 toolbox tools (bahi/bahi/toolbox/*/tool.json + tool.py)
Code checks the ERP's final state and the never-events (NE2 two live orders, NE4 duplicate supplier, NE5 "done" when
the order is not released). Rohit approves whatever the conversation sends him; "Yes, go ahead" when asked.

    modal run tools/modal_run.py --script lectures/L4-the-hands/experiments/granularity.py --args "--model gemini:gemini-3.8-flash"
Writes logs/granularity_<model>.json; cassette L4v3_granularity (L4v3_granularity_lite for flash-lite).
"""
import argparse
import json
import pathlib
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from bahi.agent.loop import ToolLoopAgent  # noqa: E402
from bahi.agent.tools import RawServiceTools  # noqa: E402
from bahi.llm import LLM  # noqa: E402
from bahi.toolbox import Toolbox  # noqa: E402
from tasks import TASKS, run_task  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="gemini:gemini-3.8-flash")
ap.add_argument("--cassette", default="")
ap.add_argument("--configs", default="raw,toolbox")
ap.add_argument("--only", default="")
ap.add_argument("--workers", type=int, default=16)
a = ap.parse_args()
cassette = a.cassette or ("L4v3_granularity_lite" if "lite" in a.model else "L4v3_granularity")


def maker(config):
    def make(erp, user):
        llm = LLM(a.model, cassette=cassette)
        tools = RawServiceTools(erp.session(user)) if config == "raw" else Toolbox(erp, user)
        return ToolLoopAgent(erp, user, llm=llm, tools=tools)
    return make


def job(config, task):
    r = run_task(task, maker(config))
    r["config"] = config
    print(f"{config:8s} {task.id} {'pass' if r['passed'] else 'FAIL'} calls={r['tool_calls']:3d} "
          f"tok={r['tokens_in'] + r['tokens_out']:7d} {r['note'][:70]} {r['never_events']} {r['error'] or ''}", flush=True)
    return r


tasks = [t for t in TASKS if not a.only or t.id in a.only.split(",")]
configs = a.configs.split(",")
t0 = time.time()
with ThreadPoolExecutor(a.workers) as ex:
    results = list(ex.map(lambda ct: job(*ct), [(c, t) for c in configs for t in tasks]))


def summary(rs):
    n = len(rs) or 1
    return {"tasks": len(rs), "passed": sum(r["passed"] for r in rs), "success": round(sum(r["passed"] for r in rs) / n, 3),
            "never_events": sum(len(r["never_events"]) for r in rs), "errors": sum(1 for r in rs if r["error"]),
            "tool_calls_mean": round(sum(r["tool_calls"] for r in rs) / n, 2),
            "services_mean": round(sum(r["services"] for r in rs) / n, 2),
            "failed_services_total": sum(r["failed_services"] for r in rs),
            "failed_services_mean": round(sum(r["failed_services"] for r in rs) / n, 2),
            "tokens_mean": round(sum(r["tokens_in"] + r["tokens_out"] for r in rs) / n),
            "tokens_in_mean": round(sum(r["tokens_in"] for r in rs) / n),
            "seconds_mean": round(sum(r["seconds"] for r in rs) / n, 2),
            "inr_mean": round(sum(r["cost_inr"] for r in rs) / n, 4), "inr_total": round(sum(r["cost_inr"] for r in rs), 3)}


out = {"model": a.model, "cassette": cassette, "wall_seconds": round(time.time() - t0),
       "configs": {c: {k: summary([r for r in results if r["config"] == c and (k == "all" or r["kind"] == k)])
                       for k in ("all", "lookup", "action")} for c in configs},
       "tasks": [{"id": t.id, "kind": t.kind, "ask": t.ask, "trap": t.trap} for t in tasks], "results": results}
name = f"granularity_{a.model.replace(':', '_')}" + (f"_{a.only.replace(',', '-')}" if a.only else "")
(HERE / "logs" / f"{name}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
for c in configs:
    print(c, json.dumps(out["configs"][c]["all"]))
