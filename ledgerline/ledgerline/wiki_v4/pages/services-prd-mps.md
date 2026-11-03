---
title: "PRD mps services"
type: "service-group"
slug: "services-prd-mps"
summary: "Ledgerline PRD services mps_get, mps_save, and mps_search for retrieving, amending, and searching master schedule records on screen PRD-MPS-05."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/mps_get.yaml", "04_service_definitions/production/mps_save.yaml", "04_service_definitions/production/mps_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| service_group | services-prd-mps |
| module | PRD |
| screen | PRD-MPS-05 |
| services | mps_get, mps_save, mps_search |
| version_introduced | Ledgerline 7.0 |
| status | current |

The `services-prd-mps` service group encompasses the Ledgerline ERP production module services used to query, list, and maintain master production schedule entries [^r1][^r9][^r15]. These services interface directly with [[screen-prd-mps-05|PRD-MPS-05]] to support master schedule planning across production lines [^r1][^r5]. All endpoints operate over HTTP POST, require valid session token authentication, and restrict invocation to authorised user roles [^r9][^r10][^r15][^r16][^r22][^r23].

## Services

### mps_get

Service `mps_get` (MASTER SCHEDULE GET) is a read service introduced in Ledgerline 7.0 that retrieves master schedule data for a specified item to populate the display grid [^r2][^r7][^r9]. It is executed on screen [[screen-prd-mps-05|PRD-MPS-05]] using function key F3 or via endpoint `POST /ll72/svc/mps_get` [^r5][^r9].

* **Required fields**: `itm_cd` (string) [^r7][^r11].
* **Optional fields**: None [^r11].
* **Errors**: Specific errors are [[err-mps-0001|ERR-MPS-0001]] (MASTER SCHEDULE NOT FOUND) and [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE) [^r7][^r13]. Common errors include ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r14].
* **Response**: Returns an envelope containing `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r12].
* **Source file**: `04_service_definitions/production/mps_get.yaml` [^r9].

### mps_save

Service `mps_save` (MASTER SCHEDULE SAVE) is a write service introduced in Ledgerline 7.0 that commits new or updated schedule line requirements to the database [^r3][^r6][^r15]. It runs backend stored procedure `sp_mps_save` and is invoked from screen [[screen-prd-mps-05|PRD-MPS-05]] using function key F8 or via endpoint `POST /ll72/svc/mps_save` [^r5][^r6][^r15][^r21].

* **Required fields**: `itm_cd` (string), `week` (string), and `qty` (integer) [^r6][^r17].
* **Optional fields**: None [^r17].
* **Errors**: Specific errors are [[err-mps-0201|ERR-MPS-0201]] (QTY MUST BE > 0) and [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE) [^r19]. Common errors include ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r20].
* **Response**: Returns an envelope containing `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r18].
* **Source file**: `04_service_definitions/production/mps_save.yaml` [^r15].

### mps_search

Service `mps_search` (MASTER SCHEDULE LIST) is a read service introduced in Ledgerline 7.0 that retrieves matching master schedule lines across production lines and planning horizons [^r1][^r4][^r22]. It is invoked from screen [[screen-prd-mps-05|PRD-MPS-05]] using F2 or Enter, or via endpoint `POST /ll72/svc/mps_search` [^r1][^r5][^r22].

* **Required fields**: None [^r24].
* **Optional fields**: `itm_cd` (string), `week` (string), `qty` (integer), and `status` (string) [^r8][^r24].
* **Errors**: Specific errors defined are [[err-mps-0201|ERR-MPS-0201]] (QTY MUST BE > 0) and [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE) [^r26].
* **Response**: Returns an envelope containing `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r25].
* **Source file**: `04_service_definitions/production/mps_search.yaml` [^r22].

## Versions and conflicts

* **mps_get request parameters**: The service definition specification mandates only `itm_cd` [^r11], whereas the user manual states that `mps_get` takes both `ITEM CD` and `WEEK` to populate schedule details [^r2].
* **mps_search error catalogue**: The service definition YAML lists [[err-mps-0201|ERR-MPS-0201]] (QTY MUST BE > 0) under specific errors for read service `mps_search` [^r26], matching the write validation error defined for `mps_save` [^r19].

## See also

* [[screen-prd-mps-05|PRD-MPS-05 Master Schedule Entry]]
* [[services-prd-mrp|PRD mrp services]]
* [[services-prd-wo|PRD wo services]]
* [[err-mps-0001|ERR-MPS-0001 Missing Mandatory Field or Invalid Format in MPS]]
* [[err-mps-0201|ERR-MPS-0201 Master Schedule Line Locked Against Modification]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 26, Retrieving existing schedule lines
[^r9]: 04_service_definitions/production/mps_get.yaml, service: mps_get
[^r15]: 04_service_definitions/production/mps_save.yaml, service: mps_save
[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 23, PRD-MPS-05 MASTER SCHEDULE ENTRY
[^r10]: 04_service_definitions/production/mps_get.yaml, auth
[^r16]: 04_service_definitions/production/mps_save.yaml, auth
[^r22]: 04_service_definitions/production/mps_search.yaml, service
[^r23]: 04_service_definitions/production/mps_search.yaml, auth
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 27, Creating or amending schedule lines
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 57, mps_get MASTER SCHEDULE GET
[^r11]: 04_service_definitions/production/mps_get.yaml, request
[^r13]: 04_service_definitions/production/mps_get.yaml, errors
[^r14]: 04_service_definitions/production/mps_get.yaml, common_errors
[^r12]: 04_service_definitions/production/mps_get.yaml, response
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 27, Creating or amending schedule lines
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 57, mps_save MASTER SCHEDULE SAVE
[^r21]: 04_service_definitions/production/mps_save.yaml, procedures
[^r17]: 04_service_definitions/production/mps_save.yaml, request.fields
[^r19]: 04_service_definitions/production/mps_save.yaml, errors
[^r20]: 04_service_definitions/production/mps_save.yaml, common_errors
[^r18]: 04_service_definitions/production/mps_save.yaml, response.envelope
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 27, Creating or amending schedule lines
[^r24]: 04_service_definitions/production/mps_search.yaml, request.fields
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 57, mps_search MASTER SCHEDULE LIST
[^r26]: 04_service_definitions/production/mps_search.yaml, errors
[^r25]: 04_service_definitions/production/mps_search.yaml, response.envelope
