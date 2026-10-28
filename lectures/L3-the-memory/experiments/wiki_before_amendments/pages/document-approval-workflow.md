---
title: Document Approval Workflows
audience: all Bahi users
sources: MAN-PUR-72 §10.1, MAN-PUR-72 §10.2, MAN-PUR-72 §10.3, MAN-PUR-72 §12.1, MAN-PUR-72 §12.2, MAN-PUR-72 §12.3, MAN-PUR-72 §12.4
compiled_by: gemini:gemini-3.8-flash
---

# Document Approval Workflows
This page explains how to review, approve, and reject purchase requests and purchase orders in Bahi ERP. Approvers can access pending documents directly from their approval inbox or via email notifications. Completing an approval changes the document status, but approved purchase orders still require release before going to the supplier.

## Rules
- Approvers review purchase requests waiting for them to approve or reject [MAN-PUR-72 §10.1].
- To approve a purchase request, open it from the approval inbox, verify the item, quantity, estimated value, and cost centre, enter a comment, and select Approve to set the status to AP [MAN-PUR-72 §10.2].
- To reject a purchase request, choose Reject and enter a reason to set the status to RJ and notify the raiser by email [MAN-PUR-72 §10.3].
- Approvers view pending orders by navigating to Purchase and then Order approval, where each row lists the document type, number, creator, and creation date [MAN-PUR-72 §12.1].
- Bahi ERP sends an email to the approver whenever a new document arrives in the approval inbox [MAN-PUR-72 §12.1].
- To approve a purchase order, open the document, check its details, and select Approve with an optional comment to change the status to AP [MAN-PUR-72 §12.2].
- To reject a purchase order, press Reject and provide a mandatory reason, which sets the status to RJ and releases the committed budget [MAN-PUR-72 §12.3].
- An approved purchase order with status AP is not sent to the supplier until it is released [MAN-PUR-72 §12.4].

## Watch out
- You cannot approve a purchase request or purchase order that you raised yourself, triggering error ERR-APR-0003 [MAN-PUR-72 §10.2] [MAN-PUR-72 §12.2].
- You cannot approve a purchase request or purchase order with a value exceeding your approval limit, triggering error ERR-APR-0004 [MAN-PUR-72 §10.2] [MAN-PUR-72 §12.2].
- A rejected purchase request cannot be resubmitted; you must create a new request instead [MAN-PUR-72 §10.3].
- You cannot approve a purchase order that is not currently pending approval, which causes error ERR-PO-0702 [MAN-PUR-72 §12.2].

## Related
- [[approval-matrix-and-delegation]] Approval Matrix and Limits
- [[purchase-requests]] Purchase Requests (PR)
- [[purchase-orders]] Purchase Order Entry and Rules
- [[po-release-and-lifecycle]] PO Release, Amendments, and History
- [[error-codes-reference]] System Error Codes and Troubleshooting
