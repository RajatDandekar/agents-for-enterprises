"""Travel · claims: the nine services, as terse as purchasing's.
Trip status codes: WL, PA, AP, BK, RJ, CN, CL. Claim status codes: SB, ST."""
from __future__ import annotations

import datetime as _dt

from ...erp.engine import LedgerlineError, service
from .._kit import F


def _trav(erp, user, trav_id):
    """Whose trip is this? Your own, unless you are the travel desk or the integration account."""
    trav = (trav_id or user).upper()
    if trav != user and erp.user(user)["role_cd"] not in ("TRV-DESK", "SYS-ADMIN"):
        raise LedgerlineError("ERR-TV-0003", "NOT YOUR TRIP")
    if not erp.user(trav):
        raise LedgerlineError("ERR-SEC-0003", "NO SUCH USER")
    return trav


@service("tv_ent_get", "TRAVEL ENTITLEMENT", [F("to_cd", desc="TO CITY CD"), F("q", desc="CITY LIKE"),
                                              F("trav_id", desc="TRAVELLER")], screen="TRV-REQ-01")
def tv_ent_get(erp, user, to_cd=None, q=None, trav_id=None):
    if q:
        rows = erp.q("SELECT city_cd,name,state,cls,km FROM tv_city WHERE lower(name) LIKE ?", f"%{q.lower()[:3]}%")
        return {"rows": rows, "_msg": f"{len(rows)} ROWS FOUND"}
    if not to_cd:
        raise LedgerlineError("ERR-SYS-0421", "TO_CD MANDATORY")
    trav = _trav(erp, user, trav_id)
    g = erp.sp("sp_tv_grade_of", trav)
    c = erp.sp("sp_tv_city", to_cd)
    cls = c["cls"].lower()
    tok = erp.sp("sp_fetch_tok_new", user, "TRV-REQ-01", f"{trav}|{c['city_cd']}")
    return {"grade": g["grade"], "modes": g["modes"], "flt_min_km": g["flt_min_km"], "km": c["km"], "cls": c["cls"],
            "hotel_cap": g[f"hotel_{cls}"], "da": g[f"da_{cls}"], "cc_cd": erp.user(trav)["default_cc"],
            "fetch_tok": tok}


@service("tv_trip_save", "TRIP REQUEST SAVE",
         [F("purpose", req=True, desc="PURPOSE"), F("from_cd", desc="FROM CITY CD"), F("to_cd", req=True, desc="TO CITY CD"),
          F("out_dt", "date", True, "OUT DT"), F("back_dt", "date", True, "BACK DT"), F("mode", req=True, desc="MODE"),
          F("cc_cd", req=True, desc="CC CD"), F("adv_amt", "float", desc="ADVANCE"), F("urgent", desc="URGENT Y/N"),
          F("trav_id", desc="TRAVELLER"), F("fetch_tok", desc="FETCH TOKEN"), F("client_ref", desc="CLIENT REF")],
         kind="write", screen="TRV-REQ-01")
def tv_trip_save(erp, user, purpose, to_cd, out_dt, back_dt, mode, cc_cd, from_cd="PUN", adv_amt=0.0, urgent="N",
                 trav_id=None, fetch_tok=None, client_ref=None):
    trav = _trav(erp, user, trav_id)
    to_cd, mode = to_cd.upper(), mode.upper()
    erp.sp("sp_fetch_tok_chk", user, fetch_tok, "TRV-REQ-01", f"{trav}|{to_cd}")
    g = erp.sp("sp_tv_grade_of", trav)
    dest = erp.sp("sp_tv_city", to_cd)
    if back_dt < out_dt:
        raise LedgerlineError("ERR-TV-0102", "BACK DT BEFORE OUT DT")
    if out_dt < erp.today:
        raise LedgerlineError("ERR-TV-0105", "OUT DT IN PAST")
    erp.sp("sp_tv_mode_chk", user, g, dest, mode)
    erp.sp("sp_tv_overlap_chk", trav, out_dt, back_dt)
    est = erp.sp("sp_tv_estimate", from_cd.upper(), dest, out_dt, back_dt, mode, g)
    if adv_amt:
        erp.sp("sp_tv_adv_chk", adv_amt, est)
    if erp.sp("sp_budget_chk", cc_cd, est["est"]) == "CLOSED":  # shared engine, the same one purchasing uses
        raise LedgerlineError("ERR-TV-0209", f"COST CENTRE {cc_cd} CLOSED")
    lead = erp.sp("sp_tv_lead_chk", out_dt, urgent)
    trip_no = erp.sp("sp_doc_no_next", "TV")
    status, warn = ("WL", "W-TV-148") if lead == "WL" else ("PA", None)
    erp.x("INSERT INTO tv_trip VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", trip_no, trav, purpose, from_cd.upper(),
          to_cd, out_dt, back_dt, mode, cc_cd, est["est"], adv_amt or 0, (urgent or "N").upper(), status, None, user,
          erp.now(), None, warn, client_ref)
    if status == "PA":
        approver = erp.sp("sp_appr_route", "TV", trip_no, trav, 0)
        erp.sp("sp_tv_status_set", trip_no, "PA", approver)
    return {"trip_no": trip_no, "status": status, "est_cost": est["est"], "_msg": f"{trip_no} SAVED"}


