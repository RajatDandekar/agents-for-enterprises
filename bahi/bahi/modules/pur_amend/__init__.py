"""Purchasing · amend PO. Before: PO list, PO amendment with its delivery schedule, re-approval. After: one sentence.

    erp = ERP(modules=["pur_amend"])
    s = erp.session("KJOSHI"); s.call("pa_sched_get", po_no="PO/2026/01182")
"""
from . import procs, services  # noqa: F401  (registers the procedures and services)
from .seed import SCHEMA, seed  # noqa: F401

KIT = {
    "name": "pur_amend",
    "title": "Purchasing · amend PO",
    "prefix": "pa_",
    "speaker": "KJOSHI",
    "after": "Push Deccan's gasket delivery to 9 November and cut it to 15,000.",
    "screens": ["PUR-POL-07", "PUR-POM-08", "PUR-POA-09"],
    "shared_engine": "sp_tax_compute (new values), sp_budget_chk / sp_budget_commit, sp_appr_route (value up)",
}

GLOSSARY = {
    "po_no": "Purchase order number, e.g. PO/2026/01182 (Kavita's 20,000 gaskets).",
    "amd_no": "Amendment number, e.g. AMD/2026/00031. One amendment = one revision of a released order.",
    "amd_type": "REV = revise quantity and/or dates. SCL = short-close: cancel the undelivered balance.",
    "qty": "The NEW total order quantity (not the change). It may not go below what has been received.",
    "need_dt": "The NEW need-by date. It must be the date of the last delivery line.",
    "s1_dt / s1_qty, s2_dt / s2_qty": "Up to two new delivery lines for the undelivered quantity. Left blank, Bahi keeps the old lines.",
    "reason_cd": "PLAN, SUPP, STCK, QLTY, DUPL or OTHR (pa_reason).",
    "rcvd_qty": "Quantity already received against the order (from the goods receipts in pa_rcpt).",
    "rev": "Revision number of the order; the supplier gets each revision when it is released.",
    "need_appr": "Y when the change needed re-approval (cut > 20%, moved > 5 days, or value up beyond the raiser's limit).",
    "fetch_tok": "Token from Fetch (pa_amd_fetch). Save without it fails with ERR-SCR-0221.",
    "client_ref": "Free text the caller can use as an idempotency key.",
}
STATUS = {"HD": "held: the delivery schedule does not add up to the new quantity and date; not routed, supplier not told",
          "PA": "pending re-approval", "AP": "approved, not yet released to the supplier",
          "RL": "released: the order is changed and the supplier has the revision", "RJ": "rejected",
          "schedule OP/RC/PR/SU/CN": "open, received, proposed by an amendment, superseded, cancelled (short-closed)"}
ERRORS = {
    "ERR-PO-0001": "order not found", "ERR-PA-0102": "order not released (unreleased orders use PUR-POM-06, po_amend)",
    "ERR-PA-0105": "another amendment of this order is still open", "ERR-PA-0201": "invalid reason code",
    "ERR-PA-0301": "quantity must be above zero", "ERR-PA-0310": "quantity below the quantity already received",
    "ERR-PA-0320": "delivery date nearer than the supplier's lead time", "ERR-PA-0331": "schedule line needs date and qty",
    "ERR-PA-0415": "cost centre closed, value cannot go up", "ERR-PA-0501": "amendment not found",
    "ERR-PA-0502": "amendment not pending", "ERR-PA-0503": "schedule locked (only a held amendment's schedule can change)",
    "ERR-PA-0504": "not your approval", "ERR-PA-0601": "type must be REV or SCL", "ERR-PA-0602": "nothing to amend",
    "ERR-PA-0611": "short-close cannot change the date", "ERR-PA-0612": "short-close quantity must equal received",
    "ERR-PA-0613": "short-close cannot carry a schedule", "ERR-PA-0614": "nothing received: cancel the order instead",
    "ERR-PA-0715": "amendment not approved, cannot release", "W-SCH-209": "schedule mismatch, amendment held",
    "ERR-SCR-0221": "Save without Fetch", "ERR-APR-0003": "self approval", "ERR-APR-0004": "value above approver's limit",
}
