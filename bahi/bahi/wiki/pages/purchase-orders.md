---
title: Purchase Order Entry and Rules
audience: all purchase staff
sources: POL-PUR-001 §3.3, POL-PUR-001 §3.4, MAN-DD-72 §6.1, MAN-DD-72 §6.2, MAN-DD-72 §6.3, MAN-DD-72 §6.4, MAN-DD-72 §6.5, MAN-DD-72 §6.6, MAN-DD-72 §6.7, MAN-DD-72 §6.8, MAN-PUR-72 §11.1, MAN-PUR-72 §11.2, MAN-PUR-72 §11.3, MAN-PUR-72 §11.4, MAN-PUR-72 §11.5, MAN-PUR-72 §11.6, MAN-PUR-72 §11.7, MAN-PUR-72 §11.8, MAN-PUR-72 §11.9, MAN-PUR-72 §11.10, MAN-PUR-72 §11.11, AMD-PUR-2026-03 §1.1, AMD-PUR-2026-03 §1.2, AMD-PUR-2026-03 §2.1, AMD-PUR-2026-03 §3.1, AMD-PUR-2026-03 §3.2
compiled_by: gemini:gemini-3.8-flash
---

# Purchase Order Entry and Rules

The purchase order entry screen creates standard and direct orders to suppliers. Standard orders require an approved purchase request, while direct orders cover low-value purchases without a request. Every order requires running the Fetch action before saving and must pass system validations.

## Rules
- Standard (STD) purchase orders must be raised against an approved purchase request entered in the Source PR field [MAN-PUR-72 §11.2].
- A direct (DIR) order has no request, must not refer to a request, and is permitted only up to a gross value (including GST) of ₹50,000; note that starting 2026-12-01, this limit is reduced to ₹25,000 [POL-PUR-001 §3.3, AMD-PUR-2026-03 §1.1, AMD-PUR-2026-03 §1.2, MAN-PUR-72 §11.2, MAN-PUR-72 §11.7].
- A purchase order raised against a request cannot exceed the requested quantity or differ in item from the request [POL-PUR-001 §3.4, MAN-PUR-72 §11.10].
- Bahi ERP assigns order numbers using the format PO/<year>/<five digits>, such as PO/2026/01182 [MAN-DD-72 §6.1, MAN-PUR-72 §11.8].
- Mandatory header fields include Supplier code, Order type (STD or DIR), Tax code, Cost centre, and Need-by date; Source PR is mandatory for STD orders [MAN-DD-72 §6.2, MAN-PUR-72 §11.5].
- Mandatory line fields are Item code, Quantity, and Rate [MAN-PUR-72 §11.6].
- Line unit of measure (UOM) is read-only, and each order supports only one item line [MAN-PUR-72 §11.6].
- After entering the supplier and item, you must press F3 (Fetch) to retrieve the rate, tax code, payment terms, and warehouse, as well as cost centre, need-by date, and quantity for STD orders [MAN-PUR-72 §11.3].
- Fetch generates a one-time token valid for one supplier and item; you must run Fetch again if you alter either field [MAN-DD-72 §6.8, MAN-PUR-72 §11.3].
- To save, press F8; the system validates details, calculates tax and gross value (gross = basic + tax), verifies cost centres and budgets, and generates the PO number [MAN-DD-72 §6.4, MAN-PUR-72 §11.8].
- Saving an order against a purchase request automatically marks that request closed (CL) [MAN-PUR-72 §11.10].
- If an order's gross value falls within your limit, or if the source request approver's limit covers the order's gross value, the order saves with status AP (approved); otherwise, it saves as PA (pending approval) and routes to the approver's inbox [MAN-PUR-72 §11.9].
- Purchase orders can only be saved for suppliers with ACTIVE status [MAN-PUR-72 §11.11].

## Watch out
- Trying to save without running Fetch for the current supplier and item fails with error ERR-SCR-0221 (FETCH NOT DONE) [MAN-PUR-72 §11.3].
- Fetch defaults the tax code to GST18-INTRA; for an out-of-state supplier, you must manually change this to the appropriate -INTER code before saving, or the save fails with ERR-PO-0412 [MAN-PUR-72 §11.4].
- Entering a request on a DIR order causes error ERR-PO-0611 [MAN-PUR-72 §11.7].
- A direct order exceeding the allowable gross limit fails with ERR-PO-0610 (currently above ₹50,000; applies above ₹25,000 starting 2026-12-01) [MAN-PUR-72 §11.7, AMD-PUR-2026-03 §3.1].
- Entering a quantity greater than the request or choosing a different item triggers ERR-PO-0604 [MAN-PUR-72 §11.10].
- Attempting to save an order with a blocked supplier triggers ERR-SUP-0031 [MAN-PUR-72 §11.11].
- If an order is saved against a closed cost centre, it saves as DR (Draft) with warning W-CC-114 and will not be routed to anyone; always check the Status field on the header after saving [MAN-DD-72 §6.7, MAN-PUR-72 §11.8, MAN-PUR-72 §11.9].

## Related
- [[purchase-requests]] Purchase Requests (PR)
- [[purchase-policy-overview]] General Purchasing Policy
- [[approval-matrix-and-delegation]] Approval Matrix and Limits
- [[cost-centres-and-budgets]] Cost Centres and Budget Checks
- [[taxation-and-payment-terms]] Tax Codes and Payment Terms
- [[supplier-onboarding-and-master]] Supplier Onboarding and Management
- [[error-codes-reference]] System Error Codes and Troubleshooting
- [[data-dictionary-and-standards]] Bahi ERP Data Standards and Statuses
