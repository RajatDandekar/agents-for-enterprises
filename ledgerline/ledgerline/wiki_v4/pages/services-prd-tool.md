---
title: "PRD tool services"
type: "service-group"
slug: "services-prd-tool"
summary: "Ledgerline production module services for reading and saving tooling master records on screen PRD-TOL-14."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/tool_get.yaml", "04_service_definitions/production/tool_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | PRD |
| Screen | [[screen-prd-tol-14|PRD-TOL-14]] |
| Services | tool_get, tool_save |
| Since | Ledgerline 7.0 |
| Endpoints | POST /ll72/svc/tool_get, POST /ll72/svc/tool_save |

The PRD tool service group provides backend services to read and update tooling records in the Ledgerline production database [^r1][^r2]. Operating behind screen [[screen-prd-tol-14|PRD-TOL-14]], these endpoints maintain tooling definitions, descriptions, and operational life cycles [^r3][^r4][^r14]. Both services require authentication through session token headers and authorized user roles [^r8][^r13].

## Services

### tool_get
The `tool_get` service executes TOOL MASTER GET to retrieve tooling records from the production database [^r1][^r2]. It operates as a read service introduced in version 7.0 at endpoint `POST /ll72/svc/tool_get` [^r7]. Invocations require a session token passed in the `X-LL-Session` header and an authorized role [^r8]. The response envelope contains `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r10].

* **Required fields**: `tool_cd` (string) [^r9].
* **Optional fields**: None [^r9].
* **Errors**: [[err-tol-0001|ERR-TOL-0001]], ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r2][^r11].
* **Source file**: `04_service_definitions/production/tool_get.yaml` [^r7].

### tool_save
The `tool_save` service executes TOOL MASTER SAVE to register new tooling records or update existing entries in the tooling master [^r1][^r3]. Available since Ledgerline 7.0, it is invoked via endpoint `POST /ll72/svc/tool_save` and is backed by stored procedure `sp_tool_save` [^r6][^r12]. Authentication requires a session token in header `X-LL-Session` and a role permitted to run the service [^r13].

* **Required fields**: `tool_cd` (string, TOOL), `descr` (string, DESCR) [^r6][^r14].
* **Optional fields**: `life_cycles` (integer, LIFE) [^r6][^r14].
* **Errors**: ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r15].
* **Source file**: `04_service_definitions/production/tool_save.yaml` [^r12].

## Versions and conflicts
* **Life cycles field requirement**: In the service definition and service manual, `life_cycles` (LIFE) is an optional integer field for `tool_save` [^r6][^r14]. However, the PRD user manual states that `tool_save` validates that `TOOL CD`, `DESCR`, and `LIFE` are properly populated [^r3]. Kind: `contradiction`.

## See also
* [[screen-prd-tol-14|PRD-TOL-14 Tool Master]]
* [[err-tol-0001|ERR-TOL-0001 Tool Master Validation Failure]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 66, Screen layout
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 69, Questions users ask
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 67, Creating a new tooling record
[^r4]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 26, PRD-TOL-14 TOOL MASTER
[^r14]: 04_service_definitions/production/tool_save.yaml, request.fields
[^r8]: 04_service_definitions/production/tool_get.yaml, auth
[^r13]: 04_service_definitions/production/tool_save.yaml, auth
[^r7]: 04_service_definitions/production/tool_get.yaml, whole file
[^r10]: 04_service_definitions/production/tool_get.yaml, response
[^r9]: 04_service_definitions/production/tool_get.yaml, request
[^r11]: 04_service_definitions/production/tool_get.yaml, errors
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 64, tool_save TOOL MASTER SAVE
[^r12]: 04_service_definitions/production/tool_save.yaml, service: tool_save
[^r15]: 04_service_definitions/production/tool_save.yaml, common_errors
