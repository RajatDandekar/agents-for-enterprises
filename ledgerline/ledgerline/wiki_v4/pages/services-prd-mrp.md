---
title: "PRD mrp services"
type: "service-group"
slug: "services-prd-mrp"
summary: "Ledgerline PRD MRP services supporting calculation runs, status queries, exception views, and planned order firming on screen PRD-MRP-09."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/mrp_exceptions.yaml", "04_service_definitions/production/mrp_firm.yaml", "04_service_definitions/production/mrp_get.yaml", "04_service_definitions/production/mrp_run.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| service_group | services-prd-mrp |
| module | PRD |
| screen | PRD-MRP-09 |
| available_since | Ledgerline 7.0 |
| services | mrp_run, mrp_get, mrp_exceptions, mrp_firm |

The PRD MRP service group provides the calculation, reporting, and order-conversion backend for material requirements planning in Ledgerline ERP 7.2 [^r15]. These services are triggered from screen [[screen-prd-mrp-09|PRD-MRP-09]] to explode bills of materials, balance on-hand inventory against demand, identify material exceptions, and convert provisional orders into permanent records [^r1][^r4][^r5]. All endpoints require an authorized user role and an active session token passed in the `X-LL-Session` header [^r11][^r16][^r21][^r26].

## Services

### mrp_run

The `mrp_run` write service initiates the MRP calculation engine using stored procedure `sp_mrp_run`, exploding bills of materials, netting stock on hand against demand, offsetting component lead times, and generating planned orders [^r1][^r6][^r25][^r27]. It has been available since version 7.0 and is linked to screen [[screen-prd-mrp-09|PRD-MRP-09]] [^r5][^r6][^r25].

* **Endpoint**: `POST /ll72/svc/mrp_run` [^r25]
* **Source file**: `04_service_definitions/production/mrp_run.yaml` [^r25]
* **Required fields**: `run_id` (string) [^r6][^r26]
* **Optional fields**: `comment` (string) [^r6][^r26]
* **Response envelope**: Returns `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r27]
* **Errors**: `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r28]

### mrp_get

The `mrp_get` read service retrieves summary statistics, execution status, and completion timestamps for a specified previous or detached calculation [^r2][^r7][^r20]. It is accessed directly or via key F3 on screen [[screen-prd-mrp-09|PRD-MRP-09]] and has been available since version 7.0 [^r5][^r20].

* **Endpoint**: `POST /ll72/svc/mrp_get` [^r20]
* **Source file**: `04_service_definitions/production/mrp_get.yaml` [^r20]
* **Required fields**: `run_id` (string) [^r7][^r22]
* **Optional fields**: None [^r7][^r22]
* **Response envelope**: Returns `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r23]
* **Errors**: [[err-mrp-0001|ERR-MRP-0001]] (MRP RUN NOT FOUND), `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r24]

### mrp_exceptions

The `mrp_exceptions` read service returns the exception list for a calculation run, detailing component shortages, late deliveries, capacity overloads, and rescheduling suggestions [^r3][^r8][^r10]. It is invoked from screen [[screen-prd-mrp-09|PRD-MRP-09]] and has been available since version 7.0 [^r5][^r10].

* **Endpoint**: `POST /ll72/svc/mrp_exceptions` [^r11]
* **Source file**: `04_service_definitions/production/mrp_exceptions.yaml` [^r10]
* **Required fields**: None [^r8][^r12]
* **Optional fields**: `horizon_days` (integer) [^r8][^r12]
* **Response envelope**: Returns `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r13]
* **Errors**: [[err-mrp-0001|ERR-MRP-0001]] (MRP RUN NOT FOUND; returned when missing), `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r8][^r14]

### mrp_firm

The `mrp_firm` write service prompts for confirmation and executes stored procedure `sp_mrp_firm` to convert provisional purchase and works orders into permanent, actionable records that cannot be reversed as a batch [^r4][^r9][^r15][^r19]. It operates on screen [[screen-prd-mrp-09|PRD-MRP-09]] and has been available since version 7.0 [^r5][^r15].

* **Endpoint**: `POST /ll72/svc/mrp_firm` [^r15]
* **Source file**: `04_service_definitions/production/mrp_firm.yaml` [^r15]
* **Required fields**: `run_id` (string) [^r9][^r17]
* **Optional fields**: `comment` (string) [^r9][^r17]
* **Response envelope**: Returns `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r18]
* **Errors**: [[err-mrp-0001|ERR-MRP-0001]] (MRP RUN NOT FOUND), `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r19]

## See also

* [[screen-prd-mrp-09|PRD-MRP-09 Mrp Run]]
* [[err-mrp-0001|ERR-MRP-0001]]
* [[services-prd-mps|PRD mps services]]
* [[services-prd-bom|PRD bom services]]
* [[services-prd-wo|PRD wo services]]
* [[services-pur-po|PUR po services]]

## References

[^r15]: 04_service_definitions/production/mrp_firm.yaml, whole file
[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 23, Screen layout and fields
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 23, Screen layout and fields
[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 23, PRD-MRP-09 MRP RUN
[^r11]: 04_service_definitions/production/mrp_exceptions.yaml, endpoint
[^r16]: 04_service_definitions/production/mrp_firm.yaml, auth
[^r21]: 04_service_definitions/production/mrp_get.yaml, auth
[^r26]: 04_service_definitions/production/mrp_run.yaml, request.fields
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 56, §6. Production services
[^r25]: 04_service_definitions/production/mrp_run.yaml, whole file
[^r27]: 04_service_definitions/production/mrp_run.yaml, response.envelope
[^r28]: 04_service_definitions/production/mrp_run.yaml, common_errors
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 23, Screen layout and fields
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 57, mrp_get MRP RUN GET
[^r20]: 04_service_definitions/production/mrp_get.yaml, service: mrp_get
[^r22]: 04_service_definitions/production/mrp_get.yaml, request
[^r23]: 04_service_definitions/production/mrp_get.yaml, response
[^r24]: 04_service_definitions/production/mrp_get.yaml, errors
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 23, Screen layout and fields
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 57, mrp_exceptions MRP RUN EXCEPTIONS
[^r10]: 04_service_definitions/production/mrp_exceptions.yaml, service
[^r12]: 04_service_definitions/production/mrp_exceptions.yaml, request.fields
[^r13]: 04_service_definitions/production/mrp_exceptions.yaml, response.envelope
[^r14]: 04_service_definitions/production/mrp_exceptions.yaml, errors
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 57, mrp_firm MRP RUN FIRM
[^r19]: 04_service_definitions/production/mrp_firm.yaml, errors
[^r17]: 04_service_definitions/production/mrp_firm.yaml, request.fields
[^r18]: 04_service_definitions/production/mrp_firm.yaml, response.envelope
