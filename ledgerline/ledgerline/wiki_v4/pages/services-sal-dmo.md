---
title: "SAL dmo services"
type: "service-group"
slug: "services-sal-dmo"
summary: "Ledgerline SAL module service group for demonstration bicycle lifecycle operations on screen SAL-DMO-17."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/sales/dmo_close.yaml", "04_service_definitions/sales/dmo_get.yaml", "04_service_definitions/sales/dmo_save.yaml", "04_service_definitions/sales/dmo_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | SAL |
| Object | dmo |
| Screen | SAL-DMO-17 |
| Services | dmo_save, dmo_get, dmo_search, dmo_close |
| Introduced | 7.1 |
| Endpoint prefix | /ll72/svc/ |

The `services-sal-dmo` group provides the backend procedures for tracking Northbridge demonstration bicycles throughout their customer evaluation lifecycle[^r1][^r6]. Exposed on [[screen-sal-dmo-17|SAL-DMO-17 Demo Bike Entry]], these services manage record creation, detail retrieval, search lookups, and demo closure[^r4][^r6]. All services operate via HTTP POST endpoints under `/ll72/svc/`, authenticate through the `X-LL-Session` header, and return standard response envelopes containing `rc`, `err_cd`, `msg`, and `data`[^r12][^r14][^r18][^r20][^r22][^r24][^r27][^r29].

## Services

### dmo_save

The `dmo_save` service (DEMO BIKE SAVE) is a write service in module SAL, present since Ledgerline ERP 7.1 and accessible via endpoint `POST /ll72/svc/dmo_save`[^r22]. It executes database stored procedure `sp_dmo_save` to validate header parameters, verify item, serial, and customer details, write state changes, save remarks, assign the next sequential system-generated reference to `DMO NO` on new records, and set `STATUS` to active[^r1][^r5][^r7][^r24]. On [[screen-sal-dmo-17|SAL-DMO-17]], it is bound to Save (F8)[^r6].

* **Required fields:** `itm_cd` (ITEM CD, string), `serial_no` (SERIAL NO, string), `cust_cd` (CUST CD, string), and `return_dt` (RETURN DT, date)[^r7][^r23].
* **Optional fields:** None[^r23].
* **Errors:** [[err-itm-0011|ERR-ITM-0011]] (`ITEM NOT FOUND OR INACTIVE`), alongside common errors `ERR-SEC-0001` (`ACCESS DENIED`), `ERR-SYS-0421` (`<FIELD> MANDATORY`), `ERR-SYS-0422` (`UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>`), and `ERR-SYS-0503` (`SERVER BUSY, TRY LATER`)[^r7][^r25].
* **Source file:** `04_service_definitions/sales/dmo_save.yaml`[^r22].

### dmo_get

The `dmo_get` service (DEMO BIKE GET) is a read service in module SAL, available since version 7.1 and invoked via `POST /ll72/svc/dmo_get` with a session token in header `X-LL-Session` where the user's role permits execution[^r17][^r18]. It reads an existing demonstration record by `DMO NO` and populates screen fields including `STATUS` and `COMMENT`[^r2][^r8]. On [[screen-sal-dmo-17|SAL-DMO-17]], it is mapped to Get (F3)[^r6].

* **Required fields:** `dmo_no` (DMO NO, string)[^r8][^r19].
* **Optional fields:** None[^r19].
* **Errors:** [[err-dmo-0001|ERR-DMO-0001]] (`DEMO BIKE NOT FOUND`), and common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503`[^r8][^r21].
* **Source file:** `04_service_definitions/sales/dmo_get.yaml`[^r17].

### dmo_search

The `dmo_search` service (DEMO BIKE LIST) is a read service in module SAL, present since version 7.1 and called via `POST /ll72/svc/dmo_search` using `X-LL-Session` header authentication[^r26][^r27]. It queries demonstration bicycle records using criteria such as customer code or serial number and returns matching records in a lookup window[^r3][^r9]. On [[screen-sal-dmo-17|SAL-DMO-17]], it is triggered by Search (F2/Enter)[^r6].

* **Required fields:** None[^r28].
* **Optional fields:** `itm_cd` (ITEM CD, string), `serial_no` (SERIAL NO, string), `cust_cd` (CUST CD, string), and `status` (STATUS, string)[^r9][^r28].
* **Errors:** [[err-itm-0011|ERR-ITM-0011]] (`ITEM NOT FOUND OR INACTIVE`), as well as common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503`[^r9][^r30][^r31].
* **Source file:** `04_service_definitions/sales/dmo_search.yaml`[^r26].

