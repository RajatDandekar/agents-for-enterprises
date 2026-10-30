"""Finance · payables. Before: invoice entry, three-way match, hold queue, payment proposal. After: one sentence.

    erp = ERP(modules=["fin_payables"])
    s = erp.session("ECLARKE"); s.call("ap_inv_list", sup_inv_no="4471")
"""
from . import procs, services  # noqa: F401  (registers the procedures and services)
from .seed import SCHEMA, seed  # noqa: F401

KIT = {
    "name": "fin_payables",
    "title": "Finance · payables",
    "prefix": "ap_",
    "speaker": "ECLARKE",
    "after": "Why is Voltway's invoice 4471 on hold, and can we pay it Friday?",
    "screens": ["FIN-AP-01", "FIN-AP-03", "FIN-AP-05"],
    "shared_engine": "sp_tax_region_chk + sp_tax_compute (VAT), sp_budget_chk + sp_budget_commit (non-PO invoices)",
}

GLOSSARY = {
    "ap_no": "Ledgerline's own invoice document number (AP/2026/03390). Not the supplier's number.",
    "sup_inv_no": "The number printed on the supplier's invoice (4471). Two suppliers can use the same number.",
    "inv_type": "PO = against a purchase order (three-way match); NPO = no order, e.g. a service (two-way, owner approves).",
    "po_no / qty / rate": "For PO invoices: the order, the quantity billed and the rate billed.",
    "amount": "For NPO invoices: the basic amount before VAT.",
    "tax_cd": "VAT code. Supplier in England: -INTRA (CGST+SGST); any other state: -INTER (IGST).",
    "cc_cd": "Cost centre. For NPO invoices it must be open; its owner approves.",
    "match_tok": "Token from Match (ap_match). Save without it fails with ERR-SCR-0221.",
    "hold_cd": "Why the invoice cannot be paid: H-PRC price, H-QTY quantity, H-GRN no receipt, H-DUP looks like a duplicate.",
    "refer_to": "The user asked to decide a hold (must be allowed to release that hold).",
    "due_dt": "Invoice date + the supplier's payment term days (N45 = 45 days).",
    "pay_dt": "The payment-run Friday the invoice should be paid in (see ap_run).",
    "early_rsn": "Reason for paying before the due date. With it the proposal goes to the controller; without it, it is parked.",
    "client_ref": "Free text the caller can use as an idempotency key.",
}
STATUS = {"HD": "invoice on hold", "PA": "waiting for approval (NPO invoice or early payment)",
          "PO": "invoice posted, clear to pay", "PD": "paid", "RJ": "rejected", "CN": "cancelled",
          "PK": "payment parked: early with no reason; in no run and nobody is told",
          "SC": "payment scheduled in a run"}
ERRORS = {
    "ERR-AP-0001": "AP document not found", "ERR-AP-0031": "supplier not active", "ERR-AP-0103": "invoice date in future",
    "ERR-AP-0118": "this supplier invoice number is already entered", "ERR-AP-0201": "PO invoice needs PO, qty and rate",
    "ERR-AP-0205": "PO belongs to another supplier", "ERR-AP-0206": "PO not released",
    "ERR-AP-0211": "NPO invoice cannot refer a PO", "ERR-AP-0212": "NPO invoice needs amount and cost centre",
    "ERR-AP-0213": "cost centre closed", "ERR-AP-0301": "invalid hold code", "ERR-AP-0302": "hold not open",
    "ERR-AP-0305": "you may not release this hold", "ERR-AP-0306": "the person referred to cannot release this hold",
    "ERR-AP-0402": "nothing pending for this document", "ERR-AP-0404": "not your approval",
    "ERR-AP-0410": "invoice not clear for payment", "ERR-AP-0412": "not a payment-run date",
    "ERR-AP-0413": "run cut-off passed", "ERR-AP-0415": "payment already proposed", "ERR-AP-0520": "run date in future",
    "ERR-AP-0521": "run already done", "ERR-PO-0412": "tax code does not match supplier state (shared tax engine)",
    "ERR-SCR-0221": "Save without Match", "ERR-APR-0003": "self approval", "W-AP-311": "early payment parked (no reason given)",
}
