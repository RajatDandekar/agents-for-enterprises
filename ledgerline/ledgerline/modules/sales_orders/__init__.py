"""Sales · orders. Before: customer, price list, quotation, sales order. After: one sentence.

    erp = ERP(modules=["sales_orders"])
    s = erp.session("ARAO"); s.call("so_cust_search", q="Annapurna")
"""
from . import procs, services  # noqa: F401  (registers the procedures and services)
from .seed import SCHEMA, seed  # noqa: F401

KIT = {
    "name": "sales_orders",
    "title": "Sales · orders",
    "prefix": "so_",
    "speaker": "ARAO",
    "after": "Quote Annapurna Stores 500 five-litre e-bikes at dealer price.",
    "screens": ["SAL-CUS-01", "SAL-QTN-02", "SAL-ORD-03"],
    "shared_engine": "sp_tax_compute (VAT on every quotation and order) and sp_appr_route (discount approval)",
}

GLOSSARY = {
    "cust_cd": "Customer code (C-PUN-0118 is Annapurna Stores, Manchester). Three customers have names like it.",
    "cust_type": "DLR registered dealer, DST distributor, RTL retailer, OWN the factory outlet.",
    "list_cd": "Price list: DLR dealer, DST distributor, RTL retail, MRP. Fixed per customer in the master.",
    "rate": "Price per piece before discount. Blank = today's price on the customer's list.",
    "disc_pct": "DISC %: discount on the rate. Above your authority (SAL-EXEC 2%) the quotation waits for approval.",
    "tax_cd": "VAT5-UK for customers in England, VAT5-RC for any other state. Fetch always offers INTRA.",
    "valid_to": "Last day the quotation can be turned into an order. Blank = 15 days.",
    "qtn_no / ord_no": "QT/2026/nnnnn quotation, SO/2026/nnnnn sales order.",
    "ord_type": "STD from an issued quotation; CSH direct cash sale from stock, no quotation, gross up to £100,000.",
    "cr_limit / outstanding / cr_avail": "Credit limit, unpaid invoices, and what is left after open and released orders.",
    "fetch_tok": "Token from Price/Fetch (so_qtn_fetch). Save without it fails with ERR-SCR-0221.",
    "client_ref": "Free text the caller can use as an idempotency key.",
}
STATUS = {"PA": "quotation waiting for discount approval", "IS": "quotation issued (can be sent and converted)",
          "CV": "quotation converted to an order", "EX": "quotation expired", "RJ": "rejected",
          "OP": "order open, ready to release", "CH": "order on credit hold (saved; never reaches dispatch)",
          "RL": "order released to dispatch", "IN": "order invoiced", "CN": "cancelled"}
ERRORS = {
    "ERR-SO-0030": "customer not found", "ERR-SO-0031": "customer blocked or inactive", "ERR-SO-0201": "qty must be > 0",
    "ERR-SO-0412": "tax code does not match the customer's state", "ERR-SO-0420": "rate not on the price list",
    "ERR-SO-0421": "no current price on that list", "ERR-SO-0425": "price list not allowed for this customer",
    "ERR-SO-0430": "discount out of range", "ERR-SO-0520": "not enough free stock to release",
    "ERR-SO-0600": "order type must be STD or CSH", "ERR-SO-0602": "STD order needs a quotation",
    "ERR-SO-0603": "quotation not issued", "ERR-SO-0604": "more than quoted", "ERR-SO-0605": "quotation expired",
    "ERR-SO-0610": "cash order above £100,000", "ERR-SO-0611": "cash order cannot refer a quotation",
    "ERR-SO-0701": "document not found", "ERR-SO-0702": "quotation not pending", "ERR-SO-0703": "not your approval",
    "ERR-SO-0704": "discount above the approver's authority", "ERR-SO-0715": "order on credit hold",
    "ERR-SO-0716": "order not releasable", "W-SO-114": "order saved on credit hold", "ERR-SCR-0221": "Save without Fetch",
    "ERR-APR-0003": "self approval",
}
