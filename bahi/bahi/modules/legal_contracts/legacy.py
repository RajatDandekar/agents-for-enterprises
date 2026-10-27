"""Legal · contracts: the before, scripted. happy_path() is Kavita's sentence done the legacy way, screen by screen;
TRAPS triggers each trap in the complexity budget and says whether Bahi behaved as the brief claims."""
from __future__ import annotations

from .._kit import ok

GSTIN, PAN = "24AAFCS8812N1Z4", "AAFCS8812N"


def happy_path(erp) -> dict:
    """Kavita: an NDA with Shakti Seals on our paper, two years. Three screens, the careful way."""
    k, a = erp.session("KJOSHI"), erp.session("APATIL")
    ok(k.call("ct_party_find", screen="LEG-REQ-01", task="Find Party", q="Shakti"))
    p = ok(k.call("ct_party_save", screen="LEG-REQ-01", task="Party Save", name="Shakti Seals", city="Vadodara",
                  state="GJ", pan=PAN, gstin=GSTIN))["party_cd"]
    tok = ok(k.call("ct_fetch", screen="LEG-REQ-01", task="Fetch", party_cd=p, tmpl_cd="NDA-MUT-v4"))["fetch_tok"]
    d = ok(k.call("ct_save", screen="LEG-REQ-01", task="Save", ct_type="NDA", party_cd=p, paper="OURS",
                  tmpl_cd="NDA-MUT-v4", term_months=24, juris="PUNE", fwd_to="APATIL", fetch_tok=tok))
    ok(a.call("ct_list", screen="LEG-REV-02", task="Inbox", status="PS"))
    ok(a.call("ct_sign", screen="LEG-REV-02", task="Sign", ct_no=d["ct_no"], decision="A", comment="ok"))
    ok(k.call("ct_reg_list", screen="LEG-REG-03", task="Show", party_cd=p))
    r = erp.q1("SELECT * FROM ct_req WHERE ct_no=?", d["ct_no"])
    sups = erp.q1("SELECT count(*) n FROM supplier WHERE name LIKE 'Shakti%'")["n"]
    return {"doc": d["ct_no"], "status": r["status"],
            "ok": r["status"] == "EX" and r["signed_by"] == "APATIL" and r["end_dt"] == "2028-10-25" and sups == 0}


def _party(s, kyc=True):
    kw = {"pan": PAN, "gstin": GSTIN} if kyc else {}
    return ok(s.call("ct_party_save", name="Shakti Seals", city="Vadodara", state="GJ", **kw))["party_cd"]


def _save(s, p, tmpl="NDA-MUT-v4", **kw):
    tok = ok(s.call("ct_fetch", party_cd=p, tmpl_cd=tmpl))["fetch_tok"]
    return s.call("ct_save", ct_type="NDA", party_cd=p, fetch_tok=tok, **({"tmpl_cd": tmpl} if tmpl else {}), **kw)


def t_silent(erp):
    s = erp.session("KJOSHI")
    r = _save(s, _party(s, kyc=False), paper="OURS", term_months=24, fwd_to="APATIL")
    no = (r["data"] or {}).get("ct_no", "")
    routed = erp.q1("SELECT 1 FROM approval WHERE doc_no=?", no)
    good = r["rc"] == "S" and r["data"]["status"] == "PK" and not routed and r["msg"].endswith("SAVED")
    return good, f"rc={r['rc']} msg='{r['msg']}' status={r['data']['status']} routed={bool(routed)}"


def t_variant_ours(erp):
    s = erp.session("KJOSHI")
    p = _party(s)
    r1 = _save(s, p, tmpl="NDA-MUT-v3", paper="OURS", term_months=24)
    r2 = _save(s, p, paper="OURS", term_months=24, fwd_to="APATIL")
    rev = erp.q1("SELECT 1 FROM approval WHERE doc_no=? AND doc_type='CT-REV'", r2["data"]["ct_no"])
    good = r1["err_cd"] == "ERR-CT-0212" and r2["data"]["status"] == "PS" and not rev
    return good, f"withdrawn template: {r1['err_cd']}; our paper, no deviation: {r2['data']['status']} (Legal skipped: {not rev})"


