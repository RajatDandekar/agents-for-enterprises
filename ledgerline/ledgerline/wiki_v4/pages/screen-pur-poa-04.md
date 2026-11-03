---
title: "PUR-POA-04 Purchase Order Approval"
type: "screen"
slug: "screen-pur-poa-04"
summary: "Ledgerline screen for reviewing, approving, or rejecting purchase orders in pending approval status."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/purchase/po_approve.yaml", "04_service_definitions/purchase/po_reject.yaml", "08_release_notes/RN-7.2.0 Ledgerline Release Notes.pdf", "11_training/QRC-06 Your approval inbox.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | PUR-POA-04 |
| Menu path | Purchase > Order approval |
| Roles permitted | PUR-SR, PUR-MGR, PLANT-HEAD, SYS-ADMIN |
| Primary services | po_approve, po_reject, po_get, po_pending_appr |
| Target status | AP (Approved) or RJ (Rejected) |

PUR-POA-04 provides a consolidated approval inbox in Ledgerline where purchase requests and orders exceeding buyer authority route for management review [^r12]. Approving an order changes its status to AP without releasing it directly to the supplier, while a rejection cancels the order to RJ and restores committed budget [^r3][^r4][^r20]. Approvers use this screen to verify department budgets, cost centres, and mandatory compliance comments prior to formal release [^r17][^r18].

## Fields

| Field | Description | Type / Mode |
|---|---|---|
| INBOX grid | Lists pending orders with document type, number, creator, and creation timestamp [^r1][^r6]. Displays originating site, supplier, cost centre, and narrative lines [^r13]. | Read-only grid (`po_pending_appr`) [^r1][^r6][^r13] |
| PO NO (`po_no`) | The purchase order number selected for review or action [^r6][^r10]. | Mandatory input [^r6][^r10] |
| COMMENT (`comment`) | Explanatory note or mandatory justification text [^r4][^r6][^r10][^r11]. Mandatory on rejection; optional on approval [^r4][^r10][^r11]. | Input [^r4][^r6][^r10][^r11] |
| SUP CD | The associated vendor code [^r6]. | Read-only [^r6] |
| RAISED BY | The originator who created the order [^r6]. | Read-only [^r6] |
| GROSS VALUE | Total order value evaluated against department budget [^r6][^r17]. | Read-only [^r6] |
| STATUS | The current document lifecycle status [^r6]. | Read-only [^r6] |

## Keys and services

* **Inbox (`po_pending_appr`)**: Loads documents waiting in the approval queue [^r1][^r6][^r24]. Background messaging automatically sends an e-mail notification with a direct record link whenever an entry arrives in the queue [^r14].
* **Fetch (`F3`, `po_get`)**: Retrieves individual order details, allowing approvers to inspect line items and cost centre allocations [^r13][^r24].
* **Approve (`F9`, `po_approve`)**: Invokes write service `POST /ll72/svc/po_approve` with mandatory `po_no` and optional `comment` [^r8][^r9][^r10][^r24]. Sets order status to AP [^r3].
* **Reject (`Shift+F9`, `po_reject`)**: Invokes write service `POST /ll72/svc/po_reject` with mandatory `po_no` and mandatory `comment` [^r8][^r11][^r24]. Sets status to RJ and releases committed budget [^r4].

External integrations generating purchase orders must leave records in pending status until approved through PUR-POA-04 prior to supplier transmission [^r15]. If an approver expects to be absent, they must notify the systems administrator in advance to redirect their queue and prevent production delays [^r23].

## Messages

* **ERR-APR-0003**: Raised if an approver attempts to approve their own purchase order, enforcing segregation of duties [^r2][^r7].
* **ERR-APR-0004**: Raised when the order value exceeds the approver's authorised limit [^r2].
* **ERR-PO-0702**: Raised if attempting to approve an order that is not currently in PA status [^r2][^r7].

## Operating rules

* Approvers must check that the gross total aligns with the department budget and confirm that split deliveries or call-offs route to matching receiving plant cost centres rather than general production inventory [^r17][^r22].
* For orders containing lithium-cell items such as battery packs or loose cells, approvers must enter `CERT OK` followed by the certificate reference into the comment field [^r18]. Omitting this entry causes inspection delays at the goods inward bay [^r19].
* Because rejecting an order permanently cancels the entry and obliges the originator to raise a fresh requisition, approvers should telephone originators regarding minor omissions prior to issuing a formal rejection [^r20][^r21].

## See also

* [[err-apr-0003]]
* [[err-apr-0004]]
* [[screen-fin-cc-01]]
* [[screen-pur-po-01]]
* [[screen-pur-por-05]]
* [[screen-pur-pr-01]]
* [[screen-pur-sup-03]]
* [[services-pur-po]]

## References

[^r12]: 08_release_notes/RN-7.2.0 Ledgerline Release Notes.pdf, p. 2, Purchasing: Approval inbox (PUR-POA-04) for requests and orders, with e-mail to th
[^r3]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 8, §12.2 Approving an order
[^r4]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 8, §12.3 Rejecting an order
[^r20]: 11_training/QRC-06 Your approval inbox.pdf, p. 1, Rejections and queries
[^r17]: 11_training/QRC-06 Your approval inbox.pdf, p. 1, Processing daily entries
[^r18]: 11_training/QRC-06 Your approval inbox.pdf, p. 1, Lithium-cell items
[^r1]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 8, §12.1 The approval inbox
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 27, PUR-POA-04 PURCHASE ORDER APPROVAL
[^r13]: 08_release_notes/RN-7.2.0 Ledgerline Release Notes.pdf, p. 2, Purchasing: Approval inbox (PUR-POA-04) for requests and orders, with e-mail to th
[^r10]: 04_service_definitions/purchase/po_approve.yaml, request.fields
[^r11]: 04_service_definitions/purchase/po_reject.yaml, service: po_reject
[^r24]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 27, PUR-POA-04 PURCHASE ORDER APPROVAL
[^r14]: 08_release_notes/RN-7.2.0 Ledgerline Release Notes.pdf, p. 2, Purchasing: Approval inbox (PUR-POA-04) for requests and orders, with e-mail to th
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 7, po_approve PO APPROVE
[^r9]: 04_service_definitions/purchase/po_approve.yaml, whole file
[^r15]: 08_release_notes/RN-7.2.0 Ledgerline Release Notes.pdf, p. 2, Purchasing: Approval inbox (PUR-POA-04) for requests and orders, with e-mail to th
[^r23]: 11_training/QRC-06 Your approval inbox.pdf, p. 1, Absence cover
[^r2]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 8, §12.2 Approving an order
[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 28, PUR-POA-04 PURCHASE ORDER APPROVAL
[^r22]: 11_training/QRC-06 Your approval inbox.pdf, p. 1, Split deliveries and call-offs
[^r19]: 11_training/QRC-06 Your approval inbox.pdf, p. 1, Lithium-cell items
[^r21]: 11_training/QRC-06 Your approval inbox.pdf, p. 1, Rejections and queries
