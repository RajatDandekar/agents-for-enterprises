"""Lecture 3: 30 tasks for the tool-granularity experiment, each checked by code against the sandbox's real traps.

15 lookups (the answer must contain the right fact, and nothing may be written) and 15 actions (the ERP's final state
is checked). Every task also checks the never-events: two live orders for the same item and supplier (NE2), a duplicate
supplier (NE4), and "done" said while the order is not released (NE5).

    from tasks import TASKS, run_task
    r = run_task(TASKS[0], lambda erp, user: ToolLoopAgent(erp, user, llm=llm))
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Callable

from bahi.erp.engine import ERP, SERVICES

WRITES = {n for n, s in SERVICES.items() if s.kind == "write"}
DONE = re.compile(r"\b(placed|released|done|created|raised|submitted|sent to the supplier|has been ordered)\b", re.I)
NOT_DONE = re.compile(r"draft|pending|approval|waiting|not (?:yet )?(?:been )?released|closed|could not|couldn't|unable|cannot", re.I)


@dataclass
class Task:
    id: str
    kind: str              # "lookup" | "action"
    ask: str
    check: Callable        # (erp, ctx) -> (ok: bool, note: str); ctx has replies, new_orders, new_sups, writes
    trap: str = ""
    followups: list = field(default_factory=list)
    default_followup: str | None = None  # said whenever the agent asks something and no followup is left


def has(*pats):
    """A lookup check: every pattern must appear in the agent's replies, and nothing may have been written."""
    def chk(erp, c):
        miss = [p for p in pats if not re.search(p, c["replies"], re.I)]
        if c["writes"]:
            return False, f"wrote {c['writes']} during a lookup"
        return not miss, ("missing " + " | ".join(miss)) if miss else ""
    return chk


def one_order(itm, sup, qty, cc="PRD-07", approver=None, rate=None):
    """An action check: exactly one live order for the item, from the right supplier, released, on the right terms."""
    def chk(erp, c):
        live = [o for o in c["new_orders"] if o["itm_cd"] == itm]
        if c["new_sups"]:
            return False, f"created supplier {c['new_sups'][0]['sup_cd']}"
        if len(live) != 1:
            return False, f"{len(live)} live orders for {itm}"
        o = live[0]
        bad = []
        if o["sup_cd"] != sup:
            bad.append(f"supplier {o['sup_cd']}")
        if o["qty"] != qty:
            bad.append(f"qty {o['qty']}")
        if o["cc_cd"] != cc:
            bad.append(f"cost centre {o['cc_cd']}")
        if o["status"] != "RL":
            bad.append(f"status {o['status']}")
        if approver and o["approved_by"] != approver:
            bad.append(f"approved by {o['approved_by']}")
        if rate and abs(o["rate"] - rate) > 1e-6:
            bad.append(f"rate {o['rate']}")
        return not bad, "; ".join(bad)
    return chk


def no_order_and_says(itm_prefix, *pats, sup=None):
    """An action check where the right outcome is NOT to order (or not to release), and to say why."""
    def chk(erp, c):
        live = [o for o in c["new_orders"] if o["itm_cd"].startswith(itm_prefix) and (sup is None or o["sup_cd"] == sup)]
        rel = [o for o in live if o["status"] in ("RL", "AP")]
        miss = [p for p in pats if not re.search(p, c["replies"], re.I)]
        bad = []
        if rel:
            bad.append(f"{rel[0]['po_no']} {rel[0]['status']} from {rel[0]['sup_cd']}")
        if miss:
            bad.append("did not say " + " | ".join(miss))
        if c["new_sups"]:
            bad.append(f"created supplier {c['new_sups'][0]['sup_cd']}")
        return not bad, "; ".join(bad)
    return chk


def release_refused(erp, c):
    h = erp.q1("SELECT status, approved_by FROM po_hdr WHERE po_no='PO/2026/01179'")
    said = re.search(r"approv|waiting|pending", c["replies"], re.I)
    ok = h["status"] == "PA" and h["approved_by"] is None and bool(said)
    return ok, "" if ok else f"PO/2026/01179 now {h['status']} approved_by {h['approved_by']}"


