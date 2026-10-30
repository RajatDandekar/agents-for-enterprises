"""Finance · payables: the nine services. Invoice status: HD, PA, PO, PD, RJ, CN. Payment status: PK, PA, SC, PD, CN."""
from __future__ import annotations

import datetime as dt

from ...erp.engine import LedgerlineError, service
from .._kit import F

SCR_ENTRY, SCR_HOLD, SCR_PAY = "FIN-AP-01", "FIN-AP-03", "FIN-AP-05"


@service("ap_inv_list", "AP INVOICE LIST", [F("sup_cd", desc="SUP CD"), F("sup_inv_no", desc="SUP INV NO"),
                                            F("status", desc="STATUS"), F("hold_cd", desc="HOLD CD"),
                                            F("po_no", desc="PO NO")], screen=SCR_HOLD)
def ap_inv_list(erp, user, sup_cd=None, sup_inv_no=None, status=None, hold_cd=None, po_no=None):
    sql, args = ("SELECT i.ap_no,i.sup_cd,s.name sup_name,i.sup_inv_no,i.inv_dt,i.po_no,i.gross,i.status,i.hold_cd,i.due_dt "
                 "FROM ap_inv i JOIN supplier s ON s.sup_cd=i.sup_cd WHERE 1=1"), []
    for col, v in (("i.sup_cd", sup_cd), ("i.status", status), ("i.hold_cd", hold_cd), ("i.po_no", po_no)):
        if v:
            sql += f" AND {col}=?"
            args.append(v)
    if sup_inv_no:
        sql += " AND upper(i.sup_inv_no) LIKE ?"
        args.append(f"%{sup_inv_no.upper()}%")
    rows = erp.q(sql + " ORDER BY i.ap_no DESC", *args)
    return {"rows": rows, "_msg": f"{len(rows)} ROWS FOUND"}


@service("ap_inv_get", "AP INVOICE GET", [F("ap_no", req=True, desc="AP NO")], screen=SCR_HOLD)
def ap_inv_get(erp, user, ap_no):
    i = erp.q1("SELECT * FROM ap_inv WHERE ap_no=?", ap_no)
    if not i:
        raise LedgerlineError("ERR-AP-0001", "AP DOC NOT FOUND")
    out = {**i, "holds": erp.q("SELECT hold_cd,detail,put_on,released_by,released_on,reason FROM ap_hold_log WHERE ap_no=? "
                               "ORDER BY id", ap_no),
           "pays": erp.q("SELECT pay_no,pay_dt,amount,status,approved_by FROM ap_pay WHERE ap_no=?", ap_no),
           "grns": erp.q("SELECT grn_no,qty_rcvd,qty_acc,grn_dt FROM ap_grn WHERE po_no=?", i["po_no"] or ""),
           "age_days": (dt.date.fromisoformat(erp.today) - dt.date.fromisoformat(i["inv_dt"])).days,
           "msme": (erp.q1("SELECT msme FROM ap_vbank WHERE sup_cd=?", i["sup_cd"]) or {}).get("msme")}
    if i["po_no"]:
        out["po_rate"] = erp.q1("SELECT rate FROM po_line WHERE po_no=?", i["po_no"])["rate"]
    return out


@service("ap_match", "INVOICE MATCH", [F("inv_type", req=True, desc="PO/NPO"), F("sup_cd", req=True, desc="SUP CD"),
                                       F("po_no", desc="PO NO"), F("qty", "int", desc="QTY"), F("rate", "float", desc="RATE"),
                                       F("amount", "float", desc="BASIC AMT (NPO)"), F("cc_cd", desc="CC CD (NPO)")],
         screen=SCR_ENTRY)
def ap_match(erp, user, inv_type, sup_cd, po_no=None, qty=None, rate=None, amount=None, cc_cd=None):
    erp.sp("sp_ap_sup_chk", sup_cd)
    if inv_type.upper() == "PO":
        if not (po_no and qty and rate):
            raise LedgerlineError("ERR-AP-0201", "PO NO, QTY, RATE MANDATORY FOR PO INVOICE")
        m = erp.sp("sp_ap_match3", sup_cd, po_no, qty, rate)
    else:
        if po_no:
            raise LedgerlineError("ERR-AP-0211", "NPO INVOICE CANNOT REFER PO")
        if not (amount and cc_cd):
            raise LedgerlineError("ERR-AP-0212", "AMOUNT AND CC CD MANDATORY FOR NPO")
        m = erp.sp("sp_ap_match2", cc_cd, amount * 1.18)
    tok = erp.sp("sp_fetch_tok_new", user, SCR_ENTRY, f"{sup_cd}|{po_no or 'NPO'}")
    return {**m, "holds": [h[0] for h in m["holds"]], "match_tok": tok,
            "_msg": "MATCHED" if not m["holds"] else "MATCHED WITH EXCEPTIONS"}


