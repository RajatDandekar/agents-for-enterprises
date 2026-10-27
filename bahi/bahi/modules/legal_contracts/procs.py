"""Legal · contracts: the stored procedures. The rules live here; services call them through erp.sp()."""
from __future__ import annotations

import calendar
import datetime as dt

from ...erp.engine import BahiError, proc


@proc("sp_ct_party_chk")
def party_chk(erp, party_cd: str) -> dict:
    p = erp.q1("SELECT * FROM ct_party WHERE party_cd=?", party_cd)
    if not p:
        raise BahiError("ERR-CT-0030", "PARTY NOT FOUND")
    if p["status"] != "ACTIVE":
        raise BahiError("ERR-CT-0031", "PARTY NOT ACTIVE")
    return p


@proc("sp_ct_kyc")
def kyc(erp, pan: str | None, gstin: str | None) -> str:
    """KYC is complete when both PAN and GSTIN are on file and the PAN is the one inside the GSTIN.
    Missing papers are not an error: the party is saved with kyc = 'N'."""
    if pan and gstin:
        if gstin[2:12].upper() != pan.upper():
            raise BahiError("ERR-CT-0122", "PAN DOES NOT MATCH GSTIN")
        return "Y"
    return "N"


@proc("sp_ct_paper_rule")
def paper_rule(erp, ct_type: str, paper: str, tmpl_cd: str | None, doc_ref: str | None) -> dict | None:
    """The two variants. OURS: an active template of the same type. THEIRS: the counterparty's document reference,
    no template, and always a full clause review by Legal."""
    if paper not in ("OURS", "THEIRS"):
        raise BahiError("ERR-CT-0201", "PAPER MUST BE OURS/THEIRS")
    if paper == "THEIRS":
        if tmpl_cd:
            raise BahiError("ERR-CT-0216", "TMPL NOT ALLOWED ON THEIR PAPER")
        if not doc_ref:
            raise BahiError("ERR-CT-0215", "DOC REF MANDATORY FOR THEIR PAPER")
        return None
    t = erp.q1("SELECT * FROM ct_tmpl WHERE tmpl_cd=?", tmpl_cd or "")
    if not t:
        raise BahiError("ERR-CT-0210", "TEMPLATE NOT FOUND")
    if not t["active"]:
        raise BahiError("ERR-CT-0212", "TEMPLATE WITHDRAWN")
    if t["ct_type"] != ct_type:
        raise BahiError("ERR-CT-0211", f"TEMPLATE IS FOR {t['ct_type']}")
    return t


@proc("sp_ct_expiry")
def expiry(erp, start_dt: str, months: int) -> str:
    """Last day of the term: start + months - 1 day (24 months from 26-10-2026 ends 25-10-2028)."""
    d = dt.date.fromisoformat(start_dt)
    y, m = divmod(d.month - 1 + months, 12)
    y, m = d.year + y, m + 1
    day = min(d.day, calendar.monthrange(y, m)[1])
    return (dt.date(y, m, day) - dt.timedelta(days=1)).isoformat()


@proc("sp_ct_dev_scan")
def dev_scan(erp, ct_no: str) -> int:
    """Compare the request with the playbook (ct_clause) and record every deviation."""
    r = erp.q1("SELECT * FROM ct_req WHERE ct_no=?", ct_no)
    erp.x("DELETE FROM ct_dev WHERE ct_no=?", ct_no)
    n = 0
    for c in erp.q("SELECT * FROM ct_clause WHERE ct_type=?", r["ct_type"]):
        v = r[c["attr"]]
        bad = (c["rule"] == "MAX" and v is not None and float(v) > float(c["limit_val"])) or \
              (c["rule"] == "EQ" and str(v or "").upper() != c["limit_val"])
        if bad:
            erp.x("INSERT INTO ct_dev VALUES (?,?,?,?,?)", ct_no, c["clause_cd"], str(v), c["limit_val"], "OPEN")
            n += 1
    return n


