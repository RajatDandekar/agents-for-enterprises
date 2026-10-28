"""Lecture 8 experiment: the same twelve Rasoi tasks (bahi.course.l5.tasks), the same toolbox over MCP (HTTP), the
same model through OpenRouter, the same instructions and step cap; only the framework differs.

    tools/mrun.sh lectures/L8-frameworks/experiments/run_modal.py --script lectures/L8-frameworks/experiments/exp_frameworks.py --args "--fw openai_agents"
    --fw   ours (L5 harness, every part) | bare (L5 harness, only the loop) | openai_agents
           | openai_agents_guarded (+ food-grade tool guardrail, verify output guardrail) | adk | langgraph
           | control (L5 LangGraph control graph)
    --model google/gemini-3.8-flash   --tag _x   --only T01,T04   --workers 6

Writes logs/fw_<fw><tag>.json: per task pass/fail, never-events, failure modes, tokens, ₹ (as OpenRouter billed it),
model seconds, wall seconds, tool calls over MCP, what each framework sent to the model (system prompt and tool
schema bytes), the transcripts, our uniform trace and the framework's own trace. Cassette: IND8_fw_<fw><ctag>.
"""
import argparse
import json
import os
import pathlib
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import httpx  # noqa: F401  import once, before the threads
import openai  # noqa: F401

from bahi.course.frameworks.meter import Meter, billed_inr
from bahi.course.l5.tasks import TASKS, run_task

ap = argparse.ArgumentParser()
ap.add_argument("--fw", default="openai_agents")
ap.add_argument("--model", default="google/gemini-3.8-flash")
ap.add_argument("--tag", default="")       # names the log file
ap.add_argument("--ctag", default="")      # names the cassette (model variants)
ap.add_argument("--only", default="")
ap.add_argument("--workers", type=int, default=6)
a = ap.parse_args()

LOGS = pathlib.Path(__file__).parent / "logs"
LOGS.mkdir(exist_ok=True)
CASSETTE = f"IND8_fw_{a.fw}{a.ctag}"
meter = Meter(cassette=CASSETTE, default_model="openrouter:" + a.model).start()
local = threading.local()
TMP = tempfile.mkdtemp()

if a.fw == "openai_agents":
    from bahi.course.frameworks.openai_agents import RECORDER, AgentsSDKPort  # noqa: F401
elif a.fw == "openai_agents_guarded":
    from bahi.course.frameworks.desks import GuardedAgentsPort
elif a.fw == "adk":
    from bahi.course.frameworks.adk import ADKPort
elif a.fw == "langgraph":
    from bahi.course.frameworks.langgraph_react import LangGraphPort
else:
    from bahi.course.frameworks.ours import graph_port, harness_port


def make(tb):
    tag = f"{a.fw}-{local.task}-{tb.user}"
    if a.fw == "openai_agents":
        ag = AgentsSDKPort(tb, meter, tag, model=a.model, session_db=os.path.join(TMP, tag + ".db"))
    elif a.fw == "openai_agents_guarded":
        ag = GuardedAgentsPort(tb, meter, tag, model=a.model, session_db=os.path.join(TMP, tag + ".db"))
    elif a.fw == "adk":
        ag = ADKPort(tb, meter, tag, model=a.model)
    elif a.fw == "langgraph":
        ag = LangGraphPort(tb, meter, tag, model=a.model)
    elif a.fw == "ours":
        ag = harness_port(tb, cassette=CASSETTE, model=a.model)
    elif a.fw == "bare":
        ag = harness_port(tb, cassette=CASSETTE, model=a.model, parts=())
    elif a.fw == "control":
        ag = graph_port(tb, cassette=CASSETTE, model=a.model)
    else:
        raise SystemExit(f"unknown framework {a.fw}")
    if a.fw in ("ours", "bare", "control"):
        local.agents.append(ag)
    return ag


from bahi.course.frameworks import base as _base  # noqa: E402
_base.ON_CREATE.append(lambda ag: local.agents.append(ag))


