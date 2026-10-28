---
title: Purchase Order Entry and Rules
audience: all purchase staff
sources: POL-PUR-001 §3.3, POL-PUR-001 §3.4, MAN-DD-72 §6.1, MAN-DD-72 §6.2, MAN-DD-72 §6.3, MAN-DD-72 §6.4, MAN-DD-72 §6.5, MAN-DD-72 §6.6, MAN-DD-72 §6.7, MAN-DD-72 §6.8, MAN-PUR-72 §11.1, MAN-PUR-72 §11.2, MAN-PUR-72 §11.3, MAN-PUR-72 §11.4, MAN-PUR-72 §11.5, MAN-PUR-72 §11.6, MAN-PUR-72 §11.7, MAN-PUR-72 §11.8, MAN-PUR-72 §11.9, MAN-PUR-72 §11.10, MAN-PUR-72 §11.11
compiled_by: gemini:gemini-3.8-flash
---

# Purchase Order Entry and Rules
The purchase order screen creates standard or direct orders for active suppliers in Bahi ERP. Standard orders require an approved purchase request, while direct orders are reserved for low-value purchases. Each order contains a single line item and must undergo a system fetch before it can be saved.

## Rules
- Standard (STD) purchase orders are raised against an approved purchase request, and direct (DIR) orders have no source request [MAN-PUR-72 §11.2].
- A direct purchase order without a request is allowed only when its gross value, including GST, is ₹50,000 or less (effective 2026-04-01) [POL-PUR-001 §3.3].
- A direct order may not refer to a purchase request [MAN-PUR-72 §11.7].
- A purchase order raised against a request may not exceed the requested quantity (effective 2026-04-01) [POL-PUR-001 §3.4].
- Order numbers follow the format PO/<year>/<five digits>, such as example PO/2026/01182 [MAN-DD-72 §6.1].
- Mandatory header fields are Supplier code, Order type, Tax code, Cost centre, and Need-by date, along with Source PR for STD orders [MAN-PUR-72 §11.5].
- Mandatory line fields are Item code, Quantity, and Rate [MAN-PUR-72 §11.6].
- Header fields also include payment terms and warehouse; remarks are optional and print on the order [MAN-PUR-72 §11.5].
- The line grid allows only one item per order; create multiple orders for multiple items [MAN-PUR-72 §11.6].
- UOM is read-only [MAN-PUR-72 §11.6].
- Press F2 to search in Supplier code, Source PR (STD only), Tax code, Cost centre, Warehouse, and Item code, or to see rate history in Rate [MAN-PUR-72 §11.4, §11.5, §11.6].
- After entering the supplier and item, press F3 (Fetch) to pull the rate, tax code, payment terms, and warehouse, as well as the cost centre, need-by date, and quantity for STD orders [MAN-PUR-72 §11.3].
- Fetch returns a single-use token (fetch_tok) valid for one supplier and item, which is mandatory to save [MAN-DD-72 §6.8].
- Press F8 to save the order; Bahi validates details, computes tax and gross value (gross = basic + tax), checks the cost centre and budget, and generates the PO number [MAN-DD-72 §6.4, MAN-PUR-72 §11.8].
- The status bar displays `<PO number> SAVED` regardless of the resulting status, so verify the Status field on the header after saving [MAN-PUR-72 §11.8].
- The order saves as Approved (AP) if its gross value is within your limit, or if the source request approver's limit covers the order's gross value [MAN-PUR-72 §11.9].
- If approval limits are not met, the order saves as Pending Approval (PA) and routes to the approver's inbox [MAN-PUR-72 §11.9].
- Saving an order against a request automatically closes (CL) the request [MAN-PUR-72 §11.10].
- Orders can be saved only for ACTIVE suppliers [MAN-PUR-72 §11.11].

## Watch out
- If you change the supplier or item after running Fetch, you must press F3 (Fetch) again; otherwise, saving fails with ERR-SCR-0221 (FETCH NOT DONE) [MAN-PUR-72 §11.3].
- Fetch automatically applies tax code GST18-INTRA; for an out-of-state supplier, manually change this to the appropriate -INTER code before saving or the order fails with ERR-PO-0412 [MAN-PUR-72 §11.4].
- A direct order exceeding the configured company limit (shipped default ₹50,000) fails on save with ERR-PO-0610; raise a purchase request instead [MAN-PUR-72 §11.7].
- Adding a request to a direct order triggers error ERR-PO-0611 [MAN-PUR-72 §11.7].
- Entering a different item or a larger quantity than stated on the source request causes error ERR-PO-0604 [MAN-PUR-72 §11.10].
- Attempting to save an order for a blocked supplier results in error ERR-SUP-0031 [MAN-PUR-72 §11.11].
- If saved against a closed cost centre, the order is set to Draft (DR) with warning W-CC-114 and is not routed to anyone [MAN-DD-72 §6.7, MAN-PUR-72 §11.9].
- Bahi does not verify supplier certificates on the purchase order screen [MAN-PUR-72 §11.11].

## Related
- [[purchase-requests]] Purchase Requests (PR)
- [[purchase-policy-overview]] General Purchasing Policy
- [[approval-matrix-and-delegation]] Approval Matrix and Limits
- [[document-approval-workflow]] Document Approval Workflows
- [[po-release-and-lifecycle]] PO Release, Amendments, and History
- [[supplier-onboarding-and-master]] Supplier Onboarding and Management
- [[taxation-and-payment-terms]] Tax Codes and Payment Terms
- [[cost-centres-and-budgets]] Cost Centres and Budget Checks
- [[error-codes-reference]] System Error Codes and Troubleshooting
- [[data-dictionary-and-standards]] Bahi ERP Data Standards and Statuses
