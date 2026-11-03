---
title: "PRD rtg services"
type: "service-group"
slug: "services-prd-rtg"
summary: "Production routing services in Ledgerline 7.2 including rtg_get, rtg_save, and rtg_search tied to screen PRD-RTG-03."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/rtg_get.yaml", "04_service_definitions/production/rtg_save.yaml", "04_service_definitions/production/rtg_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | PRD |
| Object | rtg |
| Screen | PRD-RTG-03 |
| Introduced | Ledgerline 7.0 |
| Endpoints | /ll72/svc/rtg_get, /ll72/svc/rtg_save, /ll72/svc/rtg_search |
| Auth | X-LL-Session token header |
| Stored Procedure | sp_rtg_save |

The PRD rtg services provide routing operations enquiry, maintenance, and search capabilities in Ledgerline 7.2 [^r7][^r13][^r19]. Available since Ledgerline 7.0, the group is tied to screen [[screen-prd-rtg-03|PRD-RTG-03]] and exposes endpoints for retrieving, saving, and listing operational steps [^r7][^r13][^r19]. Every service request requires session authentication via the `X-LL-Session` header and an authorised user role [^r8][^r14][^r20]. All responses share a standard envelope returning a status code `rc` (`S`, `W`, or `E`), an `err_cd` when `rc` is `E`, an uppercase message string `msg`, and the payload in `data` [^r10][^r16][^r22].

## Services

### rtg_get

The `rtg_get` service (title ROUTING GET) is a read service executed via HTTP POST to `/ll72/svc/rtg_get` and triggered from the rtg_get button on screen [[screen-prd-rtg-03|PRD-RTG-03]] [^r1][^r7]. It fetches routing steps from the database using an item code and optional operation number [^r1][^r4].

* **Required fields**: `itm_cd` (string) [^r9].
* **Optional fields**: `op_no` [^r1].
* **Errors**: [[err-rtg-0001|ERR-RTG-0001]] (ROUTING NOT FOUND) and [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE) [^r4][^r11]. Common errors include ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r12].
* **Source file**: `04_service_definitions/production/rtg_get.yaml` [^r7].

### rtg_save

The `rtg_save` service (title ROUTING SAVE) is a write service invoked via HTTP POST to `/ll72/svc/rtg_save` and called by the rtg_save button on screen [[screen-prd-rtg-03|PRD-RTG-03]] [^r3][^r13]. It persists operational routing lines to the database via stored procedure `sp_rtg_save` [^r5][^r13].

* **Required fields**: `itm_cd` (string), `op_no` (integer), `wc_cd` (string), and `std_min` (float) [^r5][^r15].
* **Optional fields**: none [^r15].
* **Errors**: [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE) and [[err-rtg-0001|ERR-RTG-0001]] if sequence validation fails [^r3][^r17]. Common errors include ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r18].
* **Source file**: `04_service_definitions/production/rtg_save.yaml` [^r13].

### rtg_search

The `rtg_search` service (title ROUTING LIST) is a read service called via HTTP POST to `/ll72/svc/rtg_search` and executed by the rtg_search button on screen [[screen-prd-rtg-03|PRD-RTG-03]] [^r2][^r19]. It returns an enquiry list of items matching partial entry parameters across routings [^r2].

* **Required fields**: none [^r21].
* **Optional fields**: `itm_cd` (string), `op_no` (integer), `wc_cd` (string), and `status` (string) [^r6][^r21].
* **Errors**: [[err-itm-0011|ERR-ITM-0011]], ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r23].
* **Source file**: `04_service_definitions/production/rtg_search.yaml` [^r19].

## See also

* [[screen-prd-rtg-03|PRD-RTG-03 Routing]]
* [[err-rtg-0001|ERR-RTG-0001 Routing Save Failed]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[screen-prd-wc-10|PRD-WC-10 Work Centre]]
* [[services-prd-wc|PRD wc services]]
* [[services-prd-opr|PRD opr services]]
* [[services-prd-bom|PRD bom services]]
* [[services-prd-wo|PRD wo services]]

## References

[^r7]: 04_service_definitions/production/rtg_get.yaml, service: rtg_get
[^r13]: 04_service_definitions/production/rtg_save.yaml, rtg_save
[^r19]: 04_service_definitions/production/rtg_search.yaml, service: rtg_search
[^r8]: 04_service_definitions/production/rtg_get.yaml, auth
[^r14]: 04_service_definitions/production/rtg_save.yaml, auth
[^r20]: 04_service_definitions/production/rtg_search.yaml, auth
[^r10]: 04_service_definitions/production/rtg_get.yaml, response.envelope
[^r16]: 04_service_definitions/production/rtg_save.yaml, response.envelope
[^r22]: 04_service_definitions/production/rtg_search.yaml, response.envelope
[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 12, Step by step
[^r4]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 55, §6. Production services
[^r9]: 04_service_definitions/production/rtg_get.yaml, request.fields
[^r11]: 04_service_definitions/production/rtg_get.yaml, errors
[^r12]: 04_service_definitions/production/rtg_get.yaml, common_errors
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 13, Amending an existing operation
[^r5]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 55, §6. Production services
[^r15]: 04_service_definitions/production/rtg_save.yaml, request.fields
[^r17]: 04_service_definitions/production/rtg_save.yaml, errors
[^r18]: 04_service_definitions/production/rtg_save.yaml, common_errors
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 13, Searching across multiple routings
[^r21]: 04_service_definitions/production/rtg_search.yaml, request.fields
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 55, §6. Production services
[^r23]: 04_service_definitions/production/rtg_search.yaml, errors