### dmo_close

The `dmo_close` service (DEMO BIKE CLOSE) is a write service in module SAL, present since version 7.1 and reached at `POST /ll72/svc/dmo_close` via session token in header `X-LL-Session`[^r11][^r12]. It executes database procedure `sp_dmo_close` to mark demonstration bicycle records as closed and release the frame serial number back to standard inventory or refurbishment stock[^r4][^r10][^r12]. On [[screen-sal-dmo-17|SAL-DMO-17]], it is exposed as the Close action[^r6].

* **Required fields:** `dmo_no` (DMO NO, string)[^r10][^r13].
* **Optional fields:** `comment` (COMMENT, string)[^r10][^r13].
* **Errors:** [[err-dmo-0001|ERR-DMO-0001]] (`DEMO BIKE NOT FOUND`), [[err-dmo-0801|ERR-DMO-0801]] (`DEMO BIKE CLOSED (<status>)`), and common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503`[^r10][^r15][^r16].
* **Source file:** `04_service_definitions/sales/dmo_close.yaml`[^r11].

## See also

* [[screen-sal-dmo-17|SAL-DMO-17 Demo Bike Entry]]
* [[err-dmo-0001|ERR-DMO-0001 DEMO BIKE NOT FOUND]]
* [[err-dmo-0801|ERR-DMO-0801 DEMO BIKE CLOSED (<status>)]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[services-sal-so|SAL so services]]
* [[services-sal-srl|SAL srl services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 67, Step by step
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 35, SAL-DMO-17 DEMO BIKE ENTRY
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 69, Worked example
[^r12]: 04_service_definitions/sales/dmo_close.yaml, endpoint
[^r14]: 04_service_definitions/sales/dmo_close.yaml, response.envelope
[^r18]: 04_service_definitions/sales/dmo_get.yaml, endpoint
[^r20]: 04_service_definitions/sales/dmo_get.yaml, response.envelope
[^r22]: 04_service_definitions/sales/dmo_save.yaml, service: dmo_save
[^r24]: 04_service_definitions/sales/dmo_save.yaml, response.envelope
[^r27]: 04_service_definitions/sales/dmo_search.yaml, service: dmo_search
[^r29]: 04_service_definitions/sales/dmo_search.yaml, response.envelope
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 69, Worked example
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 52, SAL-DMO-17
[^r23]: 04_service_definitions/sales/dmo_save.yaml, request.fields
[^r25]: 04_service_definitions/sales/dmo_save.yaml, errors
[^r17]: 04_service_definitions/sales/dmo_get.yaml, service: dmo_get
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 68, PART 14 of 14
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 52, SAL-DMO-17
[^r19]: 04_service_definitions/sales/dmo_get.yaml, request.fields
[^r21]: 04_service_definitions/sales/dmo_get.yaml, errors
[^r26]: 04_service_definitions/sales/dmo_search.yaml, service: dmo_search
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 68, PART 14 of 14
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 52, SAL-DMO-17
[^r28]: 04_service_definitions/sales/dmo_search.yaml, request.fields
[^r30]: 04_service_definitions/sales/dmo_search.yaml, errors
[^r31]: 04_service_definitions/sales/dmo_search.yaml, common_errors
[^r11]: 04_service_definitions/sales/dmo_close.yaml, service
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 52, SAL-DMO-17
[^r13]: 04_service_definitions/sales/dmo_close.yaml, request.fields
[^r15]: 04_service_definitions/sales/dmo_close.yaml, errors
[^r16]: 04_service_definitions/sales/dmo_close.yaml, common_errors
