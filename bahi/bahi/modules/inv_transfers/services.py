"""Inventory · transfers: the eight services. Note status codes: SH, PA, AP, IT, RC, RJ, CN. Gate pass: OP, OUT."""
from __future__ import annotations

from ...erp.engine import BahiError, service
from .._kit import F


def _note(erp, tn_no):
    n = erp.q1("SELECT * FROM tr_note WHERE tn_no=?", tn_no)
    if not n:
        raise BahiError("ERR-TR-0501", "TN NOT FOUND")
    return n


def _same_ou(erp, user, whs_cd, err, msg):
    u = erp.user(user)
    if u["role_cd"] != "SYS-ADMIN" and u["ou_cd"] != erp.sp("sp_tr_whs", whs_cd)["ou_cd"]:
        raise BahiError(err, msg)


@service("tr_stk_enq", "STOCK BY LOCATION", [F("itm_cd", req=True, desc="ITEM CD"), F("whs_cd", desc="WHS CD")],
         screen="INV-STK-07")
def tr_stk_enq(erp, user, itm_cd, whs_cd=None):
    rows = erp.q("SELECT whs_cd FROM stock WHERE itm_cd=?" + (" AND whs_cd=?" if whs_cd else ""),
                 *([itm_cd, whs_cd] if whs_cd else [itm_cd]))
    if not rows:
        raise BahiError("ERR-TR-0201", "NO STOCK RECORD")
    out = []
    for r in rows:
        f = erp.sp("sp_tr_free_qty", itm_cd, r["whs_cd"])
        transit = erp.q1("SELECT coalesce(sum(qty),0) q FROM tr_note WHERE itm_cd=? AND to_whs=? AND status='IT'",
                         itm_cd, r["whs_cd"])["q"]
        out.append({"whs_cd": r["whs_cd"], **f, "in_transit": transit})
    return {"rows": out, "_msg": f"{len(out)} ROWS FOUND"}


@service("tr_fetch", "TRANSFER DEFAULTS", [F("itm_cd", req=True, desc="ITEM CD"), F("from_whs", req=True, desc="FROM WHS"),
                                           F("to_whs", req=True, desc="TO WHS")], screen="INV-TRN-04")
def tr_fetch(erp, user, itm_cd, from_whs, to_whs):
    itm = erp.q1("SELECT * FROM item WHERE itm_cd=?", itm_cd)
    if not itm or not itm["active"]:
        raise BahiError("ERR-ITM-0011", "ITEM NOT FOUND OR INACTIVE")
    mv = erp.sp("sp_tr_move_type", from_whs, to_whs)
    f = erp.sp("sp_tr_free_qty", itm_cd, from_whs)
    rate = erp.q1("SELECT rate FROM tr_std_rate WHERE itm_cd=?", itm_cd)
    tok = erp.sp("sp_fetch_tok_new", user, "INV-TRN-04", f"{itm_cd}|{from_whs}|{to_whs}")
    return {"mv_type": mv, "free": f["free"], "std_rate": rate["rate"] if rate else None, "slot": "DAY",
            "fetch_tok": tok}


@service("tr_save", "TRANSFER NOTE SAVE",
         [F("itm_cd", req=True, desc="ITEM CD"), F("qty", "int", True, "QTY"), F("from_whs", req=True, desc="FROM WHS"),
          F("to_whs", req=True, desc="TO WHS"), F("slot", desc="DAY/NIGHT"), F("vehicle", desc="VEH NO"),
          F("ewb_no", desc="EWB NO"), F("fwd_to", desc="FWD TO"), F("remarks", desc="REMARKS"),
          F("fetch_tok", desc="FETCH TOKEN"), F("client_ref", desc="CLIENT REF")], kind="write", screen="INV-TRN-04")
