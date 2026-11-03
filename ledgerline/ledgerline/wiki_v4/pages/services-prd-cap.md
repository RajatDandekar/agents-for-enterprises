---
title: "PRD cap services"
type: "service-group"
slug: "services-prd-cap"
summary: "Ledgerline production capacity services cap_query and cap_load executed from screen PRD-CAP-13 to evaluate and calculate work centre load."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/cap_load.yaml", "04_service_definitions/production/cap_query.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| service_group | services-prd-cap |
| module | PRD |
| screen | PRD-CAP-13 |
| introduced | 7.0 |
| status | current |

The PRD capacity service group provides work centre capacity evaluation and recalculation functions within Ledgerline ERP 7.2 [^r8][^r14]. These services run against [[screen-prd-cap-13|PRD-CAP-13]] to query available calendar shift hours and compile total operational load across live works orders, trial assemblies, and released operations [^r1][^r2][^r5]. Authenticated execution requires an authorized user role along with a session token supplied in the `X-LL-Session` header [^r9][^r15].

| Field | Value |
|---|---|
| Service Group | services-prd-cap |
| Module | PRD |
| Primary Screen | [[screen-prd-cap-13|PRD-CAP-13]] |
| Version Introduced | 7.0 |
| Status | Current |

## Services

### cap_query

The `cap_query` service is a read-kind service under the PRD module associated with screen [[screen-prd-cap-13|PRD-CAP-13]] that has been available since version 7.0 [^r14]. It queries the production calendar and shift patterns to fill available capacity hours for a given work centre and planning week [^r1]. The service endpoint is `POST /ll72/svc/cap_query` and authenticates using a session token in header `X-LL-Session` for authorized user roles [^r15]. When the service returns no records, users should verify that the master schedule contains the factory calendar for the target period and that active operations are assigned to the work centre [^r4].

* **Source file:** `04_service_definitions/production/cap_query.yaml` [^r14]
* **Endpoint:** `POST /ll72/svc/cap_query` [^r15]
* **Required fields:** None [^r6][^r16]
* **Optional fields:**
  * `wc_cd` (WORK CENTRE, string) [^r6][^r16]
  * `week` (WEEK, string) [^r6][^r16]
* **Response envelope:** `rc` ('S | W | E'), `err_cd` ('error code when rc is E'), `msg` ('short message in capitals'), and `data` ('result') [^r17]
* **Errors:** ERR-CAP-0001 (CAPACITY NOT FOUND, raised if missing, the work centre is inactive, or the factory manufacturing calendar has not been generated for the target week) [^r3][^r6][^r18], ERR-SEC-0001 (ACCESS DENIED) [^r18], ERR-SYS-0421 (<FIELD> MANDATORY) [^r18], ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>) [^r18], and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r18].

### cap_load

The `cap_load` service is a write-kind service under the PRD module with the title CAPACITY LOAD, linked to screen [[screen-prd-cap-13|PRD-CAP-13]] and available since version 7.0 [^r8]. It compiles total operational load across live works orders, trial assemblies, and released operations, recalculating required hours and updating dependent scheduling routines via stored procedure `sp_cap_load` [^r2][^r7][^r12]. Its endpoint is `POST /ll72/svc/cap_load`, requiring an authorized role and a session token passed in the `X-LL-Session` header [^r9].

* **Source file:** `04_service_definitions/production/cap_load.yaml` [^r8]
* **Endpoint:** `POST /ll72/svc/cap_load` [^r9]
* **Required fields:**
  * `wc_cd` (WC CD, string) [^r7][^r10]
* **Optional fields:**
  * `comment` (COMMENT, string) [^r7][^r10]
* **Response envelope:** `rc` ('S | W | E'), `err_cd` ('error code when rc is E'), `msg` ('short message in capitals'), and `data` ('result') [^r11]
* **Errors:** ERR-CAP-0001 (CAPACITY NOT FOUND, raised if the work centre is inactive or if the factory manufacturing calendar has not been generated for the target week) [^r3][^r7][^r12], ERR-SEC-0001 (ACCESS DENIED) [^r13], ERR-SYS-0421 (<FIELD> MANDATORY) [^r13], ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>) [^r13], and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r13].

## See also

* [[screen-prd-cap-13|PRD-CAP-13 Capacity]]
* [[screen-prd-wc-10|PRD-WC-10 Work Centre]]
* [[services-prd-wc|PRD wc services]]
* [[screen-prd-mps-05|PRD-MPS-05 Master Schedule Entry]]
* [[services-prd-mps|PRD mps services]]
* [[services-prd-wo|PRD wo services]]
* [[services-prd-opr|PRD opr services]]

## References

[^r8]: 04_service_definitions/production/cap_load.yaml, service: cap_load
[^r14]: 04_service_definitions/production/cap_query.yaml, whole file
[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 59, Screen layout
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 59, Screen layout
[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 22, PRD-CAP-13 CAPACITY
[^r9]: 04_service_definitions/production/cap_load.yaml, endpoint
[^r15]: 04_service_definitions/production/cap_query.yaml, whole file
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 62, §19. Maintenance Order (PRD-MNT-07)
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 63, cap_query CAPACITY QUERY
[^r16]: 04_service_definitions/production/cap_query.yaml, request.fields
[^r17]: 04_service_definitions/production/cap_query.yaml, response.envelope
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 60, Messages
[^r18]: 04_service_definitions/production/cap_query.yaml, errors
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 63, cap_load CAPACITY LOAD
[^r12]: 04_service_definitions/production/cap_load.yaml, errors
[^r10]: 04_service_definitions/production/cap_load.yaml, request
[^r11]: 04_service_definitions/production/cap_load.yaml, response
[^r13]: 04_service_definitions/production/cap_load.yaml, common_errors
