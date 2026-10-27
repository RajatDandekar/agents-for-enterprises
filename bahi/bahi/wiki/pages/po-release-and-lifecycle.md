---
title: PO Release, Amendments, and History
audience: all Bahi users
sources: MAN-PUR-72 §13.1, MAN-PUR-72 §13.2, MAN-PUR-72 §13.3, MAN-PUR-72 §13.4, MAN-PUR-72 §14.1, MAN-PUR-72 §14.2, MAN-PUR-72 §14.3, MAN-PUR-72 §14.4, MAN-PUR-72 §14.5, MAN-PUR-72 §14.6, MAN-PUR-72 §15.1, MAN-PUR-72 §15.2, MAN-PUR-72 §15.3
compiled_by: gemini:gemini-3.8-flash
---

# PO Release, Amendments, and History

This page covers releasing purchase orders to suppliers, changing order details, cancellations, and checking order history. Releasing transmits approved orders to vendors and updates stock tracking. You can also amend active orders, cancel unneeded orders, or review previous purchasing records for an item.

## Rules
- Only purchase orders in status AP can be released to the supplier [MAN-PUR-72 §13.1].
- Open the order and press F9 (Release) to change the status to RL, log the release date, add the quantity to stock on order, and e-mail the order to the supplier's order address [MAN-PUR-72 §13.2].
- The supplier receives the order number, item, quantity, rate, need-by date, delivery warehouse, and any printed remarks [MAN-PUR-72 §13.4].
- You can amend an order's quantity, need-by date, or cost centre, or cancel the order [MAN-PUR-72 §14.1].
- To amend, open the order, update the fields, and press F8; Bahi recalculates the gross value, releases committed budget, checks the new cost centre, and re-commits budget [MAN-PUR-72 §14.2].
- An amended order keeps its current status if the new gross value is still covered by the original approval [MAN-PUR-72 §14.3].
- To fix an order stuck in Draft due to a closed cost centre, amend it to an open cost centre so it can move to AP or PA under normal rules [MAN-PUR-72 §14.4].
- To cancel an order, press Cancel and enter a reason; status changes to CN, committed budget is released, and quantities on released orders are removed from stock on order [MAN-PUR-72 §14.5].
- Purchase order history shows the last ten released orders for an item—optionally filtered by supplier—in newest-first order with quantity, rate, and date [MAN-PUR-72 §15.1].
- Historical rates show previous purchases only; pricing for a new order must come from the current rate contract [MAN-PUR-72 §15.2].
- Search for purchase orders by navigating to Purchase, then Order list, using filters for supplier, item, status, client reference, and creation date [MAN-PUR-72 §15.3].

## Watch out
- Attempting to release an order not in status AP triggers ERR-PO-0715 (DOCUMENT NOT IN RELEASABLE STATUS); status DR usually points to a closed cost centre at save, while PA indicates pending approval [MAN-PUR-72 §13.3].
- Amending an order to a closed cost centre reverts the order to Draft with warning W-CC-114 [MAN-PUR-72 §14.2].
- If an amendment increases the gross value beyond the original approved amount, the order reverts to status PA for re-approval, even if already released [MAN-PUR-72 §14.3].
- Bahi does not notify suppliers of cancellations; you must inform the supplier directly [MAN-PUR-72 §14.5].
- Orders in status CN, RJ, or CL cannot be amended (ERR-PO-0801) [MAN-PUR-72 §14.6].

## Related
- [[purchase-orders]] Purchase Order Entry and Rules
- [[document-approval-workflow]] Document Approval Workflows
- [[cost-centres-and-budgets]] Cost Centres and Budget Checks
- [[rate-contracts-and-pricing]] Rate Contracts and Pricing Policies
- [[error-codes-reference]] System Error Codes and Troubleshooting
