---
title: "PRD shf services"
type: "service-group"
slug: "services-prd-shf"
summary: "Ledgerline production shift services supporting shift retrieval and maintenance on screen PRD-SHF-11."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/shf_get.yaml", "04_service_definitions/production/shf_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | PRD |
| Screen | PRD-SHF-11 |
| Available since | Ledgerline 7.0 |
| Service count | 2 |
| Protocol | POST (/ll72/svc/*) |
| Status | current |

The `shf` service group provides production shift retrieval and maintenance functions within Ledgerline's PRD module [^r4][^r7][^r12]. Used primarily by screen [[screen-prd-shf-11|PRD-SHF-11]], these services allow users to fetch stored shift parameters and commit validated operational shifts to master calendar files [^r1][^r2][^r4]. Both services run over HTTP POST endpoints requiring user role authorisation and an active session token [^r8][^r13].

## Services

### shf_get

Retrieves stored operational shift parameters from the database matching the provided shift code [^r1]. The service is classified as a PRD read service, is titled SHIFT GET, and has been available since Ledgerline version 7.0 [^r7]. It operates on screen [[screen-prd-shf-11|PRD-SHF-11]] via endpoint `POST /ll72/svc/shf_get` [^r7][^r8]. Calls require user role authorisation and a session token passed in the `X-LL-Session` header [^r8].

* **Required fields:** `shf_cd` (string, SHF CD) [^r5][^r9].
* **Optional fields:** none [^r9].
* **Response envelope:** `rc` (return code: S | W | E), `err_cd` (error code when rc is E), `msg` (short message in capitals), and `data` (result) [^r10].
* **Errors:** [[err-shf-0001|ERR-SHF-0001]] (SHIFT NOT FOUND), ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (\<FIELD\> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD \<FIELD\> / BAD VALUE FOR \<FIELD\>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r5][^r11].
* **Source files:** `04_service_definitions/production/shf_get.yaml` [^r7], `MAN-SVC-72` [^r5].

### shf_save

Validates shift parameters, checks that START and END represent valid times with completion falling after start, and commits the shift record to master calendar files [^r2]. Classified as a PRD write service titled SHIFT SAVE, it executes stored procedure `sp_shf_save` for screen [[screen-prd-shf-11|PRD-SHF-11]] and has been available since version 7.0 [^r6][^r12][^r16]. Calls are submitted to endpoint `POST /ll72/svc/shf_save` and require user role authorisation along with a valid `X-LL-Session` header token [^r12][^r13].

* **Required fields:** `shf_cd` (string, SHIFT), `start` (string, START), and `end` (string, END) [^r6][^r14].
* **Optional fields:** none [^r14].
* **Response envelope:** `rc` (return code: S | W | E), `err_cd` (error code when rc is E), `msg` (short message in capitals), and `data` (result) [^r15].
* **Errors:** [[err-shf-0001|ERR-SHF-0001]] (raised if the shift code is malformed, mandatory time values are missing, or the END value precedes the START value), ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (\<FIELD\> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD \<FIELD\> / BAD VALUE FOR \<FIELD\>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r3][^r16].
* **Source files:** `04_service_definitions/production/shf_save.yaml` [^r12], `MAN-SVC-72` [^r6].

## See also

* [[screen-prd-shf-11|PRD-SHF-11 Shift]]
* [[err-shf-0001|ERR-SHF-0001 Invalid period definition / shift parameters]]

## References

[^r4]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 25, PRD-SHF-11 SHIFT
[^r7]: 04_service_definitions/production/shf_get.yaml, service
[^r12]: 04_service_definitions/production/shf_save.yaml, whole file
[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 53, Screen layout and fields
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 54, Worked example
[^r8]: 04_service_definitions/production/shf_get.yaml, endpoint
[^r13]: 04_service_definitions/production/shf_save.yaml, whole file
[^r5]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 62, shf_get SHIFT GET
[^r9]: 04_service_definitions/production/shf_get.yaml, request.fields
[^r10]: 04_service_definitions/production/shf_get.yaml, response.envelope
[^r11]: 04_service_definitions/production/shf_get.yaml, errors
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 62, shf_save SHIFT SAVE
[^r16]: 04_service_definitions/production/shf_save.yaml, common_errors
[^r14]: 04_service_definitions/production/shf_save.yaml, request.fields
[^r15]: 04_service_definitions/production/shf_save.yaml, response.envelope
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 53, Messages
