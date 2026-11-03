---
title: "SAL sinv services"
type: "service-group"
slug: "services-sal-sinv"
summary: "Backend services in module SAL for creating, retrieving, searching, posting, cancelling, and printing sales invoices via screen SAL-INV-06."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/sales/sinv_cancel.yaml", "04_service_definitions/sales/sinv_get.yaml", "04_service_definitions/sales/sinv_post.yaml", "04_service_definitions/sales/sinv_print.yaml", "04_service_definitions/sales/sinv_save.yaml", "04_service_definitions/sales/sinv_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | SAL |
| Screen | [[screen-sal-inv-06|SAL-INV-06]] |
| Services | sinv_save, sinv_get, sinv_search, sinv_post, sinv_cancel, sinv_print |
| Status | current |
| Version introduced | Ledgerline 7.0 |

The `sinv` service group handles the creation, retrieval, search, posting, cancellation, and printing of customer sales invoices in module SAL [^r4][^r11][^r22]. These services support screen [[screen-sal-inv-06|SAL-INV-06]] to manage the sales invoicing lifecycle from draft creation through to posting to the sales and general ledgers [^r4][^r8][^r11]. All endpoints require a session token passed via the `X-LL-Session` header and appropriate role permissions [^r19][^r23][^r29][^r35][^r39][^r45].

## Services

### sinv_save

The `sinv_save` service creates a sales invoice draft and assigns the next sequence number in `SINV NO` [^r7][^r12]. It verifies line balances and persists the record as a draft [^r7].

