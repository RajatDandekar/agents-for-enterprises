---
title: "PRD wo services"
type: "service-group"
slug: "services-prd-wo"
summary: "Production work order services handling creation, retrieval, searching, release, completion, and cancellation on screen PRD-WO-01 in Ledgerline ERP 7.2."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/wo_cancel.yaml", "04_service_definitions/production/wo_close.yaml", "04_service_definitions/production/wo_get.yaml", "04_service_definitions/production/wo_release.yaml", "04_service_definitions/production/wo_save.yaml", "04_service_definitions/production/wo_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| service_group | wo |
| module | PRD |
| screen | PRD-WO-01 |
| services | wo_save, wo_get, wo_search, wo_release, wo_close, wo_cancel |
| version_introduced | 7.0 |
| status | current |

The `wo` service group provides production work order processing capabilities in Ledgerline ERP 7.2 under the PRD module [^r9][^r26]. It exposes endpoints for creating, retrieving, querying, releasing, closing, and cancelling work orders, primarily called by screen [[screen-prd-wo-01|PRD-WO-01]] (Work Order Entry) [^r9][^r16][^r36]. All services require an active session token passed in the `X-LL-Session` request header and enforce role-based access permissions [^r17][^r22][^r27][^r32][^r37][^r42].

| Key | Value |
|---|---|
| Service Group | wo |
| Module | PRD |
| Primary Screen | [[screen-prd-wo-01|PRD-WO-01]] |
| Services | `wo_save`, `wo_get`, `wo_search`, `wo_release`, `wo_close`, `wo_cancel` |
| Introduced | Version 7.0 |
| Standard Envelope | `rc`, `err_cd`, `msg`, `data` |

## Services

### wo_save

The `wo_save` service creates or updates work order header records via database stored procedure `sp_wo_save` [^r1][^r10][^r36][^r40]. Running the service generates a new reference in the `WO NO` field [^r5].

* **Kind**: write [^r36]
* **Endpoint**: `POST /ll72/svc/wo_save` [^r37]
* **Required fields**: `itm_cd` (string), `qty` (integer), `start_dt` (date), `cc_cd` (string) [^r10][^r38]
* **Optional fields**: `wc_cd` (string, work centre) [^r10][^r38]
* **Errors**: [[err-wo-0201|ERR-WO-0201]] (`QTY MUST BE > 0`), [[err-itm-0011|ERR-ITM-0011]] (`ITEM NOT FOUND OR INACTIVE`), [[err-cc-0009|ERR-CC-0009]], [[err-wo-0105|ERR-WO-0105]] (`DATE IN PAST`) [^r10][^r49]
* **Source file**: `04_service_definitions/production/wo_save.yaml` [^r36]

### wo_get

The `wo_get` service provides read access to retrieve complete work order details [^r11][^r26].

* **Kind**: read [^r26]
* **Endpoint**: `POST /ll72/svc/wo_get` [^r26]
* **Required fields**: `wo_no` (string) [^r11][^r28]
* **Optional fields**: none [^r28]
* **Errors**: [[err-wo-0001|ERR-WO-0001]] (`WORK ORDER NOT FOUND`), `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, `ERR-SYS-0503` [^r11][^r30][^r47]
* **Source file**: `04_service_definitions/production/wo_get.yaml` [^r26]

### wo_search

The `wo_search` service queries work order lists using filter criteria [^r12][^r41].

* **Kind**: read [^r41]
* **Endpoint**: `POST /ll72/svc/wo_search` [^r41]
* **Required fields**: none [^r43]
* **Optional fields**: `itm_cd` (string), `qty` (integer), `start_dt` (date), `status` (string) [^r12][^r43]
* **Errors**: [[err-wo-0201|ERR-WO-0201]] (`QTY MUST BE > 0`), [[err-itm-0011|ERR-ITM-0011]] (`ITEM NOT FOUND OR INACTIVE`), [[err-wo-0105|ERR-WO-0105]] (`DATE IN PAST`), `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, `ERR-SYS-0503` [^r12][^r45][^r46][^r49]
* **Source file**: `04_service_definitions/production/wo_search.yaml` [^r41]

### wo_release

The `wo_release` service validates component stock availability, creates warehouse reservations, and advances the work order status to released via stored procedure `sp_wo_release` [^r2][^r6][^r13][^r31][^r34].

* **Kind**: write [^r31]
* **Endpoint**: `POST /ll72/svc/wo_release` [^r32]
* **Required fields**: `wo_no` (string) [^r13][^r33]
* **Optional fields**: `comment` (string) [^r13][^r33]
* **Errors**: [[err-wo-0001|ERR-WO-0001]] (`WORK ORDER NOT FOUND`), [[err-wo-0007|ERR-WO-0007]] (`WORK ORDER NOT RELEASED`), [[err-wo-0310|ERR-WO-0310]] (`COMPONENT SHORTAGE (<itm_cd>)`), [[err-bom-0001|ERR-BOM-0001]] (`Parent assembly not found on bill of materials master`) [^r13][^r35][^r47][^r48]
* **Source file**: `04_service_definitions/production/wo_release.yaml` [^r31]

### wo_close

The `wo_close` service completes an order, executes job variance calculations, and marks the record closed through database stored procedure `sp_wo_close` after assembly and quality checks finish [^r3][^r7][^r14][^r21][^r25].

* **Kind**: write [^r21]
* **Endpoint**: `POST /ll72/svc/wo_close` [^r21]
* **Required fields**: `wo_no` (string) [^r14][^r23]
* **Optional fields**: `comment` (string) [^r14][^r23]
* **Errors**: [[err-wo-0001|ERR-WO-0001]] (`WORK ORDER NOT FOUND`), [[err-wo-0801|ERR-WO-0801]] (`WORK ORDER CLOSED (<status>)`) [^r14][^r47][^r50]
* **Source file**: `04_service_definitions/production/wo_close.yaml` [^r21]

