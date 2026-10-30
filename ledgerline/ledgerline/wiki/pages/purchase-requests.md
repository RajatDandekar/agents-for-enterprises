---
title: Purchase Requests (PR)
audience: all purchase staff
sources: POL-PUR-001 §3.1, POL-PUR-001 §3.2, POL-PUR-001 §5.4, MAN-DD-72 §5.1, MAN-DD-72 §5.2, MAN-DD-72 §5.3, MAN-DD-72 §5.4, MAN-DD-72 §5.5, MAN-PUR-72 §9.1, MAN-PUR-72 §9.2, MAN-PUR-72 §9.3, MAN-PUR-72 §9.4, MAN-PUR-72 §9.5, MAN-PUR-72 §9.6
compiled_by: gemini:gemini-3.8-flash
---

# Purchase Requests (PR)
A purchase request (PR) initiates the buying process in Ledgerline ERP. It captures key details such as the item, quantity, need-by date, warehouse, and cost centre before an order can be created. Approving a request routes it based on estimated value and covers subsequent order generation.

## Rules
- Every purchase must begin with a purchase request in Ledgerline, unless it qualifies as a direct order under §3.3 [POL-PUR-001 §3.1].
- From 2026-04-01, each purchase request must name the item, quantity, need-by date, warehouse, and the cost centre that carries the spend [POL-PUR-001 §3.2].
- Mandatory screen fields on PUR-PR-01 include Item code (F2), Quantity, Need-by date, and Cost centre (F2); optional or defaulted fields are Warehouse (F2; defaults to WH-MAN-STR), Estimated rate, and Remarks [MAN-PUR-72 §9.2].
- The request type (`pr_type`) is STD for standard requests [MAN-DD-72 §5.2, MAN-PUR-72 §9.2].
- Press F3 (Fetch) after entering the item code to automatically populate the unit of measure, warehouse, default cost centre, and estimated rate [MAN-PUR-72 §9.3].
- Request numbers follow the format `pr_no` PR/<year>/<five digits> (for example, PR/2026/04417) [MAN-DD-72 §5.1].
- Press F8 to save the request; Ledgerline assigns a request number and sets the status to DR (Draft) [MAN-PUR-72 §9.4].
- The estimated value (`est_value`) is calculated as: quantity × estimated rate × 1.20 [MAN-DD-72 §5.4, MAN-PUR-72 §9.4].
- Press F9 (Submit) to submit the request; if the estimated value is within your limit, it is approved immediately (status AP) [MAN-PUR-72 §9.5].
- If the estimated value exceeds your limit, Ledgerline routes the request up the management line to an approver whose limit covers it, marks the status PA (pending approval), and sends an email notification [MAN-PUR-72 §9.5].
- PR approval covers the purchase order raised against it, provided the approver's limit covers the order's gross value [POL-PUR-001 §5.4].
- The system stores audit details including `raised_by`, `raised_on`, and `approved_by` [MAN-DD-72 §5.5].
- Standard database fields recorded for each request are `cc_cd` (Cost centre), `need_dt` (Need-by date), `whs_cd` (Warehouse), and remarks [MAN-DD-72 §5.3].

## Watch out
- The estimated rate fetched by F3 uses the rate from the last released purchase order for the item, not the current contract rate [MAN-PUR-72 §9.3].
- Estimated value calculations automatically apply an assumed 20% VAT regardless of the item's actual tax rate [MAN-PUR-72 §9.4].
- The need-by date must be today or in the future; entering a past date triggers error ERR-PR-0105 [MAN-PUR-72 §9.6].

## Related
- [[purchase-orders]] Purchase Order Entry and Rules
- [[approval-matrix-and-delegation]] Approval Matrix and Limits
- [[purchase-policy-overview]] General Purchasing Policy
- [[document-approval-workflow]] Document Approval Workflows
- [[cost-centres-and-budgets]] Cost Centres and Budget Checks
- [[data-dictionary-and-standards]] Ledgerline ERP Data Standards and Statuses
- [[error-codes-reference]] System Error Codes and Troubleshooting
