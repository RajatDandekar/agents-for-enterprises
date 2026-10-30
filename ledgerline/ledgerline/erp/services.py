"""The 38 services of Ledgerline's purchasing module, exactly as terse as the real thing.

Payloads are flat (at most 12 fields). Field names and descriptions are the legacy ones; the data
dictionary (docs/data-dictionary.md) explains them. Responses come back in the legacy envelope
{rc, err_cd, msg, data}, with status codes DR, PA, AP, RL, RJ, CN, CL.
"""
from __future__ import annotations

from .engine import LedgerlineError, service

F = lambda name, t="str", req=False, desc="": (name, t, req, desc)  # noqa: E731


def _like(text: str, q: str) -> bool:
    t = text.lower()
    t2 = t.replace(" ", "")
    return all(tok in t or tok in t2 for tok in q.lower().split())


# ----------------------------------------------------------------------------- masters: items
@service("itm_search", "ITEM ENQUIRY", [F("q", req=True, desc="SEARCH TEXT")], screen="INV-ITM-03")
def itm_search(erp, user, q):
    rows = [r for r in erp.q("SELECT itm_cd,descr,uom_cd,active FROM item") if _like(r["itm_cd"] + " " + r["descr"], q)]
    return {"rows": rows[:20], "_msg": f"{len(rows)} ROWS FOUND"}


@service("itm_get", "ITEM MASTER GET", [F("itm_cd", req=True, desc="ITEM CD")])
def itm_get(erp, user, itm_cd):
    r = erp.q1("SELECT * FROM item WHERE itm_cd=?", itm_cd)
    if not r:
        raise LedgerlineError("ERR-ITM-0010", "ITEM NOT FOUND")
    return r


# ----------------------------------------------------------------------------- masters: suppliers
@service("sup_search", "SUPPLIER ENQUIRY", [F("q", req=True, desc="NAME LIKE")], screen="PUR-SUP-03")
def sup_search(erp, user, q):
    rows = erp.q("SELECT sup_cd,name,city,state,status FROM supplier WHERE lower(name) LIKE ?", f"%{q.lower()}%")
    return {"rows": rows, "_msg": f"{len(rows)} ROWS FOUND"}


@service("sup_get", "SUPPLIER MASTER GET", [F("sup_cd", req=True, desc="SUP CD")])
def sup_get(erp, user, sup_cd):
    r = erp.q1("SELECT * FROM supplier WHERE sup_cd=?", sup_cd)
    if not r:
        raise LedgerlineError("ERR-SUP-0030", "SUPPLIER NOT FOUND")
    return r


@service("sup_create", "SUPPLIER CREATE", [F("name", req=True, desc="SUP NAME"), F("city", req=True, desc="CITY"),
                                           F("state", req=True, desc="COUNTRY CD (2)"), F("vat_no", desc="VAT number"),
                                           F("pt_cd", desc="PAY TERM CD")], kind="write", screen="PUR-SUP-01")
def sup_create(erp, user, name, city, state, vat_no=None, pt_cd="N30"):
    if vat_no and erp.q1("SELECT 1 FROM supplier WHERE vat_no=?", vat_no):
        raise LedgerlineError("ERR-SUP-0118", "VAT NO ALREADY REGISTERED")
    initials = "".join(w[0] for w in name.replace("&", " ").split() if w[0].isalpha())[:3].upper()
    n = erp.q1("SELECT count(*) n FROM supplier")["n"] + 101
    sup_cd = f"{initials}-{city[:3].upper()}-{n:04d}"
    erp.x("INSERT INTO supplier VALUES (?,?,?,?,?,?,?,?,?)", sup_cd, name, vat_no, state.upper()[:2], city,
          "ACTIVE", pt_cd or "N30", user, erp.today)
    return {"sup_cd": sup_cd, "_msg": f"SUPPLIER {sup_cd} CREATED"}


@service("sup_cert_get", "SUPPLIER CERT LIST", [F("sup_cd", req=True, desc="SUP CD")])
def sup_cert_get(erp, user, sup_cd):
    return {"rows": erp.q("SELECT cert_type,doc_ref,valid_to FROM sup_cert WHERE sup_cd=?", sup_cd)}


