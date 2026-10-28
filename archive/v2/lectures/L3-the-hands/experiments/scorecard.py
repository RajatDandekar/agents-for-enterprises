"""Lecture 3 scorecard: the six course scenarios with this lecture's layer.

  harness   ToolLoopAgent + the 8 intent tools, in Kavita's session, our system prompt   (the Lecture 3 agent)
  host      the same 8 tools over MCP, a generic client and a generic system prompt     (a marketplace host)

    python scorecard.py --models gemini:gemini-3.8-flash          (cassette L3_scorecard)
Writes logs/scorecard_<model>.json
"""
import argparse
import json
import pathlib
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "bahi"))

from bahi.agent.loop import GENERIC_SYSTEM, ToolLoopAgent  # noqa: E402
from bahi.agent.tools import CORE, IntentTools  # noqa: E402
from bahi.llm import LLM  # noqa: E402
from bahi.mcp_server import MCPClient, MCPClientTools, build_bahi_server  # noqa: E402
from bahi.scenarios import SCENARIOS, run_scenario  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--models", default="gemini:gemini-3.8-flash")
ap.add_argument("--configs", default="harness,host")
a = ap.parse_args()
LOG = HERE / "logs"
LOG.mkdir(exist_ok=True)


def job(model, config, sc):
    made = []

    def make(erp, user):
        llm = LLM(model, cassette="L3_scorecard")
        if config == "harness":
            ag = ToolLoopAgent(erp, user, llm=llm, tools=IntentTools(erp.session(user), CORE))
        else:
            ag = ToolLoopAgent(erp, user, llm=llm, tools=MCPClientTools(MCPClient(build_bahi_server(erp, user, CORE))),
                               system=GENERIC_SYSTEM)
        made.append(ag)
        return ag

    r = run_scenario(make, sc)
    if made and hasattr(made[0].tools, "close"):
        made[0].tools.close()
    d = dict(r.__dict__)
    d.update(config=config, model=model, trace=made[0].trace if made else [])
    print(model, config, sc.id, "pass" if r.passed else "FAIL", r.never_events, r.notes, flush=True)
    return d


for model in a.models.split(","):
    jobs = [(model, c, sc) for c in a.configs.split(",") for sc in SCENARIOS]
    with ThreadPoolExecutor(12) as ex:
        res = list(ex.map(lambda j: job(*j), jobs))
    summ = {c: {"passed": sum(r["passed"] for r in res if r["config"] == c),
                "tokens": sum(r["tokens_in"] + r["tokens_out"] for r in res if r["config"] == c),
                "cost_inr": round(sum(r["cost_inr"] for r in res if r["config"] == c), 3),
                "seconds": round(sum(r["seconds"] for r in res if r["config"] == c), 1)} for c in a.configs.split(",")}
    print(model, summ)
    (LOG / f"scorecard_{model.replace(':', '_')}.json").write_text(
        json.dumps({"model": model, "summary": summ, "results": res}, indent=1, ensure_ascii=False, default=str))
