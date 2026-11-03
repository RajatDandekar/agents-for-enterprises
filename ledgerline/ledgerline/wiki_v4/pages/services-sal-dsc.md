---
title: "SAL dsc services"
type: "service-group"
slug: "services-sal-dsc"
summary: "Ledgerline sales discount services (dsc_get, dsc_save, dsc_search) serving screen SAL-DSC-10 for managing customer commercial discount agreements."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/sales/dsc_get.yaml", "04_service_definitions/sales/dsc_save.yaml", "04_service_definitions/sales/dsc_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | SAL |
| Object | dsc |
| Screen | SAL-DSC-10 |
| Available since | Ledgerline 7.0 |
| Services | dsc_get, dsc_save, dsc_search |

The `services-sal-dsc` service group manages commercial discount agreements linked to customer ledger accounts in Ledgerline's sales module [^r1][^r3][^r9]. Introduced in version 7.0, these services power discount inquiries, record retrieval, and validation updates on screen [[screen-sal-dsc-10|SAL-DSC-10]] [^r5][^r9][^r14][^r18]. All endpoints require role authorization and session token authentication passed via the `X-LL-Session` header [^r10][^r15][^r18].

## Services

### dsc_get

Service `dsc_get` (DISCOUNT GET) is a read service exposed at `POST /ll72/svc/dsc_get` that retrieves discount agreement details from central pricing tables for screen [[screen-sal-dsc-10|SAL-DSC-10]] [^r2][^r6][^r9][^r10]. On the screen interface, it maps to Get (F3) and populates fields `CUST CD`, `DISC %`, `VALID TO`, and `STATUS` [^r2][^r5].

* **Required fields:** `dsc_cd` (string, DSC CD) [^r6][^r11].
* **Optional fields:** none [^r11].
* **Errors:** [[err-dsc-0001|ERR-DSC-0001]] when the discount identifier is not found, along with common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r6][^r13].
* **Response:** Returns standard envelope fields `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r12].
* **Source files:** `04_service_definitions/sales/dsc_get.yaml`, `MAN-SAL-72`, `MAN-SCR-72`, `MAN-SVC-72` [^r2][^r5][^r6][^r9].

### dsc_save

Service `dsc_save` (DISCOUNT SAVE) is a write service exposed at `POST /ll72/svc/dsc_save` that validates discount field values against customer ledger rules and writes new or amended terms to core database tables using stored procedure `sp_dsc_save` [^r3][^r7][^r14][^r17]. On screen [[screen-sal-dsc-10|SAL-DSC-10]], it maps to Save (F8) [^r5][^r7].

* **Required fields:** `cust_cd` (string, CUST CD) and `dsc_pct` (float, DISC %) [^r7][^r16].
* **Optional fields:** `valid_to` (date, VALID TO) [^r7][^r16].
* **Errors:** [[err-dsc-0001|ERR-DSC-0001]] if the customer account does not exist, fails structural validation, exceeds permitted category terms, or carries an administrative hold or stop [^r4]. Standard common errors include `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r17].
* **Source files:** `04_service_definitions/sales/dsc_save.yaml`, `MAN-SAL-72`, `MAN-SCR-72`, `MAN-SVC-72` [^r3][^r4][^r5][^r7][^r14].

### dsc_search

Service `dsc_search` (DISCOUNT LIST) is a read service exposed at `POST /ll72/svc/dsc_search` that renders an inquiry overlay of existing commercial discount agreements and associated customer codes on screen [[screen-sal-dsc-10|SAL-DSC-10]] [^r1][^r8][^r18]. On the screen, it is invoked via Search (F2 or Enter) [^r5].

* **Required fields:** none [^r19].
* **Optional fields:** `cust_cd` (string), `dsc_pct` (float), `valid_to` (date), and `status` (string) [^r8][^r19].
* **Errors:** Standard common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r20].
* **Response:** Returns standard envelope fields `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r20].
* **Source files:** `04_service_definitions/sales/dsc_search.yaml`, `MAN-SAL-72`, `MAN-SCR-72`, `MAN-SVC-72` [^r1][^r5][^r8][^r18].

## See also

* [[screen-sal-dsc-10|SAL-DSC-10 Discount]]
* [[err-dsc-0001|ERR-DSC-0001]]
* [[screen-sal-cus-01|SAL-CUS-01 Customer Master Entry]]
* [[services-sal-cust|SAL cust services]]
* [[services-sal-prc|SAL prc services]]
* [[services-sal-so|SAL so services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 38, Available buttons and services
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 38, Available buttons and services
[^r9]: 04_service_definitions/sales/dsc_get.yaml, whole file
[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 35, SAL-DSC-10 DISCOUNT
[^r14]: 04_service_definitions/sales/dsc_save.yaml, service: dsc_save
[^r18]: 04_service_definitions/sales/dsc_search.yaml, service: dsc_search
[^r10]: 04_service_definitions/sales/dsc_get.yaml, auth
[^r15]: 04_service_definitions/sales/dsc_save.yaml, auth
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 38, Available buttons and services
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 47, dsc_get DISCOUNT GET
[^r11]: 04_service_definitions/sales/dsc_get.yaml, request.fields
[^r13]: 04_service_definitions/sales/dsc_get.yaml, errors
[^r12]: 04_service_definitions/sales/dsc_get.yaml, response.envelope
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 47, dsc_save DISCOUNT SAVE
[^r17]: 04_service_definitions/sales/dsc_save.yaml, procedures
[^r16]: 04_service_definitions/sales/dsc_save.yaml, request.fields
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 41, Questions users ask
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 47, dsc_search DISCOUNT LIST
[^r19]: 04_service_definitions/sales/dsc_search.yaml, request.fields
[^r20]: 04_service_definitions/sales/dsc_search.yaml, response.envelope
