---
title: "PRD opr services"
type: "service-group"
slug: "services-prd-opr"
summary: "Ledgerline PRD module services for operation confirmations on screen PRD-OPR-04, covering opr_save, opr_get, and opr_search."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/opr_get.yaml", "04_service_definitions/production/opr_save.yaml", "04_service_definitions/production/opr_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | PRD |
| Object | opr |
| Screen | PRD-OPR-04 |
| Since version | 7.0 |
| Endpoints | POST /ll72/svc/opr_* |

The PRD opr services manage production operation confirmations in Ledgerline ERP 7.2 [^r8][^r19]. They operate against screen [[screen-prd-opr-04|PRD-OPR-04]] (Operation Confirmation Entry) to search pending routing operations, retrieve operation details, and post completed production quantities [^r1][^r2][^r3][^r4]. Saving an operation confirmation commits confirmed quantities, initiates automatic backflush material deductions, and updates routing step progression [^r3].

| Field | Value |
|---|---|
| Module | PRD [^r8] |
| Object | opr [^r8] |
| Primary screen | [[screen-prd-opr-04|PRD-OPR-04]] [^r4][^r8] |
| Available since | Ledgerline 7.0 [^r8][^r13][^r19] |
| Endpoints | POST `/ll72/svc/opr_get`, POST `/ll72/svc/opr_save`, POST `/ll72/svc/opr_search` [^r8][^r13][^r20] |

## Services

### opr_save

Service `opr_save` (OPERATION CONFIRMATION SAVE) is a write service in the PRD module available since Ledgerline 7.0 that commits confirmed production quantities, triggers backflush material deductions, and updates routing step statuses [^r3][^r13]. On screen [[screen-prd-opr-04|PRD-OPR-04]], it is mapped to key F8 and posts data to endpoint `POST /ll72/svc/opr_save` by executing database procedure `sp_opr_save` [^r4][^r5][^r13][^r18]. Callers must authenticate with a session token in header `X-LL-Session` and possess an authorised role [^r14].

* **Required fields**: `wo_no` (string), `op_no` (integer), `qty_ok` (integer) [^r5][^r15].
* **Optional fields**: `qty_rej` (integer) [^r5][^r15].
* **Response**: envelope containing `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r16].
* **Errors**: `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (`<FIELD>` MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD `<FIELD>` / BAD VALUE FOR `<FIELD>`), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r17].
* **Source file**: `04_service_definitions/production/opr_save.yaml` [^r13].

### opr_get

Service `opr_get` (OPERATION CONFIRMATION GET) is a read service in module PRD available since Ledgerline 7.0 that retrieves operation confirmation details and populates description and status based on `wo_no` and `op_no` [^r2][^r8]. It is assigned to key F3 on screen [[screen-prd-opr-04|PRD-OPR-04]] and called via endpoint `POST /ll72/svc/opr_get` [^r4][^r8]. Authentication requires an active session token in header `X-LL-Session` and a role permitted to run the service [^r9].

* **Required fields**: `wo_no` (string) [^r6][^r10].
* **Optional fields**: none [^r10].
* **Response**: envelope containing `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r11].
* **Errors**: [[err-opr-0001|ERR-OPR-0001]] (OPERATION CONFIRMATION NOT FOUND / Operation confirmation conflict or invalid data), along with common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r6][^r12].
* **Source file**: `04_service_definitions/production/opr_get.yaml` [^r8].

### opr_search

Service `opr_search` (OPERATION CONFIRMATION LIST) is a read service in the PRD module introduced in Ledgerline 7.0 that returns lists of outstanding works order operations queued for confirmation [^r1][^r19]. Executed from screen [[screen-prd-opr-04|PRD-OPR-04]] using F2 or Enter, it targets endpoint `POST /ll72/svc/opr_search` [^r4][^r19][^r20]. Requests require header `X-LL-Session` with an authorised role [^r20].

* **Required fields**: none [^r21].
* **Optional fields**: `wo_no` (string), `op_no` (integer), `qty_ok` (integer), and `status` (string) [^r7][^r21].
* **Response**: envelope containing `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r22].
* **Errors**: `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (`<FIELD>` MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD `<FIELD>` / BAD VALUE FOR `<FIELD>`), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r23].
* **Source file**: `04_service_definitions/production/opr_search.yaml` [^r19].

## See also

* [[screen-prd-opr-04|PRD-OPR-04 Operation Confirmation Entry]]
* [[err-opr-0001|ERR-OPR-0001: Operation confirmation conflict or invalid data]]
* [[services-prd-wo|PRD wo services]]
* [[services-prd-bkf|PRD bkf services]]

## References

[^r8]: 04_service_definitions/production/opr_get.yaml, service: opr_get
[^r19]: 04_service_definitions/production/opr_search.yaml, whole file
[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 19, Search and retrieval
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 20, Search and retrieval
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 20, Step by step
[^r4]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 24, PRD-OPR-04 OPERATION CONFIRMATION ENTRY
[^r13]: 04_service_definitions/production/opr_save.yaml, service
[^r20]: 04_service_definitions/production/opr_search.yaml, whole file
[^r5]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 56, §6. Production services
[^r18]: 04_service_definitions/production/opr_save.yaml, procedures
[^r14]: 04_service_definitions/production/opr_save.yaml, auth
[^r15]: 04_service_definitions/production/opr_save.yaml, request.fields
[^r16]: 04_service_definitions/production/opr_save.yaml, response.envelope
[^r17]: 04_service_definitions/production/opr_save.yaml, common_errors
[^r9]: 04_service_definitions/production/opr_get.yaml, auth
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 56, §6. Production services
[^r10]: 04_service_definitions/production/opr_get.yaml, request.fields
[^r11]: 04_service_definitions/production/opr_get.yaml, response.envelope
[^r12]: 04_service_definitions/production/opr_get.yaml, errors
[^r21]: 04_service_definitions/production/opr_search.yaml, request
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 56, §6. Production services
[^r22]: 04_service_definitions/production/opr_search.yaml, response
[^r23]: 04_service_definitions/production/opr_search.yaml, common_errors