@service("ap_save", "INVOICE SAVE", [F("inv_type", req=True, desc="PO/NPO"), F("sup_cd", req=True, desc="SUP CD"),
                                     F("sup_inv_no", req=True, desc="SUP INV NO"), F("inv_dt", "date", True, "INV DT"),
                                     F("po_no", desc="PO NO"), F("qty", "int", desc="QTY"), F("rate", "float", desc="RATE"),
                                     F("amount", "float", desc="BASIC AMT (NPO)"), F("tax_cd", req=True, desc="TAX CD"),
                                     F("cc_cd", desc="CC CD (NPO)"), F("match_tok", desc="MATCH TOKEN"),
                                     F("client_ref", desc="CLIENT REF")], kind="write", screen=SCR_ENTRY)
def ap_save(erp, user, inv_type, sup_cd, sup_inv_no, inv_dt, tax_cd, po_no=None, qty=None, rate=None, amount=None,
            cc_cd=None, match_tok=None, client_ref=None):
    inv_type = inv_type.upper()
    erp.sp("sp_fetch_tok_chk", user, match_tok, SCR_ENTRY, f"{sup_cd}|{po_no or 'NPO'}")
    sup = erp.sp("sp_ap_sup_chk", sup_cd)
    if inv_dt > erp.today:
        raise LedgerlineError("ERR-AP-0103", "INV DT IN FUTURE")
    erp.sp("sp_tax_region_chk", sup_cd, tax_cd, erp.user(user)["ou_cd"])  # shared engine
    if inv_type == "PO":
        if not (po_no and qty and rate):
            raise LedgerlineError("ERR-AP-0201", "PO NO, QTY, RATE MANDATORY FOR PO INVOICE")
        basic = round(qty * rate, 2)
        m = erp.sp("sp_ap_match3", sup_cd, po_no, qty, rate)
        cc_cd = m["cc_cd"]
    else:
        if po_no:
            raise LedgerlineError("ERR-AP-0211", "NPO INVOICE CANNOT REFER PO")
        if not (amount and cc_cd):
            raise LedgerlineError("ERR-AP-0212", "AMOUNT AND CC CD MANDATORY FOR NPO")
        basic, qty, rate = round(amount, 2), None, None
    tax, gross = erp.sp("sp_tax_compute", basic, tax_cd)  # shared engine
    if inv_type == "NPO":
        m = erp.sp("sp_ap_match2", cc_cd, gross)
    holds = list(m["holds"])
    twin = erp.sp("sp_ap_dup_chk", sup_cd, sup_inv_no, gross, po_no)
    if twin:
        holds.append(("H-DUP", f"LIKE {twin}"))
    ap_no = erp.sp("sp_doc_no_next", "APINV")
    status = "HD" if holds else ("PA" if inv_type == "NPO" else "PO")
    erp.x("INSERT INTO ap_inv VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", ap_no, inv_type, sup_cd, sup_inv_no,
          inv_dt, po_no, qty, rate, basic, tax_cd, tax, gross, cc_cd, status, holds[0][0] if holds else None,
          erp.sp("sp_ap_due_dt", sup, inv_dt), user, erp.now(), None, None, client_ref)
    if holds:
        erp.sp("sp_ap_hold_put", ap_no, holds)
    elif inv_type == "NPO":
        erp.sp("sp_ap_route", "APINV", ap_no, m["approver"], user, f"Non-PO invoice {sup_inv_no}, {gross:,.2f}")
    else:
        erp.sp("sp_ap_post", ap_no)
    return {"ap_no": ap_no, "status": status, "gross": gross, "_msg": f"{ap_no} SAVED"}  # holds are on the document


@service("ap_hold_refer", "HOLD REFER", [F("ap_no", req=True, desc="AP NO"), F("hold_cd", req=True, desc="HOLD CD"),
                                         F("refer_to", req=True, desc="USER ID"), F("note", desc="NOTE")],
         kind="write", screen=SCR_HOLD)
