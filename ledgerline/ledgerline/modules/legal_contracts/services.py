"""Legal · contracts: the nine services, as terse as purchasing's. Status codes: PK, LR, PS, EX, RJ."""
from __future__ import annotations

from ...erp.engine import LedgerlineError, service
from .._kit import F


@service("ct_party_find", "PARTY ENQUIRY", [F("q", desc="NAME LIKE"), F("vat_no", desc="VAT number")], screen="LEG-REQ-01")
def ct_party_find(erp, user, q=None, vat_no=None):
    if not q and not vat_no:
        raise LedgerlineError("ERR-SYS-0421", "Q OR VAT number MANDATORY")
    sql, args = "SELECT party_cd,name,city,state,status,sup_cd,nda_till FROM ct_party WHERE 1=1", []
    if q:
        sql += " AND lower(name) LIKE ?"
        args.append(f"%{q.lower()}%")
    if vat_no:
        sql += " AND vat_no=?"
        args.append(vat_no.upper())
    rows = erp.q(sql + " ORDER BY party_cd", *args)
    return {"rows": rows, "_msg": f"{len(rows)} ROWS FOUND"}


@service("ct_party_save", "PARTY SAVE", [F("party_cd", desc="PARTY CD (BLANK=NEW)"), F("name", desc="PARTY NAME"),
                                         F("city", desc="CITY"), F("state", desc="COUNTRY CD (2)"), F("pan", desc="PAN"),
                                         F("vat_no", desc="VAT number"), F("sup_cd", desc="SUP CD IF ANY")],
         kind="write", screen="LEG-REQ-01")
def ct_party_save(erp, user, party_cd=None, name=None, city=None, state=None, pan=None, vat_no=None, sup_cd=None):
    vat_no = vat_no.upper() if vat_no else None
    if vat_no:
        dup = erp.q1("SELECT party_cd FROM ct_party WHERE vat_no=? AND party_cd<>?", vat_no, party_cd or "")
        if dup:
            raise LedgerlineError("ERR-CT-0118", f"VAT number ALREADY ON REGISTER ({dup['party_cd']})")
    if party_cd:  # update: fill in KYC on an existing party
        p = erp.q1("SELECT * FROM ct_party WHERE party_cd=?", party_cd)
        if not p:
            raise LedgerlineError("ERR-CT-0030", "PARTY NOT FOUND")
        pan, vat_no = pan or p["pan"], vat_no or p["vat_no"]
        k = erp.sp("sp_ct_kyc", pan, vat_no)
        erp.x("UPDATE ct_party SET pan=?, vat_no=?, kyc=? WHERE party_cd=?", pan, vat_no, k, party_cd)
        return {"party_cd": party_cd, "_msg": f"PARTY {party_cd} UPDATED"}
    if not (name and city and state):
        raise LedgerlineError("ERR-SYS-0421", "NAME/CITY/STATE MANDATORY")
    k = erp.sp("sp_ct_kyc", pan, vat_no)
    party_cd = erp.sp("sp_doc_no_next", "CTP")
    erp.x("INSERT INTO ct_party VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", party_cd, name, city, state.upper()[:2], pan, vat_no,
          k, sup_cd, "ACTIVE", None, user, erp.today)
    return {"party_cd": party_cd, "_msg": f"PARTY {party_cd} CREATED"}  # kyc is stored, not shown


@service("ct_fetch", "CONTRACT DEFAULTS", [F("party_cd", req=True, desc="PARTY CD"), F("tmpl_cd", desc="TMPL CD")],
         screen="LEG-REQ-01")
def ct_fetch(erp, user, party_cd, tmpl_cd=None):
    erp.sp("sp_ct_party_chk", party_cd)
    out = {"paper": "THEIRS", "term_months": None, "juris": "MANCHESTER"}
    if tmpl_cd:
        t = erp.q1("SELECT * FROM ct_tmpl WHERE tmpl_cd=?", tmpl_cd)
        if not t:
            raise LedgerlineError("ERR-CT-0210", "TEMPLATE NOT FOUND")
        out = {"paper": t["paper"], "ct_type": t["ct_type"], "term_months": t["def_term"], "juris": t["juris"]}
    out["fetch_tok"] = erp.sp("sp_fetch_tok_new", user, "LEG-REQ-01", f"{party_cd}|{tmpl_cd or ''}")
    return out


@service("ct_save", "CONTRACT REQUEST SAVE",
         [F("ct_type", req=True, desc="NDA/MSA/SLA"), F("party_cd", req=True, desc="PARTY CD"),
          F("paper", req=True, desc="OURS/THEIRS"), F("tmpl_cd", desc="TMPL CD"), F("doc_ref", desc="THEIR DOC REF"),
          F("term_months", "int", desc="TERM (MTHS)"), F("start_dt", "date", desc="START DT"), F("juris", desc="JURIS"),
          F("value", "float", desc="VALUE"), F("fwd_to", desc="FWD TO"), F("fetch_tok", desc="FETCH TOKEN"),
          F("client_ref", desc="CLIENT REF")], kind="write", screen="LEG-REQ-01")
