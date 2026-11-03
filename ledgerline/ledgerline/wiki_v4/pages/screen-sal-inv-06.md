---
title: "SAL-INV-06 Sales Invoice Entry"
type: "screen"
slug: "screen-sal-inv-06"
summary: "Ledgerline screen SAL-INV-06 for sales invoice entry, posting, cancellation, and printing against dispatch references."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/sales/sinv_cancel.yaml", "04_service_definitions/sales/sinv_get.yaml", "04_service_definitions/sales/sinv_post.yaml", "04_service_definitions/sales/sinv_print.yaml", "04_service_definitions/sales/sinv_save.yaml", "04_service_definitions/sales/sinv_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen | SAL-INV-06 |
| Title | Sales Invoice Entry |
| Menu path | Sales > Sales invoice |
| Module | Sales |
| Roles | SAL-EXEC, SAL-MGR, SYS-ADMIN |
| Services | sinv_save, sinv_get, sinv_search, sinv_post, sinv_cancel, sinv_print |

Screen SAL-INV-06 is the Ledgerline interface used to record customer commercial indebtedness, apply VAT, credit turnover accounts, and generate formal billing paperwork [^r1][^r2]. Located under menu path `Sales > Sales invoice`, it allows authorized roles to create, retrieve, search, post, cancel, and print sales invoices [^r1][^r9]. Prior to generating an invoice on this screen, goods must be flagged as dispatched, customer accounts must not be subject to administrative credit holds, and carriage charges or concessions must already exist on the order [^r3].

| Field | Detail |
|---|---|
| Screen code | SAL-INV-06 [^r1] |
| Title | Sales Invoice Entry [^r9] |
| Navigation | Sales > Sales invoice [^r1][^r9] |
| Permitted roles | SAL-EXEC, SAL-MGR, SYS-ADMIN [^r9] |
| Primary services | `sinv_save`, `sinv_get`, `sinv_search`, `sinv_post`, `sinv_cancel`, `sinv_print` [^r1] |

## Fields

Screen SAL-INV-06 contains both mandatory and optional fields for document identification and processing [^r9][^r19]:

* **DLV NO**: Mandatory dispatch note reference identifying the goods shipped [^r4][^r9][^r19]. Saving a sales invoice requires entering this delivery number [^r17].
* **INV DT**: Mandatory invoice date [^r9][^r17][^r19]. Staff must not overwrite this date unless explicitly instructed by the finance controller for end-of-month reconciliations [^r7].
* **SINV NO**: Mandatory sales invoice document number, used to look up or cancel invoices [^r6][^r9][^r11][^r12][^r19].
* **REASON**: Mandatory explanation text required when executing an invoice cancellation [^r6][^r9][^r11][^r19].
* **COMMENT**: Optional field used for delivery instructions or specific store booking-in references for the printed document, and passed during posting [^r5][^r9][^r14][^r19].
* **STATUS**: Optional field reflecting invoice state and available as a search criterion [^r9][^r18][^r19].

## Keys and services

SAL-INV-06 binds its interface actions and function keys to the [[services-sal-sinv|SAL sinv services]] [^r1][^r10]:

* **Save (F8)**: Invokes write service `sinv_save` (POST `/ll72/svc/sinv_save`), requiring parameters `dlv_no` and `inv_dt` [^r10][^r16][^r17].
* **Get (F3)**: Invokes read service `sinv_get` (POST `/ll72/svc/sinv_get`) to retrieve a specific invoice record using mandatory parameter `sinv_no` [^r4][^r10][^r12].
* **Search (F2/Enter)**: Invokes read service `sinv_search` to query and list sales invoices matching criteria entered in `DLV NO`, `INV DT`, or `STATUS` [^r4][^r10][^r18].
* **Post (F9)**: Invokes write service `sinv_post` (POST `/ll72/svc/sinv_post`), passing mandatory `sinv_no` and optional `comment` to execute stored procedure `sp_sinv_post` and post the invoice to the sales ledger [^r10][^r13][^r14].
* **Cancel (Shift+F8)**: Invokes write service `sinv_cancel`, passing `sinv_no` and `reason` [^r10][^r11]. This cancellation action is only permitted while an invoice remains unposted; once committed with `sinv_post`, staff must contact the sales ledger team to raise a credit note on [[screen-sal-crn-09|SAL-CRN-09 Customer Credit Note Entry]] rather than cancelling [^r6][^r8].
* **Print**: Invokes write service `sinv_print` to generate formal billing paperwork [^r1][^r2][^r10][^r15].

## Messages

Screen SAL-INV-06 can raise the following error codes from [[errors-sin|Errors SIN (ERR-SIN-*)]] during processing [^r10]:

* `ERR-SIN-0001` [^r10]
* `ERR-SIN-0007` [^r10]
* `ERR-SIN-0801` [^r10]

## See also

* [[services-sal-sinv|SAL sinv services]]
* [[screen-sal-dlv-05|SAL-DLV-05 Despatch Entry]]
* [[screen-sal-crn-09|SAL-CRN-09 Customer Credit Note Entry]]
* [[screen-sal-crd-11|SAL-CRD-11 Credit Control Check]]
* [[screen-sal-so-01|SAL-SO-01 Sales Order]]
* [[errors-sin|Errors SIN (ERR-SIN-*)]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 25, §9. Sales Invoice (SAL-INV-06)
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 26, Purpose
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 36, SAL-INV-06 SALES INVOICE ENTRY
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 26, Before you start
[^r19]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 25, §9. Sales Invoice (SAL-INV-06)
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 27, Step by step
[^r17]: 04_service_definitions/sales/sinv_save.yaml, request
[^r7]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 28, Tips
[^r6]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 27, Step by step
[^r11]: 04_service_definitions/sales/sinv_cancel.yaml, screen
[^r12]: 04_service_definitions/sales/sinv_get.yaml, service: sinv_get
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 27, Step by step
[^r14]: 04_service_definitions/sales/sinv_post.yaml, request.fields
[^r18]: 04_service_definitions/sales/sinv_search.yaml, whole file
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 37, SAL-INV-06 SALES INVOICE ENTRY
[^r16]: 04_service_definitions/sales/sinv_save.yaml, screen
[^r13]: 04_service_definitions/sales/sinv_post.yaml, service
[^r8]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 29, Questions users ask
[^r15]: 04_service_definitions/sales/sinv_print.yaml, service: sinv_print
