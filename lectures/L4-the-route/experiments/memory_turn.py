"""Lecture 4: what each memory level contributes to one turn, on two recorded runs (cassette L4_graph, replay).

  turn A: scenario 2 after the preview, before Kavita says 'Yes, go ahead.'
  turn B: scenario 4 after the certificate question, before 'I don't have a certificate from them yet.'
          (the company level is what the Ask-for-certificate step searched for)
"""
import json
import pathlib

from bahi.agent.graph import CERT_QUERY, GraphAgent
from bahi.agent.memory import context_for_turn
from bahi.erp.engine import ERP
from bahi.llm import LLM
from bahi.scenarios import SCENARIOS

out = {}
for tag, sc, nxt, q in (("A", SCENARIOS[1], "Yes, go ahead.", None),
                        ("B", SCENARIOS[3], "I don't have a certificate from them yet.", CERT_QUERY)):
    agent = GraphAgent(ERP(), "KJOSHI", llm=LLM("gemini:gemini-3.8-flash", cassette="L4_graph"), k=3)
    reply = agent.respond(sc.ask)
    ctx = context_for_turn(agent, nxt, company_query=q)
    out[tag] = {"scenario": sc.id, "next_message": nxt, "reply": reply, "levels": ctx,
                "tokens_this_turn": [{"tokens_in": r.tokens_in, "tokens_out": r.tokens_out} for r in agent.llm.log]}
    print(tag, {k: v["chars"] for k, v in ctx.items()})
out["user_memory"] = agent.memory_user.get("KJOSHI")
(pathlib.Path(__file__).parent / "logs" / "memory_turn.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
