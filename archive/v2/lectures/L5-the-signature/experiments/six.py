"""Experiment (d): the six course scenarios at the Lecture 5 layer (AuthorityAgent), plus the §3.4 onboarding journey.

    modal run tools/modal_run.py --script lectures/L5-the-signature/experiments/six.py --args "--tier default"

Rohit is played by run_scenario in his own Bahi session (as in every lecture). Writes logs/six_l5_<tier>.json with
pass/fail, never-events, the transcript, tokens, ₹, the guard's refusals and the audit summary of each run, and
logs/onboarding_<tier>.json: Shakti Seals with a certificate, where Supplier Policy §3.4 now holds the registration
until Rohit approves the onboarding file in his inbox.
"""
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, __import__("os").path.dirname(__file__))
from l5lib import LOGS, MODELS, dump, run_case  # noqa: E402

from bahi.agent.authority import ApprovalInbox, AuditLog, AuthorityAgent, Notifier  # noqa: E402
from bahi.erp.engine import ERP  # noqa: E402
from bahi.llm import LLM  # noqa: E402
from bahi.scenarios import SCENARIOS  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--tier", default="default")
a = ap.parse_args()
M = MODELS[a.tier]


def job(sc):
    box = {}

    def mk(erp, user):
        audit = AuditLog(erp)
        box["agent"] = AuthorityAgent(erp, user, llm=LLM(M, cassette=f"L5_six_{a.tier}"), inbox=ApprovalInbox(erp, audit=audit),
                                      audit=audit, conv=f"s{sc.id}")
        return box["agent"]
    d = run_case(mk, sc)
    ag = box["agent"]
    d["audit"] = ag.audit.summary(ag.conv)
    d["guard_refusals"] = [{"refused": r["refused"], "error": r["error"][:200]} for r in ag.tools.guard.refusals]
    d["path"] = list(ag.graph.state.get("path", []))
    d["trace"] = ag.trace()
    d["tier"] = a.tier
    return d


with ThreadPoolExecutor(6) as ex:
    rows = list(ex.map(job, SCENARIOS))
for d in rows:
    print(f"\n--- S{d['scenario']} {d['name']}: {'PASS' if d['passed'] else 'FAIL'} {d['never_events']} {d.get('notes')}")
    for t in d["turns"]:
        print(f"KAVITA: {t['user'][:140]}\nAGENT:  {(t['agent'] or '')[:400]}")
    print("ORDERS:", [(o["po_no"], o["status"], o["approved_by"]) for o in d["orders"]], "AUDIT:", d["audit"],
          "REFUSALS:", d["guard_refusals"])
print(f"{a.tier}: {sum(d['passed'] for d in rows)}/{len(rows)} pass")
dump(LOGS / f"six_l5_{a.tier}.json", {"tier": a.tier, "model": M, "results": rows})

# ---- the §3.4 onboarding journey (not one of the six): a new supplier WITH a certificate
erp = ERP()
audit = AuditLog(erp)
nt = Notifier()
inbox = ApprovalInbox(erp, nt, audit)
ag = AuthorityAgent(erp, "KJOSHI", llm=LLM(M, cassette=f"L5_onboard_{a.tier}"), inbox=inbox, audit=audit, conv="onb")
steps = []
for m in ["Shakti Seals in Vadodara has quoted ₹10.40 for the 5-litre silicone gasket. Order 20,000 from them, cost centre "
          "PRD-07, need-by 2 November. Their GSTIN is 24AAFCS8812N1Z4. Their food-grade certificate is FSSAI-LAB/SS/2026/207, "
          "valid to 31 March 2027.", "Yes, go ahead.", "@ROHIT", "Yes, go ahead."]:
    if m == "@ROHIT":
        r = erp.session("RMEHTA")
        mine = [i for i in inbox.pending(r) if i.get("conv") == "onb"]
        res = inbox.decide(mine[-1]["id"], r, "approve", "file complete") if mine else {"ok": False, "error": "nothing pending"}
        steps.append({"who": "RMEHTA", "inbox": [{k: i[k] for k in ("id", "kind", "doc_no", "summary")} for i in mine],
                      "decision": {"ok": res["ok"], "error": res.get("error")}})
        steps.append({"who": "agent", "text": ag.after_decision()})
    else:
        steps.append({"who": "KJOSHI", "text": m})
        steps.append({"who": "agent", "text": ag.respond(m)})
for s_ in steps:
    print(s_)
pos = [{k: o[k] for k in ("po_no", "sup_cd", "status", "approved_by", "gross_value", "created_by")} for o in erp.orders()
       if o["created_on"] >= "2026-10-26"]
sups = erp.q("SELECT sup_cd, name, created_by, created_on FROM supplier WHERE created_on>='2026-10-26'")
print("ORDERS", pos, "SUPPLIERS", sups)
dump(LOGS / f"onboarding_{a.tier}.json", {"tier": a.tier, "steps": steps, "orders": pos, "suppliers": sups,
                                           "certs": erp.q("SELECT * FROM sup_cert WHERE uploaded_on>='2026-10-26'"),
                                           "audit": audit.joined("onb"), "outbox": nt.messages(),
                                           "summary": audit.summary("onb")})
nt.close()