def tr_save(erp, user, itm_cd, qty, from_whs, to_whs, slot="DAY", vehicle=None, ewb_no=None, fwd_to=None, remarks="",
            fetch_tok=None, client_ref=None):
    erp.sp("sp_fetch_tok_chk", user, fetch_tok, "INV-TRN-04", f"{itm_cd}|{from_whs}|{to_whs}")
    slot = slot.upper()
    if slot not in ("DAY", "NIGHT"):
        raise BahiError("ERR-TR-0105", "SLOT MUST BE DAY/NIGHT")
    if qty <= 0:
        raise BahiError("ERR-TR-0201", "QTY MUST BE > 0")
    mv = erp.sp("sp_tr_move_type", from_whs, to_whs)
    f = erp.sp("sp_tr_free_qty", itm_cd, from_whs)
    if qty > f["on_hand"] - f["allocated"]:
        raise BahiError("ERR-TR-0310", "QTY EXCEEDS STOCK")
    if vehicle and not erp.q1("SELECT 1 FROM tr_vehicle WHERE veh_no=?", vehicle):
        raise BahiError("ERR-TR-0120", "VEHICLE NOT IN MASTER")
    basic, gross = erp.sp("sp_tr_value", itm_cd, qty)
    tn_no = erp.sp("sp_doc_no_next", "TRN")
    status, warn, approver = "AP", None, None
    if qty > f["free"]:
        status, warn = "SH", "W-TR-215"  # part of it is QC-held: saved, waits for QC release, never reaches a gate pass
    erp.x("INSERT INTO tr_note VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", tn_no, itm_cd, qty, from_whs, to_whs, mv,
          slot, vehicle, basic, gross, ewb_no, status, None, user, erp.now(), warn, client_ref, remarks)
    if status != "SH":
        erp.sp("sp_tr_reserve", itm_cd, from_whs, qty)
        if mv == "IUT" and slot == "NIGHT":
            approver = erp.sp("sp_tr_route_appr", tn_no, user, gross, fwd_to)
            erp.sp("sp_tr_status_set", tn_no, "PA", approver)
            status = "PA"
    return {"tn_no": tn_no, "status": status, "mv_type": mv, "gross": gross, "_msg": f"{tn_no} SAVED"}


@service("tr_list", "TRANSFER NOTE LIST", [F("tn_no", desc="TN NO"), F("itm_cd", desc="ITEM CD"), F("status", desc="STATUS"),
                                           F("to_whs", desc="TO WHS"), F("approver", desc="APPROVER"),
                                           F("client_ref", desc="CLIENT REF")], screen="INV-STK-07")
def tr_list(erp, user, tn_no=None, itm_cd=None, status=None, to_whs=None, approver=None, client_ref=None):
    sql, args = ("SELECT n.tn_no,n.itm_cd,n.qty,n.from_whs,n.to_whs,n.mv_type,n.slot,n.gross,n.ewb_no,n.status,n.approver,"
                 "n.created_by,n.created_on,n.warn_cd,n.client_ref,g.gp_no,g.status gp_status FROM tr_note n "
                 "LEFT JOIN tr_gp g ON g.tn_no=n.tn_no WHERE 1=1"), []
    for col, v in (("n.tn_no", tn_no), ("n.itm_cd", itm_cd), ("n.status", status), ("n.to_whs", to_whs),
                   ("n.approver", approver), ("n.client_ref", client_ref)):
        if v:
            sql += f" AND {col}=?"
            args.append(v)
    return {"rows": erp.q(sql + " ORDER BY n.tn_no DESC", *args)}


@service("tr_approve", "NIGHT TRANSFER APPROVE", [F("tn_no", req=True, desc="TN NO"), F("decision", req=True, desc="A/R"),
                                                  F("comment", desc="COMMENT")], kind="write", screen="INV-TRN-04")
def tr_approve(erp, user, tn_no, decision, comment=""):
    n = _note(erp, tn_no)
    if n["status"] != "PA":
        raise BahiError("ERR-TR-0502", f"TN NOT PENDING ({n['status']})")
    if n["created_by"] == user:
        raise BahiError("ERR-APR-0003", "SELF APPROVAL NOT ALLOWED")
    want = erp.q1("SELECT approver FROM approval WHERE doc_no=? AND status='PENDING' ORDER BY appr_id DESC", tn_no)
    if want and want["approver"] != user and erp.user(user)["role_cd"] != "SYS-ADMIN":
        raise BahiError("ERR-TR-0504", f"NOT YOUR APPROVAL ({want['approver']})")
    ok = decision.upper().startswith("A")
    erp.sp("sp_tr_status_set", tn_no, "AP" if ok else "RJ", user)
    erp.x("UPDATE approval SET status=?, decided_on=?, comment=? WHERE doc_no=? AND status='PENDING'",
          "APPROVED" if ok else "REJECTED", erp.now(), comment, tn_no)
    if not ok:
        erp.sp("sp_tr_reserve", n["itm_cd"], n["from_whs"], -n["qty"])
    return {"tn_no": tn_no, "status": "AP" if ok else "RJ", "_msg": f"{tn_no} {'APPROVED' if ok else 'REJECTED'} BY {user}"}


@service("tr_gp_create", "GATE PASS CREATE", [F("tn_no", req=True, desc="TN NO"), F("vehicle", desc="VEH NO"),
                                              F("ewb_no", desc="EWB NO")], kind="write", screen="INV-GTP-05")
