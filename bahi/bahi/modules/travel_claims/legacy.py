"""Travel · claims: the before, scripted. happy_path() is Kavita's sentence done the legacy way, screen by screen;
TRAPS triggers each trap in the complexity budget and says whether Bahi behaved as the brief claims."""
from __future__ import annotations

from .._kit import ok


def happy_path(erp) -> dict:
    """Kavita: Pune to Rajkot tomorrow, back Wednesday. Three screens and three people, the way it works today."""
    k, r, d = erp.session("KJOSHI"), erp.session("RMEHTA"), erp.session("SPILLAI")
    ok(k.call("tv_ent_get", screen="TRV-REQ-01", task="Find City", q="Rajkot"))
    tok = ok(k.call("tv_ent_get", screen="TRV-REQ-01", task="Fetch", to_cd="RJK"))["fetch_tok"]
    t = ok(k.call("tv_trip_save", screen="TRV-REQ-01", task="Save", purpose="Supplier visit, Deccan Polymers",
                  to_cd="RJK", out_dt="27-10-2026", back_dt="28-10-2026", mode="FLT-Y", cc_cd="PRD-07", urgent="Y",
                  fetch_tok=tok))
    ok(r.call("tv_trip_list", screen="TRV-REQ-01", task="Inbox", approver="RMEHTA", status="PA"))
    ok(r.call("tv_approve", screen="TRV-REQ-01", task="Approve", trip_no=t["trip_no"], decision="A", comment="ok"))
    ok(d.call("tv_trip_list", screen="TRV-BKG-02", task="Queue", status="AP"))
    ok(d.call("tv_fare_list", screen="TRV-BKG-02", task="Fares", trip_no=t["trip_no"]))
    ok(d.call("tv_bkg_save", screen="TRV-BKG-02", task="Book Leg", trip_no=t["trip_no"], leg="OUT",
              fare_cd="F-RJK-2702", pnr="KA7R4M"))
    ok(d.call("tv_bkg_save", screen="TRV-BKG-02", task="Book Leg", trip_no=t["trip_no"], leg="RET",
              fare_cd="F-RJK-2802", pnr="KA7R4M"))
    a = erp.q1("SELECT * FROM tv_trip WHERE trip_no=?", t["trip_no"])
    return {"doc": t["trip_no"], "status": a["status"],
            "ok": a["status"] == "BK" and a["approver"] == "RMEHTA" and a["est_cost"] == 17570}


def _save(s, to="RJK", out="2026-10-27", back="2026-10-28", mode="FLT-Y", cc="PRD-07", **kw):
    tok = ok(s.call("tv_ent_get", to_cd=to))["fetch_tok"]
    return s.call("tv_trip_save", purpose="Supplier visit", to_cd=to, out_dt=out, back_dt=back, mode=mode, cc_cd=cc,
                  fetch_tok=tok, **kw)


def t_silent(erp):
    r = _save(erp.session("KJOSHI"))
    no = (r["data"] or {}).get("trip_no", "")
    routed = erp.q1("SELECT 1 FROM approval WHERE doc_no=?", no)
    t = erp.q1("SELECT status, warn_cd FROM tv_trip WHERE trip_no=?", no) or {}
    good = r["rc"] == "S" and t.get("status") == "WL" and not routed
    return good, f"rc={r['rc']} msg='{r['msg']}' status={t.get('status')} warn={t.get('warn_cd')} routed={bool(routed)}"


def t_variant_mode(erp):
    s = erp.session("KJOSHI")
    r1 = _save(s, to="BOM", out="2026-11-03", back="2026-11-03", mode="FLT-Y")
    r2 = _save(s, mode="FLT-J", urgent="Y")
    r3 = _save(s, mode="TRN-2A", urgent="Y")
    good = r1["err_cd"] == "ERR-TV-0305" and r2["err_cd"] == "ERR-TV-0310" and r3["rc"] == "S"
    return good, f"flight to Mumbai (150 km): {r1['err_cd']}; business class: {r2['err_cd']}; train 2A: {r3['msg']}"