@proc("sp_ct_route_review")
def route_review(erp, ct_no: str, requester: str) -> str:
    legal = erp.q1("SELECT user_id, email FROM app_user WHERE role_cd='LEGAL' ORDER BY user_id")
    if not legal:
        raise BahiError("ERR-CT-0409", "NO LEGAL REVIEWER")
    erp.x("INSERT INTO approval(doc_type,doc_no,approver,status,requested_by,requested_on) VALUES (?,?,?,?,?,?)",
          "CT-REV", ct_no, legal["user_id"], "PENDING", requester, erp.now())
    erp.sp("sp_ntf_enqueue", "EMAIL", legal["email"], f"{ct_no} for clause review", f"Raised by {requester}")
    return legal["user_id"]


@proc("sp_ct_route_sign")
def route_sign(erp, ct_no: str, requester: str, value: float, fwd_to: str | None) -> str:
    """Who signs? The person typed in FWD TO, or else the shared approval engine sp_appr_route, which walks the
    requester's manager chain by value. For a ₹0 NDA that stops at the first manager. (The Delegation of
    Authority says only the plant head signs NDAs; Bahi does not know that.)"""
    if fwd_to:
        u = erp.user(fwd_to)
        if not u:
            raise BahiError("ERR-CT-0410", "FWD TO USER NOT FOUND")
        erp.x("INSERT INTO approval(doc_type,doc_no,approver,status,requested_by,requested_on) VALUES (?,?,?,?,?,?)",
              "CT-SGN", ct_no, fwd_to, "PENDING", requester, erp.now())
        erp.sp("sp_ntf_enqueue", "EMAIL", u["email"], f"{ct_no} awaiting your signature", f"Raised by {requester}")
        return fwd_to
    return erp.sp("sp_appr_route", "CT-SGN", ct_no, requester, value or 0)


@proc("sp_ct_dispatch")
def dispatch(erp, ct_no: str, user: str) -> tuple[str, str | None]:
    """Where a saved request goes next. No KYC: PK, silently, nowhere. Their paper or any deviation: Legal (LR).
    Our paper with no deviation: fast track to the signatory (PS)."""
    r = erp.q1("SELECT * FROM ct_req WHERE ct_no=?", ct_no)
    p = erp.q1("SELECT * FROM ct_party WHERE party_cd=?", r["party_cd"])
    if p["kyc"] != "Y":
        erp.sp("sp_ct_status_set", ct_no, "PK", warn="W-CT-117")
        return "PK", None
    devs = erp.sp("sp_ct_dev_scan", ct_no)
    if r["paper"] == "THEIRS" or devs:
        rev = erp.sp("sp_ct_route_review", ct_no, user)
        erp.x("UPDATE ct_req SET reviewer=? WHERE ct_no=?", rev, ct_no)
        erp.sp("sp_ct_status_set", ct_no, "LR")
        return "LR", rev
    sig = erp.sp("sp_ct_route_sign", ct_no, r["req_by"], r["value"], r["fwd_to"])
    erp.x("UPDATE ct_req SET signatory=? WHERE ct_no=?", sig, ct_no)
    erp.sp("sp_ct_status_set", ct_no, "PS")
    return "PS", sig


@proc("sp_ct_reg_post")
def reg_post(erp, r: dict):
    """Cascade 1: an executed contract goes into the register with a renewal reminder 60 days before expiry."""
    remind = (dt.date.fromisoformat(r["end_dt"]) - dt.timedelta(days=60)).isoformat()
    erp.x("INSERT INTO ct_reg VALUES (?,?,?,?,?,?,?,?)", r["ct_no"], r["party_cd"], r["ct_type"], r["start_dt"],
          r["end_dt"], r["signed_by"], remind, "ACTIVE")
    erp.sp("sp_ntf_enqueue", "EMAIL", erp.user(r["req_by"])["email"], f"Renewal due: {r['ct_no']}",
           f"{r['ct_type']} with {r['party_cd']} expires {r['end_dt']}; reminder set for {remind}")


@proc("sp_ct_party_upd")
def party_upd(erp, r: dict):
    """Cascade 2: the party's record shows the NDA it now has (purchase and Legal both read nda_till)."""
    if r["ct_type"] == "NDA":
        erp.x("UPDATE ct_party SET nda_till=? WHERE party_cd=?", r["end_dt"], r["party_cd"])


@proc("sp_ct_status_set")
def status_set(erp, ct_no: str, status: str, warn: str | None = None):
    erp.x("UPDATE ct_req SET status=?, warn_cd=? WHERE ct_no=?", status, warn, ct_no)