@service("tv_trip_list", "TRIP LIST", [F("trip_no", desc="TRIP NO"), F("trav_id", desc="TRAVELLER"),
                                       F("status", desc="STATUS"), F("approver", desc="APPROVER"),
                                       F("client_ref", desc="CLIENT REF")], screen="TRV-BKG-02")
def tv_trip_list(erp, user, trip_no=None, trav_id=None, status=None, approver=None, client_ref=None):
    sql, args = ("SELECT trip_no,user_id,purpose,from_cd,to_cd,out_dt,back_dt,mode,cc_cd,est_cost,adv_amt,urgent,status,"
                 "approver,warn_cd,client_ref FROM tv_trip WHERE 1=1"), []
    for col, v in (("trip_no", trip_no), ("user_id", trav_id), ("status", status), ("approver", approver),
                   ("client_ref", client_ref)):
        if v:
            sql += f" AND {col}=?"
            args.append(v.upper() if col in ("user_id", "approver", "status") else v)
    rows = erp.q(sql + " ORDER BY trip_no DESC", *args)
    if trip_no and rows:
        rows[0]["bkg"] = erp.q("SELECT leg,fare_cd,pnr,fare,status FROM tv_bkg WHERE trip_no=?", trip_no)
    return {"rows": rows}


@service("tv_approve", "TRIP APPROVE", [F("trip_no", req=True, desc="TRIP NO"), F("decision", req=True, desc="A/R"),
                                        F("comment", desc="COMMENT")], kind="write", screen="TRV-REQ-01")
def tv_approve(erp, user, trip_no, decision, comment=""):
    t = erp.q1("SELECT * FROM tv_trip WHERE trip_no=?", trip_no)
    if not t:
        raise LedgerlineError("ERR-TV-0501", "TRIP NOT FOUND")
    if t["status"] != "PA":
        raise LedgerlineError("ERR-TV-0502", f"TRIP NOT PENDING ({t['status']})")
    if t["user_id"] == user:
        raise LedgerlineError("ERR-APR-0003", "SELF APPROVAL NOT ALLOWED")
    if t["approver"] != user and erp.user(user)["role_cd"] != "SYS-ADMIN":
        raise LedgerlineError("ERR-TV-0504", f"NOT YOUR APPROVAL ({t['approver']})")
    ok = decision.upper().startswith("A")
    erp.sp("sp_tv_status_set", trip_no, "AP" if ok else "RJ", user)
    erp.x("UPDATE approval SET status=?, decided_on=?, comment=? WHERE doc_no=? AND status='PENDING'",
          "APPROVED" if ok else "REJECTED", erp.now(), comment, trip_no)
    if ok:
        erp.sp("sp_budget_commit", t["cc_cd"], t["est_cost"])
        erp.sp("sp_tv_desk_queue", {**t, "status": "AP"})
    return {"trip_no": trip_no, "status": "AP" if ok else "RJ", "_msg": f"{trip_no} {'APPROVED' if ok else 'REJECTED'} BY {user}"}


@service("tv_cancel", "TRIP CANCEL", [F("trip_no", req=True, desc="TRIP NO"), F("reason", req=True, desc="REASON")],
         kind="write", screen="TRV-REQ-01")
