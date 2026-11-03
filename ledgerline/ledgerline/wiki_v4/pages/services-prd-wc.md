---
title: "PRD wc services"
type: "service-group"
slug: "services-prd-wc"
summary: "PRD work centre services providing retrieval, listing, and maintenance for screen PRD-WC-10 in Ledgerline 7.2."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/wc_get.yaml", "04_service_definitions/production/wc_list.yaml", "04_service_definitions/production/wc_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | PRD |
| Target Screen | [[screen-prd-wc-10|PRD-WC-10]] |
| Services | wc_get, wc_list, wc_save |
| Authentication | Header X-LL-Session |
| Introduced | Ledgerline 7.0 |
| Status | Current |

The work centre service group handles the retrieval, querying, and maintenance of production work centres across the Manchester and Leeds sites [^r2][^r4]. Operating within the PRD module since Ledgerline 7.0, these services back the operational interface on screen [[screen-prd-wc-10|PRD-WC-10]] [^r4][^r9][^r14][^r19]. They validate and persist work centre codes, descriptive names, and daily operational hour capacities in the production master files [^r1][^r3][^r21].

## Services

### wc_get

The `wc_get` service is a read service in the PRD module introduced in Ledgerline 7.0 to retrieve operational database records for screen [[screen-prd-wc-10|PRD-WC-10]] [^r1][^r5][^r9]. It is accessed by sending a `POST` request to `/ll72/svc/wc_get` and authenticates using a session token supplied in header `X-LL-Session` for an authorised user role [^r10].

* **Required fields:** `wc_cd` (string, WC CD) [^r5][^r11].
* **Optional fields:** None [^r11].
* **Response:** Returns standard envelope fields `rc` ('S | W | E'), `err_cd`, `msg`, and `data` [^r12]. When successful, it populates `NAME` and `HRS/DAY` on [[screen-prd-wc-10|PRD-WC-10]] [^r1].
* **Errors:** Returns service-specific error [[err-wc-0001|ERR-WC-0001]] (WORK CENTRE NOT FOUND) if the work centre does not exist, alongside common system errors `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r5][^r13].
* **Source file:** `04_service_definitions/production/wc_get.yaml` [^r9].

### wc_list

The `wc_list` service is a read service available since Ledgerline 7.0 that returns the register of existing work centres across the Manchester and Leeds sites for screen [[screen-prd-wc-10|PRD-WC-10]] [^r2][^r8][^r14]. It executes no stored procedure and is called via `POST` to `/ll72/svc/wc_list` requiring an authorised session token in header `X-LL-Session` [^r8][^r15].

* **Required fields:** None [^r16].
* **Optional fields:** `wc_cd` (string, WORK CENTRE) as a filter [^r8][^r16].
* **Response:** Returns envelope fields `rc` ('S | W | E'), `err_cd`, `msg`, and `data` containing the matching records [^r17].
* **Errors:** Common errors include `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r18].
* **Source file:** `04_service_definitions/production/wc_list.yaml` [^r14].

### wc_save

The `wc_save` service is a write service present since Ledgerline 7.0 that commits new or amended work centre details to the production master files from screen [[screen-prd-wc-10|PRD-WC-10]] [^r3][^r6][^r19]. Calls are dispatched via `POST` to `/ll72/svc/wc_save` with header `X-LL-Session` authenticated against an authorised user role, triggering stored procedure `sp_wc_save` [^r7][^r20][^r22].

* **Required fields:** `wc_cd` (string, WORK CENTRE) and `name` (string, NAME) [^r7][^r21].
* **Optional fields:** `hrs_per_day` (float, HRS/DAY) [^r7][^r21].
* **Response:** Executes `sp_wc_save` and returns envelope fields `rc`, `err_cd`, `msg`, and `data` [^r22].
* **Errors:** Validates data integrity and returns [[err-wc-0001|ERR-WC-0001]] upon failure, as well as common errors `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r3][^r23].
* **Source file:** `04_service_definitions/production/wc_save.yaml` [^r19].

## See also

* [[screen-prd-wc-10|PRD-WC-10 Work Centre]]
* [[err-wc-0001|ERR-WC-0001 Work Centre Processing Failure]]
* [[services-prd-wo|PRD wo services]]
* [[services-prd-rtg-03|PRD-RTG-03 Routing]]
* [[services-prd-bom|PRD bom services]]

## References

[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 51, Questions users ask
[^r4]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 26, PRD-WC-10 WORK CENTRE
[^r9]: 04_service_definitions/production/wc_get.yaml, service: wc_get
[^r14]: 04_service_definitions/production/wc_list.yaml, service: wc_list
[^r19]: 04_service_definitions/production/wc_save.yaml, service: wc_save
[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 49, Retrieving an existing work centre record
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 50, Amending an existing work centre
[^r21]: 04_service_definitions/production/wc_save.yaml, request.fields
[^r5]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 61, wc_get WORK CENTRE GET
[^r10]: 04_service_definitions/production/wc_get.yaml, auth
[^r11]: 04_service_definitions/production/wc_get.yaml, request.fields
[^r12]: 04_service_definitions/production/wc_get.yaml, response.envelope
[^r13]: 04_service_definitions/production/wc_get.yaml, errors
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 62, wc_list WORK CENTRE LIST
[^r15]: 04_service_definitions/production/wc_list.yaml, auth
[^r16]: 04_service_definitions/production/wc_list.yaml, request.fields
[^r17]: 04_service_definitions/production/wc_list.yaml, response.envelope
[^r18]: 04_service_definitions/production/wc_list.yaml, common_errors
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 61, wc_save WORK CENTRE SAVE
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 62, PRD-WC-10
[^r20]: 04_service_definitions/production/wc_save.yaml, endpoint
[^r22]: 04_service_definitions/production/wc_save.yaml, response.envelope
[^r23]: 04_service_definitions/production/wc_save.yaml, common_errors