@service("sup_cert_upload", "SUPPLIER CERT UPLOAD",
         [F("sup_cd", req=True, desc="SUP CD"), F("cert_type", req=True, desc="CERT TYPE"),
          F("doc_ref", req=True, desc="DOC REF"), F("valid_to", "date", True, desc="VALID TO")], kind="write")
def sup_cert_upload(erp, user, sup_cd, cert_type, doc_ref, valid_to):
    if not erp.q1("SELECT 1 FROM supplier WHERE sup_cd=?", sup_cd):
        raise LedgerlineError("ERR-SUP-0030", "SUPPLIER NOT FOUND")
    erp.x("INSERT INTO sup_cert VALUES (?,?,?,?,?,?)", sup_cd, cert_type.upper(), doc_ref, valid_to, user, erp.today)
    return {"_msg": "CERT SAVED"}


@service("sup_rate_get", "RATE CONTRACT GET", [F("sup_cd", req=True, desc="SUP CD"), F("itm_cd", req=True, desc="ITEM CD")])
def sup_rate_get(erp, user, sup_cd, itm_cd):
    rows = erp.q("SELECT rate,valid_from,valid_to FROM sup_rate WHERE sup_cd=? AND itm_cd=? ORDER BY valid_from", sup_cd, itm_cd)
    cur = [r for r in rows if r["valid_from"] <= erp.today <= r["valid_to"]]
    return {"current": cur[-1] if cur else None, "rows": rows}


# ----------------------------------------------------------------------------- masters: other
@service("cc_list", "COST CENTRE LIST")
def cc_list(erp, user):
    return {"rows": erp.q("SELECT cc_cd,name,status FROM cost_centre")}


@service("cc_get", "COST CENTRE GET", [F("cc_cd", req=True, desc="CC CD")])
def cc_get(erp, user, cc_cd):
    r = erp.q1("SELECT * FROM cost_centre WHERE cc_cd=?", cc_cd)
    if not r:
        raise LedgerlineError("ERR-CC-0009", "COST CENTRE NOT FOUND")
    return r


@service("whs_list", "WAREHOUSE LIST")
def whs_list(erp, user):
    return {"rows": erp.q("SELECT * FROM warehouse")}


@service("tax_list", "TAX CODE LIST")
def tax_list(erp, user):
    return {"rows": erp.q("SELECT * FROM tax_code")}


@service("pt_list", "PAY TERM LIST")
def pt_list(erp, user):
    return {"rows": erp.q("SELECT * FROM pay_term")}


@service("usr_get", "USER GET", [F("user_id", req=True, desc="USER ID")])
def usr_get(erp, user, user_id):
    r = erp.q1("SELECT user_id,name,role_cd,ou_cd,appr_limit,manager_id,default_cc FROM app_user WHERE user_id=?", user_id.upper())
    if not r:
        raise LedgerlineError("ERR-SEC-0003", "NO SUCH USER")
    return r


@service("usr_roles", "USER ROLE SERVICES", [F("user_id", req=True, desc="USER ID")])
def usr_roles(erp, user, user_id):
    u = erp.user(user_id.upper())
    if not u:
        raise LedgerlineError("ERR-SEC-0003", "NO SUCH USER")
    return {"role_cd": u["role_cd"], "svcs": [r["svc"] for r in erp.q("SELECT svc FROM role_perm WHERE role_cd=?", u["role_cd"])]}


# ----------------------------------------------------------------------------- inventory
@service("stk_query", "STOCK STATUS ENQUIRY", [F("itm_cd", req=True, desc="ITEM CD"), F("whs_cd", desc="WHS CD")],
         screen="INV-STK-02")
def stk_query(erp, user, itm_cd, whs_cd="WH-MAN-STR"):
    s = erp.q1("SELECT * FROM stock WHERE itm_cd=? AND whs_cd=?", itm_cd, whs_cd)
    i = erp.q1("SELECT avg_daily_issue, reorder_lvl FROM item WHERE itm_cd=?", itm_cd)
    if not s or not i:
        raise LedgerlineError("ERR-STK-0001", "NO STOCK RECORD")
    adi = i["avg_daily_issue"]
    return {**s, "avg_daily_issue": adi, "reorder_lvl": i["reorder_lvl"],
            "cover_days": int((s["on_hand"] - s["allocated"]) / adi) if adi else None}


