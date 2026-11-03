---
title: "SAL alc services"
type: "service-group"
slug: "services-sal-alc"
summary: "Ledgerline Sales allocation services executed from screen SAL-ALC-03 to query, run, and cancel stock reservations against sales orders."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/sales/alc_cancel.yaml", "04_service_definitions/sales/alc_get.yaml", "04_service_definitions/sales/alc_run.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| module | SAL |
| screen | SAL-ALC-03 |
| services | alc_get, alc_run, alc_cancel |
| version_introduced | 7.0 |
| status | current |

The `alc` service group manages stock allocations for sales orders within the Ledgerline Sales (`SAL`) module [^r4][^r8]. Triggered from [[screen-sal-alc-03|SAL-ALC-03 Allocation]], these services retrieve order reservation states, match pickable inventory to order lines, and release allocated quantities back to general stock [^r1][^r2][^r3][^r4]. All services run under the `/ll72/svc/` endpoint and require an authenticated session token in header `X-LL-Session` with an authorised role [^r9][^r15][^r20].

## Services

### alc_get

Retrieves allocation details from the central database, including sales order lines, quantities, active allocations, and available stock [^r1]. Available since Ledgerline 7.0, it operates as a read service attached to screen [[screen-sal-alc-03|SAL-ALC-03]] and does not execute a stored procedure [^r6][^r14].

* **Endpoint**: `POST /ll72/svc/alc_get` [^r14]
* **Kind**: Read [^r6][^r14]
* **Source file**: `04_service_definitions/sales/alc_get.yaml` [^r14]
* **Required fields**: `so_no` (SO NO, string) [^r6][^r16]
* **Optional fields**: None [^r6][^r16]
* **Response**: Envelope containing `rc` (`S | W | E`), `err_cd` (error code when `rc` is `E`), `msg` (short message in capitals), and `data` (result) [^r17]
* **Errors**: `ERR-ALC-0001` (ALLOCATION NOT FOUND) [^r6][^r18], `ERR-SEC-0001` (ACCESS DENIED) [^r18], `ERR-SYS-0421` (<FIELD> MANDATORY) [^r18], `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>) [^r18], `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r18]

### alc_run

Executes stock allocation by matching available pickable inventory against sales order lines and marking inventory ledger statuses as allocated [^r2]. It is a write service introduced in version 7.0 and executes database stored procedure `sp_alc_run` [^r5][^r19][^r23].

* **Endpoint**: `POST /ll72/svc/alc_run` [^r19]
* **Kind**: Write [^r5][^r19]
* **Procedure**: `sp_alc_run` [^r5][^r23]
* **Source file**: `04_service_definitions/sales/alc_run.yaml` [^r19][^r23]
* **Required fields**: `so_no` (SO NO, string) [^r5][^r21]
* **Optional fields**: `comment` (COMMENT, string) [^r5][^r21]
* **Response**: Envelope containing `rc` (`S | W | E`), `err_cd` (error code when `rc` is `E`), `msg` (short message in capitals), and `data` (result) [^r22]
* **Errors**: `ERR-SEC-0001` [^r23], `ERR-SYS-0421` [^r23], `ERR-SYS-0422` [^r23], `ERR-SYS-0503` [^r23]

### alc_cancel

Cancels existing reservations on sales order lines and returns allocated stock to the general unallocated pool [^r3]. Available since version 7.0, it runs as a write service linked to screen [[screen-sal-alc-03|SAL-ALC-03]] and executes database stored procedure `sp_alc_cancel` [^r7][^r8][^r11].

* **Endpoint**: `POST /ll72/svc/alc_cancel` [^r9]
* **Kind**: Write [^r7][^r8]
* **Procedure**: `sp_alc_cancel` [^r7][^r11]
* **Source file**: `04_service_definitions/sales/alc_cancel.yaml` [^r8][^r11]
* **Required fields**: `so_no` (SO NO, string), `reason` (REASON, string) [^r7][^r10]
* **Optional fields**: None [^r7][^r10]
* **Response**: Envelope containing `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r11]
* **Errors**: `ERR-ALC-0001` (ALLOCATION NOT FOUND) [^r7][^r12], `ERR-ALC-0801` (ALLOCATION CLOSED (<status>)) [^r7][^r12], `ERR-SEC-0001` (ACCESS DENIED) [^r13], `ERR-SYS-0421` (<FIELD> MANDATORY) [^r13], `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>) [^r13], `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r13]

## See also

* [[screen-sal-alc-03|SAL-ALC-03 Allocation]]
* [[screen-sal-so-01|SAL-SO-01 Sales Order]]
* [[services-sal-so|SAL so services]]
* [[services-sal-pck|SAL pck services]]
* [[services-sal-dlv|SAL dlv services]]

## References

[^r4]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 32, SAL-ALC-03 ALLOCATION
[^r8]: 04_service_definitions/sales/alc_cancel.yaml, service: alc_cancel
[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 15, Step by Step
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 16, Step by Step
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 16, Step by Step
[^r9]: 04_service_definitions/sales/alc_cancel.yaml, endpoint
[^r15]: 04_service_definitions/sales/alc_get.yaml, auth
[^r20]: 04_service_definitions/sales/alc_run.yaml, alc_run
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 42, alc_get ALLOCATION GET
[^r14]: 04_service_definitions/sales/alc_get.yaml, whole file
[^r16]: 04_service_definitions/sales/alc_get.yaml, request
[^r17]: 04_service_definitions/sales/alc_get.yaml, response
[^r18]: 04_service_definitions/sales/alc_get.yaml, errors
[^r5]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 42, alc_run ALLOCATION RUN
[^r19]: 04_service_definitions/sales/alc_run.yaml, alc_run
[^r23]: 04_service_definitions/sales/alc_run.yaml, procedures
[^r21]: 04_service_definitions/sales/alc_run.yaml, request.fields
[^r22]: 04_service_definitions/sales/alc_run.yaml, response
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 42, alc_cancel ALLOCATION CANCEL
[^r11]: 04_service_definitions/sales/alc_cancel.yaml, response.envelope
[^r10]: 04_service_definitions/sales/alc_cancel.yaml, request.fields
[^r12]: 04_service_definitions/sales/alc_cancel.yaml, errors
[^r13]: 04_service_definitions/sales/alc_cancel.yaml, common_errors