def ap_hold_refer(erp, user, ap_no, hold_cd, refer_to, note=""):
    h = erp.q1("SELECT * FROM ap_hold_log WHERE ap_no=? AND hold_cd=? AND released_on IS NULL", ap_no, hold_cd)
    if not h:
        raise LedgerlineError("ERR-AP-0302", "HOLD NOT OPEN")
    refer_to = refer_to.upper()
    if not erp.user(refer_to):
        raise LedgerlineError("ERR-SEC-0003", "NO SUCH USER")
    if not erp.sp("sp_ap_hold_auth", refer_to, hold_cd) or erp.user(refer_to)["role_cd"] == "SYS-ADMIN":
        raise LedgerlineError("ERR-AP-0306", f"{refer_to} CANNOT RELEASE {hold_cd}")
    erp.sp("sp_ap_route", "APHLD", ap_no, refer_to, user, hold_cd)
    return {"ap_no": ap_no, "referred_to": refer_to, "_msg": f"{ap_no} {hold_cd} REFERRED TO {refer_to}"}


@service("ap_hold_release", "HOLD RELEASE", [F("ap_no", req=True, desc="AP NO"), F("hold_cd", req=True, desc="HOLD CD"),
                                             F("reason", req=True, desc="REASON")], kind="write", screen=SCR_HOLD)
def ap_hold_release(erp, user, ap_no, hold_cd, reason):
    i = erp.q1("SELECT * FROM ap_inv WHERE ap_no=?", ap_no)
    if not i:
        raise LedgerlineError("ERR-AP-0001", "AP DOC NOT FOUND")
    h = erp.q1("SELECT * FROM ap_hold_log WHERE ap_no=? AND hold_cd=? AND released_on IS NULL", ap_no, hold_cd)
    if not h:
        raise LedgerlineError("ERR-AP-0302", "HOLD NOT OPEN")
    if not erp.sp("sp_ap_hold_auth", user, hold_cd):
        raise LedgerlineError("ERR-AP-0305", f"NOT AUTHORISED TO RELEASE {hold_cd}")
    erp.x("UPDATE ap_hold_log SET released_by=?, released_on=?, reason=? WHERE id=?", user, erp.now(), reason, h["id"])
    erp.x("UPDATE approval SET status='APPROVED', decided_on=?, comment=? WHERE doc_type='APHLD' AND doc_no=? "
          "AND comment=? AND status='PENDING'", erp.now(), f"{hold_cd}: {reason}", ap_no, hold_cd)
    left = erp.q1("SELECT hold_cd FROM ap_hold_log WHERE ap_no=? AND released_on IS NULL ORDER BY id", ap_no)
    if left:
        erp.x("UPDATE ap_inv SET hold_cd=? WHERE ap_no=?", left["hold_cd"], ap_no)
        return {"ap_no": ap_no, "status": "HD", "hold_cd": left["hold_cd"], "_msg": f"{hold_cd} RELEASED"}
    if i["inv_type"] == "NPO":
        erp.x("UPDATE ap_inv SET status='PA', hold_cd=NULL WHERE ap_no=?", ap_no)
        owner = erp.q1("SELECT owner FROM cost_centre WHERE cc_cd=?", i["cc_cd"])["owner"]
        erp.sp("sp_ap_route", "APINV", ap_no, owner, user, f"Non-PO invoice {i['sup_inv_no']}")
        return {"ap_no": ap_no, "status": "PA", "_msg": f"{hold_cd} RELEASED"}
    erp.sp("sp_ap_post", ap_no)
    return {"ap_no": ap_no, "status": "PO", "_msg": f"{hold_cd} RELEASED"}


@service("ap_approve", "AP APPROVE", [F("doc_no", req=True, desc="AP NO/PAY NO"), F("decision", req=True, desc="A/R"),
                                      F("comment", desc="COMMENT")], kind="write", screen=SCR_PAY)
def ap_approve(erp, user, doc_no, decision, comment=""):
    a = erp.q1("SELECT * FROM approval WHERE doc_no=? AND doc_type IN ('APINV','APPAY') AND status='PENDING' "
               "ORDER BY appr_id DESC", doc_no)
    if not a:
        raise LedgerlineError("ERR-AP-0402", "NOTHING PENDING FOR DOC")
    if a["approver"] != user and erp.user(user)["role_cd"] != "SYS-ADMIN":
        raise LedgerlineError("ERR-AP-0404", f"NOT YOUR APPROVAL ({a['approver']})")
    ok = decision.upper().startswith("A")
    doc = erp.q1("SELECT entered_by who FROM ap_inv WHERE ap_no=?", doc_no) if a["doc_type"] == "APINV" else \
        erp.q1("SELECT sched_by who FROM ap_pay WHERE pay_no=?", doc_no)
    if doc["who"] == user and erp.user(user)["role_cd"] != "SYS-ADMIN":  # the superuser passes every check
        raise LedgerlineError("ERR-APR-0003", "SELF APPROVAL NOT ALLOWED")
    erp.x("UPDATE approval SET status=?, decided_on=?, comment=? WHERE appr_id=?",
          "APPROVED" if ok else "REJECTED", erp.now(), comment, a["appr_id"])
    if a["doc_type"] == "APINV":
        i = erp.q1("SELECT * FROM ap_inv WHERE ap_no=?", doc_no)
        if not ok:
            erp.x("UPDATE ap_inv SET status='RJ' WHERE ap_no=?", doc_no)
            return {"doc_no": doc_no, "status": "RJ", "_msg": f"{doc_no} REJECTED"}
        erp.x("UPDATE ap_inv SET approved_by=? WHERE ap_no=?", user, doc_no)
        erp.sp("sp_budget_commit", i["cc_cd"], i["gross"])  # shared engine: the spend lands on the cost centre
        erp.sp("sp_ap_post", doc_no)
        return {"doc_no": doc_no, "status": "PO", "_msg": f"{doc_no} APPROVED"}
    st = "SC" if ok else "CN"
    erp.x("UPDATE ap_pay SET status=?, approved_by=? WHERE pay_no=?", st, user if ok else None, doc_no)
    return {"doc_no": doc_no, "status": st, "_msg": f"{doc_no} {'APPROVED' if ok else 'REJECTED'}"}