@service("stk_ledger", "STOCK LEDGER", [F("itm_cd", req=True, desc="ITEM CD")])
def stk_ledger(erp, user, itm_cd):
    return {"rows": erp.q("SELECT dt,whs_cd,txn,qty,ref FROM stk_ledger WHERE itm_cd=? ORDER BY id", itm_cd)}


@service("stk_reorder_list", "ITEMS BELOW REORDER LEVEL")
def stk_reorder_list(erp, user):
    return {"rows": erp.q("SELECT s.itm_cd, i.descr, s.whs_cd, s.on_hand, i.reorder_lvl FROM stock s JOIN item i "
                          "ON i.itm_cd=s.itm_cd WHERE s.on_hand + s.on_order < i.reorder_lvl")}


# ----------------------------------------------------------------------------- purchase request
@service("pr_fetch", "PR DEFAULTS", [F("itm_cd", req=True, desc="ITEM CD")], screen="PUR-PR-01")
def pr_fetch(erp, user, itm_cd):
    itm = erp.q1("SELECT * FROM item WHERE itm_cd=?", itm_cd)
    if not itm:
        raise LedgerlineError("ERR-ITM-0010", "ITEM NOT FOUND")
    last = erp.q1("SELECT l.rate FROM po_line l JOIN po_hdr h ON h.po_no=l.po_no WHERE l.itm_cd=? AND h.status='RL' "
                  "ORDER BY h.created_on DESC", itm_cd)
    u = erp.user(user)
    return {"uom_cd": itm["uom_cd"], "whs_cd": "WH-MAN-STR", "cc_cd": u["default_cc"],
            "est_rate": last["rate"] if last else 0.0, "pr_type": "STD"}


@service("pr_save", "PR SAVE", [F("pr_type", desc="PR TYPE"), F("cc_cd", req=True, desc="CC CD"),
                                F("need_dt", "date", True, "NEED DT"), F("itm_cd", req=True, desc="ITEM CD"),
                                F("qty", "int", True, "QTY"), F("whs_cd", desc="WHS CD"),
                                F("est_rate", "float", desc="EST RATE"), F("remarks", desc="REMARKS")],
         kind="write", screen="PUR-PR-01")
def pr_save(erp, user, cc_cd, need_dt, itm_cd, qty, pr_type="STD", whs_cd="WH-MAN-STR", est_rate=None, remarks=""):
    if est_rate is None:
        est_rate = pr_fetch(erp, user, itm_cd)["est_rate"]
    r = erp.sp("sp_pr_save", user, pr_type, cc_cd, need_dt, itm_cd, qty, whs_cd, est_rate, remarks)
    return {**r, "status": "DR", "_msg": f"{r['pr_no']} SAVED"}


@service("pr_submit", "PR SUBMIT", [F("pr_no", req=True, desc="PR NO")], kind="write", screen="PUR-PR-01")
def pr_submit(erp, user, pr_no):
    pr = erp.q1("SELECT * FROM pr_hdr WHERE pr_no=?", pr_no)
    if not pr:
        raise LedgerlineError("ERR-PR-0001", "PR NOT FOUND")
    if pr["status"] != "DR":
        raise LedgerlineError("ERR-PR-0007", f"PR NOT IN DRAFT ({pr['status']})")
    if pr["est_value"] <= erp.user(user)["appr_limit"]:
        erp.x("UPDATE pr_hdr SET status='AP', approved_by=? WHERE pr_no=?", user, pr_no)
        return {"pr_no": pr_no, "status": "AP", "_msg": f"{pr_no} APPROVED (WITHIN LIMIT)"}
    approver = erp.sp("sp_appr_route", "PR", pr_no, user, pr["est_value"])
    erp.x("UPDATE pr_hdr SET status='PA' WHERE pr_no=?", pr_no)
    return {"pr_no": pr_no, "status": "PA", "approver": approver, "_msg": f"{pr_no} SUBMITTED FOR APPROVAL"}


@service("pr_approve", "PR APPROVE/REJECT", [F("pr_no", req=True, desc="PR NO"), F("decision", req=True, desc="A/R"),
                                             F("comment", desc="COMMENT")], kind="write", screen="PUR-PR-04")
