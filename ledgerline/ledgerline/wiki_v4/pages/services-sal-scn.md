---
title: "SAL scn services"
type: "service-group"
slug: "services-sal-scn"
summary: "Ledgerline sales credit note service group providing draft creation, retrieval, and posting operations for customer credit notes on screen SAL-CRN-09."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/sales/scn_get.yaml", "04_service_definitions/sales/scn_post.yaml", "04_service_definitions/sales/scn_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | SAL |
| Object | scn |
| Screens | SAL-CRN-09 |
| Services | scn_get, scn_post, scn_save |
| Ledgerline version | 7.0+ |
| Endpoint base | /ll72/svc/ |

The SAL scn service group manages customer credit note operations against posted customer invoices in Ledgerline [^r1]. It provides read, draft creation, and ledger posting capabilities backing screen [[screen-sal-crn-09|SAL-CRN-09]] [^r1][^r5]. All services authenticate through the `X-LL-Session` header with role-based execution permissions [^r10][^r16][^r22].

## Services

### scn_get

The `scn_get` service retrieves customer credit note header and transaction data [^r2]. Available since version 7.0 under endpoint `POST /ll72/svc/scn_get`, it provides read functionality supporting screen [[screen-sal-crn-09|SAL-CRN-09]] [^r5][^r9][^r10].

* **Required fields:** `scn_no` (string) [^r7][^r11].
* **Optional fields:** none [^r11].
* **Errors:** [[err-scn-0001|ERR-SCN-0001]] (CUSTOMER CREDIT NOTE NOT FOUND) [^r7][^r13], `ERR-SEC-0001` (ACCESS DENIED) [^r14], `ERR-SYS-0421` (<FIELD> MANDATORY) [^r14], `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>) [^r14], and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r14].
* **Source file:** `04_service_definitions/sales/scn_get.yaml` [^r9].

The response envelope returns `rc` (`S`, `W`, or `E`), `err_cd` when `rc` is `E`, short message `msg` in capitals, and payload `data` [^r12].

### scn_post

The `scn_post` write service executes stored procedure `sp_scn_post` to post customer credit adjustments to the general ledger, reducing open customer balances and posting to sales returns [^r4][^r8][^r15]. It operates at endpoint `POST /ll72/svc/scn_post` and supports screen [[screen-sal-crn-09|SAL-CRN-09]] [^r5][^r8][^r15].

* **Required fields:** `scn_no` (string) [^r8][^r17].
* **Optional fields:** `comment` (string) [^r8][^r17].
* **Errors:** [[err-scn-0001|ERR-SCN-0001]] (CUSTOMER CREDIT NOTE NOT FOUND) [^r8][^r19], [[err-scn-0007|ERR-SCN-0007]] (CUSTOMER CREDIT NOTE NOT IN DRAFT (<status>)) [^r8][^r19], `ERR-SEC-0001` (ACCESS DENIED) [^r20], `ERR-SYS-0421` (<FIELD> MANDATORY) [^r20], `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>) [^r20], and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r20].
* **Source file:** `04_service_definitions/sales/scn_post.yaml` [^r15].

The service returns standard envelope fields `rc`, `err_cd`, `msg`, and `data` [^r18].

### scn_save

The `scn_save` write service writes an unposted draft credit note to the sales ledger buffer and allocates an internal sequence number via stored procedure `sp_scn_save` [^r3][^r6][^r24]. Available since version 7.0 at endpoint `POST /ll72/svc/scn_save`, it processes draft entry on screen [[screen-sal-crn-09|SAL-CRN-09]] [^r5][^r6][^r21][^r22].

* **Required fields:** `cust_cd` (string), `sinv_no` (string), `reason_cd` (string), and `amount` (float) [^r6][^r23].
* **Optional fields:** none [^r23].
* **Errors:** `ERR-SEC-0001` [^r25], `ERR-SYS-0421` [^r25], `ERR-SYS-0422` [^r25], and `ERR-SYS-0503` [^r25].
* **Source file:** `04_service_definitions/sales/scn_save.yaml` [^r21].

The service response envelope returns `rc`, `err_cd`, `msg`, and `data` [^r24].

## See also

* [[screen-sal-crn-09|SAL-CRN-09 Customer Credit Note Entry]]
* [[err-scn-0001|ERR-SCN-0001 Invoice not found for customer account]]
* [[err-scn-0007|ERR-SCN-0007 Customer credit note posting validation failure]]
* [[services-sal-sinv|SAL sinv services]]
* [[services-sal-cust|SAL cust services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 41, §13. Customer Credit Note (SAL-CRN-09)
[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 33, SAL-CRN-09 CUSTOMER CREDIT NOTE ENTRY
[^r10]: 04_service_definitions/sales/scn_get.yaml, endpoint
[^r16]: 04_service_definitions/sales/scn_post.yaml, auth
[^r22]: 04_service_definitions/sales/scn_save.yaml, service: scn_save
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 42, Retrieving existing documents
[^r9]: 04_service_definitions/sales/scn_get.yaml, service: scn_get
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 48, scn_get CUSTOMER CREDIT NOTE GET
[^r11]: 04_service_definitions/sales/scn_get.yaml, request.fields
[^r13]: 04_service_definitions/sales/scn_get.yaml, errors
[^r14]: 04_service_definitions/sales/scn_get.yaml, common_errors
[^r12]: 04_service_definitions/sales/scn_get.yaml, response.envelope
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 43, Checking and posting the credit note
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 48, scn_post CUSTOMER CREDIT NOTE POST
[^r15]: 04_service_definitions/sales/scn_post.yaml, service: scn_post
[^r17]: 04_service_definitions/sales/scn_post.yaml, request
[^r19]: 04_service_definitions/sales/scn_post.yaml, errors
[^r20]: 04_service_definitions/sales/scn_post.yaml, common_errors
[^r18]: 04_service_definitions/sales/scn_post.yaml, response
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 43, Creating a new credit note
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 48, scn_save CUSTOMER CREDIT NOTE SAVE
[^r24]: 04_service_definitions/sales/scn_save.yaml, response
[^r21]: 04_service_definitions/sales/scn_save.yaml, service: scn_save
[^r23]: 04_service_definitions/sales/scn_save.yaml, request
[^r25]: 04_service_definitions/sales/scn_save.yaml, common_errors
