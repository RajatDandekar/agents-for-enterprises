---
title: "SAL cust services"
type: "service-group"
slug: "services-sal-cust"
summary: "Ledgerline customer master services for creating, fetching, searching, updating, blocking, and checking credit profiles on screen SAL-CUS-01."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/sales/cust_block.yaml", "04_service_definitions/sales/cust_credit.yaml", "04_service_definitions/sales/cust_get.yaml", "04_service_definitions/sales/cust_save.yaml", "04_service_definitions/sales/cust_search.yaml", "04_service_definitions/sales/cust_update.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Service Group | services-sal-cust |
| Module | SAL |
| Screen | SAL-CUS-01 |
| Kind | Read / Write |
| Available Since | Ledgerline 7.0 |
| Endpoints Base | POST /ll72/svc/ |

The `services-sal-cust` group encompasses the Ledgerline ERP sales services used to maintain customer account profiles on [[screen-sal-cus-01|SAL-CUS-01 Customer Master Entry]] [^r7]. Available since Ledgerline 7.0, these services handle master record creation, search lookups, full record retrieval, credit limit calculations, record modifications, and order blocking [^r1][^r2][^r3][^r4][^r5][^r6][^r7][^r14][^r19][^r24][^r29][^r34][^r39]. All services operate over HTTPS POST endpoints requiring an active session token in header `X-LL-Session` and appropriate role authorisation [^r15][^r20][^r25][^r30][^r35][^r40].

## Services

### cust_save

The `cust_save` (CUSTOMER MASTER SAVE) write service commits a new customer account, validates mandatory fields across database tables, executes backend stored procedure `sp_cust_save`, and returns the assigned permanent `CUST CD` [^r1][^r8][^r29][^r33]. It is exposed at endpoint `POST /ll72/svc/cust_save` and returns a standard response envelope containing `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r30][^r32].

* **Required fields:** `name` (CUST NAME), `city` (CITY), `country` (COUNTRY CD (2)) [^r8][^r31].
* **Optional fields:** `vat_no` (VAT number), `pt_cd` (PAY TERM CD), `price_list` (PRICE LIST) [^r8][^r31].
* **Errors:** Common errors `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r33].
* **Source file:** `04_service_definitions/sales/cust_save.yaml` [^r29].

### cust_get

The `cust_get` (CUSTOMER MASTER GET) read service retrieves the customer master record and populates associated address, tax, and commercial terms on [[screen-sal-cus-01|SAL-CUS-01]] [^r2][^r9][^r24]. It is invoked at endpoint `POST /ll72/svc/cust_get` and returns a standard response envelope (`rc`, `err_cd`, `msg`, `data`) [^r24][^r27].

* **Required fields:** `cust_cd` (CUST CD) [^r9][^r26].
* **Optional fields:** None [^r26].
* **Errors:** [[err-cus-0001|ERR-CUS-0001]] (CUSTOMER MASTER NOT FOUND), alongside common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r9][^r28].
* **Source file:** `04_service_definitions/sales/cust_get.yaml` [^r24].

### cust_search

The `cust_search` (CUSTOMER MASTER LIST) read service presents a selection overlay of matching bike shops and retailers when filtering customer master listings on [[screen-sal-cus-01|SAL-CUS-01]] [^r3][^r10][^r34]. It runs via endpoint `POST /ll72/svc/cust_search` and returns the standard envelope (`rc`, `err_cd`, `msg`, `data`) [^r34][^r37].

* **Required fields:** None [^r36].
* **Optional fields:** `name` (CUST NAME), `city` (CITY), `country` (COUNTRY CD (2)), `status` (STATUS) [^r10][^r36].
* **Errors:** Common errors `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r38].
* **Source file:** `04_service_definitions/sales/cust_search.yaml` [^r34].

### cust_update

The `cust_update` (CUSTOMER MASTER UPDATE) write service updates customer master modifications and refreshes database buffers and audit logs via backend procedure `sp_cust_update` [^r4][^r11][^r39][^r43]. It is accessible at endpoint `POST /ll72/svc/cust_update` and returns the standard response envelope with `rc`, `err_cd`, `msg`, and `data` [^r40][^r42].

* **Required fields:** `cust_cd` (CUST CD) [^r11][^r41].
* **Optional fields:** `name` (CUST NAME), `city` (CITY), `country` (COUNTRY CD (2)), `vat_no` (VAT number) [^r41].
* **Errors:** [[err-cus-0001|ERR-CUS-0001]], [[err-cus-0801|ERR-CUS-0801]], and common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r11][^r43].
* **Source file:** `04_service_definitions/sales/cust_update.yaml` [^r39].

### cust_block

The `cust_block` (CUSTOMER MASTER BLOCK) write service executes database procedure `sp_cust_block` to validate changes and set STATUS to show a blocked condition, preventing the customer account from being picked on new sales orders or delivery notes [^r5][^r12][^r14][^r17]. It is invoked at endpoint `POST /ll72/svc/cust_block` with the standard envelope structure [^r15][^r17].

* **Required fields:** `cust_cd` (CUST CD) [^r12][^r16].
* **Optional fields:** `reason` (REASON) [^r16].
* **Errors:** [[err-cus-0001|ERR-CUS-0001]] (CUSTOMER MASTER NOT FOUND), `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r12][^r18].
* **Source file:** `04_service_definitions/sales/cust_block.yaml` [^r14].

