"""Lecture 7: what a lost reply does to Kavita's order, without and with idempotency keys. No model is called.

    from bahi.course.l7.retry import drill, lost_reply
    drill(n=50)        # 50 injected faults x three clients; counts duplicate orders, extra rupees, wrong reports
    lost_reply()       # one po_save that commits and then times out: what Bahi did vs what the caller saw

The three clients do the same job, Kavita's order end to end (request, Rohit approves, order, release):
  redo_job     no key: on any failure, start the whole job again        (bahi.durable.drills.naive_job)
  retry_call   no key: press the failed button again, up to 3 times      (bahi.durable.drills.naive_call)
  keyed_tools  the course toolbox: every write carries a key made from the order's content and looks itself
               up before writing; on any failure, start the job again (the same policy as redo_job)
  keyed_fixed  the same, with the two fixes this drill found (see FixedToolbox below)
"""
from __future__ import annotations

from dataclasses import replace

from ...agent.tools import content_key
from ...durable.drills import ORDER, _base, _truth, naive_call, naive_job, plan_trials
from ...erp.engine import ERP, ServiceTimeout
from ...toolbox import Toolbox


def keyed_tools(erp: ERP, o, attempts: int = 3, box=Toolbox) -> dict:
    kav, roh = box(erp, o.user), box(erp, "RMEHTA")
    last, steps = "", []
    for a in range(1, attempts + 1):
        try:
            pr = kav.call("create_purchase_request", {"item_code": o.item_code, "quantity": o.quantity,
                                                      "cost_centre": o.cost_centre, "need_by": o.need_by, "confirm": True})
            steps.append(("create_purchase_request", pr.get("status") or pr.get("error")))
            if not pr.get("ok"):
                raise RuntimeError(pr.get("error"))
            if pr["status_code"] == "PA":
                roh.call("approve_purchase_request", {"request_no": pr["request_no"], "decision": "approve"})
            po = kav.call("create_purchase_order", {"supplier_code": o.supplier_code, "request_no": pr["request_no"],
                                                    "confirm": True})
            steps.append(("create_purchase_order", po.get("status") or po.get("error")))
            if not po.get("ok"):
                raise RuntimeError(po.get("error"))
            if po["status_code"] == "PA":
                roh.call("approve_purchase_order", {"po_no": po["po_no"]})
            rel = kav.call("release_purchase_order", {"po_no": po["po_no"]})
            steps.append(("release_purchase_order", rel.get("status") or rel.get("error")))
            if not rel.get("sent_to_supplier"):
                raise RuntimeError(rel.get("error") or rel.get("status"))
            return {"reported": "released", "attempts": a, "steps": steps}
        except (RuntimeError, ServiceTimeout) as e:
            last = str(e)
    return {"reported": "failed", "attempts": attempts, "last_error": last, "steps": steps}


# ---------------------------------------------------------------------------------------------- the fix the drill found
# keyed_tools never duplicated, but it got stuck in two places. Both are in the shared toolbox; the lead owns it, so the
# fix lives here until it is merged (see lectures/L7-trust/NOTES.md, "shared-code changes"):
#   1. create_purchase_request: the key finds a request whose save committed but whose submit never ran (DRAFT).
#      It returned already_done and the request stayed a draft forever. Fix: submit it.
#   2. create_purchase_order: when the request is already CLOSED (an order was made from it), it refused before it
#      looked the order up by its key. Fix: look up by key first, then check the request.
def _fixed_request(s, item_code, quantity, cost_centre, need_by, confirm=False):
    from ...agent.tools import _bahi
    from ...toolbox.create_purchase_request import tool as T
    key = content_key("PR", s.user_id, item_code, quantity, cost_centre, need_by)
    for p in _bahi(s, "pr_search", raised_by=s.user_id)["rows"]:
        if f"key:{key}" in (p["remarks"] or "") and p["status"] != "RJ":
            if p["status"] == "DR" and confirm:
                _bahi(s, "pr_submit", pr_no=p["pr_no"])  # finish what the lost reply interrupted
            return {"ok": True, "already_done": True, **T._receipt(s, p["pr_no"])}
    return T.run(s, item_code, quantity, cost_centre, need_by, confirm)


def _fixed_order(s, supplier_code, request_no=None, confirm=False, **kw):
    from ...agent.tools import _bahi, _receipt
    from ...toolbox.create_purchase_order import tool as T
    if request_no:
        pr = _bahi(s, "pr_get", pr_no=request_no)
        ln = pr["lines"][0]
        key = content_key("PO", s.user_id, supplier_code, ln["itm_cd"], ln["qty"], pr["cc_cd"], pr["need_dt"])
        found = _bahi(s, "po_search", client_ref=key)["rows"]
        if found:
            return {"ok": True, "already_done": True, **_receipt(s, found[0]["po_no"])}
    return T.run(s, supplier_code, request_no=request_no, confirm=confirm, **kw)