def ct_save(erp, user, ct_type, party_cd, paper, tmpl_cd=None, doc_ref=None, term_months=None, start_dt=None,
            juris="MANCHESTER", value=0.0, fwd_to=None, fetch_tok=None, client_ref=None):
    erp.sp("sp_fetch_tok_chk", user, fetch_tok, "LEG-REQ-01", f"{party_cd}|{tmpl_cd or ''}")
    ct_type, paper, juris = ct_type.upper(), paper.upper(), (juris or "MANCHESTER").upper()
    erp.sp("sp_ct_party_chk", party_cd)
    t = erp.sp("sp_ct_paper_rule", ct_type, paper, tmpl_cd, doc_ref)
    term = term_months or (t["def_term"] if t else None)
    if not term or term <= 0:
        raise LedgerlineError("ERR-CT-0220", "TERM MANDATORY")
    start = start_dt or erp.today
    if start < erp.today:
        raise LedgerlineError("ERR-CT-0105", "START DT IN PAST")
    end = erp.sp("sp_ct_expiry", start, term)
    ct_no = erp.sp("sp_doc_no_next", "CT")
    erp.x("INSERT INTO ct_req VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", ct_no, ct_type, party_cd, paper,
          tmpl_cd, doc_ref, term, start, end, juris, value or 0, "DR", user, erp.now(), None, None, None, None, None,
          fwd_to, None, client_ref)
    status, who = erp.sp("sp_ct_dispatch", ct_no, user)
    return {"ct_no": ct_no, "status": status, "end_dt": end, "_msg": f"{ct_no} SAVED"}  # PK is never spelt out


@service("ct_submit", "CONTRACT RESUBMIT", [F("ct_no", req=True, desc="CT NO"), F("fwd_to", desc="FWD TO")],
         kind="write", screen="LEG-REQ-01")
def ct_submit(erp, user, ct_no, fwd_to=None):
    """Send a request that was parked for KYC (PK) on its way again, once the party's KYC is complete."""
    r = erp.q1("SELECT * FROM ct_req WHERE ct_no=?", ct_no)
    if not r:
        raise LedgerlineError("ERR-CT-0501", "CT NOT FOUND")
    if r["status"] != "PK":
        raise LedgerlineError("ERR-CT-0502", f"CT NOT PENDING KYC ({r['status']})")
    if r["req_by"] != user and erp.user(user)["role_cd"] != "SYS-ADMIN":
        raise LedgerlineError("ERR-CT-0003", "NOT YOUR REQUEST")
    p = erp.q1("SELECT kyc FROM ct_party WHERE party_cd=?", r["party_cd"])
    if p["kyc"] != "Y":
        raise LedgerlineError("ERR-CT-0117", "PARTY KYC PENDING")
    if fwd_to:
        erp.x("UPDATE ct_req SET fwd_to=? WHERE ct_no=?", fwd_to, ct_no)
    status, who = erp.sp("sp_ct_dispatch", ct_no, user)
    return {"ct_no": ct_no, "status": status, "_msg": f"{ct_no} SUBMITTED"}


@service("ct_list", "CONTRACT REQUEST LIST", [F("ct_no", desc="CT NO"), F("party_cd", desc="PARTY CD"),
                                               F("status", desc="STATUS"), F("req_by", desc="USER ID"),
                                               F("client_ref", desc="CLIENT REF")], screen="LEG-REV-02")
def ct_list(erp, user, ct_no=None, party_cd=None, status=None, req_by=None, client_ref=None):
    sql = ("SELECT ct_no,ct_type,party_cd,paper,tmpl_cd,term_months,start_dt,end_dt,juris,status,req_by,reviewer,"
           "signatory,signed_by,warn_cd,client_ref FROM ct_req WHERE 1=1")
    args = []
    for col, v in (("ct_no", ct_no), ("party_cd", party_cd), ("status", status), ("req_by", req_by),
                   ("client_ref", client_ref)):
        if v:
            sql += f" AND {col}=?"
            args.append(v.upper() if col in ("status", "req_by") else v)
    rows = erp.q(sql + " ORDER BY ct_no DESC", *args)
    if ct_no and rows:
        rows[0]["devs"] = erp.q("SELECT clause_cd,found,expected,status FROM ct_dev WHERE ct_no=?", ct_no)
    return {"rows": rows}


@service("ct_review", "CLAUSE REVIEW", [F("ct_no", req=True, desc="CT NO"), F("decision", req=True, desc="A/R"),
                                         F("comment", desc="COMMENT")], kind="write", screen="LEG-REV-02")