* **Type**: Write [^r12][^r38]
* **Endpoint**: `POST /ll72/svc/sinv_save` [^r38]
* **Stored procedure**: `sp_sinv_save` [^r12][^r42]
* **Required fields**: `dlv_no` (str, DLV NO), `inv_dt` (date, INV DT) [^r12][^r40]
* **Optional fields**: None [^r40]
* **Errors**: Common errors `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r43]
* **Source file**: `04_service_definitions/sales/sinv_save.yaml` [^r38]

The response envelope returns `rc` ('S | W | E'), `err_cd`, `msg`, and `data` [^r41].

### sinv_get

The `sinv_get` service retrieves existing sales invoice header data, customer details, billing terms, line quantities, serial numbers, net rates, and carriage additions from dispatch and sales order tables [^r6][^r13].

* **Type**: Read [^r13][^r22]
* **Endpoint**: `POST /ll72/svc/sinv_get` [^r23]
* **Stored procedure**: None [^r13]
* **Required fields**: `sinv_no` (str, SINV NO) [^r13][^r24]
* **Optional fields**: None [^r24]
* **Errors**: Specific error `ERR-SIN-0001` (SALES INVOICE NOT FOUND); common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, `ERR-SYS-0503` [^r1][^r13][^r26][^r27]
* **Source file**: `04_service_definitions/sales/sinv_get.yaml` [^r22]

The response envelope returns `rc` ('S | W | E'), `err_cd`, `msg`, and `data` [^r25].

### sinv_search

The `sinv_search` service queries sales invoice records or launches a lookup dialogue displaying completed retailer dispatches to return delivery references [^r5][^r14][^r44].

* **Type**: Read [^r14][^r44]
* **Endpoint**: `POST /ll72/svc/sinv_search` [^r45]
* **Stored procedure**: None [^r14]
* **Required fields**: None [^r46]
* **Optional fields**: `dlv_no` (str, DLV NO), `inv_dt` (date, INV DT), `status` (str, STATUS) [^r14][^r46]
* **Errors**: Common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, `ERR-SYS-0503` [^r47]
* **Source file**: `04_service_definitions/sales/sinv_search.yaml` [^r44]

### sinv_post

The `sinv_post` service permanently locks invoice lines, posts transactions to customer trading balances across the sales and general ledgers, and updates invoice status to fully committed [^r8][^r15].

* **Type**: Write [^r15][^r28]
* **Endpoint**: `POST /ll72/svc/sinv_post` [^r28]
* **Stored procedure**: `sp_sinv_post` [^r15][^r32]
* **Required fields**: `sinv_no` (str, SINV NO) [^r15][^r30]
* **Optional fields**: `comment` (str, COMMENT) [^r15][^r30]
* **Errors**: Specific errors `ERR-SIN-0001` (SALES INVOICE NOT FOUND) and `ERR-SIN-0007` (SALES INVOICE NOT IN DRAFT (<status>)); common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, `ERR-SYS-0503` [^r1][^r2][^r15][^r32][^r33]
* **Source file**: `04_service_definitions/sales/sinv_post.yaml` [^r28]

The response envelope returns `rc` ('S | W | E'), `err_cd`, `msg`, and `data` [^r31].

### sinv_cancel

The `sinv_cancel` service validates clearance rules, records reversing accounting entries if the invoice was committed, changes the invoice status to cancelled, and releases the underlying delivery record for re-billing if permitted [^r10][^r16].

* **Type**: Write [^r16][^r18]
* **Endpoint**: `POST /ll72/svc/sinv_cancel` [^r18]
* **Stored procedure**: `sp_sinv_cancel` [^r16][^r48]
* **Required fields**: `sinv_no` (str, SINV NO), `reason` (str, REASON) [^r16][^r20]
* **Optional fields**: None [^r20]
* **Errors**: Specific errors `ERR-SIN-0001` (SALES INVOICE NOT FOUND) and `ERR-SIN-0801` (SALES INVOICE CLOSED (<status>)); common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, `ERR-SYS-0503` [^r1][^r3][^r16][^r48]
* **Source file**: `04_service_definitions/sales/sinv_cancel.yaml` [^r18]

The response envelope returns `rc` ('S | W | E'), `err_cd`, `msg`, and `data` [^r21].

### sinv_print

The `sinv_print` service routes formatted invoice output to designated print queues for postal dispatch or inclusion in courier pouches [^r9][^r17][^r34].

* **Type**: Write [^r17][^r34]
* **Endpoint**: `POST /ll72/svc/sinv_print` [^r35]
* **Stored procedure**: `sp_sinv_print` [^r17][^r34]
* **Required fields**: `sinv_no` (str, SINV NO) [^r17][^r36]
* **Optional fields**: None [^r36]
* **Errors**: Specific error `ERR-SIN-0001` (SALES INVOICE NOT FOUND); common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, `ERR-SYS-0503` [^r1][^r17][^r37]
* **Source file**: `04_service_definitions/sales/sinv_print.yaml` [^r34]

## See also

* [[screen-sal-inv-06|SAL-INV-06 Sales Invoice Entry]]
* [[services-sal-dlv|SAL dlv services]]
* [[services-sal-so|SAL so services]]
* [[errors-sin|Errors SIN (ERR-SIN-*)]]
* [[services-ap-inv|AP inv services]]

## References

[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 25, §9. Sales Invoice (SAL-INV-06)
[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 37, SAL-INV-06 SALES INVOICE ENTRY
[^r22]: 04_service_definitions/sales/sinv_get.yaml, service: sinv_get
[^r8]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 27, Step by step
[^r19]: 04_service_definitions/sales/sinv_cancel.yaml, auth
[^r23]: 04_service_definitions/sales/sinv_get.yaml, endpoint
[^r29]: 04_service_definitions/sales/sinv_post.yaml, auth
[^r35]: 04_service_definitions/sales/sinv_print.yaml, service: sinv_print
[^r39]: 04_service_definitions/sales/sinv_save.yaml, auth
[^r45]: 04_service_definitions/sales/sinv_search.yaml, auth
[^r7]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 27, Step by step
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 44, sinv_save SALES INVOICE SAVE
[^r38]: 04_service_definitions/sales/sinv_save.yaml, service: sinv_save
[^r42]: 04_service_definitions/sales/sinv_save.yaml, procedures
[^r40]: 04_service_definitions/sales/sinv_save.yaml, request
[^r43]: 04_service_definitions/sales/sinv_save.yaml, common_errors
[^r41]: 04_service_definitions/sales/sinv_save.yaml, response
[^r6]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 27, Step by step
[^r13]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 44, sinv_get SALES INVOICE GET
[^r24]: 04_service_definitions/sales/sinv_get.yaml, request.fields
[^r1]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 24, ERR-SIN-0001 SALES INVOICE NOT FOUND
[^r26]: 04_service_definitions/sales/sinv_get.yaml, errors
[^r27]: 04_service_definitions/sales/sinv_get.yaml, common_errors
[^r25]: 04_service_definitions/sales/sinv_get.yaml, response.envelope
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 27, Step by step
[^r14]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 44, sinv_search SALES INVOICE LIST
[^r44]: 04_service_definitions/sales/sinv_search.yaml, whole file
[^r46]: 04_service_definitions/sales/sinv_search.yaml, request.fields
[^r47]: 04_service_definitions/sales/sinv_search.yaml, common_errors
[^r15]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 44, sinv_post SALES INVOICE POST
[^r28]: 04_service_definitions/sales/sinv_post.yaml, service
[^r32]: 04_service_definitions/sales/sinv_post.yaml, errors
[^r30]: 04_service_definitions/sales/sinv_post.yaml, request.fields
[^r2]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 24, ERR-SIN-0007 SALES INVOICE NOT IN DRAFT (<status>)
[^r33]: 04_service_definitions/sales/sinv_post.yaml, common_errors
[^r31]: 04_service_definitions/sales/sinv_post.yaml, response.envelope
[^r10]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 27, Step by step
[^r16]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 45, sinv_cancel SALES INVOICE CANCEL
[^r18]: 04_service_definitions/sales/sinv_cancel.yaml, service: sinv_cancel
[^r48]: 04_service_definitions/sales/sinv_cancel.yaml, errors
[^r20]: 04_service_definitions/sales/sinv_cancel.yaml, request.fields
[^r3]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 24, ERR-SIN-0801 SALES INVOICE CLOSED (<status>)
[^r21]: 04_service_definitions/sales/sinv_cancel.yaml, response.envelope
[^r9]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 27, Step by step
[^r17]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 45, sinv_print SALES INVOICE PRINT
[^r34]: 04_service_definitions/sales/sinv_print.yaml, service: sinv_print
[^r36]: 04_service_definitions/sales/sinv_print.yaml, request
[^r37]: 04_service_definitions/sales/sinv_print.yaml, errors
