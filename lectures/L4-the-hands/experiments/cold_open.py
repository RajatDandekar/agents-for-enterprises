"""Lecture 4 cold open: Ask Rasoi as Lecture 3 left it (the 'knowledge' stage: search_policy only).

It can explain Rasoi's rules with a citation, but asked to check stock and raise the PR it has no hands.
gemini-3.8-flash, HANDS_SYSTEM, Toolbox(names=["search_policy"]), one tool round per message. Cassette L4v3_coldopen.
Writes logs/cold_open.json.
"""
import json
import pathlib

from bahi.course.l4 import HANDS_SYSTEM, one_round
from bahi.erp.engine import ERP
from bahi.llm import LLM
from bahi.toolbox import Toolbox

erp = ERP()
tb = Toolbox(erp, "KJOSHI", names=["search_policy"])
llm = LLM("gemini:gemini-3.8-flash", cassette="L4v3_coldopen")
msgs = [{"role": "system", "content": HANDS_SYSTEM.format(name="Kavita Joshi", user_id="KJOSHI", first="Kavita")}]
turns = []
for q in ["Can we buy the 5-litre gaskets from Shakti Seals? They quoted Rs 10.40.",
          "OK, then check stock of the 5-litre gasket and raise a purchase request for 20,000 on PRD-07, needed by 9 November."]:
    msgs.append({"role": "user", "content": q})
    c0 = len(erp.calls)
    r = one_round(llm, tb, msgs)
    turns.append({"user": q, "calls": [{"tool": c["tool"], "args": c["args"]} for c in r["calls"]],
                  "answer": r["answer"], "bahi_calls": len(erp.calls) - c0})
    print(f"\nKavita: {q}\n  calls: {turns[-1]['calls']}\n  Ask Rasoi: {r['answer']}")
out = {"stage": "knowledge (search_policy only)", "model": llm.model, "turns": turns,
       "pr_rows_after": len(erp.q("SELECT * FROM pr_hdr WHERE pr_no>='PR/2026/04417'")), "totals": llm.totals()}
(pathlib.Path(__file__).resolve().parent / "logs" / "cold_open.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
