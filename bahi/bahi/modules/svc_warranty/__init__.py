"""Service · warranty. Before: serial lookup, warranty check and ticket, goodwill waiver. After: one sentence.

    erp = ERP(modules=["svc_warranty"])
    s = erp.session("FSHAIKH"); s.call("wr_ser_get", serial="RS5-2609-1187")
"""
from . import procs, services  # noqa: F401  (registers the procedures and services)
from .seed import SCHEMA, seed  # noqa: F401

KIT = {
    "name": "svc_warranty",
    "title": "Service · warranty",
    "prefix": "wr_",
    "speaker": "FSHAIKH",
    "after": "A customer's whistle broke after three weeks; replace it.",
    "screens": ["SVC-SER-01", "SVC-TKT-02", "SVC-WAV-03"],
    "shared_engine": "sp_tax_compute (GST on chargeable repairs) and sp_appr_route (waivers above the desk's limit)",
}

GLOSSARY = {
    "serial": "Cooker serial number, e.g. RS5-2609-1187: RS5 = steel 5 L (RA5 aluminium 5 L, RS3 3 L, RS7 7.5 L), "
              "2609 = made September 2026, then a running number.",
    "model": "Finished-goods item code of the cooker (PC-SS-05L etc.).",
    "sold_dt / inv_ref": "Sale date and the dealer's invoice number, registered by the dealer or the desk. Blank = not registered.",
    "part_cd": "The spare part being replaced (WHS-STD-01 whistle, GSK-SIL-05L gasket, LID-SS-05L lid ...).",
    "grp / months": "Warranty group of the part and its warranty in months (WHISTLE 6, GASKET 6, HANDLE 12, LID 24, BODY 60).",
    "in_wty / basis / wty_to": "Verify's answer: in warranty Y/N, counted from SALE or (if no sale registered) MFG, and until when.",
    "cmp_cd / cause_cd": "Complaint (BRK, LEK, NWS, CRK) and cause (MFD, WRN, PHY, NGP, OVH, UNK). Bahi does not act on the cause.",
    "chg": "N = free under warranty, Y = chargeable, W = waived as goodwill. Blank on Save = from Verify.",
    "amount": "Chargeable amount: service price plus 18% GST.",
    "rcpt_no": "The customer's payment receipt; needed to issue a part on a chargeable ticket.",
    "fwd_to": "FWD TO: send the waiver to this approver instead of letting Bahi decide.",
    "fetch_tok": "Token from Verify (wr_verify). Save without it fails with ERR-SCR-0221.",
    "cncl": "Y on Close cancels a ticket that has not had a part issued.",
}
STATUS = {"OP": "open, part to be issued free", "CQ": "chargeable, waiting for the customer's payment (no part goes out)",
          "WA": "waiver waiting for an approver", "PI": "part issued", "CL": "closed, dealer told", "CN": "cancelled"}
ERRORS = {
    "ERR-WR-0101": "serial not found", "ERR-WR-0110": "serial blocked (reported stolen)", "ERR-WR-0120": "sale already registered",
    "ERR-WR-0121": "sale date before manufacture or in the future", "ERR-WR-0122": "dealer not found",
    "ERR-WR-0215": "part does not fit this model", "ERR-WR-0220": "invalid complaint or cause code",
    "ERR-WR-0240": "out of warranty: cannot save as free", "ERR-WR-0301": "an open ticket exists for this serial and part",
    "ERR-WR-0405": "ticket not chargeable, nothing to waive", "ERR-WR-0410": "FWD TO user not found",
    "ERR-WR-0420": "chargeable: payment receipt needed before issue", "ERR-WR-0421": "waiver pending",
    "ERR-WR-0422": "part cannot be issued in this status", "ERR-WR-0430": "no stock of the part",
    "ERR-WR-0501": "ticket not found", "ERR-WR-0502": "no waiver pending", "ERR-WR-0504": "not your approval",
    "ERR-WR-0510": "close before part issue", "ERR-WR-0511": "cannot cancel after issue",
    "ERR-SCR-0221": "Save without Verify", "ERR-APR-0003": "self approval", "ERR-APR-0004": "above approver's limit",
}