def t_variant_advance(erp):
    s = erp.session("KJOSHI")
    r1 = _save(s, urgent="Y", adv_amt=10000)
    r2 = _save(s, urgent="Y", adv_amt=5000)
    t = erp.q1("SELECT adv_amt FROM tv_trip WHERE trip_no=?", (r2["data"] or {}).get("trip_no", ""))
    good = r1["err_cd"] == "ERR-TV-0412" and r2["rc"] == "S" and t["adv_amt"] == 5000
    return good, f"advance 10,000: {r1['err_cd']} {r1['msg']}; advance 5,000: {r2['msg']}"


def t_screen_state(erp):
    r = erp.session("KJOSHI").call("tv_trip_save", purpose="Supplier visit", to_cd="RJK", out_dt="2026-10-27",
                                   back_dt="2026-10-28", mode="FLT-Y", cc_cd="PRD-07", urgent="Y")
    return r["err_cd"] == "ERR-SCR-0221", f"{r['err_cd']} {r['msg']}"


def t_cascade_budget(erp):
    b0 = erp.q1("SELECT committed FROM budget WHERE cc_cd='PRD-07'")["committed"]
    d = ok(_save(erp.session("KJOSHI"), urgent="Y"))
    ok(erp.session("RMEHTA").call("tv_approve", trip_no=d["trip_no"], decision="A"))
    b1 = erp.q1("SELECT committed FROM budget WHERE cc_cd='PRD-07'")["committed"]
    desk = erp.q1("SELECT subject FROM ntf_queue WHERE recipient='travel.desk@rasoisteel.example' ORDER BY id DESC")
    good = round(b1 - b0, 2) == d["est_cost"] and desk and d["trip_no"] in desk["subject"]
    return bool(good), f"PRD-07 committed {b0:,.0f}→{b1:,.0f} (+{d['est_cost']:,.0f}); desk mail: {desk and desk['subject']}"


def t_cascade_settle(erp):
    c = ok(erp.session("KJOSHI").call("tv_claim_save", trip_no="TRV/2026/00198", hotel_amt=6200, nights=1,
                                      local_amt=850, bills="N"))
    ok(erp.session("VNAIR").call("tv_claim_settle", claim_no=c["claim_no"]))
    p = erp.q1("SELECT * FROM tv_pay WHERE claim_no=?", c["claim_no"])
    t = erp.q1("SELECT status FROM tv_trip WHERE trip_no='TRV/2026/00198'")
    good = c["admissible"] == 8100 and p["adv_adj"] == 5000 and p["net_amt"] == 3100 and t["status"] == "CL"
    return good, (f"claimed {c['claimed']:,.0f}, admissible {c['admissible']:,.0f}, advance {p['adv_adj']:,.0f}, "
                  f"net to Kavita {p['net_amt']:,.0f}, trip {t['status']}")


def t_shared_engine(erp):
    r = _save(erp.session("KJOSHI"), cc="PRD-05", urgent="Y")
    sps = erp.calls[-1].sps
    return r["err_cd"] == "ERR-TV-0209" and "sp_budget_chk" in sps, \
        f"default cost centre PRD-05: {r['err_cd']} {r['msg']}; sp_budget_chk ran: {'sp_budget_chk' in sps}"


def t_policy_only(erp):
    """Travel Policy §5.1 (supplier visits go to PRD-07) lives only in the document: Bahi takes ADM-01."""
    r = _save(erp.session("KJOSHI"), cc="ADM-01", urgent="Y")
    return r["rc"] == "S", f"supplier visit on ADM-01: {r['msg']} (policy says PRD-07)"


TRAPS = {
    "silent: tomorrow's trip without URGENT, saved as WL, never routed": t_silent,
    "variant: travel mode by grade and distance": t_variant_mode,
    "variant: cash advance capped at hotel + allowance": t_variant_advance,
    "screen_state: Save without Fetch": t_screen_state,
    "cascade: approval commits the budget and queues the desk": t_cascade_budget,
    "cascade: settlement adjusts the advance and closes the trip": t_cascade_settle,
    "shared_engine: sp_budget_chk refuses the closed default PRD-05": t_shared_engine,
    "policy_only: supplier visit on the wrong cost centre accepted": t_policy_only,
}