def ct_review(erp, user, ct_no, decision, comment=""):
    r = erp.q1("SELECT * FROM ct_req WHERE ct_no=?", ct_no)
    if not r:
        raise LedgerlineError("ERR-CT-0501", "CT NOT FOUND")
    if r["status"] != "LR":
        raise LedgerlineError("ERR-CT-0503", f"CT NOT IN LEGAL REVIEW ({r['status']})")
    if r["req_by"] == user:
        raise LedgerlineError("ERR-APR-0003", "SELF APPROVAL NOT ALLOWED")
    if r["reviewer"] != user and erp.user(user)["role_cd"] != "SYS-ADMIN":
        raise LedgerlineError("ERR-CT-0504", f"NOT YOUR REVIEW ({r['reviewer']})")
    ok = decision.upper().startswith("A")
    erp.x("UPDATE approval SET status=?, decided_on=?, comment=? WHERE doc_no=? AND doc_type='CT-REV' AND status='PENDING'",
          "APPROVED" if ok else "REJECTED", erp.now(), comment, ct_no)
    erp.x("UPDATE ct_req SET legal_by=? WHERE ct_no=?", user, ct_no)
    if not ok:
        erp.sp("sp_ct_status_set", ct_no, "RJ")
        return {"ct_no": ct_no, "status": "RJ", "_msg": f"{ct_no} RETURNED BY LEGAL"}
    erp.x("UPDATE ct_dev SET status='ACCEPTED' WHERE ct_no=?", ct_no)
    sig = erp.sp("sp_ct_route_sign", ct_no, r["req_by"], r["value"], r["fwd_to"])
    erp.x("UPDATE ct_req SET signatory=? WHERE ct_no=?", sig, ct_no)
    erp.sp("sp_ct_status_set", ct_no, "PS")
    return {"ct_no": ct_no, "status": "PS", "signatory": sig, "_msg": f"{ct_no} CLEARED BY LEGAL"}


@service("ct_sign", "CONTRACT SIGN", [F("ct_no", req=True, desc="CT NO"), F("decision", req=True, desc="A/R"),
                                       F("comment", desc="COMMENT")], kind="write", screen="LEG-REV-02")
def ct_sign(erp, user, ct_no, decision, comment=""):
    r = erp.q1("SELECT * FROM ct_req WHERE ct_no=?", ct_no)
    if not r:
        raise LedgerlineError("ERR-CT-0501", "CT NOT FOUND")
    if r["status"] != "PS":
        raise LedgerlineError("ERR-CT-0505", f"CT NOT PENDING SIGNATURE ({r['status']})")
    if r["req_by"] == user:
        raise LedgerlineError("ERR-APR-0003", "SELF APPROVAL NOT ALLOWED")
    if r["signatory"] != user and erp.user(user)["role_cd"] != "SYS-ADMIN":
        raise LedgerlineError("ERR-CT-0506", f"NOT YOUR SIGNATURE ({r['signatory']})")
    ok = decision.upper().startswith("A")
    erp.x("UPDATE approval SET status=?, decided_on=?, comment=? WHERE doc_no=? AND doc_type='CT-SGN' AND status='PENDING'",
          "APPROVED" if ok else "REJECTED", erp.now(), comment, ct_no)
    if not ok:
        erp.sp("sp_ct_status_set", ct_no, "RJ")
        return {"ct_no": ct_no, "status": "RJ", "_msg": f"{ct_no} REJECTED"}
    erp.x("UPDATE ct_req SET signed_by=?, signed_on=? WHERE ct_no=?", user, erp.now(), ct_no)
    erp.sp("sp_ct_status_set", ct_no, "EX")
    r = erp.q1("SELECT * FROM ct_req WHERE ct_no=?", ct_no)
    erp.sp("sp_ct_reg_post", r)
    erp.sp("sp_ct_party_upd", r)
    return {"ct_no": ct_no, "status": "EX", "end_dt": r["end_dt"], "_msg": f"{ct_no} EXECUTED"}


@service("ct_reg_list", "CONTRACT REGISTER", [F("party_cd", desc="PARTY CD"), F("ct_type", desc="TYPE"),
                                               F("status", desc="ACTIVE/EXPIRED")], screen="LEG-REG-03")
def ct_reg_list(erp, user, party_cd=None, ct_type=None, status=None):
    sql = ("SELECT g.ct_no,g.party_cd,p.name,g.ct_type,g.start_dt,g.end_dt,g.signed_by,g.remind_on,"
           "CASE WHEN g.end_dt<? THEN 'EXPIRED' ELSE 'ACTIVE' END status FROM ct_reg g JOIN ct_party p "
           "ON p.party_cd=g.party_cd WHERE 1=1")
    args = [erp.today]
    for col, v in (("g.party_cd", party_cd), ("g.ct_type", ct_type)):
        if v:
            sql += f" AND {col}=?"
            args.append(v)
    rows = erp.q(sql + " ORDER BY g.end_dt DESC", *args)
    if status:
        rows = [r for r in rows if r["status"] == status.upper()]
    return {"rows": rows, "_msg": f"{len(rows)} ROWS FOUND"}