def tr_gp_create(erp, user, tn_no, vehicle=None, ewb_no=None):
    n = _note(erp, tn_no)
    if n["mv_type"] == "INT":
        raise BahiError("ERR-TR-0605", "NO GATE PASS FOR INTRA-UNIT MOVE")
    if n["status"] != "AP":
        raise BahiError("ERR-TR-0602", f"TN NOT APPROVED ({n['status']})")
    _same_ou(erp, user, n["from_whs"], "ERR-TR-0603", "GATE PASS ONLY BY ISSUING UNIT")
    if erp.q1("SELECT 1 FROM tr_gp WHERE tn_no=?", tn_no):
        raise BahiError("ERR-TR-0606", "GATE PASS ALREADY EXISTS")
    vehicle = vehicle or n["vehicle"]
    if not vehicle:
        raise BahiError("ERR-TR-0121", "VEHICLE MANDATORY")
    if not erp.q1("SELECT 1 FROM tr_vehicle WHERE veh_no=?", vehicle):
        raise BahiError("ERR-TR-0120", "VEHICLE NOT IN MASTER")
    ewb_no = ewb_no or n["ewb_no"]
    if ewb_no:
        erp.x("UPDATE tr_note SET ewb_no=? WHERE tn_no=?", ewb_no, tn_no)
    gp_no = erp.sp("sp_doc_no_next", "TRG")
    erp.x("INSERT INTO tr_gp VALUES (?,?,?,?,?,?,?,?,?,?)", gp_no, tn_no, "NRGP", vehicle, ewb_no, "OP", user, erp.now(),
          None, None)
    return {"gp_no": gp_no, "status": "OP", "_msg": f"{gp_no} CREATED"}


@service("tr_gp_out", "GATE PASS CHECK OUT", [F("gp_no", req=True, desc="GP NO")], kind="write", screen="INV-GTP-05")
def tr_gp_out(erp, user, gp_no):
    g = erp.q1("SELECT * FROM tr_gp WHERE gp_no=?", gp_no)
    if not g:
        raise BahiError("ERR-TR-0701", "GP NOT FOUND")
    if g["status"] != "OP":
        raise BahiError("ERR-TR-0702", f"GP NOT OPEN ({g['status']})")
    n = _note(erp, g["tn_no"])
    _same_ou(erp, user, n["from_whs"], "ERR-TR-0703", "CHECK OUT ONLY AT ISSUING GATE")
    erp.sp("sp_tr_ewb_chk", n["gross"], g["ewb_no"])
    erp.x("UPDATE tr_gp SET status='OUT', out_by=?, out_on=? WHERE gp_no=?", user, erp.now(), gp_no)
    erp.sp("sp_tr_stock_out", n, gp_no)
    erp.sp("sp_tr_status_set", n["tn_no"], "IT")
    return {"gp_no": gp_no, "tn_no": n["tn_no"], "status": "OUT", "_msg": f"{gp_no} CHECKED OUT"}


@service("tr_receive", "TRANSFER RECEIPT", [F("tn_no", req=True, desc="TN NO"), F("qty_rcvd", "int", True, "QTY RCVD"),
                                            F("remarks", desc="REMARKS")], kind="write", screen="INV-GTP-05")
def tr_receive(erp, user, tn_no, qty_rcvd, remarks=""):
    n = _note(erp, tn_no)
    _same_ou(erp, user, n["to_whs"], "ERR-TR-0803", "RECEIPT ONLY BY RECEIVING UNIT")
    if n["mv_type"] == "IUT" and n["status"] != "IT":
        raise BahiError("ERR-TR-0520", f"GOODS NOT DISPATCHED ({n['status']})")
    if n["mv_type"] == "INT" and n["status"] != "AP":
        raise BahiError("ERR-TR-0521", f"TN NOT APPROVED ({n['status']})")
    if qty_rcvd <= 0 or qty_rcvd > n["qty"]:
        raise BahiError("ERR-TR-0522", "QTY RCVD MUST BE 1..TN QTY")
    if n["mv_type"] == "INT":  # inside one unit: both sides move at once, no gate
        erp.sp("sp_tr_stock_out", n, tn_no)
    rc_no = erp.sp("sp_doc_no_next", "TRR")
    erp.x("INSERT INTO tr_rcpt VALUES (?,?,?,?,?,?)", rc_no, tn_no, qty_rcvd, user, erp.now(), remarks)
    erp.sp("sp_tr_stock_in", n, qty_rcvd, rc_no)
    erp.sp("sp_tr_status_set", tn_no, "RC")
    short = n["qty"] - qty_rcvd
    if short:
        erp.x("UPDATE tr_note SET warn_cd='W-TR-411' WHERE tn_no=?", tn_no)
    return {"rc_no": rc_no, "tn_no": tn_no, "status": "RC", "short": short, "_msg": f"{rc_no} SAVED"}
