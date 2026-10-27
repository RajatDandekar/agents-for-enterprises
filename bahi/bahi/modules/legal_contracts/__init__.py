"""Legal · contracts. Before: contract request, clause review, contract register. After: one sentence.

    erp = ERP(modules=["legal_contracts"])
    s = erp.session("KJOSHI"); s.call("ct_party_find", q="Shakti")
"""
from . import procs, services  # noqa: F401  (registers the procedures and services)
from .seed import SCHEMA, seed  # noqa: F401

KIT = {
    "name": "legal_contracts",
    "title": "Legal · contracts",
    "prefix": "ct_",
    "speaker": "KJOSHI",
    "after": "Raise an NDA with Shakti Seals on our paper, valid two years.",
    "screens": ["LEG-REQ-01", "LEG-REV-02", "LEG-REG-03"],
    "shared_engine": "sp_appr_route (signatory routing by value; a ₹0 NDA stops at the first manager)",
}

GLOSSARY = {
    "party_cd": "Counterparty code on the contract party register (CP-0017). Not a supplier code: an NDA does not onboard a supplier.",
    "pan / gstin": "KYC papers. Both must be on file, and the PAN must be the one inside the GSTIN (characters 3-12).",
    "kyc": "Y when PAN and GSTIN are both on file and agree; N otherwise. Not shown on the request screen.",
    "ct_type": "NDA non-disclosure, MSA master supply agreement, SLA service agreement.",
    "paper": "OURS = our template (tmpl_cd); THEIRS = the counterparty's draft (doc_ref), always reviewed by Legal.",
    "tmpl_cd": "Template code. NDA-MUT-v4 is the current mutual NDA; NDA-MUT-v3 was withdrawn in March 2025.",
    "doc_ref": "Their document's reference, for their paper only.",
    "term_months / end_dt": "Term in months; end_dt = start + term - 1 day (24 months from 26-10-2026 ends 25-10-2028).",
    "juris": "Courts with jurisdiction. Playbook: PUNE.",
    "fwd_to": "FWD TO: send the request to this signatory instead of the one Bahi's value routing picks.",
    "fetch_tok": "Token from Fetch (ct_fetch). Save without it fails with ERR-SCR-0221.",
    "reviewer / legal_by": "Legal reviewer assigned, and who actually cleared it.",
    "signatory / signed_by": "Who should sign, and who did.",
    "client_ref": "Free text the caller can use as an idempotency key.",
}
STATUS = {"DR": "being saved", "PK": "pending KYC (parked silently: reaches neither Legal nor the signatory)",
          "LR": "with Legal for clause review", "PS": "pending signature", "EX": "executed and in the register",
          "RJ": "returned or rejected"}
ERRORS = {
    "ERR-CT-0003": "not your request", "ERR-CT-0030": "party not found", "ERR-CT-0031": "party not active (blocked)",
    "ERR-CT-0105": "start date in past", "ERR-CT-0117": "party KYC still pending", "ERR-CT-0118": "GSTIN already on the register",
    "ERR-CT-0122": "PAN does not match GSTIN", "ERR-CT-0201": "paper must be OURS or THEIRS",
    "ERR-CT-0210": "template not found", "ERR-CT-0211": "template is for another contract type",
    "ERR-CT-0212": "template withdrawn", "ERR-CT-0215": "their paper needs a document reference",
    "ERR-CT-0216": "no template on their paper", "ERR-CT-0220": "term mandatory",
    "ERR-CT-0409": "no Legal reviewer", "ERR-CT-0410": "FWD TO user not found", "ERR-CT-0501": "request not found",
    "ERR-CT-0502": "not pending KYC", "ERR-CT-0503": "not in Legal review", "ERR-CT-0504": "not your review",
    "ERR-CT-0505": "not pending signature", "ERR-CT-0506": "not your signature",
    "W-CT-117": "saved, parked for KYC; never routed", "ERR-SCR-0221": "Save without Fetch",
    "ERR-APR-0003": "self approval", "ERR-APR-0009": "no approver found in the manager chain",
}