def pr_approve(erp, user, pr_no, decision, comment=""):
    pr = erp.q1("SELECT * FROM pr_hdr WHERE pr_no=?", pr_no)
    if not pr:
        raise LedgerlineError("ERR-PR-0001", "PR NOT FOUND")
    if pr["status"] != "PA":
        raise LedgerlineError("ERR-PR-0008", f"PR NOT PENDING ({pr['status']})")
    if pr["raised_by"] == user:
        raise LedgerlineError("ERR-APR-0003", "SELF APPROVAL NOT ALLOWED")
    if erp.user(user)["appr_limit"] < pr["est_value"]:
        raise LedgerlineError("ERR-APR-0004", "VALUE ABOVE YOUR LIMIT")
    st = "AP" if decision.upper().startswith("A") else "RJ"
    erp.x("UPDATE pr_hdr SET status=?, approved_by=? WHERE pr_no=?", st, user if st == "AP" else None, pr_no)
    erp.x("UPDATE approval SET status=?, decided_on=?, comment=? WHERE doc_no=? AND status='PENDING'",
          "APPROVED" if st == "AP" else "REJECTED", erp.now(), comment, pr_no)
    return {"pr_no": pr_no, "status": st, "_msg": f"{pr_no} {'APPROVED' if st == 'AP' else 'REJECTED'} BY {user}"}


@service("pr_get", "PR GET", [F("pr_no", req=True, desc="PR NO")])
def pr_get(erp, user, pr_no):
    pr = erp.q1("SELECT * FROM pr_hdr WHERE pr_no=?", pr_no)
    if not pr:
        raise LedgerlineError("ERR-PR-0001", "PR NOT FOUND")
    return {**pr, "lines": erp.q("SELECT * FROM pr_line WHERE pr_no=?", pr_no)}


@service("pr_search", "PR LIST", [F("status", desc="STATUS"), F("raised_by", desc="USER ID")])
def pr_search(erp, user, status=None, raised_by=None):
    sql, args = "SELECT pr_no,cc_cd,need_dt,status,raised_by,est_value,remarks FROM pr_hdr WHERE 1=1", []
    if status:
        sql += " AND status=?"; args.append(status)
    if raised_by:
        sql += " AND raised_by=?"; args.append(raised_by)
    return {"rows": erp.q(sql + " ORDER BY pr_no DESC", *args)}


# ----------------------------------------------------------------------------- purchase order
@service("po_fetch", "PO DEFAULTS", [F("sup_cd", req=True, desc="SUP CD"), F("itm_cd", req=True, desc="ITEM CD"),
                                     F("pr_no", desc="PR NO")], screen="PUR-PO-01")
def po_fetch(erp, user, sup_cd, itm_cd, pr_no=None):
    sup = erp.q1("SELECT * FROM supplier WHERE sup_cd=?", sup_cd)
    if not sup:
        raise LedgerlineError("ERR-SUP-0030", "SUPPLIER NOT FOUND")
    rate = sup_rate_get(erp, user, sup_cd, itm_cd)["current"]
    if not rate:
        last = erp.q1("SELECT l.rate FROM po_line l JOIN po_hdr h ON h.po_no=l.po_no WHERE h.sup_cd=? AND l.itm_cd=? "
                      "ORDER BY h.created_on DESC", sup_cd, itm_cd)
        rate = {"rate": last["rate"] if last else None}
    tok = erp.sp("sp_fetch_tok_new", user, "PUR-PO-01", f"{sup_cd}|{itm_cd}")
    out = {"rate": rate["rate"], "tax_cd": "VAT20-UK", "pt_cd": sup["pt_cd"], "whs_cd": "WH-MAN-STR",
           "fetch_tok": tok}  # tax code defaults to the plant's own state, whatever the supplier's
    if pr_no:
        pr = erp.q1("SELECT * FROM pr_hdr WHERE pr_no=?", pr_no)
        if pr:
            line = erp.q1("SELECT * FROM pr_line WHERE pr_no=?", pr_no)
            out.update(cc_cd=pr["cc_cd"], need_dt=pr["need_dt"], qty=line["qty"])
    return out


@service("po_save", "PO SAVE", [F("po_type", desc="STD/DIR"), F("pr_no", desc="PR NO"), F("sup_cd", req=True, desc="SUP CD"),
                                F("itm_cd", req=True, desc="ITEM CD"), F("qty", "int", True, "QTY"),
                                F("rate", "float", True, "RATE"), F("tax_cd", req=True, desc="TAX CD"),
                                F("cc_cd", req=True, desc="CC CD"), F("need_dt", "date", True, "NEED DT"),
                                F("whs_cd", desc="WHS CD"), F("fetch_tok", desc="FETCH TOKEN"),
                                F("client_ref", desc="CLIENT REF")], kind="write", screen="PUR-PO-01")