def one(task):
    local.task, local.agents = task.id, []
    t0 = time.perf_counter()
    try:
        r = run_task(make, task, persist=a.fw in ("ours", "openai_agents", "openai_agents_guarded"))
    except Exception as e:  # noqa: BLE001
        import traceback
        return {"id": task.id, "name": task.name, "passed": False, "crashed": f"{type(e).__name__}: {e}",
                "trace_err": traceback.format_exc()[-3000:]}
    wall = time.perf_counter() - t0
    # cost and time from the replies themselves (billed ₹ where OpenRouter told us)
    if a.fw in ("ours", "bare", "control"):
        replies = [x for ag in local.agents for x in ag.llm.log]
        shapes = []
    else:
        rows = meter.records(f"{a.fw}-{task.id}-")
        replies = [x for k, v in meter.replies.items() if k.startswith(f"{a.fw}-{task.id}-") for x in v]
        shapes = [{k: row[k] for k in ("messages", "tools", "tools_bytes", "system_bytes", "tokens_in", "tokens_out",
                                       "seconds", "calls")} for row in rows]
    r["cost_inr"] = round(sum(billed_inr(x) for x in replies), 4)
    r["billed"] = sum(1 for x in replies if (x.raw or {}).get("cost_usd") is not None)
    r["model_seconds"] = round(sum(x.seconds for x in replies), 2)
    r["wall_seconds"] = round(wall, 1)
    srvs = {id(getattr(ag, "srv", None) or getattr(getattr(ag, "tb", None), "srv", None)):
            (getattr(ag, "srv", None) or getattr(getattr(ag, "tb", None), "srv", None)) for ag in local.agents}
    tool_ms = [c["ms"] for s in srvs.values() if s is not None for c in s.calls]
    r["mcp_calls"], r["tool_ms"] = len(tool_ms), round(sum(tool_ms), 1)
    r["request_shapes"] = shapes
    r["first_request"] = meter.first.get(f"{a.fw}-{task.id}-KJOSHI") if task.id in ("T03", "T04") else None
    r["guard_log"] = [g for ag in local.agents for g in getattr(ag, "guard_log", [])]
    r["native"] = {getattr(ag, "tag", f"{a.fw}-{i}"): getattr(ag, "native", None) for i, ag in enumerate(local.agents)}
    return r


tasks = [t for t in TASKS if not a.only or t.id in a.only.split(",")]
with ThreadPoolExecutor(a.workers) as ex:
    rows = list(ex.map(one, tasks))

for r in rows:
    if r.get("trace_err"):
        print(f"\n--- {r['id']} CRASHED {r['crashed']}\n{r['trace_err']}")
        continue
    print(f"\n--- {r['id']} {r['name']}: {'PASS' if r['passed'] else 'FAIL'}  {r['note']}  NE={r['never_events']} "
          f"crash={r['crashed']} fail={ {k: v for k, v in r['failures'].items() if v} }  calls={r['model_calls']} "
          f"tok={r['tokens_in']} ₹{r['cost_inr']} wall={r['wall_seconds']}s model={r['model_seconds']}s")
    for t in r["turns"]:
        print(f"  [{t['who']} d{t['day']} {t['kind']}] {t['user'][:120]}\n      -> {(t['agent'] or '')[:300]}")
ok_rows = [r for r in rows if "failures" in r]
fails = {k: sum(1 for r in ok_rows if r["failures"][k]) for k in ok_rows[0]["failures"]} if ok_rows else {}
summ = {"framework": a.fw, "model": a.model, "tasks": len(rows), "passed": sum(bool(r.get("passed")) for r in rows),
        "never_event_tasks": sum(1 for r in ok_rows if r["never_events"]),
        "never_events": [ne for r in ok_rows for ne in r["never_events"]],
        "failure_tasks": fails, "crashed": sum(1 for r in rows if r.get("crashed")),
        "person_messages": sum(r.get("person_messages", 0) for r in ok_rows),
        "model_calls": sum(r.get("model_calls", 0) for r in ok_rows),
        "tool_calls": sum(r.get("mcp_calls", 0) for r in ok_rows),
        "tokens_in": sum(r.get("tokens_in", 0) for r in ok_rows),
        "tokens_out": sum(r.get("tokens_out", 0) for r in ok_rows),
        "model_seconds": round(sum(r.get("model_seconds", 0) for r in ok_rows), 1),
        "wall_seconds": round(sum(r.get("wall_seconds", 0) for r in ok_rows), 1),
        "cost_inr": round(sum(r.get("cost_inr", 0) for r in ok_rows), 3),
        "billed_replies": sum(r.get("billed", 0) for r in ok_rows),
        "replayed": sum(r.get("replayed", 0) for r in ok_rows),
        "mode": os.environ.get("BAHI_LLM_MODE"), "cassette": CASSETTE,
        "per_task": {r["id"]: {"passed": bool(r.get("passed")), "calls": r.get("model_calls"),
                               "tools": r.get("mcp_calls"), "tokens": r.get("tokens_in", 0) + r.get("tokens_out", 0),
                               "inr": r.get("cost_inr"), "wall": r.get("wall_seconds"), "model_s": r.get("model_seconds"),
                               "ne": r.get("never_events"), "crashed": r.get("crashed"),
                               "fail": [k for k, v in (r.get("failures") or {}).items() if v and k not in
                                        ("blocked_by_harness", "verify_sent_back")]} for r in rows}}
try:
    import importlib.metadata as md
    summ["versions"] = {p: md.version(p) for p in ("openai-agents", "google-adk", "litellm", "langgraph",
                                                    "langchain-openai", "langchain-mcp-adapters", "fastmcp", "mcp",
                                                    "openai")}
except Exception:
    pass
print("\nSUMMARY", json.dumps({k: v for k, v in summ.items() if k != "per_task"}))
out = LOGS / f"fw_{a.fw}{a.tag}{('_' + a.only.replace(',', '_')) if a.only else ''}.json"
out.write_text(json.dumps({"summary": summ, "results": rows}, indent=1, default=str, ensure_ascii=False))
print("wrote", out.name)
meter.stop()
sys.stdout.flush()
os._exit(0)  # daemon servers and loops: do not wait for them