class FixedToolbox(Toolbox):
    FIX = {"create_purchase_request": _fixed_request, "create_purchase_order": _fixed_order}

    def call(self, name, args=None):
        if name not in self.FIX:
            return super().call(name, args)
        from ...agent.tools import ToolError
        from ...toolbox import SPECS
        try:
            return self.FIX[name](self.s, **SPECS[name].check(args or {}))
        except ToolError as e:
            return e.as_dict()
        except ServiceTimeout as e:
            return {"ok": False, "error": f"Bahi did not reply in time ({e}).", "bahi_code": "TIMEOUT"}


def keyed_fixed(erp: ERP, o, attempts: int = 3) -> dict:
    return keyed_tools(erp, o, attempts, box=FixedToolbox)


CLIENTS = {"redo_job": naive_job, "retry_call": naive_call, "keyed_tools": keyed_tools, "keyed_fixed": keyed_fixed}


def drill(n: int = 50, seed: int = 7) -> dict:
    trials = plan_trials(n, seed)  # the same 50 faults v2 used: half before the commit, half after, on 3 writes
    rows = []
    for t in trials:
        o = replace(ORDER, quantity=t["qty"], ref=f"trial-{t['trial']}", key="")
        row = dict(t)
        for name, fn in CLIENTS.items():
            erp = ERP()
            bp, bq = _base(erp)
            erp.inject(t["svc"], t["mode"], t["times"])
            rep = fn(erp, o)
            tr = _truth(erp, bp, bq, o.item_code)
            tr["wrong_report"] = (rep["reported"] == "released") != (tr["released"] >= 1)
            row[name] = {**rep, **tr}
        rows.append(row)
    summary = {}
    for name in CLIENTS:
        for mode in ("error_before", "timeout_after_commit", "all"):
            sel = [r[name] for r in rows if mode == "all" or r["mode"] == mode]
            summary[f"{name}/{mode}"] = {
                "trials": len(sel), "trials_with_duplicate": sum(x["duplicate_orders"] > 0 for x in sel),
                "duplicate_orders": sum(x["duplicate_orders"] for x in sel),
                "extra_inr": round(sum(x["extra_inr"] for x in sel), 2),
                "wrong_reports": sum(x["wrong_report"] for x in sel),
                "stuck_unreleased": sum(x["released"] == 0 for x in sel),
                "exactly_one_released": sum(x["orders"] == 1 and x["released"] == 1 for x in sel)}
    return {"n": n, "seed": seed, "trials": rows, "summary": summary}


def lost_reply() -> dict:
    """One Save that Bahi commits, whose reply is then lost. What each side saw, and what a key lookup finds."""
    erp = ERP()
    kav, roh = Toolbox(erp, "KJOSHI"), Toolbox(erp, "RMEHTA")
    pr = kav.call("create_purchase_request", {"item_code": "GSK-SIL-05L", "quantity": 20000, "cost_centre": "PRD-07",
                                              "need_by": "2026-11-02", "confirm": True})
    roh.call("approve_purchase_request", {"request_no": pr["request_no"], "decision": "approve"})
    s = erp.session("KJOSHI")
    key = content_key("PO", "KJOSHI", "DP-RJK-0042", "GSK-SIL-05L", 20000, "PRD-07", "2026-11-02")
    tok = s.call("po_fetch", sup_cd="DP-RJK-0042", itm_cd="GSK-SIL-05L", pr_no=pr["request_no"])["data"]["fetch_tok"]
    budget_before = erp.q1("SELECT committed FROM budget WHERE cc_cd='PRD-07'")["committed"]
    erp.inject("po_save", "timeout_after_commit", 1)
    n0 = len(erp.calls)
    seen = None
    try:
        s.call("po_save", po_type="STD", pr_no=pr["request_no"], sup_cd="DP-RJK-0042", itm_cd="GSK-SIL-05L", qty=20000,
               rate=11.90, tax_cd="GST18-INTER", cc_cd="PRD-07", need_dt="2026-11-02", fetch_tok=tok, client_ref=key)
    except ServiceTimeout as e:
        seen = f"ServiceTimeout: {e}"
    rec = erp.calls[n0]
    return {"request_no": pr["request_no"], "key": key,
            "bahi_did": {"svc": rec.svc, "rc": rec.rc, "msg": rec.msg, "data": rec.data},
            "caller_saw": seen,
            "budget_prd07_before": budget_before,
            "budget_prd07_after": erp.q1("SELECT committed FROM budget WHERE cc_cd='PRD-07'")["committed"],
            "lookup_by_key": s.call("po_search", client_ref=key)["data"]["rows"]}