def po_save(erp, user, **a):
    a.setdefault("po_type", "STD")
    erp.sp("sp_fetch_tok_chk", user, a.get("fetch_tok"), "PUR-PO-01", f"{a['sup_cd']}|{a['itm_cd']}")
    r = erp.sp("sp_po_hdr_save", user, a)
    return {**r, "_msg": f"{r['doc_no']} SAVED"}  # the status is in the data; the message never mentions it


@service("po_get", "PO GET", [F("po_no", req=True, desc="PO NO")])
def po_get(erp, user, po_no):
    h = erp.q1("SELECT * FROM po_hdr WHERE po_no=?", po_no)
    if not h:
        raise LedgerlineError("ERR-PO-0001", "PO NOT FOUND")
    return {**h, "lines": erp.q("SELECT * FROM po_line WHERE po_no=?", po_no)}


@service("po_search", "PO LIST", [F("sup_cd", desc="SUP CD"), F("itm_cd", desc="ITEM CD"), F("status", desc="STATUS"),
                                  F("client_ref", desc="CLIENT REF"), F("from_dt", "date", desc="FROM DT")])
def po_search(erp, user, sup_cd=None, itm_cd=None, status=None, client_ref=None, from_dt=None):
    sql = ("SELECT h.po_no,h.sup_cd,l.itm_cd,l.qty,l.rate,h.gross_value,h.status,h.created_on,h.created_by,h.client_ref "
           "FROM po_hdr h JOIN po_line l ON l.po_no=h.po_no WHERE 1=1")
    args = []
    for col, v in (("h.sup_cd", sup_cd), ("l.itm_cd", itm_cd), ("h.status", status), ("h.client_ref", client_ref)):
        if v:
            sql += f" AND {col}=?"; args.append(v)
    if from_dt:
        sql += " AND h.created_on>=?"; args.append(from_dt)
    return {"rows": erp.q(sql + " ORDER BY h.po_no DESC", *args)}


@service("po_hist", "PO HISTORY BY ITEM", [F("itm_cd", req=True, desc="ITEM CD"), F("sup_cd", desc="SUP CD")],
         screen="PUR-POH-02")
def po_hist(erp, user, itm_cd, sup_cd=None):
    sql = ("SELECT h.po_no,h.sup_cd,s.name sup_name,l.qty,l.rate,h.created_on,h.status FROM po_hdr h JOIN po_line l "
           "ON l.po_no=h.po_no JOIN supplier s ON s.sup_cd=h.sup_cd WHERE l.itm_cd=? AND h.status='RL'")
    args = [itm_cd]
    if sup_cd:
        sql += " AND h.sup_cd=?"; args.append(sup_cd)
    return {"rows": erp.q(sql + " ORDER BY h.created_on DESC LIMIT 10", *args)}


@service("po_pending_appr", "APPROVAL INBOX", [F("approver", desc="USER ID")])
def po_pending_appr(erp, user, approver=None):
    return {"rows": erp.q("SELECT appr_id,doc_type,doc_no,requested_by,requested_on FROM approval WHERE approver=? "
                          "AND status='PENDING'", (approver or user).upper())}


@service("po_approve", "PO APPROVE", [F("po_no", req=True, desc="PO NO"), F("comment", desc="COMMENT")],
         kind="write", screen="PUR-POA-04")
def po_approve(erp, user, po_no, comment=""):
    h = erp.q1("SELECT * FROM po_hdr WHERE po_no=?", po_no)
    if not h:
        raise LedgerlineError("ERR-PO-0001", "PO NOT FOUND")
    if h["status"] != "PA":
        raise LedgerlineError("ERR-PO-0702", f"PO NOT PENDING APPROVAL ({h['status']})")
    if h["created_by"] == user:
        raise LedgerlineError("ERR-APR-0003", "SELF APPROVAL NOT ALLOWED")
    if erp.user(user)["appr_limit"] < h["gross_value"]:
        raise LedgerlineError("ERR-APR-0004", "VALUE ABOVE YOUR LIMIT")
    erp.x("UPDATE po_hdr SET status='AP', approved_by=?, approved_on=? WHERE po_no=?", user, erp.now(), po_no)
    erp.x("UPDATE approval SET status='APPROVED', decided_on=?, comment=? WHERE doc_no=? AND status='PENDING'",
          erp.now(), comment, po_no)
    return {"po_no": po_no, "status": "AP", "_msg": f"{po_no} APPROVED"}


