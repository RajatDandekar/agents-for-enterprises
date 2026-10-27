"""Services (~8): flat payloads, at most 12 fields, terse legacy names, the legacy envelope."""
from ...erp.engine import BahiError, service
from .._kit import F


@service("xx_list", "DOC LIST", [F("status", desc="STATUS")], screen="XX-ABC-01")
def xx_list(erp, user, status=None):
    sql, args = "SELECT * FROM xx_doc WHERE 1=1", []
    if status:
        sql += " AND status=?"; args.append(status)
    return {"rows": erp.q(sql + " ORDER BY doc_no DESC", *args)}


@service("xx_fetch", "DOC DEFAULTS", [F("party", req=True, desc="PARTY")], screen="XX-ABC-02")
def xx_fetch(erp, user, party):
    tok = erp.sp("sp_fetch_tok_new", user, "XX-ABC-02", party)        # screen state: Fetch before Save
    return {"cc_cd": erp.user(user)["default_cc"], "fetch_tok": tok}


@service("xx_save", "DOC SAVE", [F("party", req=True, desc="PARTY"), F("qty", "int", True, "QTY"),
                                 F("amount", "float", True, "AMT"), F("cc_cd", req=True, desc="CC CD"),
                                 F("fetch_tok", desc="FETCH TOKEN"), F("client_ref", desc="CLIENT REF")],
         kind="write", screen="XX-ABC-02")
def xx_save(erp, user, party, qty, amount, cc_cd, fetch_tok=None, client_ref=None):
    erp.sp("sp_fetch_tok_chk", user, fetch_tok, "XX-ABC-02", party)
    r = erp.sp("sp_xx_save", user, party, qty, amount, cc_cd, client_ref)
    return {**r, "_msg": f"{r['doc_no']} SAVED"}       # never say the status in the message: that is the trap


@service("xx_approve", "DOC APPROVE", [F("doc_no", req=True, desc="DOC NO"), F("decision", req=True, desc="A/R")],
         kind="write", screen="XX-ABC-03")
def xx_approve(erp, user, doc_no, decision):
    d = erp.q1("SELECT * FROM xx_doc WHERE doc_no=?", doc_no)
    if not d or d["status"] != "PA":
        raise BahiError("ERR-XX-0702", "DOC NOT PENDING")
    if d["created_by"] == user:
        raise BahiError("ERR-APR-0003", "SELF APPROVAL NOT ALLOWED")
    st = "AP" if decision.upper().startswith("A") else "RJ"
    erp.x("UPDATE xx_doc SET status=?, approver=? WHERE doc_no=?", st, user, doc_no)
    erp.x("UPDATE approval SET status=?, decided_on=? WHERE doc_no=? AND status='PENDING'",
          "APPROVED" if st == "AP" else "REJECTED", erp.now(), doc_no)
    return {"doc_no": doc_no, "status": st, "_msg": f"{doc_no} {'APPROVED' if st == 'AP' else 'REJECTED'}"}