def tv_cancel(erp, user, trip_no, reason):
    t = erp.q1("SELECT * FROM tv_trip WHERE trip_no=?", trip_no)
    if not t:
        raise LedgerlineError("ERR-TV-0501", "TRIP NOT FOUND")
    _trav(erp, user, t["user_id"])
    if t["status"] in ("CN", "RJ", "CL"):
        raise LedgerlineError("ERR-TV-0507", f"TRIP CLOSED ({t['status']})")
    if t["status"] == "BK" and t["out_dt"] <= erp.today:
        raise LedgerlineError("ERR-TV-0508", "TRIP ALREADY STARTED")
    if t["status"] in ("AP", "BK"):
        erp.x("UPDATE budget SET committed=round(committed-?,2) WHERE cc_cd=? AND period='2026-Q4'", t["est_cost"], t["cc_cd"])
    for b in erp.q("SELECT * FROM tv_bkg WHERE trip_no=? AND status='OK'", trip_no):
        erp.x("UPDATE tv_fare SET seats=seats+1 WHERE fare_cd=?", b["fare_cd"])
    erp.x("UPDATE tv_bkg SET status='CX' WHERE trip_no=?", trip_no)
    erp.sp("sp_tv_status_set", trip_no, "CN")
    erp.x("UPDATE approval SET status='WITHDRAWN' WHERE doc_no=? AND status='PENDING'", trip_no)
    return {"trip_no": trip_no, "status": "CN", "_msg": f"{trip_no} CANCELLED"}


@service("tv_fare_list", "FARE ENQUIRY", [F("trip_no", desc="TRIP NO"), F("from_cd", desc="FROM"), F("to_cd", desc="TO"),
                                          F("dt", "date", desc="DATE"), F("mode", desc="MODE")], screen="TRV-BKG-02")
def tv_fare_list(erp, user, trip_no=None, from_cd=None, to_cd=None, dt=None, mode=None):
    if trip_no:
        t = erp.q1("SELECT * FROM tv_trip WHERE trip_no=?", trip_no)
        if not t:
            raise LedgerlineError("ERR-TV-0501", "TRIP NOT FOUND")
        legs = (("OUT", t["from_cd"], t["to_cd"], t["out_dt"]), ("RET", t["to_cd"], t["from_cd"], t["back_dt"]))
        return {"rows": [{"leg": lg, **r} for lg, a, b, d in legs for r in erp.q(
            "SELECT fare_cd,carrier,dep_dt,dep_tm,mode,fare,seats FROM tv_fare WHERE from_cd=? AND to_cd=? AND dep_dt=? "
            "AND mode=? ORDER BY fare", a, b, d, t["mode"])]}
    sql, args = "SELECT * FROM tv_fare WHERE 1=1", []
    for col, v in (("from_cd", from_cd), ("to_cd", to_cd), ("dep_dt", dt), ("mode", mode)):
        if v:
            sql += f" AND {col}=?"
            args.append(v.upper() if col != "dep_dt" else v)
    return {"rows": erp.q(sql + " ORDER BY dep_dt, fare", *args)}


@service("tv_bkg_save", "BOOKING SAVE", [F("trip_no", req=True, desc="TRIP NO"), F("leg", req=True, desc="OUT/RET"),
                                         F("fare_cd", req=True, desc="FARE CD"), F("pnr", req=True, desc="PNR")],
         kind="write", screen="TRV-BKG-02")
def tv_bkg_save(erp, user, trip_no, leg, fare_cd, pnr):
    t = erp.q1("SELECT * FROM tv_trip WHERE trip_no=?", trip_no)
    if not t:
        raise LedgerlineError("ERR-TV-0501", "TRIP NOT FOUND")
    if t["status"] != "AP":
        raise LedgerlineError("ERR-TV-0515", f"TRIP NOT APPROVED ({t['status']})")
    leg = leg.upper()
    f = erp.q1("SELECT * FROM tv_fare WHERE fare_cd=?", fare_cd)
    want = (t["from_cd"], t["to_cd"], t["out_dt"]) if leg == "OUT" else (t["to_cd"], t["from_cd"], t["back_dt"])
    if not f or (f["from_cd"], f["to_cd"], f["dep_dt"]) != want:
        raise LedgerlineError("ERR-TV-0520", "FARE NOT FOR THIS LEG")
    if f["mode"] != t["mode"]:
        raise LedgerlineError("ERR-TV-0521", "FARE MODE NOT AS TRIP")
    if f["seats"] <= 0:
        raise LedgerlineError("ERR-TV-0522", "SOLD OUT")
    if erp.q1("SELECT 1 FROM tv_bkg WHERE trip_no=? AND leg=? AND status='OK'", trip_no, leg):
        raise LedgerlineError("ERR-TV-0523", f"{leg} ALREADY BOOKED")
    erp.x("INSERT INTO tv_bkg VALUES (?,?,?,?,?,?,?,?)", trip_no, leg, fare_cd, pnr, f["fare"], "OK", user, erp.now())
    erp.x("UPDATE tv_fare SET seats=seats-1 WHERE fare_cd=?", fare_cd)
    legs = {r["leg"] for r in erp.q("SELECT leg FROM tv_bkg WHERE trip_no=? AND status='OK'", trip_no)}
    status = "AP"
    if legs == {"OUT", "RET"}:
        status = "BK"
        erp.sp("sp_tv_status_set", trip_no, "BK")
        erp.sp("sp_ntf_enqueue", "EMAIL", erp.user(t["user_id"])["email"], f"{trip_no} booked",
               f"{t['from_cd']}-{t['to_cd']} {t['out_dt']}, back {t['back_dt']}")
    return {"trip_no": trip_no, "leg": leg, "status": status, "_msg": f"{trip_no} {leg} BOOKED"}