@service("po_reject", "PO REJECT", [F("po_no", req=True, desc="PO NO"), F("comment", req=True, desc="COMMENT")],
         kind="write", screen="PUR-POA-04")
def po_reject(erp, user, po_no, comment):
    h = erp.q1("SELECT * FROM po_hdr WHERE po_no=?", po_no)
    if not h or h["status"] != "PA":
        raise LedgerlineError("ERR-PO-0702", "PO NOT PENDING APPROVAL")
    erp.x("UPDATE po_hdr SET status='RJ' WHERE po_no=?", po_no)
    erp.x("UPDATE budget SET committed=round(committed-?,2) WHERE cc_cd=? AND period='2026-Q4'", h["gross_value"], h["cc_cd"])
    erp.x("UPDATE approval SET status='REJECTED', decided_on=?, comment=? WHERE doc_no=? AND status='PENDING'",
          erp.now(), comment, po_no)
    return {"po_no": po_no, "status": "RJ", "_msg": f"{po_no} REJECTED"}


@service("po_release", "PO RELEASE", [F("po_no", req=True, desc="PO NO")], kind="write", screen="PUR-POR-05")
def po_release(erp, user, po_no):
    h = erp.q1("SELECT * FROM po_hdr WHERE po_no=?", po_no)
    if not h:
        raise LedgerlineError("ERR-PO-0001", "PO NOT FOUND")
    if h["status"] != "AP":
        raise LedgerlineError("ERR-PO-0715", f"DOCUMENT NOT IN RELEASABLE STATUS ({h['status']})")
    erp.sp("sp_po_status_set", po_no, "RL")
    erp.x("UPDATE po_hdr SET released_on=? WHERE po_no=?", erp.now(), po_no)
    line = erp.q1("SELECT * FROM po_line WHERE po_no=?", po_no)
    erp.sp("sp_stk_onorder_upd", line["itm_cd"], h["whs_cd"], line["qty"])
    sup = erp.q1("SELECT * FROM supplier WHERE sup_cd=?", h["sup_cd"])
    erp.sp("sp_ntf_enqueue", "EMAIL", f"orders@{h['sup_cd'].lower()}.example", f"Purchase order {po_no}",
           f"{sup['name']}: please supply {line['qty']} x {line['itm_cd']} by {h['need_dt']}.")
    return {"po_no": po_no, "status": "RL", "_msg": f"{po_no} RELEASED"}


@service("po_amend", "PO AMEND", [F("po_no", req=True, desc="PO NO"), F("qty", "int", desc="QTY"),
                                  F("need_dt", "date", desc="NEED DT"), F("cc_cd", desc="CC CD")],
         kind="write", screen="PUR-POM-06")
