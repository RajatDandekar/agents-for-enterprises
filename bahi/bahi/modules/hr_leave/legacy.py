"""HR · leave: the before, scripted. happy_path() is Kavita's sentence done the legacy way, screen by screen;
TRAPS triggers each trap in the complexity budget and says whether Bahi behaved as the brief claims."""
from __future__ import annotations

from .._kit import ok


def happy_path(erp) -> dict:
    """Kavita: Thursday and Friday off. Three screens, the way she does it today."""
    k, r = erp.session("KJOSHI"), erp.session("RMEHTA")
    emp = ok(k.call("lv_emp_get", screen="HR-LV-01", task="Find Emp"))["emp_cd"]
    ok(k.call("lv_bal_get", screen="HR-LV-01", task="Show", emp_cd=emp))
    ok(k.call("lv_hol_list", screen="HR-LV-01", task="Holidays"))
    tok = ok(k.call("lv_fetch", screen="HR-LV-02", task="Fetch", emp_cd=emp, lv_cd="EL"))["fetch_tok"]
    d = ok(k.call("lv_save", screen="HR-LV-02", task="Save", emp_cd=emp, lv_cd="EL", from_dt="29-10-2026",
                  to_dt="30-10-2026", reason="Sister's wedding", fetch_tok=tok))
    ok(r.call("lv_list", screen="HR-LV-04", task="Inbox", approver="RMEHTA", status="PA"))
    ok(r.call("lv_approve", screen="HR-LV-04", task="Decide", lv_no=d["lv_no"], decision="A", comment="ok"))
    a = erp.q1("SELECT * FROM lv_app WHERE lv_no=?", d["lv_no"])
    return {"doc": d["lv_no"], "status": a["status"], "ok": a["status"] == "AP" and a["days"] == 2 and a["lwp_days"] == 0}


def _apply(s, emp, lv_cd, f, t, **kw):
    tok = ok(s.call("lv_fetch", emp_cd=emp, lv_cd=lv_cd))["fetch_tok"]
    return s.call("lv_save", emp_cd=emp, lv_cd=lv_cd, from_dt=f, to_dt=t, reason="test", fetch_tok=tok, **kw)


def t_silent(erp):
    r = _apply(erp.session("KJOSHI"), "E-1042", "CL", "2026-10-29", "2026-10-30")
    routed = erp.q1("SELECT 1 FROM approval WHERE doc_no=?", (r["data"] or {}).get("lv_no", ""))
    good = r["rc"] == "S" and r["data"]["status"] == "HD" and r["data"]["lwp_days"] == 1 and not routed
    return good, f"rc={r['rc']} msg='{r['msg']}' status={r['data']['status']} lwp={r['data']['lwp_days']} routed={bool(routed)}"


def t_variant_half(erp):
    r = _apply(erp.session("KJOSHI"), "E-1042", "EL", "2026-10-29", "2026-10-30", half="1H")
    return r["err_cd"] == "ERR-LV-0611", f"{r['err_cd']} {r['msg']}"


def t_variant_co(erp):
    s = erp.session("KJOSHI")
    r1 = _apply(s, "E-1042", "CO", "2026-11-02", "2026-11-02")
    r2 = _apply(s, "E-1042", "CO", "2026-11-02", "2026-11-02", ref_dt="2026-10-20")
    return r1["err_cd"] == "ERR-LV-0620" and r2["rc"] == "S", f"no ref_dt: {r1['err_cd']}; with ref_dt: {r2['msg']}"


def t_screen_state(erp):
    r = erp.session("KJOSHI").call("lv_save", emp_cd="E-1042", lv_cd="EL", from_dt="2026-10-29", to_dt="2026-10-30",
                                   reason="test")
    return r["err_cd"] == "ERR-SCR-0221", f"{r['err_cd']} {r['msg']}"


def t_cascade_balance(erp):
    b0 = erp.q1("SELECT availed,pending FROM lv_bal WHERE emp_cd='E-1042' AND lv_cd='EL'")
    d = ok(_apply(erp.session("KJOSHI"), "E-1042", "EL", "2026-10-29", "2026-10-30"))
    b1 = erp.q1("SELECT availed,pending FROM lv_bal WHERE emp_cd='E-1042' AND lv_cd='EL'")
    ok(erp.session("RMEHTA").call("lv_approve", lv_no=d["lv_no"], decision="A"))
    b2 = erp.q1("SELECT availed,pending FROM lv_bal WHERE emp_cd='E-1042' AND lv_cd='EL'")
    good = b1["pending"] == b0["pending"] + 2 and b2["availed"] == b0["availed"] + 2 and b2["pending"] == b0["pending"]
    return good, f"EL availed {b0['availed']}→{b2['availed']}, pending {b0['pending']}→{b1['pending']}→{b2['pending']}"


def t_cascade_roster(erp):
    d = ok(_apply(erp.session("KJOSHI"), "E-1042", "CL", "2026-10-29", "2026-10-30"))  # 1 CL + 1 LWP, held
    ok(erp.session("MGOKHALE").call("lv_hr_clear", lv_no=d["lv_no"], decision="L"))
    ok(erp.session("RMEHTA").call("lv_approve", lv_no=d["lv_no"], decision="A"))
    ros = erp.q("SELECT dt,code FROM lv_roster WHERE ref=?", d["lv_no"])
    feed = erp.q("SELECT * FROM lv_pay_feed WHERE ref=?", d["lv_no"])
    good = [r["code"] for r in ros] == ["CL", "LWP"] and len(feed) == 1 and feed[0]["lwp_days"] == 1
    return good, f"roster {[(r['dt'], r['code']) for r in ros]}, payroll LWP feed {[f['lwp_days'] for f in feed]}"


def t_shared_engine(erp):
    d = ok(_apply(erp.session("KJOSHI"), "E-1042", "EL", "2026-10-29", "2026-10-30"))
    sps = erp.calls[-1].sps
    inbox = ok(erp.session("RMEHTA").call("po_pending_appr"))["rows"]
    good = "sp_appr_route" in sps and any(r["doc_no"] == d["lv_no"] for r in inbox)
    return good, f"sp_appr_route in save: {'sp_appr_route' in sps}; in Rohit's purchasing inbox: {any(r['doc_no'] == d['lv_no'] for r in inbox)}"


def t_policy_only(erp):
    """Leave Policy §5.2 (Diwali run needs the plant head) lives only in the document: Bahi routes Neha to Rohit."""
    d = ok(_apply(erp.session("NDESAI"), "E-1108", "EL", "2026-11-05", "2026-11-06"))
    a = erp.q1("SELECT approver FROM lv_app WHERE lv_no=?", d["lv_no"])
    return a["approver"] == "RMEHTA", f"Neha's Diwali-run leave routed to {a['approver']} (policy says APATIL)"


TRAPS = {
    "silent: CL short, saved as HD with 1 day unpaid": t_silent,
    "variant: half day on two dates refused": t_variant_half,
    "variant: comp-off needs the worked date": t_variant_co,
    "screen_state: Save without Fetch": t_screen_state,
    "cascade: approval posts the balance": t_cascade_balance,
    "cascade: roster and payroll LWP feed": t_cascade_roster,
    "shared_engine: sp_appr_route, visible in the purchasing inbox": t_shared_engine,
    "policy_only: Diwali-run rule not enforced": t_policy_only,
}
