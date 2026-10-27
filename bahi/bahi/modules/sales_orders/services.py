"""Sales · orders: the nine services, as terse as purchasing's.
Quotation status: PA, IS, CV, EX, RJ. Order status: OP, CH, RL, IN, CN."""
from __future__ import annotations

from ...erp.engine import BahiError, service
from .._kit import F


@service("so_cust_search", "CUSTOMER ENQUIRY", [F("q", req=True, desc="NAME LIKE")], screen="SAL-CUS-01")
def so_cust_search(erp, user, q):
    rows = erp.q("SELECT cust_cd,name,city,state,cust_type,status FROM so_cust WHERE lower(name) LIKE ?", f"%{q.lower()}%")
    return {"rows": rows, "_msg": f"{len(rows)} ROWS FOUND"}


@service("so_cust_get", "CUSTOMER MASTER GET", [F("cust_cd", req=True, desc="CUST CD")], screen="SAL-CUS-01")
def so_cust_get(erp, user, cust_cd):
    c = erp.q1("SELECT * FROM so_cust WHERE cust_cd=?", cust_cd)
    if not c:
        raise BahiError("ERR-SO-0030", "CUSTOMER NOT FOUND")
    open_ = erp.q1("SELECT coalesce(sum(gross_value),0) v FROM so_ord WHERE cust_cd=? AND status IN ('OP','RL')", cust_cd)["v"]
    return {**c, "open_orders": open_, "cr_avail": round(c["cr_limit"] - c["outstanding"] - open_, 2)}


@service("so_price_get", "PRICE LIST ENQUIRY", [F("itm_cd", req=True, desc="ITEM CD"), F("list_cd", desc="LIST CD")],
         screen="SAL-CUS-01")
def so_price_get(erp, user, itm_cd, list_cd=None):
    sql, args = "SELECT list_cd,rate,valid_from,valid_to FROM so_price WHERE itm_cd=?", [itm_cd]
    if list_cd:
        sql += " AND list_cd=?"
        args.append(list_cd)
    return {"rows": erp.q(sql + " ORDER BY list_cd, valid_from", *args)}  # every row, expired ones too


@service("so_qtn_fetch", "QUOTATION DEFAULTS", [F("cust_cd", req=True, desc="CUST CD"), F("itm_cd", req=True, desc="ITEM CD")],
         screen="SAL-QTN-02")
def so_qtn_fetch(erp, user, cust_cd, itm_cd):
    c = erp.sp("sp_so_cust_chk", cust_cd)
    rate = erp.sp("sp_so_price_cur", c["list_cd"], itm_cd)
    tok = erp.sp("sp_fetch_tok_new", user, "SAL-QTN-02", f"{cust_cd}|{itm_cd}")
    return {"list_cd": c["list_cd"], "rate": rate, "tax_cd": "GST12-INTRA",  # defaults to the plant's state
            "disc_lim": erp.sp("sp_so_disc_lim", user), "fetch_tok": tok}


@service("so_qtn_save", "QUOTATION SAVE",
         [F("cust_cd", req=True, desc="CUST CD"), F("itm_cd", req=True, desc="ITEM CD"), F("qty", "int", True, "QTY"),
          F("list_cd", desc="LIST CD"), F("rate", "float", desc="RATE"), F("disc_pct", "float", desc="DISC %"),
          F("tax_cd", req=True, desc="TAX CD"), F("valid_to", "date", desc="VALID TO"), F("fetch_tok", desc="FETCH TOKEN"),
          F("client_ref", desc="CLIENT REF"), F("remarks", desc="REMARKS")], kind="write", screen="SAL-QTN-02")
def so_qtn_save(erp, user, **a):
    erp.sp("sp_fetch_tok_chk", user, a.get("fetch_tok"), "SAL-QTN-02", f"{a['cust_cd']}|{a['itm_cd']}")
    r = erp.sp("sp_so_qtn_save", user, a)
    return {**r, "_msg": f"{r['qtn_no']} SAVED"}


@service("so_list", "SALES DOCUMENT LIST", [F("doc_no", desc="QT/SO NO"), F("cust_cd", desc="CUST CD"),
                                            F("status", desc="STATUS"), F("client_ref", desc="CLIENT REF")],
         screen="SAL-ORD-03")
