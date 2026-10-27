"""Lecture 7 experiment: the six scenarios at this lecture's layer.

The ToolLoopAgent with the Lecture 3 intent tools, except that the commit goes through the durable workflow
(bahi.durable.agent_tools.DurableIntentTools) and every write passes the kill-switch flags. run_scenario plays
Kavita and approves as Rohit in Bahi; the workflow notices on its own (read-back), with no special signal.

    modal run tools/modal_run.py --script lectures/L7-the-night-shift/experiments/durable_scorecard.py
Cassette: L7_durable. Log: experiments/logs/durable_scorecard_<model>.json
"""
import argparse
import json
import pathlib

from bahi.agent.loop import ToolLoopAgent
from bahi.agent.tools import IntentTools
from bahi.durable.agent_tools import DurableIntentTools
from bahi.durable.killswitch import Flags
from bahi.durable.runtime import DurableBahi
from bahi.llm import LLM
from bahi.scenarios import SCENARIOS, run_scenario, scorecard

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="gemini:gemini-3.8-flash")
ap.add_argument("--only", default="")
a = ap.parse_args()
out = pathlib.Path(__file__).parent / "logs"
out.mkdir(exist_ok=True)

rows = []
for sc in [s for s in SCENARIOS if not a.only or str(s.id) in a.only.split(",")]:
    box = {}

    def make(erp, user):
        d = DurableBahi(erp, identity=f"scenario-{sc.id}")
        tools = DurableIntentTools(IntentTools(erp.session(user)), d, Flags())
        box.update(d=d, tools=tools, erp=erp)
        return ToolLoopAgent(erp, user, llm=LLM(a.model, cassette="L7_durable"), tools=tools)

    res = run_scenario(make, sc, verbose=True)
    d, erp = box["d"], box["erp"]
    wfs = {}
    for k, wid in box["tools"].started.items():
        st = d.status(wid)
        wfs[wid] = {"stage": st["stage"], "request_no": st["request_no"], "po_no": st["po_no"], "checks": st["checks"],
                    "diary": st["diary"]}
    d.close()
    rows.append({"scenario": sc.id, "name": sc.name, "passed": res.passed, "never_events": res.never_events,
                 "notes": res.notes, "tokens": res.tokens_in + res.tokens_out, "seconds": res.seconds,
                 "cost_inr": res.cost_inr, "services": res.services_called, "workflows": wfs, "turns": res.turns,
                 "orders": [{k: o[k] for k in ("po_no", "itm_cd", "qty", "status", "approved_by", "client_ref")}
                            for o in erp.orders() if o["created_on"] >= "2026-10-26"]})
    print(f"== scenario {sc.id}: passed={res.passed} NE={res.never_events} workflows={[(w['stage'], w['po_no']) for w in wfs.values()]}")

name = f"durable_scorecard_{a.model.replace(':', '_')}.json"
(out / name).write_text(json.dumps({"model": a.model, "passed": sum(r["passed"] for r in rows), "of": len(rows),
                                    "rows": rows}, indent=1, default=str, ensure_ascii=False))
print(f"{sum(r['passed'] for r in rows)}/{len(rows)} passed -> logs/{name}")