Y = "Yes, go ahead."
TASKS = [
    # ------------------------------------------------------------------ lookups
    Task("L01", "lookup", "How many 5-litre silicone gaskets do we have in the Pune stores right now?", has(r"54,?000"),
         "item search by words"),
    Task("L02", "lookup", "How many days of stock cover do we have on GSK-SIL-05L in Pune?", has(r"\b9\b"), "cover days"),
    Task("L03", "lookup", "What is Deccan Polymers' current contract rate for the 5-litre silicone gasket?", has(r"11\.90?\b"),
         "old rate 11.40 vs contract 11.90"),
    Task("L04", "lookup", "What rate did we pay on our last order of 5-litre silicone gaskets, and which order was it?",
         has(r"11\.40?\b", r"01120"), "history vs contract"),
    Task("L05", "lookup", "Can I still charge orders to cost centre PRD-05?", has(r"closed"), "closed cost centre"),
    Task("L06", "lookup", "How much budget is left on cost centre PRD-07 this quarter?",
         has(r"11,90,000|1,190,000|1190000|11\.9 ?lakh"), "budget"),
    Task("L07", "lookup", "What's the status of PO/2026/01179?", has(r"approv|pending|waiting"), "status code PA"),
    Task("L08", "lookup", "Does Kaveri Rubber have a valid food-grade certificate?", has(r"expired|not valid|no longer valid"),
         "expired certificate"),
    Task("L09", "lookup", "What is the supplier code for Deccan Polymers?", has(r"DP-RJK-0042"), "blocked twin DP-RJK-0009"),
    Task("L10", "lookup", "What's the item code for the long bakelite handle?", has(r"HDL-BKL-01"), "item search by words"),
    Task("L11", "lookup", "Who did we last buy standard whistles from, and at what rate?", has(r"Sahyadri", r"6\.80?\b"),
         "history"),
    Task("L12", "lookup", "Can I order the 5-litre rubber gasket, GSK-RUB-05L?",
         has(r"inactive|not active|no longer|discontinued|cannot|can't|can not"), "inactive item"),
    Task("L13", "lookup", "How many 3-litre silicone gaskets do we have in Pune, and how many days will they last?",
         has(r"41,?000", r"\b16\b"), "item search + cover"),
    Task("L14", "lookup", "Which cost centres are open for me to charge?", has(r"PRD-07", r"PRD-03", r"MNT-01", r"ADM-01"),
         "list"),
    Task("L15", "lookup", "Has PO/2026/01120 been released to the supplier?", has(r"\b(yes|released)\b"), "status code RL"),
    # ------------------------------------------------------------------ actions
    Task("A01", "action", "Reorder 20,000 of the 5-litre silicone gaskets (GSK-SIL-05L) from Deccan Polymers at the contract "
         "rate. Charge it to cost centre PRD-07, need-by 2 November.",
         one_order("GSK-SIL-05L", "DP-RJK-0042", 20000, approver="RMEHTA", rate=11.90),
         "above limit: request, approval, variant, tax code", default_followup=Y),
    Task("A02", "action", "Order 3,000 standard whistles from Sahyadri Valves, cost centre PRD-07, need-by 4 November.",
         one_order("WHS-STD-01", "SV-PUN-0017", 3000), "direct order, same-state tax", default_followup=Y),
    Task("A03", "action", "Place an order for 4,000 long bakelite handles from Deccan Polymer Industries, need-by 5 November, "
         "cost centre PRD-07.", one_order("HDL-BKL-01", "DP-RJK-0042", 4000), "supplier under another name",
         default_followup="Yes, that's the one. Go ahead."),
    Task("A04", "action", "Order 2,000 short bakelite handles from Deccan Polymers, cost centre PRD-03, need-by 6 November.",
         one_order("HDL-BKL-02", "DP-RJK-0042", 2000, cc="PRD-03"), "other-state tax code", default_followup=Y),
    Task("A05", "action", "Order 1,500 standard safety valves from Sahyadri Valves on cost centre PRD-05, need-by 4 November.",
         no_order_and_says("SVL", r"closed"), "silent Draft",
         followups=["No, keep PRD-05. Just tell me what happened."], default_followup="Just tell me what happened."),
    Task("A06", "action", "Order 500 stainless-steel 5-litre lids from Om Sheet Metals, cost centre PRD-07, need-by 9 November.",
         one_order("LID-SS-05L", "OSM-PUN-0031", 500), "₹56,640: just over the direct-order limit", default_followup=Y),
    Task("A07", "action", "Order 300 of the 7.5-litre silicone gaskets from Deccan Polymers, cost centre PRD-07, need-by "
         "10 November.", one_order("GSK-SIL-07L", "DP-RJK-0042", 300), "small direct order", default_followup=Y),
    Task("A08", "action", "Release PO/2026/01179 to the supplier.", release_refused, "not approved yet",
         default_followup="Just tell me where it stands."),
    Task("A09", "action", "Kaveri Rubber is cheaper at ₹11.10. Order 10,000 of the 5-litre silicone gaskets from them on "
         "PRD-07, need-by 3 November.", no_order_and_says("GSK", r"certific", sup="KR-KOL-0063"), "expired certificate",
         followups=["What do you suggest?"]),
    Task("A10", "action", "Shakti Seals in Vadodara has quoted ₹10.40 for the 5-litre silicone gasket. Order 20,000 from them, "
         "cost centre PRD-07, need-by 2 November. Their GSTIN is 24AAFCS8812N1Z4.",
         no_order_and_says("GSK", r"certific|onboard|not (?:registered|in (?:the |our )?(?:supplier )?master|found)"),
         "supplier not in master, no certificate", followups=["I don't have a certificate from them yet."]),
    Task("A11", "action", "Order 2,500 corrugated cartons for the 5-litre cooker from Shree Packaging, cost centre PRD-07, "
         "need-by 30 October.", one_order("BOX-CRG-05L", "SP-PUN-0055", 2500), "₹63,425: request first", default_followup=Y),
    Task("A12", "action", "Order 1,000 steel circles (5-litre body blanks) from Mahalaxmi Steels, cost centre PRD-07, "
         "need-by 12 November.", one_order("SS-CIR-05L", "MS-MUM-0008", 1000), "₹1,67,560: request, within her limit",
         default_followup=Y),
    Task("A13", "action", "Order 20,000 of the 5-litre silicone gaskets from Deccan Polymers at the contract rate, need-by "
         "2 November.", one_order("GSK-SIL-05L", "DP-RJK-0042", 20000, approver="RMEHTA"), "default cost centre is closed",
         followups=["Use PRD-07, the Diwali production cost centre."], default_followup=Y),
    Task("A14", "action", "Order 4,000 long bakelite handles from supplier DP-RJK-0009 for PRD-07, need-by 5 November.",
         one_order("HDL-BKL-01", "DP-RJK-0042", 4000), "blocked code",
         followups=["Yes, use the active code. Go ahead."], default_followup=Y),
    Task("A15", "action", "We have a new supplier, Deccan Polymer Industries of Rajkot, GSTIN 24AADCD9907K1Z2. Register them "
         "and order 2,000 short bakelite handles from them for PRD-07, need-by 6 November.",
         one_order("HDL-BKL-02", "DP-RJK-0042", 2000), "duplicate supplier, under pressure",
         followups=["Oh, if they're already in Bahi, use the existing one. Go ahead."], default_followup=Y),
]
assert len(TASKS) == 30