### wo_cancel

The `wo_cancel` service relieves component inventory reservations and archives a work order via stored procedure `sp_wo_cancel` [^r4][^r15][^r16][^r17].

* **Kind**: write [^r16]
* **Endpoint**: `POST /ll72/svc/wo_cancel` [^r17]
* **Required fields**: `wo_no` (string), `reason` (string) [^r4][^r8][^r15][^r18]
* **Optional fields**: none [^r18]
* **Errors**: [[err-wo-0001|ERR-WO-0001]] (`WORK ORDER NOT FOUND`), [[err-wo-0801|ERR-WO-0801]] (`WORK ORDER CLOSED (<status>)`), `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, `ERR-SYS-0503` [^r15][^r19][^r20][^r47][^r50]
* **Source file**: `04_service_definitions/production/wo_cancel.yaml` [^r16]

## Versions and conflicts

* Today's rule: Service specifications and error manuals establish that [[err-wo-0105|ERR-WO-0105]] corresponds to `DATE IN PAST` and [[err-wo-0201|ERR-WO-0201]] corresponds to `QTY MUST BE > 0` on `wo_save` and `wo_search` [^r10][^r12][^r45][^r49]; [[err-wo-0310|ERR-WO-0310]] indicates component shortages on `wo_release` [^r13][^r35][^r48]; and [[err-wo-0801|ERR-WO-0801]] signals closed status conflicts on `wo_close` and `wo_cancel` [^r14][^r15][^r19][^r50].
* Contradiction: Manual `MAN-PRD-72` describes conflicting and transposed mappings for these error codes in narrative text [^r1][^r2][^r3][^r4][^r5][^r6][^r7][^r8]. It states that `ERR-WO-0001` or `ERR-WO-0007` represent missing save fields [^r1], `ERR-WO-0105` represents database sequence failures [^r5] or component stock shortages [^r2], `ERR-WO-0201` denotes failed stock reservations, on-hold work centres, or unposted movements [^r3][^r6], `ERR-WO-0310` represents missing cancel reasons or unresolved scrap bookings [^r4][^r7], and `ERR-WO-0007` denotes cancellation after processing has commenced [^r8].

## See also

* [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]
* [[errors-wo|ERR-WO error codes]]
* [[err-wo-0310|ERR-WO-0310 Component Shortage on Work Order Release]]
* [[err-bom-0001|ERR-BOM-0001 Parent assembly not found on bill of materials master]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[err-cc-0009|ERR-CC-0009]]
* [[services-prd-bom|PRD bom services]]
* [[services-prd-opr|PRD opr services]]
* [[services-prd-bkf|PRD bkf services]]
* [[services-prd-mrp|PRD mrp services]]
* [[services-prd-mps|PRD mps services]]
* [[services-pur-po|PUR po services]]

## References

[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 26, PRD-WO-01 WORK ORDER ENTRY
[^r26]: 04_service_definitions/production/wo_get.yaml, whole file
[^r16]: 04_service_definitions/production/wo_cancel.yaml, service: wo_cancel
[^r36]: 04_service_definitions/production/wo_save.yaml, service: wo_save
[^r17]: 04_service_definitions/production/wo_cancel.yaml, service: wo_cancel
[^r22]: 04_service_definitions/production/wo_close.yaml, auth
[^r27]: 04_service_definitions/production/wo_get.yaml, auth
[^r32]: 04_service_definitions/production/wo_release.yaml, endpoint
[^r37]: 04_service_definitions/production/wo_save.yaml, service: wo_save
[^r42]: 04_service_definitions/production/wo_search.yaml, auth
[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 6, Messages
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 52, §6. Production services
[^r40]: 04_service_definitions/production/wo_save.yaml, procedures
[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 7
[^r38]: 04_service_definitions/production/wo_save.yaml, request.fields
[^r49]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 27
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 53, §6. Production services
[^r28]: 04_service_definitions/production/wo_get.yaml, request.fields
[^r30]: 04_service_definitions/production/wo_get.yaml, errors
[^r47]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 27
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 53, §6. Production services
[^r41]: 04_service_definitions/production/wo_search.yaml, service: wo_search
[^r43]: 04_service_definitions/production/wo_search.yaml, request.fields
[^r45]: 04_service_definitions/production/wo_search.yaml, errors
[^r46]: 04_service_definitions/production/wo_search.yaml, common_errors
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 6, Messages
[^r6]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 7
[^r13]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 53, §6. Production services
[^r31]: 04_service_definitions/production/wo_release.yaml, service: wo_release
[^r34]: 04_service_definitions/production/wo_release.yaml, response.envelope
[^r33]: 04_service_definitions/production/wo_release.yaml, request.fields
[^r35]: 04_service_definitions/production/wo_release.yaml, errors
[^r48]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 27
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 6, Messages
[^r7]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 7
[^r14]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 53, §6. Production services
[^r21]: 04_service_definitions/production/wo_close.yaml, service: wo_close
[^r25]: 04_service_definitions/production/wo_close.yaml, procedures
[^r23]: 04_service_definitions/production/wo_close.yaml, request.fields
[^r50]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 28
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 6, Messages
[^r15]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 53, §6. Production services
[^r8]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 7
[^r18]: 04_service_definitions/production/wo_cancel.yaml, request
[^r19]: 04_service_definitions/production/wo_cancel.yaml, errors
[^r20]: 04_service_definitions/production/wo_cancel.yaml, common_errors