def t_variant_theirs(erp):
    s = erp.session("KJOSHI")
    p = _party(s)
    r1 = _save(s, p, tmpl=None, paper="THEIRS", term_months=60, juris="SINGAPORE")
    r2 = _save(s, p, tmpl=None, paper="THEIRS", doc_ref="SS/NDA/0921", term_months=60, juris="SINGAPORE")
    devs = [d["clause_cd"] for d in erp.q("SELECT clause_cd FROM ct_dev WHERE ct_no=?", r2["data"]["ct_no"])]
    good = r1["err_cd"] == "ERR-CT-0215" and r2["data"]["status"] == "LR" and len(devs) == 3
    return good, f"no doc ref: {r1['err_cd']}; their paper: {r2['data']['status']}, deviations {devs}"


def t_screen_state(erp):
    s = erp.session("KJOSHI")
    r = s.call("ct_save", ct_type="NDA", party_cd=_party(s), paper="OURS", tmpl_cd="NDA-MUT-v4", term_months=24)
    return r["err_cd"] == "ERR-SCR-0221", f"{r['err_cd']} {r['msg']}"


def _executed(erp):
    s = erp.session("KJOSHI")
    p = _party(s)
    d = ok(_save(s, p, paper="OURS", term_months=24, fwd_to="APATIL"))
    ok(erp.session("APATIL").call("ct_sign", ct_no=d["ct_no"], decision="A"))
    return p, d["ct_no"]


def t_cascade_register(erp):
    n0 = erp.q1("SELECT count(*) n FROM ntf_queue")["n"]
    p, no = _executed(erp)
    reg = erp.q1("SELECT * FROM ct_reg WHERE ct_no=?", no)
    ntf = erp.q("SELECT subject FROM ntf_queue WHERE subject LIKE 'Renewal due%'")
    good = bool(reg) and reg["end_dt"] == "2028-10-25" and reg["remind_on"] == "2028-08-26" and len(ntf) == 1
    return good, f"register {no} ends {reg and reg['end_dt']}, reminder {reg and reg['remind_on']}, mails queued {erp.q1('SELECT count(*) n FROM ntf_queue')['n'] - n0}"


def t_cascade_party(erp):
    p, no = _executed(erp)
    party = erp.q1("SELECT nda_till FROM ct_party WHERE party_cd=?", p)
    return party["nda_till"] == "2028-10-25", f"{p} nda_till = {party['nda_till']}"


def t_shared_engine(erp):
    s = erp.session("KJOSHI")
    d = ok(_save(s, _party(s), paper="OURS", term_months=24))
    sps = erp.calls[-1].sps
    inbox = ok(erp.session("RMEHTA").call("po_pending_appr"))["rows"]
    seen = any(r["doc_no"] == d["ct_no"] for r in inbox)
    return "sp_appr_route" in sps and seen, f"sp_appr_route in save: {'sp_appr_route' in sps}; in Rohit's purchasing inbox: {seen}"


def t_policy_only(erp):
    """Delegation of Authority: only the plant head signs NDAs. Bahi's value routing sends a ₹0 NDA to Rohit."""
    s = erp.session("KJOSHI")
    d = ok(_save(s, _party(s), paper="OURS", term_months=24))
    r = erp.q1("SELECT signatory FROM ct_req WHERE ct_no=?", d["ct_no"])
    return r["signatory"] == "RMEHTA", f"NDA routed for signature to {r['signatory']} (DoA says APATIL)"


TRAPS = {
    "silent: party without KYC, request saved as PK and routed nowhere": t_silent,
    "variant: our paper (withdrawn template refused; no deviation skips Legal)": t_variant_ours,
    "variant: their paper (doc ref required; always Legal, deviations recorded)": t_variant_theirs,
    "screen_state: Save without Fetch": t_screen_state,
    "cascade: signing writes the register and a renewal reminder": t_cascade_register,
    "cascade: signing updates the party's NDA date": t_cascade_party,
    "shared_engine: sp_appr_route, visible in the purchasing inbox": t_shared_engine,
    "policy_only: NDA signatory rule not enforced": t_policy_only,
}
