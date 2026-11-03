---
title: "SAL prc services"
type: "service-group"
slug: "services-sal-prc"
summary: "Ledgerline SAL module services for retrieving, creating, searching, and duplicating price list schedules on screen SAL-PRC-08."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/sales/prc_copy.yaml", "04_service_definitions/sales/prc_get.yaml", "04_service_definitions/sales/prc_save.yaml", "04_service_definitions/sales/prc_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| service_group | services-sal-prc |
| module | SAL |
| screen | SAL-PRC-08 |
| introduced | Ledgerline 7.0 |
| services | prc_get, prc_save, prc_search, prc_copy |
| status | current |

The `services-sal-prc` service group provides pricing and tariff schedule maintenance within the Sales (`SAL`) module of Ledgerline [^r1][^r11]. Operating against screen [[screen-sal-prc-08|SAL-PRC-08]], these services handle price list searching, line retrieval, line updates, and tariff copying [^r4][^r6]. All services require an authenticated session token in header `X-LL-Session` with an authorized user role [^r12][^r16][^r21][^r26].

## Services

### prc_get

`prc_get` (PRICE LIST GET) is a read service that retrieves price list line details—including price, valid from date, and status—into the working buffer [^r2][^r7][^r15]. It runs via HTTP POST at `/ll72/svc/prc_get` without an associated database procedure [^r7][^r15].

* **Required fields**: `price_list` (str) [^r7][^r17].
* **Optional fields**: None [^r7][^r17].
* **Errors**: [[err-prc-0001|ERR-PRC-0001]] (PRICE LIST NOT FOUND), along with common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r7][^r19].
* **Source file**: `04_service_definitions/sales/prc_get.yaml` [^r15].

### prc_save

`prc_save` (PRICE LIST SAVE) is a write service that validates and commits changes or additions to price list lines by invoking stored procedure `sp_prc_save` [^r3][^r8][^r20][^r24]. It is exposed at endpoint POST `/ll72/svc/prc_save` [^r21].

* **Required fields**: `price_list` (str), `itm_cd` (str), `price` (float), and `valid_from` (date) [^r8][^r22].
* **Optional fields**: None [^r22].
* **Errors**: [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE) when the item code is not found in inventory tables, [[err-prc-0001|ERR-PRC-0001]] if mandatory parameters are missing or identical lines overlap for the same VALID FROM date, and common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r3][^r24].
* **Source file**: `04_service_definitions/sales/prc_save.yaml` [^r20].

### prc_search

`prc_search` (PRICE LIST LIST) is a read service that queries tariff schedules and price lists across the database [^r1][^r9][^r25]. It operates at endpoint POST `/ll72/svc/prc_search` [^r25].

* **Required fields**: None [^r27].
* **Optional fields**: `price_list` (str), `itm_cd` (str), `price` (float), and `status` (str) [^r9][^r27].
* **Errors**: [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE) [^r9][^r28].
* **Source file**: `04_service_definitions/sales/prc_search.yaml` [^r25].

### prc_copy

`prc_copy` (PRICE LIST COPY) is a write service executing stored procedure `sp_prc_copy` that duplicates an existing tariff schedule under a new identifier and start date, bypassing manual line re-entry [^r4][^r10][^r11][^r14]. Users invoke this after retrieving a price list with `prc_get` and commit adjustments using `prc_save` [^r5]. It runs at endpoint POST `/ll72/svc/prc_copy` [^r12].

* **Required fields**: `price_list` (str) [^r10][^r13].
* **Optional fields**: `itm_cd` (str), `price` (float), and `valid_from` (date) [^r10][^r13].
* **Errors**: [[err-prc-0001|ERR-PRC-0001]] (PRICE LIST NOT FOUND) and [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE) [^r10][^r14].
* **Source file**: `04_service_definitions/sales/prc_copy.yaml` [^r11].

## Versions and conflicts

* **prc_save required fields**: The service definition requires `valid_from` alongside `price_list`, `itm_cd`, and `price` [^r22]. The service reference summary lists only `price_list`, `itm_cd`, and `price` [^r8] (contradiction).
* **prc_save error codes**: User documentation notes `prc_save` raises [[err-prc-0001|ERR-PRC-0001]] when mandatory parameters are absent or identical lines overlap for the same date [^r3]. The service YAML definition lists only [[err-itm-0011|ERR-ITM-0011]] among domain-specific error codes [^r24] (contradiction).

## See also

* [[screen-sal-prc-08|screen-sal-prc-08]]: SAL-PRC-08 Price List
* [[err-prc-0001|err-prc-0001]]: ERR-PRC-0001 Mandatory parameters absent or pricing conflict
* [[err-itm-0011|err-itm-0011]]: ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE
* [[services-sal-dsc|services-sal-dsc]]: SAL dsc services
* [[services-sal-so|services-sal-so]]: SAL so services

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 34, Screen layout
[^r11]: 04_service_definitions/sales/prc_copy.yaml, whole file
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 34, Screen layout
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 37, SAL-PRC-08 PRICE LIST
[^r12]: 04_service_definitions/sales/prc_copy.yaml, whole file
[^r16]: 04_service_definitions/sales/prc_get.yaml, auth
[^r21]: 04_service_definitions/sales/prc_save.yaml, endpoint
[^r26]: 04_service_definitions/sales/prc_search.yaml, auth
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 34, Step by step: Retrieving and viewing existing prices
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 46, prc_get PRICE LIST GET
[^r15]: 04_service_definitions/sales/prc_get.yaml, service: prc_get
[^r17]: 04_service_definitions/sales/prc_get.yaml, request.fields
[^r19]: 04_service_definitions/sales/prc_get.yaml, errors
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 35, Messages
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 46, prc_save PRICE LIST SAVE
[^r20]: 04_service_definitions/sales/prc_save.yaml, service: prc_save
[^r24]: 04_service_definitions/sales/prc_save.yaml, errors
[^r22]: 04_service_definitions/sales/prc_save.yaml, request.fields
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 47, prc_search PRICE LIST LIST
[^r25]: 04_service_definitions/sales/prc_search.yaml, whole file
[^r27]: 04_service_definitions/sales/prc_search.yaml, request.fields
[^r28]: 04_service_definitions/sales/prc_search.yaml, errors
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 47, prc_copy PRICE LIST COPY
[^r14]: 04_service_definitions/sales/prc_copy.yaml, errors
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 37, §12. Discount (SAL-DSC-10)
[^r13]: 04_service_definitions/sales/prc_copy.yaml, request