@service("ap_pay_sched", "PAYMENT PROPOSAL", [F("ap_no", req=True, desc="AP NO"), F("pay_dt", "date", True, "PAY DT"),
                                              F("early_rsn", desc="EARLY PAY REASON"), F("client_ref", desc="CLIENT REF")],
         kind="write", screen=SCR_PAY)
def ap_pay_sched(erp, user, ap_no, pay_dt, early_rsn=None, client_ref=None):
    i = erp.q1("SELECT * FROM ap_inv WHERE ap_no=?", ap_no)
    if not i:
        raise LedgerlineError("ERR-AP-0001", "AP DOC NOT FOUND")
    if i["status"] != "PO":
        raise LedgerlineError("ERR-AP-0410", f"INVOICE NOT CLEAR FOR PAYMENT ({i['status']})")
    run = erp.q1("SELECT * FROM ap_run WHERE run_dt=?", pay_dt)
    if not run:
        raise LedgerlineError("ERR-AP-0412", "PAY DT NOT A RUN DATE")
    if erp.today > run["cutoff_dt"]:
        raise LedgerlineError("ERR-AP-0413", "RUN CUT-OFF PASSED")
    if erp.q1("SELECT 1 FROM ap_pay WHERE ap_no=? AND status NOT IN ('CN')", ap_no):
        raise LedgerlineError("ERR-AP-0415", "PAYMENT ALREADY PROPOSED")
    pay_no = erp.sp("sp_doc_no_next", "APPAY")
    status, warn = "SC", None
    if pay_dt < i["due_dt"]:
        if early_rsn:
            status = "PA"
        else:
            status, warn = "PK", "W-AP-311"  # early, no reason: parked, silently, outside every run
    erp.x("INSERT INTO ap_pay VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", pay_no, ap_no, pay_dt, i["gross"], status, early_rsn,
          user, erp.now(), None, None, warn, client_ref)
    if status == "PA":
        ctrl = erp.q1("SELECT user_id FROM app_user WHERE role_cd='FIN-CTRL' ORDER BY user_id")["user_id"]
        erp.sp("sp_ap_route", "APPAY", pay_no, ctrl, user, f"Early payment of {ap_no} on {pay_dt}: {early_rsn}")
    return {"pay_no": pay_no, "status": status, "_msg": f"{pay_no} SCHEDULED"}  # the reply never says parked


@service("ap_pay_run", "PAYMENT RUN", [F("run_dt", "date", True, "RUN DT")], kind="write", screen=SCR_PAY)
def ap_pay_run(erp, user, run_dt):
    run = erp.q1("SELECT * FROM ap_run WHERE run_dt=?", run_dt)
    if not run:
        raise LedgerlineError("ERR-AP-0412", "NOT A RUN DATE")
    if run_dt > erp.today:
        raise LedgerlineError("ERR-AP-0520", "RUN DT IN FUTURE")
    if run["status"] == "DONE":
        raise LedgerlineError("ERR-AP-0521", "RUN ALREADY DONE")
    pays = erp.q("SELECT * FROM ap_pay WHERE pay_dt=? AND status='SC'", run_dt)
    for p in pays:
        erp.sp("sp_ap_pay_exec", p)
    erp.x("UPDATE ap_run SET status='DONE' WHERE run_dt=?", run_dt)
    return {"paid": len(pays), "amount": round(sum(p["amount"] for p in pays), 2), "_msg": f"RUN {run_dt} DONE"}