def so_list(erp, user, doc_no=None, cust_cd=None, status=None, client_ref=None):
    out = {}
    for key, table, cols in (("quotations", "so_qtn", "qtn_no,cust_cd,itm_cd,qty,rate,disc_pct,tax_cd,gross_value,"
                                                       "valid_to,status,created_by,approved_by,client_ref"),
                             ("orders", "so_ord", "ord_no,ord_type,qtn_no,cust_cd,itm_cd,qty,rate,gross_value,status,"
                                                  "warn_cd,released_on,client_ref")):
        pk = cols.split(",")[0]
        sql, args = f"SELECT {cols} FROM {table} WHERE 1=1", []
        for col, v in ((pk, doc_no), ("cust_cd", cust_cd), ("status", status), ("client_ref", client_ref)):
            if v:
                sql += f" AND {col}=?"
                args.append(v)
        out[key] = erp.q(sql + f" ORDER BY {pk} DESC", *args)
    return out


@service("so_disc_approve", "DISCOUNT APPROVE", [F("qtn_no", req=True, desc="QT NO"), F("decision", req=True, desc="A/R"),
                                                 F("comment", desc="COMMENT")], kind="write", screen="SAL-QTN-02")
def so_disc_approve(erp, user, qtn_no, decision, comment=""):
    q = erp.q1("SELECT * FROM so_qtn WHERE qtn_no=?", qtn_no)
    if not q:
        raise BahiError("ERR-SO-0701", "QUOTATION NOT FOUND")
    if q["status"] != "PA":
        raise BahiError("ERR-SO-0702", f"QUOTATION NOT PENDING ({q['status']})")
    if q["created_by"] == user:
        raise BahiError("ERR-APR-0003", "SELF APPROVAL NOT ALLOWED")
    a = erp.q1("SELECT approver FROM approval WHERE doc_no=? AND status='PENDING'", qtn_no)
    if a and a["approver"] != user and erp.user(user)["role_cd"] != "SYS-ADMIN":
        raise BahiError("ERR-SO-0703", f"NOT YOUR APPROVAL ({a['approver']})")
    if erp.sp("sp_so_disc_lim", user) < q["disc_pct"]:
        raise BahiError("ERR-SO-0704", "DISCOUNT ABOVE YOUR AUTHORITY")
    ok = decision.upper().startswith("A")
    st = "IS" if ok else "RJ"
    erp.x("UPDATE so_qtn SET status=?, approved_by=?, approved_on=? WHERE qtn_no=?", st, user if ok else None,
          erp.now() if ok else None, qtn_no)
    erp.x("UPDATE approval SET status=?, decided_on=?, comment=? WHERE doc_no=? AND status='PENDING'",
          "APPROVED" if ok else "REJECTED", erp.now(), comment, qtn_no)
    erp.sp("sp_ntf_enqueue", "EMAIL", erp.user(q["created_by"])["email"], f"{qtn_no} {'APPROVED' if ok else 'REJECTED'}",
           comment or "")
    return {"qtn_no": qtn_no, "status": st, "_msg": f"{qtn_no} {'APPROVED' if ok else 'REJECTED'} BY {user}"}


@service("so_ord_save", "SALES ORDER SAVE",
         [F("ord_type", desc="STD/CSH"), F("qtn_no", desc="QT NO"), F("cust_cd", desc="CUST CD"),
          F("itm_cd", desc="ITEM CD"), F("qty", "int", desc="QTY"), F("tax_cd", desc="TAX CD"),
          F("client_ref", desc="CLIENT REF")], kind="write", screen="SAL-ORD-03")
def so_ord_save(erp, user, **a):
    r = erp.sp("sp_so_ord_save", user, a)
    return {**r, "_msg": f"{r['ord_no']} SAVED"}  # the status is in the data; the message never mentions it


@service("so_ord_release", "SALES ORDER RELEASE", [F("ord_no", req=True, desc="SO NO")], kind="write",
         screen="SAL-ORD-03")
def so_ord_release(erp, user, ord_no):
    o = erp.q1("SELECT * FROM so_ord WHERE ord_no=?", ord_no)
    if not o:
        raise BahiError("ERR-SO-0701", "ORDER NOT FOUND")
    if o["status"] == "CH":
        raise BahiError("ERR-SO-0715", "ORDER ON CREDIT HOLD")
    if o["status"] != "OP":
        raise BahiError("ERR-SO-0716", f"ORDER NOT IN RELEASABLE STATUS ({o['status']})")
    erp.sp("sp_so_stk_alloc", o["itm_cd"], o["whs_cd"], o["qty"])
    erp.sp("sp_so_status_set", "so_ord", "ord_no", ord_no, "RL")
    erp.x("UPDATE so_ord SET released_on=? WHERE ord_no=?", erp.now(), ord_no)
    erp.sp("sp_so_dsp_advice", o)
    return {"ord_no": ord_no, "status": "RL", "_msg": f"{ord_no} RELEASED"}
