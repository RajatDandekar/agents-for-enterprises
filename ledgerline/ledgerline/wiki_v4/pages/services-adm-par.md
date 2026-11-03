---
title: "ADM par services"
type: "service-group"
slug: "services-adm-par"
summary: "Ledgerline ADM services operating on screen SYS-PAR-04 to query, update, list, and review history of system parameters."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/admin/par_get.yaml", "04_service_definitions/admin/par_hist.yaml", "04_service_definitions/admin/par_list.yaml", "04_service_definitions/admin/par_set.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | ADM |
| Object | par |
| Primary screen | [[screen-sys-par-04|SYS-PAR-04]] |
| Available since | Ledgerline 7.0 |
| Endpoints | POST /ll72/svc/par_* |
| Header | X-LL-Session |
| Backend procedure | sp_par_set |

The `par` service group provides core administration functions in the ADM module to query, configure, enumerate, and inspect the audit history of Ledgerline system parameters [^r1][^r6]. All services correspond to screen [[screen-sys-par-04|SYS-PAR-04]] and execute over HTTP POST against `/ll72/svc/` endpoints [^r1][^r2][^r7]. Calls require an active session token passed in the `X-LL-Session` header and an authorised role [^r7][^r12][^r17][^r23].

## Services

### par_get
* **Description**: Read service titled SYSTEM PARAMETER GET that queries a single system parameter [^r3][^r6]. Associated with key F3 on screen [[screen-sys-par-04|SYS-PAR-04]] and available since version 7.0 [^r2][^r6].
* **Endpoint**: `POST /ll72/svc/par_get` [^r7]
* **Source file**: `04_service_definitions/admin/par_get.yaml` [^r6]
* **Required fields**: `par_cd` (str) [^r3][^r8].
* **Optional fields**: None [^r8].
* **Response**: Returns an envelope with `rc` (`S | W | E`), `err_cd` (when `rc` is `E`), `msg` (short message in capitals), and `data` (result) [^r9].
* **Errors**: `ERR-PAR-0001` (SYSTEM PARAMETER NOT FOUND), along with common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r3][^r10].

### par_set
* **Description**: Write service titled SYSTEM PARAMETER SET that sets a parameter value by executing backend procedure `sp_par_set` on screen [[screen-sys-par-04|SYS-PAR-04]] [^r4][^r21][^r22][^r25]. Available since Ledgerline version 7.0 [^r22].
* **Endpoint**: `POST /ll72/svc/par_set` [^r23]
* **Source file**: `04_service_definitions/admin/par_set.yaml` [^r21]
* **Required fields**: `par_cd` (str) and `value` (str) [^r4][^r24].
* **Optional fields**: `ou_cd` (str) [^r4][^r24].
* **Errors**: `ERR-PAR-0001` (SYSTEM PARAMETER NOT FOUND), `ERR-PAR-0101` (UNKNOWN PARAMETER), `ERR-PAR-0110` (VALUE OUT OF RANGE), and common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r2][^r4][^r26][^r27].

### par_list
* **Description**: Read service titled SYSTEM PARAMETER LIST that retrieves system parameters [^r5][^r16]. Available since Ledgerline version 7.0 and operates on screen [[screen-sys-par-04|SYS-PAR-04]] [^r1][^r16].
* **Endpoint**: `POST /ll72/svc/par_list` [^r17]
* **Source file**: `04_service_definitions/admin/par_list.yaml` [^r16]
* **Required fields**: None [^r18].
* **Optional fields**: `par_cd` (str) [^r5][^r18].
* **Response**: Returns an envelope with `rc` (`S | W | E`), `err_cd` (when `rc` is `E`), `msg` (short message in capitals), and `data` (result) [^r19].
* **Errors**: Common errors `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r20].

### par_hist
* **Description**: Read service titled SYSTEM PARAMETER HIST that retrieves the change history of a parameter on screen [[screen-sys-par-04|SYS-PAR-04]] [^r1][^r5][^r11]. Available since Ledgerline version 7.0 [^r11].
* **Endpoint**: `POST /ll72/svc/par_hist` [^r11]
* **Source file**: `04_service_definitions/admin/par_hist.yaml` [^r11]
* **Required fields**: `par_cd` (str) [^r5][^r13].
* **Optional fields**: None [^r13].
* **Response**: Returns an envelope with `rc` (`S | W | E`), `err_cd` (when `rc` is `E`), `msg` (short message in capitals), and `data` (result) [^r14].
* **Errors**: `ERR-PAR-0001` (SYSTEM PARAMETER NOT FOUND) and common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r15].

## See also
* [[screen-sys-par-04|SYS-PAR-04 System Parameter]]
* [[services-adm-dlg|ADM dlg services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 5, §4. System parameters
[^r6]: 04_service_definitions/admin/par_get.yaml, whole file
[^r2]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 43, SYS-PAR-04 SYSTEM PARAMETER
[^r7]: 04_service_definitions/admin/par_get.yaml, whole file
[^r12]: 04_service_definitions/admin/par_hist.yaml, auth
[^r17]: 04_service_definitions/admin/par_list.yaml, whole file
[^r23]: 04_service_definitions/admin/par_set.yaml, endpoint: POST /ll72/svc/par_set
[^r3]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 67, par_get SYSTEM PARAMETER GET
[^r8]: 04_service_definitions/admin/par_get.yaml, request
[^r9]: 04_service_definitions/admin/par_get.yaml, response
[^r10]: 04_service_definitions/admin/par_get.yaml, errors
[^r4]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 67, par_set SYSTEM PARAMETER SET
[^r21]: 04_service_definitions/admin/par_set.yaml, service: par_set
[^r22]: 04_service_definitions/admin/par_set.yaml, screen: SYS-PAR-04
[^r25]: 04_service_definitions/admin/par_set.yaml, procedures
[^r24]: 04_service_definitions/admin/par_set.yaml, request.fields
[^r26]: 04_service_definitions/admin/par_set.yaml, errors
[^r27]: 04_service_definitions/admin/par_set.yaml, common_errors
[^r5]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 68, par_hist SYSTEM PARAMETER HIST
[^r16]: 04_service_definitions/admin/par_list.yaml, whole file
[^r18]: 04_service_definitions/admin/par_list.yaml, request
[^r19]: 04_service_definitions/admin/par_list.yaml, response
[^r20]: 04_service_definitions/admin/par_list.yaml, common_errors
[^r11]: 04_service_definitions/admin/par_hist.yaml, service: par_hist
[^r13]: 04_service_definitions/admin/par_hist.yaml, request.fields
[^r14]: 04_service_definitions/admin/par_hist.yaml, response.envelope
[^r15]: 04_service_definitions/admin/par_hist.yaml, errors
