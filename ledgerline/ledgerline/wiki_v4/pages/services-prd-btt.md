---
title: "PRD btt services"
type: "service-group"
slug: "services-prd-btt"
summary: "Ledgerline PRD battery end-of-line test services managing pack test records, queries, electrical measurement validation, and archive searches on screen QA-BTT-03."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/btt_get.yaml", "04_service_definitions/production/btt_save.yaml", "04_service_definitions/production/btt_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | PRD |
| Object | btt (Battery End-Of-Line Test) |
| Screen | QA-BTT-03 |
| Introduced | Ledgerline 7.2.0 |
| Protocol | POST (/ll72/svc/btt_*) |
| Auth | X-LL-Session header |

The `btt` service group provides backend services in the PRD module for managing battery pack end-of-line test records on screen [[screen-qa-btt-03|QA-BTT-03]] [^r3][^r7]. Introduced in Ledgerline 7.2.0, the group comprises `btt_save`, `btt_get`, and `btt_search` to record, retrieve, and search electrical testing results including pack serial numbers, item codes, open-circuit voltages (OCV), internal resistances, and pass/fail statuses [^r3][^r8][^r11][^r21]. All endpoints require POST requests with session token authentication supplied in the `X-LL-Session` header and an authorised role [^r12][^r17][^r22].

## Services

### btt_get

Retrieves battery end-of-line test data from the battery archive for screen [[screen-qa-btt-03|QA-BTT-03]] [^r4][^r9][^r11].

* **Endpoint**: `POST /ll72/svc/btt_get` [^r12]
* **Operation**: Read [^r11]
* **Required fields**: `serial_no` (string, PACK SERIAL) [^r4][^r9][^r13]
* **Optional fields**: None [^r13]
* **Returns**: Envelope with `rc`, `err_cd`, `msg`, and `data` containing `itm_cd`, `ocv`, `ir_mohm`, `result`, and `status` [^r4][^r14]
* **Errors**: `ERR-BTT-0001` (BATTERY END-OF-LINE TEST NOT FOUND), `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, `ERR-SYS-0503` [^r1][^r15]
* **Source file**: `04_service_definitions/production/btt_get.yaml` [^r11]

### btt_save

Validates electrical measurements, writes the battery end-of-line test record to the database via stored procedure `sp_btt_save`, and locks the record against modification [^r6][^r8][^r20].

* **Endpoint**: `POST /ll72/svc/btt_save` [^r16]
* **Operation**: Write [^r8][^r16]
* **Required fields**: `serial_no` (string, PACK SERIAL), `itm_cd` (string, ITEM CD), `ocv` (float, OCV (V)), `ir_mohm` (float, IR (MOHM)), and `result` (string, PASS/FAIL) [^r8][^r18]
* **Optional fields**: None [^r18]
* **Returns**: Envelope with `rc`, `err_cd`, `msg`, and `data` [^r19]
* **Errors**: `ERR-BTT-0110` (battery serial number already tested), `ERR-BTT-0120` (open-circuit voltage out of range) [^r2]
* **Source file**: `04_service_definitions/production/btt_save.yaml` [^r16]

### btt_search

Queries and returns a list of recent battery end-of-line test records filtered by criteria on screen [[screen-qa-btt-03|QA-BTT-03]] [^r5][^r10][^r21].

* **Endpoint**: `POST /ll72/svc/btt_search` [^r21]
* **Operation**: Read [^r21]
* **Required fields**: None [^r23]
* **Optional fields**: `serial_no` (string, PACK SERIAL), `itm_cd` (string, ITEM CD), `ocv` (float, OCV (V)), and `status` (string, STATUS) [^r10][^r23]
* **Returns**: Envelope with `rc`, `err_cd`, `msg`, and `data` [^r24]
* **Errors**: [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE), `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, `ERR-SYS-0503` [^r25]
* **Source file**: `04_service_definitions/production/btt_search.yaml` [^r21]

## See also

* [[screen-qa-btt-03|QA-BTT-03 Battery End-Of-Line Test Entry]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[services-prd-wo|PRD wo services]]
* [[services-prd-qin|PRD qin services]]
* [[services-prd-cal|PRD cal services]]

## References

[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 41, §13. Battery End-Of-Line Test (QA-BTT-03)
[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 31, QA-BTT-03 BATTERY END-OF-LINE TEST ENTRY
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 60, btt_save BATTERY END-OF-LINE TEST SAVE
[^r11]: 04_service_definitions/production/btt_get.yaml, service: btt_get
[^r21]: 04_service_definitions/production/btt_search.yaml, service: btt_search
[^r12]: 04_service_definitions/production/btt_get.yaml, service: btt_get
[^r17]: 04_service_definitions/production/btt_save.yaml, auth
[^r22]: 04_service_definitions/production/btt_search.yaml, auth
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 42, Step by step
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 61, btt_get BATTERY END-OF-LINE TEST GET
[^r13]: 04_service_definitions/production/btt_get.yaml, request.fields
[^r14]: 04_service_definitions/production/btt_get.yaml, response.envelope
[^r1]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 4, §2. Codes
[^r15]: 04_service_definitions/production/btt_get.yaml, errors
[^r6]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 42, Step by step
[^r20]: 04_service_definitions/production/btt_save.yaml, procedures
[^r16]: 04_service_definitions/production/btt_save.yaml, service: btt_save
[^r18]: 04_service_definitions/production/btt_save.yaml, request
[^r19]: 04_service_definitions/production/btt_save.yaml, response
[^r2]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 4, §2. Codes
[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 44, Questions users ask
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 61, btt_search BATTERY END-OF-LINE TEST LIST
[^r23]: 04_service_definitions/production/btt_search.yaml, request.fields
[^r24]: 04_service_definitions/production/btt_search.yaml, response.envelope
[^r25]: 04_service_definitions/production/btt_search.yaml, errors
