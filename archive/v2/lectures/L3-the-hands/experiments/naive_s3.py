"""Lecture 3 opener: scenario 3 ("Deccan Polymer Industries") with Lecture 1's naive agent (38 raw services, service
account, no harness), and the same scenario with the Lecture 3 agent (intent tools, Kavita's session).
Writes logs/naive_s3_<model>.json with the transcript, every service call and the ERP's final state."""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "bahi"))

from bahi.agent.loop import ToolLoopAgent  # noqa: E402
from bahi.agent.naive import NaiveAgent  # noqa: E402
from bahi.llm import LLM  # noqa: E402
from bahi.scenarios import SCENARIOS, run_scenario  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--models", default="gemini:gemini-3.8-flash")
a = ap.parse_args()
LOG = pathlib.Path(__file__).parent / "logs"
LOG.mkdir(exist_ok=True)
sc = SCENARIOS[2]
for model in a.models.split(","):
    out = {"model": model, "scenario": sc.__dict__ | {"setup": None}}
    for label, make in (("naive", lambda erp, user, llm: NaiveAgent(erp, user, llm=llm)),
                        ("intent_tools", lambda erp, user, llm: ToolLoopAgent(erp, user, llm=llm))):
        llm = LLM(model, cassette="L3_naive")
        box = {}

        def mk(erp, user):
            box["erp"], box["agent"] = erp, make(erp, user, llm)
            return box["agent"]

        res = run_scenario(mk, sc, max_turns=4, verbose=True)
        erp, agent = box["erp"], box["agent"]
        out[label] = {"passed": res.passed, "never_events": res.never_events, "notes": res.notes, "turns": res.turns,
                      "tokens_in": res.tokens_in, "tokens_out": res.tokens_out, "seconds": res.seconds, "cost_inr": res.cost_inr,
                      "live_run": erp.live_run(),
                      "suppliers_after": erp.q("SELECT sup_cd,name,city,state,gstin,status,created_by,created_on FROM supplier"),
                      "new_orders": [{k: o[k] for k in ("po_no", "sup_cd", "itm_cd", "qty", "rate", "status", "gross_value",
                                                         "created_by", "approved_by", "cc_cd")}
                                     for o in erp.orders() if o["created_on"] >= "2026-10-26"],
                      "messages": [m for m in agent.messages if m["role"] != "system"]}
        print(label, "passed" if res.passed else "FAILED", res.never_events, res.notes)
    (LOG / f"naive_s3_{model.replace(':', '_')}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
