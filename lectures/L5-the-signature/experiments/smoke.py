"""Smoke test of the Lecture 5 stack (AuthorityAgent + inbox + guard + audit) on two journeys. Not a plate source."""
import json
import pathlib
import sys
import traceback

from bahi.agent.authority import ApprovalInbox, AuditLog, AuthorityAgent, Notifier
from bahi.erp.engine import ERP
from bahi.llm import LLM

MODEL = sys.argv[1] if len(sys.argv) > 1 else "gemini:gemini-3.8-flash"
LOGS = pathlib.Path(__file__).parent / "logs"


def journey(name, msgs, approve_after=None, durable=False, mcp=False):
    erp = ERP()
    audit = AuditLog(erp)
    nt = Notifier()
    d = None
    if durable:
        from bahi.durable.runtime import DurableBahi, quiet_logs
        quiet_logs()
        d = DurableBahi(erp)
    inbox = ApprovalInbox(erp, nt, audit, durable=d)
    ag = AuthorityAgent(erp, "KJOSHI", llm=LLM(MODEL, cassette="L5_smoke"), inbox=inbox, audit=audit, durable=d, mcp=mcp)
    out = []
    for m in msgs:
        if m == "@ROHIT":
            r = erp.session("RMEHTA")
            items = inbox.pending(r)
            print("ROHIT INBOX:", [(i["id"], i["doc_no"], i["summary"]) for i in items])
            mine = [i for i in items if i.get("conv") == ag.conv]
            res = inbox.decide(mine[-1]["id"], r, "approve", "ok")
            print("DECIDE:", res["ok"], res.get("error"), res["item"]["status"])
            rep = ag.after_decision()
            out.append(("after_decision", rep))
        else:
            rep = ag.respond(m)
            out.append((m, rep))
        print(f"\n>>> {out[-1][0]}\n{out[-1][1]}")
    print("\nPOs:", [(o["po_no"], o["status"], o["approved_by"], o["created_by"]) for o in erp.orders() if o["created_on"] >= "2026-10-26"])
    print("SUPPLIERS new:", erp.q("SELECT sup_cd,name,created_by FROM supplier WHERE created_on>='2026-10-26'"))
    print("AUDIT:", audit.summary(ag.conv))
    for t in ag.trace():
        print("  ", t["kind"], t["line"][:150])
    print("OUTBOX:", [(m["channel"], m["text"][:90]) for m in nt.messages()])
    nt.close()
    if d:
        d.close()


try:
    journey("s2", ["Reorder 20,000 of the 5-litre silicone gaskets (GSK-SIL-05L) from Deccan Polymers at the contract rate. "
                   "Charge it to cost centre PRD-07, need-by 2 November.", "Yes, go ahead.", "@ROHIT"])
except Exception:
    traceback.print_exc()
try:
    journey("onboard", ["Shakti Seals in Vadodara has quoted ₹10.40 for the 5-litre silicone gasket. Order 20,000 from them, "
                        "cost centre PRD-07, need-by 2 November. Their GSTIN is 24AAFCS8812N1Z4. Their food-grade certificate "
                        "is FSSAI-LAB/SS/2026/207, valid to 31 March 2027.", "Yes, go ahead.", "@ROHIT", "Yes, go ahead."])
except Exception:
    traceback.print_exc()
if "--durable" in sys.argv:
    try:
        journey("s2d", ["Reorder 20,000 of the 5-litre silicone gaskets (GSK-SIL-05L) from Deccan Polymers at the contract rate. "
                        "Charge it to cost centre PRD-07, need-by 2 November.", "Yes, go ahead.", "@ROHIT"], durable=True, mcp=True)
    except Exception:
        traceback.print_exc()