def po_amend(erp, user, po_no, qty=None, need_dt=None, cc_cd=None):
    h = erp.q1("SELECT * FROM po_hdr WHERE po_no=?", po_no)
    if not h:
        raise LedgerlineError("ERR-PO-0001", "PO NOT FOUND")
    if h["status"] in ("CN", "RJ", "CL"):
        raise LedgerlineError("ERR-PO-0801", f"PO CLOSED ({h['status']})")
    line = erp.q1("SELECT * FROM po_line WHERE po_no=?", po_no)
    qty = qty or line["qty"]
    need_dt = need_dt or h["need_dt"]
    cc_cd = cc_cd or h["cc_cd"]
    basic = round(qty * line["rate"], 2)
    tax, gross = erp.sp("sp_tax_compute", basic, h["tax_cd"])
    if h["status"] in ("AP", "PA", "RL"):  # give back what this order had committed before re-checking
        erp.x("UPDATE budget SET committed=round(committed-?,2) WHERE cc_cd=? AND period='2026-Q4'", h["gross_value"], h["cc_cd"])
    state = erp.sp("sp_budget_chk", cc_cd, gross)
    status, warn = h["status"], h["warn_cd"]
    if state == "CLOSED":
        status, warn = ("DR", "W-CC-114") if h["status"] != "RL" else ("RL", "W-CC-114")
    else:
        warn = None
        pr = erp.q1("SELECT * FROM pr_hdr WHERE pr_no=?", h["pr_no"] or "")
        covered_by = None
        if gross <= erp.user(user)["appr_limit"]:
            covered_by = user
        elif pr and pr["approved_by"] and erp.user(pr["approved_by"])["appr_limit"] >= gross:
            covered_by = pr["approved_by"]  # the request's approval still covers the order
        elif h["approved_by"] and gross <= h["gross_value"]:
            covered_by = h["approved_by"]
        within = covered_by is not None
        if within and h["status"] != "RL":
            erp.x("UPDATE po_hdr SET approved_by=?, approved_on=? WHERE po_no=?", covered_by, erp.now(), po_no)
        if h["status"] in ("DR", "AP", "PA"):
            status = "AP" if within else "PA"
        elif h["status"] == "RL" and not within:
            status = "PA"  # a released order that grows goes back for approval
        erp.sp("sp_budget_commit", cc_cd, gross)
        if status == "PA" and h["status"] != "PA":
            erp.sp("sp_appr_route", "PO", po_no, user, gross)
    erp.x("UPDATE po_hdr SET need_dt=?, cc_cd=?, basic_value=?, tax_value=?, gross_value=?, status=?, warn_cd=? "
          "WHERE po_no=?", need_dt, cc_cd, basic, tax, gross, status, warn, po_no)
    erp.x("UPDATE po_line SET qty=? WHERE po_no=?", qty, po_no)
    return {"po_no": po_no, "status": status, "_msg": f"{po_no} AMENDED"}


@service("po_cancel", "PO CANCEL", [F("po_no", req=True, desc="PO NO"), F("reason", req=True, desc="REASON")],
         kind="write", screen="PUR-POM-06")
def po_cancel(erp, user, po_no, reason):
    h = erp.q1("SELECT * FROM po_hdr WHERE po_no=?", po_no)
    if not h:
        raise LedgerlineError("ERR-PO-0001", "PO NOT FOUND")
    if h["status"] in ("CN", "CL"):
        raise LedgerlineError("ERR-PO-0801", f"PO CLOSED ({h['status']})")
    if h["status"] in ("AP", "PA", "RL"):
        erp.x("UPDATE budget SET committed=round(committed-?,2) WHERE cc_cd=? AND period='2026-Q4'", h["gross_value"], h["cc_cd"])
    if h["status"] == "RL":
        line = erp.q1("SELECT * FROM po_line WHERE po_no=?", po_no)
        erp.sp("sp_stk_onorder_upd", line["itm_cd"], h["whs_cd"], -line["qty"])
    erp.sp("sp_po_status_set", po_no, "CN")
    erp.x("UPDATE approval SET status='WITHDRAWN' WHERE doc_no=? AND status='PENDING'", po_no)
    return {"po_no": po_no, "status": "CN", "_msg": f"{po_no} CANCELLED"}


# ----------------------------------------------------------------------------- shared engines
@service("tax_compute", "TAX ENGINE", [F("basic", "float", True, "BASIC VALUE"), F("tax_cd", req=True, desc="TAX CD")])
def tax_compute(erp, user, basic, tax_cd):
    t, g = erp.sp("sp_tax_compute", basic, tax_cd)
    return {"tax": t, "gross": g}


@service("bud_check", "BUDGET CHECK", [F("cc_cd", req=True, desc="CC CD"), F("amount", "float", True, "AMOUNT")])
def bud_check(erp, user, cc_cd, amount):
    state = erp.sp("sp_budget_chk", cc_cd, amount)
    b = erp.q1("SELECT * FROM budget WHERE cc_cd=? AND period='2026-Q4'", cc_cd)
    return {"cc_state": state, "available": round(b["amount"] - b["committed"], 2) if b else None}


@service("ntf_send", "NOTIFICATION SEND", [F("channel", req=True, desc="EMAIL/SMS"), F("recipient", req=True, desc="TO"),
                                           F("msg", req=True, desc="TEXT")], kind="write")
def ntf_send(erp, user, channel, recipient, msg):
    erp.sp("sp_ntf_enqueue", channel.upper(), recipient, f"Message from {user}", msg)
    return {"_msg": "QUEUED"}