@service("tv_claim_save", "EXPENSE CLAIM SAVE",
         [F("trip_no", req=True, desc="TRIP NO"), F("hotel_amt", "float", desc="HOTEL AMT"), F("nights", "int", desc="NIGHTS"),
          F("local_amt", "float", desc="LOCAL CONV"), F("bills", desc="BILLS Y/N"), F("remarks", desc="REMARKS"),
          F("client_ref", desc="CLIENT REF")], kind="write", screen="TRV-CLM-03")
def tv_claim_save(erp, user, trip_no, hotel_amt=0.0, nights=None, local_amt=0.0, bills="Y", remarks="", client_ref=None):
    t = erp.q1("SELECT * FROM tv_trip WHERE trip_no=?", trip_no)
    if not t:
        raise LedgerlineError("ERR-TV-0501", "TRIP NOT FOUND")
    if t["user_id"] != user and erp.user(user)["role_cd"] != "SYS-ADMIN":
        raise LedgerlineError("ERR-TV-0003", "NOT YOUR TRIP")
    if t["status"] != "BK" or t["back_dt"] >= erp.today:
        raise LedgerlineError("ERR-TV-0702", f"TRIP NOT COMPLETED ({t['status']})")

    if (_dt.date.fromisoformat(erp.today) - _dt.date.fromisoformat(t["back_dt"])).days > 30:
        raise LedgerlineError("ERR-TV-0703", "CLAIM AFTER 30 DAYS")
    if erp.q1("SELECT 1 FROM tv_claim WHERE trip_no=? AND status<>'CN'", trip_no):
        raise LedgerlineError("ERR-TV-0705", "CLAIM ALREADY EXISTS")
    days = (_dt.date.fromisoformat(t["back_dt"]) - _dt.date.fromisoformat(t["out_dt"])).days + 1
    nights = days - 1 if nights is None else nights
    c = erp.sp("sp_tv_claim_calc", t, hotel_amt or 0, nights, local_amt or 0, bills)
    claim_no = erp.sp("sp_doc_no_next", "TVC")
    erp.x("INSERT INTO tv_claim VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", claim_no, trip_no, hotel_amt or 0, nights,
          local_amt or 0, (bills or "Y").upper(), c["da"], c["admissible"], "SB", user, erp.now(), None, None, remarks,
          client_ref)
    erp.x("INSERT INTO approval(doc_type,doc_no,approver,status,requested_by,requested_on) VALUES (?,?,?,?,?,?)",
          "TVC", claim_no, "VNAIR", "PENDING", t["user_id"], erp.now())
    claimed = (hotel_amt or 0) + (local_amt or 0) + c["da"]
    return {"claim_no": claim_no, "status": "SB", "claimed": claimed, "admissible": c["admissible"],
            "_msg": f"{claim_no} SAVED"}


@service("tv_claim_settle", "CLAIM SETTLE", [F("claim_no", req=True, desc="CLAIM NO"), F("comment", desc="COMMENT")],
         kind="write", screen="TRV-CLM-03")
def tv_claim_settle(erp, user, claim_no, comment=""):
    c = erp.q1("SELECT * FROM tv_claim WHERE claim_no=?", claim_no)
    if not c:
        raise LedgerlineError("ERR-TV-0709", "CLAIM NOT FOUND")
    if c["status"] != "SB":
        raise LedgerlineError("ERR-TV-0710", f"CLAIM NOT SUBMITTED ({c['status']})")
    t = erp.q1("SELECT * FROM tv_trip WHERE trip_no=?", c["trip_no"])
    if t["user_id"] == user:
        raise LedgerlineError("ERR-APR-0003", "SELF APPROVAL NOT ALLOWED")
    net = erp.sp("sp_tv_settle", c, t, user)
    erp.x("UPDATE approval SET status='APPROVED', decided_on=?, comment=? WHERE doc_no=? AND status='PENDING'",
          erp.now(), comment, claim_no)
    return {"claim_no": claim_no, "status": "ST", "net_amt": net, "_msg": f"{claim_no} SETTLED"}
