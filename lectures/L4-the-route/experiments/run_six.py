"""Lecture 4: the six course scenarios with the control graph (GraphAgent), and with the Lecture 3 free tool loop.

    modal run tools/modal_run.py --script lectures/L4-the-route/experiments/run_six.py --args "--agents graph,loop"

Writes logs/six_graph.json and logs/six_loop.json: per scenario, pass/fail, never-events, the transcript, tokens,
seconds and ₹, and for the graph the path of nodes, every typed decision and every checkpoint of the draft.
"""
import argparse
import json
import pathlib
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from l4lib import MODEL, agent_trace, dump  # noqa: E402

from bahi.agent.graph import GraphAgent  # noqa: E402
from bahi.agent.loop import ToolLoopAgent  # noqa: E402
from bahi.llm import LLM  # noqa: E402
from bahi.scenarios import SCENARIOS, run_scenario  # noqa: E402
from l4lib import Belt, PolicyTool  # noqa: E402
from bahi.agent.tools import CORE, EXTRA, IntentTools  # noqa: E402
from bahi.erp import seed as SEED  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--agents", default="graph,loop")
ap.add_argument("--only", default="")
ap.add_argument("--model", default=MODEL)
ap.add_argument("--tag", default="")
a = ap.parse_args()
LOGS = pathlib.Path(__file__).parent / "logs"
LOGS.mkdir(exist_ok=True)
scs = [s for s in SCENARIOS if not a.only or str(s.id) in a.only.split(",")]

SEED_SUPS = {x[0] for x in SEED.SUPPLIERS}


def make(kind, erp, user):
    if kind == "graph":
        return GraphAgent(erp, user, llm=LLM(a.model, cassette="L4_graph" + a.tag), k=3)
    return ToolLoopAgent(erp, user, llm=LLM(a.model, cassette="L4_loop" + a.tag),
                         tools=Belt(IntentTools(erp.session(user), CORE + EXTRA), PolicyTool()))


def job(kind, sc):
    holder = {}

    def mk(erp, user):
        holder["agent"], holder["erp"] = make(kind, erp, user), erp
        return holder["agent"]
    try:
        r = run_scenario(mk, sc, max_turns=5)
    except Exception as e:  # noqa: BLE001
        import traceback
        traceback.print_exc()
        return {"scenario": sc.id, "name": sc.name, "passed": False, "never_events": [], "notes": [f"crash {e}"],
                "turns": [], "tokens_in": 0, "tokens_out": 0, "seconds": 0, "cost_inr": 0, "orders": [],
                "new_suppliers": [], "model_calls": 0, "replayed": 0, "crashed": repr(e)}
    d = dict(r.__dict__)
    d.update(agent_trace(holder["agent"]))
    erp = holder["erp"]
    d["orders"] = [{k: o[k] for k in ("po_no", "sup_cd", "itm_cd", "qty", "rate", "cc_cd", "status", "approved_by",
                                      "gross_value", "created_by")} for o in erp.orders() if o["created_on"] >= "2026-10-26"]
    d["new_suppliers"] = [s for s in erp.q("SELECT sup_cd,name,city,created_by FROM supplier") if s["sup_cd"] not in SEED_SUPS]
    d["certs_added"] = erp.q("SELECT * FROM sup_cert WHERE uploaded_on>='2026-10-26'")
    d["model_calls"] = len(holder["agent"].llm.log)
    d["replayed"] = sum(1 for x in holder["agent"].llm.log if x.replayed)
    return d


for kind in a.agents.split(","):
    with ThreadPoolExecutor(6) as ex:
        rows = list(ex.map(lambda sc: job(kind, sc), scs))
    print(f"\n===== {kind} =====")
    for d in rows:
        print(f"\n--- S{d['scenario']} {d['name']}: {'PASS' if d['passed'] else 'FAIL'} {d['never_events']} {d['notes']}")
        for t in d["turns"]:
            print(f"KAVITA: {t['user']}\nAGENT:  {t['agent']}\n   services: {t['services']}")
        if d.get("path"):
            print("PATH:", " > ".join(d["path"]))
        print("ORDERS:", d["orders"], "NEW SUPPLIERS:", d["new_suppliers"])
        print(f"tokens {d['tokens_in']}+{d['tokens_out']} · {d['seconds']} s · ₹{d['cost_inr']} · calls {d['model_calls']} (replayed {d['replayed']})")
    print(f"{kind}: {sum(d['passed'] for d in rows)}/{len(rows)} pass")
    dump(LOGS / f"six_{kind}{a.tag}.json", {"model": a.model, "agent": kind, "results": rows})
