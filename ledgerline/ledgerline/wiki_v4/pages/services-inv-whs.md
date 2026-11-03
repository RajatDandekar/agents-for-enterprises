---
title: "INV whs services"
type: "service-group"
slug: "services-inv-whs"
summary: "Ledgerline inventory services whs_get and whs_save for retrieving and maintaining warehouse master records on screen INV-WHS-01."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/whs_get.yaml", "04_service_definitions/inventory/whs_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | INV |
| Object | whs |
| Screen | INV-WHS-01 |
| Services | whs_get, whs_save |
| Ledgerline version | 7.2 (available since 7.0) |
| Status | current |

The warehouse service group in Ledgerline's INV module provides endpoints to retrieve and maintain warehouse master definitions across Northbridge Cycles [^r1][^r2][^r3]. These services back the [[screen-inv-whs-01|INV-WHS-01]] Warehouse Master screen and require session authentication via HTTP header `X-LL-Session` with suitable role permissions [^r5][^r8][^r9][^r13][^r14]. Available since Ledgerline 7.0, both services return standard response envelopes containing a return code, error code, message, and data payload [^r8][^r11][^r13][^r16].

## Services

### whs_get

The `whs_get` service (WAREHOUSE MASTER GET) is a read service executed via `POST /ll72/svc/whs_get` or function key F3 on screen [[screen-inv-whs-01|INV-WHS-01]] to retrieve warehouse master records or fetch the active warehouse list across Northbridge Cycles [^r1][^r3][^r5][^r8].

* **Required fields:** `whs_cd` (str, WHS CD) [^r10].
* **Optional fields:** none [^r10].
* **Errors:** [[err-whs-0001|ERR-WHS-0001]] (WAREHOUSE MASTER NOT FOUND) when the code is not found, along with common errors ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (`<FIELD>` MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD `<FIELD>` / BAD VALUE FOR `<FIELD>`), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r6][^r12].
* **Source file:** `04_service_definitions/inventory/whs_get.yaml` [^r8].

### whs_save

The `whs_save` service (WAREHOUSE MASTER SAVE) is a write service called via `POST /ll72/svc/whs_save` or function key F8 on screen [[screen-inv-whs-01|INV-WHS-01]] to create or overwrite warehouse records in the master database [^r2][^r5][^r13][^r14]. It executes underlying stored procedure `sp_whs_save` after confirming mandatory inputs and checking that the warehouse code is not duplicated or conflicting with operating unit codes [^r4][^r7][^r17].

* **Required fields:** `whs_cd` (str, WHS CD), `name` (str, NAME), and `ou_cd` (str, OU CD) [^r7][^r15].
* **Optional fields:** `whs_type` (str, TYPE) [^r7][^r15].
* **Errors:** ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (`<FIELD>` MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD `<FIELD>` / BAD VALUE FOR `<FIELD>`), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r17].
* **Source file:** `04_service_definitions/inventory/whs_save.yaml` [^r13].

## Versions and conflicts

* **Superseded manuals:** Under current manual MAN-INV-72 v7.2.3 (dated 2025-01-15) and service definitions, `whs_get` and `whs_save` govern warehouse record retrieval and master commits on screen [[screen-inv-whs-01|INV-WHS-01]] [^r1][^r2][^r5][^r8][^r13]. This supersedes the descriptions in MAN-INV-72 v7.2.2 (dated 2024-06-10), which previously defined `whs_get` and `whs_save` execution [^r18][^r19].

## See also

* [[screen-inv-whs-01|INV-WHS-01 Warehouse Master]]
* [[err-whs-0001|ERR-WHS-0001 Warehouse validation failure]]
* [[services-inv-bin|INV bin services]]
* [[services-inv-itm|INV itm services]]
* [[services-inv-stk|INV stk services]]
* [[services-inv-txf|INV txf services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 37, Step by step
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 38, Step by step
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 39, Worked example
[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 21, INV-WHS-01 WAREHOUSE MASTER
[^r8]: 04_service_definitions/inventory/whs_get.yaml, service: whs_get
[^r9]: 04_service_definitions/inventory/whs_get.yaml, auth
[^r13]: 04_service_definitions/inventory/whs_save.yaml, service: whs_save
[^r14]: 04_service_definitions/inventory/whs_save.yaml, auth
[^r11]: 04_service_definitions/inventory/whs_get.yaml, response
[^r16]: 04_service_definitions/inventory/whs_save.yaml, response.envelope
[^r10]: 04_service_definitions/inventory/whs_get.yaml, request
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 18, whs_get WAREHOUSE MASTER GET
[^r12]: 04_service_definitions/inventory/whs_get.yaml, errors
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 39, Worked example
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 18, whs_save WAREHOUSE MASTER SAVE
[^r17]: 04_service_definitions/inventory/whs_save.yaml, procedures
[^r15]: 04_service_definitions/inventory/whs_save.yaml, request.fields
[^r18]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 17, Step by step
[^r19]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 17, Step by step