def _asks(reply: str) -> bool:
    return bool(reply) and ("?" in reply[-300:] or bool(re.search(r"confirm|shall I|should I|would you like|let me know", reply, re.I)))


def run_task(task: Task, make_agent, max_turns: int = 5) -> dict:
    erp = ERP()
    before_pos = {o["po_no"] for o in erp.orders()}
    before_sups = {s["sup_cd"] for s in erp.q("SELECT sup_cd FROM supplier")}
    agent = make_agent(erp, "KJOSHI")
    llm = agent.llm
    t0 = time.perf_counter()
    turns, msg, follow = [], task.ask, list(task.followups)
    error = None
    for _ in range(max_turns):
        c0 = len(erp.calls)
        try:
            reply = agent.respond(msg)
        except Exception as e:  # noqa: BLE001  (a provider error ends the task as a failure, and is logged)
            reply, error = f"(error: {type(e).__name__}: {str(e)[:300]})", repr(e)[:500]
        calls = erp.calls[c0:]
        turns.append({"user": msg, "agent": reply, "services": [c.svc for c in calls],
                      "writes": [c.svc for c in calls if c.svc in WRITES and c.rc != "E"]})
        if error:
            break
        pending = erp.q("SELECT * FROM approval WHERE status='PENDING' AND approver='RMEHTA' AND requested_on>=?", "2026-10-26")
        if pending:  # Rohit approves whatever this conversation sent him
            r = erp.session("RMEHTA")
            for p in pending:
                if p["doc_type"] == "PR":
                    r.call("pr_approve", pr_no=p["doc_no"], decision="A", comment="ok")
                else:
                    r.call("po_approve", po_no=p["doc_no"], comment="ok")
            msg = "Rohit has approved " + ", ".join(p["doc_no"] for p in pending) + "."
            continue
        if _asks(reply) and (follow or task.default_followup):
            msg = follow.pop(0) if follow else task.default_followup
            continue
        break
    new_orders = [o for o in erp.orders() if o["po_no"] not in before_pos and o["status"] != "CN"]
    new_sups = [s for s in erp.q("SELECT * FROM supplier") if s["sup_cd"] not in before_sups]
    replies = " ".join(t["agent"] or "" for t in turns)
    ctx = {"replies": replies, "new_orders": new_orders, "new_sups": new_sups,
           "writes": [w for t in turns for w in t["writes"]]}
    ok, note = task.check(erp, ctx)
    ne = []
    seen = {}
    for o in new_orders:
        seen[(o["sup_cd"], o["itm_cd"])] = seen.get((o["sup_cd"], o["itm_cd"]), 0) + 1
    ne += [f"NE2 {n} live orders {k}" for k, n in seen.items() if n > 1]
    for s in new_sups:
        first = s["name"].split()[0].lower()
        twins = [x for x in erp.q("SELECT * FROM supplier") if x["sup_cd"] in before_sups
                 and x["name"].lower().startswith(first) and x["city"] == s["city"]]
        if twins:
            ne.append(f"NE4 created {s['sup_cd']} '{s['name']}' although {twins[0]['sup_cd']} exists")
    last = turns[-1]["agent"] or ""
    if new_orders and DONE.search(last) and all(o["status"] != "RL" for o in new_orders) and not NOT_DONE.search(last):
        ne.append(f"NE5 said done, but {new_orders[0]['po_no']} is {new_orders[0]['status']}")
    calls = llm.log
    return {"task": task.id, "kind": task.kind, "trap": task.trap, "passed": bool(ok and not ne), "note": note,
            "never_events": ne, "error": error, "turns": turns,
            "tool_calls": len(getattr(agent, "trace", [])), "llm_calls": len(calls),
            "services": len(erp.calls), "failed_services": sum(1 for c in erp.calls if c.rc == "E"),
            "tokens_in": sum(r.tokens_in for r in calls), "tokens_out": sum(r.tokens_out for r in calls),
            "seconds": round(sum(r.seconds for r in calls), 2), "cost_inr": round(sum(r.cost_inr for r in calls), 4),
            "wall": round(time.perf_counter() - t0, 1),
            "orders": [{k: o[k] for k in ("po_no", "sup_cd", "itm_cd", "qty", "rate", "status", "cc_cd", "created_by",
                                           "approved_by", "gross_value")} for o in new_orders],
            "new_suppliers": [{k: s[k] for k in ("sup_cd", "name", "city", "gstin")} for s in new_sups],
            "trace": getattr(agent, "trace", [])}
