"""Purchasing · amend PO: the before, scripted. happy_path() is Kavita's sentence done the legacy way, screen by
screen; TRAPS triggers each trap in the complexity budget and says whether Bahi behaved as the brief claims."""
from __future__ import annotations

from .._kit import ok
from .scenarios import HANDLES, kavita_po


def happy_path(erp) -> dict:
    """Kavita: push Deccan's gasket delivery to 9 November and cut it to 15,000. Three screens and Rohit."""
    k, r = erp.session("KJOSHI"), erp.session("RMEHTA")
    rows = ok(k.call("pa_po_list", screen="PUR-POL-07", task="Search", q="Deccan", status="RL"))["rows"]
    po = [x for x in rows if x["itm_cd"] == "GSK-SIL-05L" and x["need_dt"] >= erp.today][0]["po_no"]
    ok(k.call("pa_po_get", screen="PUR-POL-07", task="Open", po_no=po))
    ok(k.call("pa_sched_get", screen="PUR-POL-07", task="Schedule", po_no=po))
    tok = ok(k.call("pa_amd_fetch", screen="PUR-POM-08", task="Fetch", po_no=po))["fetch_tok"]
    d = ok(k.call("pa_amd_save", screen="PUR-POM-08", task="Save", po_no=po, amd_type="REV", qty=15000,
                  need_dt="09-11-2026", reason_cd="PLAN", s1_dt="09-11-2026", s1_qty=15000, fetch_tok=tok))
    ok(r.call("pa_amd_list", screen="PUR-POA-09", task="Inbox", approver="RMEHTA", status="PA"))
    ok(r.call("pa_amd_approve", screen="PUR-POA-09", task="Decide", amd_no=d["amd_no"], decision="A", comment="ok"))
    ok(k.call("pa_amd_release", screen="PUR-POM-08", task="Release Rev", amd_no=d["amd_no"]))
    a = erp.q1("SELECT * FROM pa_amd WHERE amd_no=?", d["amd_no"])
    o = erp.orders(**{"h.po_no": po})[0]
    return {"doc": d["amd_no"], "status": a["status"],
            "ok": a["status"] == "RL" and o["qty"] == 15000 and o["need_dt"] == "2026-11-09" and a["approved_by"] == "RMEHTA"}


def _amend(erp, po, user="KJOSHI", **kw):
    s = erp.session(user)
    tok = ok(s.call("pa_amd_fetch", po_no=po))["fetch_tok"]
    return s.call("pa_amd_save", po_no=po, fetch_tok=tok, reason_cd=kw.pop("reason_cd", "PLAN"), **kw)


def _full(erp, **kw):
    """Save with the schedule, Rohit approves, Kavita releases. Returns the amendment number."""
    d = ok(_amend(erp, kavita_po(erp), qty=15000, need_dt="2026-11-09", s1_dt="2026-11-09", s1_qty=15000, **kw))
    ok(erp.session("RMEHTA").call("pa_amd_approve", amd_no=d["amd_no"], decision="A"))
    ok(erp.session("KJOSHI").call("pa_amd_release", amd_no=d["amd_no"]))
    return d["amd_no"]


def t_silent(erp):
    po = kavita_po(erp)
    r = _amend(erp, po, qty=15000, need_dt="2026-11-09")  # header only; the schedule grid left as it was
    d = r["data"] or {}
    routed = erp.q1("SELECT 1 FROM approval WHERE doc_no=?", d.get("amd_no", ""))
    told = erp.q1("SELECT 1 FROM ntf_queue WHERE subject LIKE '%revision%'")
    qty = erp.q1("SELECT qty FROM po_line WHERE po_no=?", po)["qty"]
    warn = erp.q1("SELECT warn_cd FROM pa_amd WHERE amd_no=?", d.get("amd_no", ""))
    good = r["rc"] == "S" and d.get("status") == "HD" and not routed and not told and qty == 20000
    return good, (f"rc={r['rc']} msg='{r['msg']}' status={d.get('status')} warn={warn and warn['warn_cd']} "
                  f"routed={bool(routed)} supplier told={bool(told)} PO qty still {qty}")


