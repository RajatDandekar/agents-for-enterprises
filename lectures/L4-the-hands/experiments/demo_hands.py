"""Lecture 4's practical ending: Ask Rasoi at the 'hands' stage checks stock and raises the PR.

Ask Rasoi = gemini-3.8-flash + HANDS_SYSTEM + the toolbox DISCOVERED over MCP (build_toolbox_server bound to the
signed-in user's session), one tool round per message (bahi.course.l4.one_round). Kavita's conversation, then Rohit
opens his own Ask Rasoi (a second server, bound to RMEHTA) and approves. Also: the same first question without the
item code, to show what one round cannot do. Cassette L4v3_demo. Writes logs/demo_hands.json.
"""
import json
import pathlib

from bahi.course.l4 import HANDS_SYSTEM, one_round
from bahi.erp.engine import ERP
from bahi.llm import LLM
from bahi.mcp_server import MCPClient, MCPClientTools
from bahi.toolbox.mcp import build_toolbox_server

LOG = pathlib.Path(__file__).resolve().parent / "logs"


def session(erp, user):
    u = erp.user(user)
    client = MCPClient(build_toolbox_server(erp, user))
    return client, MCPClientTools(client), [{"role": "system", "content": HANDS_SYSTEM.format(
        name=u["name"], user_id=user, first=u["name"].split()[0])}]


def turn(llm, tools, msgs, who, text, log):
    msgs.append({"role": "user", "content": text})
    r = one_round(llm, tools, msgs)
    log.append({"who": who, "user": text, "calls": r["calls"], "wanted_more": r["wanted_more"], "answer": r["answer"],
                "tokens_in": sum(x.tokens_in for x in r["replies"]), "tokens_out": sum(x.tokens_out for x in r["replies"]),
                "seconds": round(sum(x.seconds for x in r["replies"]), 2), "inr": round(sum(x.cost_inr for x in r["replies"]), 4)})
    print(f"\n[{who}] {text}\n  calls: {[(c['tool'], c['args']) for c in r['calls']]}  wanted_more: {r['wanted_more']}\n  {r['answer'][:500]}")


llm = LLM("gemini:gemini-3.8-flash", cassette="L4v3_demo")
erp = ERP()
kc, kt, km = session(erp, "KJOSHI")
log = []
turn(llm, kt, km, "Kavita", "Check stock of the 5-litre gasket, GSK-SIL-05L.", log)
turn(llm, kt, km, "Kavita", "We need 20,000 more before the Diwali run. Raise a purchase request on PRD-07, needed by 9 November.", log)
turn(llm, kt, km, "Kavita", "Yes, go ahead.", log)
rc, rt, rm = session(erp, "RMEHTA")
turn(llm, rt, rm, "Rohit", "What is waiting for my approval?", log)
turn(llm, rt, rm, "Rohit", "Approve PR/2026/04417.", log)
pr = dict(erp.q1("SELECT pr_no,status,raised_by,approved_by,est_value FROM pr_hdr WHERE pr_no='PR/2026/04417'") or {})
print("\nBahi:", pr)
mcp_methods = [w["method"] for w in kc.wire] + [w["method"] for w in rc.wire]
kc.close(); rc.close()

# the same first question without the code: one round is not enough
erp2 = ERP()
c2, t2, m2 = session(erp2, "KJOSHI")
nocode = []
turn(llm, t2, m2, "Kavita", "Check stock of the 5-litre gasket.", nocode)
c2.close()

out = {"model": llm.model, "stage": "hands: toolbox over MCP, one tool round per message", "turns": log,
       "bahi_pr": pr, "mcp_methods": mcp_methods, "no_code_variant": nocode, "totals": llm.totals()}
(LOG / "demo_hands.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
print("totals", llm.totals())
