"""Lecture 3 experiment: how big should a tool be?

Four agents on the same 30 tasks (tasks.py), same model, same loop (ToolLoopAgent), all in Kavita's own session:
  raw      38 raw Bahi services as tools                                   (finest)
  generic  one call_service(name, payload) tool, the catalogue in its description   (coarsest)
  intent   8 intent tools (bahi.agent.tools.CORE), our harness's system prompt
  host     the same 8 tools discovered over MCP by a generic client with a generic system prompt (a marketplace host)

    python granularity.py --model gemini:gemini-3.8-flash --cassette L3_granularity
Writes logs/granularity_<model>.json
"""
import argparse
import json
import pathlib
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "bahi"))
sys.path.insert(0, str(HERE))

from bahi.agent.loop import GENERIC_SYSTEM, SYSTEM, ToolLoopAgent  # noqa: E402
from bahi.agent.tools import CORE, GenericServiceTool, IntentTools, RawServiceTools  # noqa: E402
from bahi.llm import LLM  # noqa: E402
from tasks import TASKS, run_task  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="gemini:gemini-3.8-flash")
ap.add_argument("--cassette", default="L3_granularity")
ap.add_argument("--configs", default="raw,generic,intent,host")
ap.add_argument("--only", default="")
ap.add_argument("--workers", type=int, default=12)
a = ap.parse_args()
LOG = HERE / "logs"
LOG.mkdir(exist_ok=True)


def maker(config):
    def make(erp, user):
        llm = LLM(a.model, cassette=a.cassette)
        s = erp.session(user)
        if config == "raw":
            return ToolLoopAgent(erp, user, llm=llm, tools=RawServiceTools(s))
        if config == "generic":
            return ToolLoopAgent(erp, user, llm=llm, tools=GenericServiceTool(s))
        if config == "intent":
            return ToolLoopAgent(erp, user, llm=llm, tools=IntentTools(s, CORE))
        from bahi.mcp_server import MCPClient, MCPClientTools, build_bahi_server
        return ToolLoopAgent(erp, user, llm=llm, tools=MCPClientTools(MCPClient(build_bahi_server(erp, user, CORE))),
                             system=GENERIC_SYSTEM)
    return make


def job(config, task):
    agents = []

    def mk(erp, user):
        agents.append(maker(config)(erp, user))
        return agents[-1]

    r = run_task(task, mk)
    if agents and hasattr(agents[0].tools, "close"):
        agents[0].tools.close()
    r["config"] = config
    print(f"{config:8s} {task.id} {'pass' if r['passed'] else 'FAIL'} calls={r['tool_calls']:3d} tok={r['tokens_in'] + r['tokens_out']:7d} "
          f"{r['note'][:60]} {r['never_events']} {r['error'] or ''}", flush=True)
    return r


tasks = [t for t in TASKS if not a.only or t.id in a.only.split(",")]
configs = a.configs.split(",")
t0 = time.time()
with ThreadPoolExecutor(a.workers) as ex:
    results = list(ex.map(lambda ct: job(*ct), [(c, t) for c in configs for t in tasks]))


def summary(rs):
    n = len(rs)
    return {"tasks": n, "passed": sum(r["passed"] for r in rs), "success": round(sum(r["passed"] for r in rs) / n, 3),
            "never_events": sum(len(r["never_events"]) for r in rs),
            "errors": sum(1 for r in rs if r["error"]),
            "tool_calls_mean": round(sum(r["tool_calls"] for r in rs) / n, 2),
            "services_mean": round(sum(r["services"] for r in rs) / n, 2),
            "failed_services_mean": round(sum(r["failed_services"] for r in rs) / n, 2),
            "tokens_mean": round(sum(r["tokens_in"] + r["tokens_out"] for r in rs) / n),
            "tokens_in_mean": round(sum(r["tokens_in"] for r in rs) / n),
            "seconds_mean": round(sum(r["seconds"] for r in rs) / n, 2),
            "inr_mean": round(sum(r["cost_inr"] for r in rs) / n, 4),
            "inr_total": round(sum(r["cost_inr"] for r in rs), 3)}


out = {"model": a.model, "cassette": a.cassette, "wall_seconds": round(time.time() - t0),
       "configs": {c: {"all": summary([r for r in results if r["config"] == c]),
                       "lookup": summary([r for r in results if r["config"] == c and r["kind"] == "lookup"]),
                       "action": summary([r for r in results if r["config"] == c and r["kind"] == "action"])}
                   for c in configs},
       "tasks": [{"id": t.id, "kind": t.kind, "ask": t.ask, "trap": t.trap} for t in tasks],
       "results": results}
name = f"granularity_{a.model.replace(':', '_')}" + (f"_{a.only.replace(',', '-')}" if a.only else "")
(LOG / f"{name}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
for c in configs:
    print(c, json.dumps(out["configs"][c]["all"]))