### cust_credit

The `cust_credit` (CUSTOMER MASTER CREDIT) read service queries sales ledger balances, committed bicycle orders, and unbilled dispatches to calculate credit headroom for an account on [[screen-sal-cus-01|SAL-CUS-01]] [^r6][^r13][^r19]. It is accessed at endpoint `POST /ll72/svc/cust_credit` and provides a standard envelope response [^r20][^r22].

* **Required fields:** `cust_cd` (CUST CD) [^r13][^r21].
* **Optional fields:** `name` (CUST NAME), `city` (CITY), `country` (COUNTRY CD (2)), `vat_no` (VAT number) [^r21].
* **Errors:** [[err-cus-0001|ERR-CUS-0001]] (CUSTOMER MASTER NOT FOUND), `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r13][^r23].
* **Source file:** `04_service_definitions/sales/cust_credit.yaml` [^r19].

## See also

* [[screen-sal-cus-01|SAL-CUS-01 Customer Master Entry]]
* [[screen-sal-so-01|SAL-SO-01 Sales Order]]
* [[services-sal-so|SAL so services]]
* [[services-sal-dlv|SAL dlv services]]
* [[err-cus-0001|ERR-CUS-0001 Mandatory Field Missing or Invalid in Customer Master]]
* [[err-cus-0801|ERR-CUS-0801 Invalid or Duplicate VAT Number]]

## References

[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 34, SAL-CUS-01 CUSTOMER MASTER ENTRY
[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 4, Step by step
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 4, Step by step
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 5, Step by step
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 5, Step by step
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 5, Step by step
[^r6]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 5, Step by step
[^r14]: 04_service_definitions/sales/cust_block.yaml, service: cust_block
[^r19]: 04_service_definitions/sales/cust_credit.yaml, service: cust_credit
[^r24]: 04_service_definitions/sales/cust_get.yaml, service: cust_get
[^r29]: 04_service_definitions/sales/cust_save.yaml, header
[^r34]: 04_service_definitions/sales/cust_search.yaml, service: cust_search
[^r39]: 04_service_definitions/sales/cust_update.yaml, service
[^r15]: 04_service_definitions/sales/cust_block.yaml, endpoint
[^r20]: 04_service_definitions/sales/cust_credit.yaml, service: cust_credit
[^r25]: 04_service_definitions/sales/cust_get.yaml, auth
[^r30]: 04_service_definitions/sales/cust_save.yaml, endpoint / auth
[^r35]: 04_service_definitions/sales/cust_search.yaml, auth
[^r40]: 04_service_definitions/sales/cust_update.yaml, endpoint
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 38, §5. Sales services
[^r33]: 04_service_definitions/sales/cust_save.yaml, procedures
[^r32]: 04_service_definitions/sales/cust_save.yaml, response.envelope
[^r31]: 04_service_definitions/sales/cust_save.yaml, request.fields
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 38, cust_get CUSTOMER MASTER GET
[^r27]: 04_service_definitions/sales/cust_get.yaml, response
[^r26]: 04_service_definitions/sales/cust_get.yaml, request
[^r28]: 04_service_definitions/sales/cust_get.yaml, errors
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 38, cust_search CUSTOMER MASTER LIST
[^r37]: 04_service_definitions/sales/cust_search.yaml, response.envelope
[^r36]: 04_service_definitions/sales/cust_search.yaml, request.fields
[^r38]: 04_service_definitions/sales/cust_search.yaml, common_errors
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 38, cust_update CUSTOMER MASTER UPDATE
[^r43]: 04_service_definitions/sales/cust_update.yaml, procedures
[^r42]: 04_service_definitions/sales/cust_update.yaml, response.envelope
[^r41]: 04_service_definitions/sales/cust_update.yaml, request.fields
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 38, cust_block CUSTOMER MASTER BLOCK
[^r17]: 04_service_definitions/sales/cust_block.yaml, response.envelope
[^r16]: 04_service_definitions/sales/cust_block.yaml, request.fields
[^r18]: 04_service_definitions/sales/cust_block.yaml, errors
[^r13]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 39, cust_credit CUSTOMER MASTER CREDIT
[^r22]: 04_service_definitions/sales/cust_credit.yaml, response
[^r21]: 04_service_definitions/sales/cust_credit.yaml, request
[^r23]: 04_service_definitions/sales/cust_credit.yaml, errors