def t_variant_rev(erp):
    d = ok(_amend(erp, kavita_po(erp), qty=15000, need_dt="2026-11-09", s1_dt="2026-11-09", s1_qty=15000))
    a = erp.q1("SELECT need_appr, approver FROM pa_amd WHERE amd_no=?", d["amd_no"])
    return d["status"] == "PA" and a["approver"] == "RMEHTA", \
        f"REV with schedule: {d['status']}, re-approval {a['need_appr']} by {a['approver']}, new gross {d['new_gross']:,}"


def t_variant_scl(erp):
    r1 = _amend(erp, HANDLES, amd_type="SCL", need_dt="2026-11-09", reason_cd="STCK")
    r2 = _amend(erp, HANDLES, amd_type="SCL", reason_cd="STCK")
    a = erp.q1("SELECT new_qty FROM pa_amd WHERE amd_no=?", (r2["data"] or {}).get("amd_no", ""))
    good = r1["err_cd"] == "ERR-PA-0611" and r2["rc"] == "S" and r2["data"]["status"] == "PA" and a["new_qty"] == 15000
    return good, f"SCL with a date: {r1['err_cd']}; SCL: {r2['data'] and r2['data']['status']}, new qty {a and a['new_qty']}"


def t_rule_received(erp):
    r = _amend(erp, HANDLES, qty=10000)
    return r["err_cd"] == "ERR-PA-0310", f"cut handles to 10,000 with 15,000 received: {r['err_cd']} {r['msg']}"


def t_screen_state(erp):
    r = erp.session("KJOSHI").call("pa_amd_save", po_no=kavita_po(erp), qty=15000, need_dt="2026-11-09",
                                   reason_cd="PLAN", s1_dt="2026-11-09", s1_qty=15000)
    return r["err_cd"] == "ERR-SCR-0221", f"{r['err_cd']} {r['msg']}"


def t_cascade_budget(erp):
    b0 = erp.q1("SELECT committed FROM budget WHERE cc_cd='PRD-07'")["committed"]
    _full(erp)
    b1 = erp.q1("SELECT committed FROM budget WHERE cc_cd='PRD-07'")["committed"]
    return round(b0 - b1, 2) == 70210.0, f"PRD-07 committed {b0:,.0f} → {b1:,.0f} (released {b0 - b1:,.0f})"


def t_cascade_stock(erp):
    q = "SELECT on_order FROM stock WHERE itm_cd='GSK-SIL-05L' AND whs_cd='WH-PUN-STR'"
    s0 = erp.q1(q)["on_order"]
    _full(erp)
    s1 = erp.q1(q)["on_order"]
    mail = erp.q1("SELECT recipient, subject FROM ntf_queue WHERE subject LIKE '%revision%'")
    good = s0 - s1 == 5000 and mail and mail["recipient"] == "orders@dp-rjk-0042.example"
    return good, f"gaskets on order {s0:,} → {s1:,}; supplier mail: {mail and mail['subject']}"


def t_shared_engine(erp):
    d = ok(_amend(erp, kavita_po(erp), qty=15000, need_dt="2026-11-09", s1_dt="2026-11-09", s1_qty=15000))
    sps = erp.calls[-1].sps
    return "sp_tax_compute" in sps and d["new_gross"] == 210630.0, \
        f"sp_tax_compute in save: {'sp_tax_compute' in sps}; 15,000 x 11.90 + 18% IGST = {d['new_gross']:,}"


def t_policy_only(erp):
    """PO Amendment Policy §5.1 (no delivery on a Sunday or holiday) lives only in the document."""
    d = ok(_amend(erp, kavita_po(erp), qty=15000, need_dt="2026-11-08", s1_dt="2026-11-08", s1_qty=15000))
    return d["status"] == "PA", f"delivery on Sunday 8 Nov accepted: status {d['status']} (policy forbids it)"


TRAPS = {
    "silent: header saved, schedule left as it was → HD, never routed, supplier not told": t_silent,
    "variant: REV with a new schedule goes to the original approver": t_variant_rev,
    "variant: SCL short-closes at the received quantity and cannot change the date": t_variant_scl,
    "rule: quantity below received refused": t_rule_received,
    "screen_state: Save without Fetch": t_screen_state,
    "cascade: release moves the cost centre's committed budget": t_cascade_budget,
    "cascade: release cuts stock on order and sends the supplier the revision": t_cascade_stock,
    "shared_engine: sp_tax_compute values the revision": t_shared_engine,
    "policy_only: Sunday delivery not checked": t_policy_only,
}
