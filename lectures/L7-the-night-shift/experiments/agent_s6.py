"""Lecture 7 experiment: scenario 6 (Bahi times out after saving) with real agents.

    modal run tools/modal_run.py --script lectures/L7-the-night-shift/experiments/agent_s6.py --args "--models gemini:gemini-3.8-flash"

The naive agent (38 raw services, service account), the same agent seeing a bare "HTTP 504 Gateway Timeout"
(agent "naive504", cassette L7_naive504), and the ToolLoopAgent (intent tools, Kavita's own session,
create_purchase_order checks the key before writing and again after a timeout). Model replies are recorded in
the cassettes L7_naive and L7_toolloop, so NB7 replays the same transcripts with no key.
Logs: experiments/logs/agent_s6_<agent>_<model>.json (transcript, every service call, every order written).
"""
import argparse
import json
import pathlib

from bahi.agent.loop import ToolLoopAgent
from bahi.agent.naive import NaiveAgent
from bahi.erp.engine import ServiceTimeout
from bahi.llm import LLM
from bahi.scenarios import SCENARIOS, run_scenario

ap = argparse.ArgumentParser()
ap.add_argument("--models", default="gemini:gemini-3.8-flash")
ap.add_argument("--agents", default="naive,toolloop")
a = ap.parse_args()
out = pathlib.Path(__file__).parent / "logs"
out.mkdir(exist_ok=True)
sc = next(s for s in SCENARIOS if s.id == 6)


class Bare504:
    """Variant "naive504": the timeout reaches the agent as a bare gateway error, the way a load balancer in front of
    a real ERP reports it, without Bahi's helpful "(the server may or may not have saved)"."""

    def __init__(self, session):
        self.s = session

    def call(self, svc, **payload):
        try:
            return self.s.call(svc, **payload)
        except ServiceTimeout:
            raise ServiceTimeout("HTTP 504 Gateway Timeout")

for model in a.models.split(","):
    for which in a.agents.split(","):
        box = {}

        def make(erp, user, which=which, model=model):
            llm = LLM(model, cassette=f"L7_{which}")
            if which == "toolloop":
                ag = ToolLoopAgent(erp, user, llm=llm)
            else:
                ag = NaiveAgent(erp, user, llm=llm)
                if which == "naive504":
                    ag.session = Bare504(ag.session)
            box.update(erp=erp, agent=ag)
            return ag

        res = run_scenario(make, sc, verbose=True)
        erp = box["erp"]
        orders = [o for o in erp.orders(itm_cd="GSK-SIL-05L") if o["created_on"] >= "2026-10-26"]
        calls = erp.live_run()
        timeouts = [c for c in calls if c["timed_out"]]
        msgs = box["agent"].messages
        tool_trace = []
        for m in msgs:
            for tc in m.get("tool_calls") or []:
                tool_trace.append({"call": tc["function"]["name"], "args": json.loads(tc["function"]["arguments"])})
            if m["role"] == "tool":
                tool_trace.append({"result": m["content"][:1200]})
        log = {"agent": which, "model": model, "passed": res.passed, "never_events": res.never_events,
               "notes": res.notes, "turns": res.turns, "tokens_in": res.tokens_in, "tokens_out": res.tokens_out,
               "seconds": res.seconds, "cost_inr": res.cost_inr,
               "orders": [{k: o[k] for k in ("po_no", "status", "qty", "rate", "gross_value", "approved_by",
                                             "created_by", "client_ref", "created_on")} for o in orders],
               "gaskets_ordered": sum(o["qty"] for o in orders if o["status"] != "CN"),
               "inr_committed": round(sum(o["gross_value"] for o in orders if o["status"] != "CN"), 2),
               "timed_out_calls": timeouts,
               "service_calls": [{k: c[k] for k in ("seq", "svc", "payload", "rc", "err_cd", "msg", "timed_out")}
                                 for c in calls],
               "tool_trace": tool_trace}
        name = f"agent_s6_{which}_{model.replace(':', '_')}.json"
        (out / name).write_text(json.dumps(log, indent=1, default=str, ensure_ascii=False))
        print(f"== {which} · {model}: passed={res.passed} NE={res.never_events} orders={[(o['po_no'], o['status']) for o in orders]} "
              f"gaskets={log['gaskets_ordered']} ₹={log['inr_committed']} timeouts={len(timeouts)} -> logs/{name}")
