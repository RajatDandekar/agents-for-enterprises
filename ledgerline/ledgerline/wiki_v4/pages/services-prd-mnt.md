---
title: "PRD mnt services"
type: "service-group"
slug: "services-prd-mnt"
summary: "PRD maintenance order backend services providing creation, retrieval, searching, and closure of maintenance orders on screen PRD-MNT-07."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/mnt_close.yaml", "04_service_definitions/production/mnt_get.yaml", "04_service_definitions/production/mnt_save.yaml", "04_service_definitions/production/mnt_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | PRD |
| Screen | PRD-MNT-07 |
| Services | mnt_save, mnt_get, mnt_search, mnt_close |
| Available since | Ledgerline ERP 7.0 |
| Protocol | POST (/ll72/svc/*) |
| Status | current |

The maintenance order service group handles the life cycle of plant and machinery maintenance orders within the production module [^r6][^r10]. Available since Ledgerline ERP 7.0, these services support creating, retrieving, listing, and closing maintenance records [^r10][^r16][^r20][^r24]. All operations execute against database procedures and are invoked directly from [[screen-prd-mnt-07|PRD-MNT-07]] Maintenance Order Entry [^r5][^r10][^r13][^r23].

## Services

### mnt_save

Service `mnt_save` (MAINTENANCE ORDER SAVE) is a write service under the PRD module introduced in version 7.0 [^r20]. It validates asset and cost centre records, executes stored procedure `sp_mnt_save`, and saves the order details, returning a newly generated maintenance order number for new records [^r1][^r6][^r23]. It is invoked on screen [[screen-prd-mnt-07]] via the F8 key or endpoint `POST /ll72/svc/mnt_save`, requiring an `X-LL-Session` header and an authorized role [^r5][^r21].

* **Required fields:** `asset_cd` (ASSET), `fault` (FAULT), `cc_cd` (CC CD) [^r6][^r22].
* **Optional fields:** `priority` (PRIORITY) [^r22].
* **Errors:** [[err-cc-0009|ERR-CC-0009]] (when cost centre is not found) [^r6][^r23].
* **Source file:** `04_service_definitions/production/mnt_save.yaml` [^r20][^r21][^r22][^r23].

### mnt_get

Service `mnt_get` (MAINTENANCE ORDER GET) is a read service under the PRD module introduced in version 7.0 [^r16]. It fetches an existing maintenance order using the order reference and populates the asset, fault, priority, cost centre, status, and comment fields [^r2][^r7]. It is invoked on screen [[screen-prd-mnt-07]] via the F3 key or endpoint `POST /ll72/svc/mnt_get`, requiring an `X-LL-Session` header and an authorized role [^r5][^r16][^r17]. The service returns an envelope containing `rc` (S, W, or E), `err_cd`, `msg`, and `data` [^r19].

* **Required fields:** `mno_no` (MNO NO) [^r7][^r18].
* **Optional fields:** none [^r18].
* **Errors:** ERR-MNO-0001 (MAINTENANCE ORDER NOT FOUND), ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r7][^r29].
* **Source file:** `04_service_definitions/production/mnt_get.yaml` [^r16][^r17][^r18][^r19][^r29].

### mnt_search

Service `mnt_search` (MAINTENANCE ORDER LIST) is a read service under the PRD module introduced in Ledgerline 7.0 and associated with screen [[screen-prd-mnt-07]] [^r24]. It returns a selectable list of maintenance orders when the reference is unknown [^r3]. It is triggered by F2 or Enter on screen [[screen-prd-mnt-07]] or via endpoint `POST /ll72/svc/mnt_search`, requiring an `X-LL-Session` header and an authorized role [^r5][^r25]. It returns a standard envelope containing `rc` (S, W, or E), `err_cd`, `msg`, and `data` [^r27].

* **Required fields:** none [^r26].
* **Optional fields:** `asset_cd` (ASSET), `fault` (FAULT), `priority` (PRIORITY), `status` (STATUS) [^r8][^r26].
* **Errors:** ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r28].
* **Source file:** `04_service_definitions/production/mnt_search.yaml` [^r24][^r25][^r26][^r27][^r28].

### mnt_close

Service `mnt_close` (MAINTENANCE ORDER CLOSE) is a write service under the PRD module introduced in Ledgerline ERP 7.0 [^r10]. It executes stored procedure `sp_mnt_close` to validate order details and set the order status to closed [^r4][^r9][^r13]. It is invoked on screen [[screen-prd-mnt-07]] or via endpoint `POST /ll72/svc/mnt_close`, requiring an `X-LL-Session` header and an authorized role [^r5][^r10][^r11]. The response returns a standard envelope containing `rc`, `err_cd`, `msg`, and `data` [^r13].

* **Required fields:** `mno_no` [^r9][^r12].
* **Optional fields:** `comment` [^r12].
* **Errors:** ERR-MNO-0001 (MAINTENANCE ORDER NOT FOUND), ERR-MNO-0801 (MAINTENANCE ORDER CLOSED (<status>)), ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r9][^r14][^r15].
* **Source file:** `04_service_definitions/production/mnt_close.yaml` [^r10][^r11][^r12][^r13][^r14][^r15].

## See also

* [[screen-prd-mnt-07|PRD-MNT-07 Maintenance Order Entry]]
* [[err-cc-0009|ERR-CC-0009]]
* [[services-prd-cal|PRD cal services]]
* [[services-prd-tool|PRD tool services]]
* [[services-prd-wc|PRD wc services]]

## References

[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 63, mnt_save MAINTENANCE ORDER SAVE
[^r10]: 04_service_definitions/production/mnt_close.yaml, service: mnt_close
[^r16]: 04_service_definitions/production/mnt_get.yaml, service: mnt_get
[^r20]: 04_service_definitions/production/mnt_save.yaml, service: mnt_save
[^r24]: 04_service_definitions/production/mnt_search.yaml, whole file
[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 23, PRD-MNT-07 MAINTENANCE ORDER ENTRY
[^r13]: 04_service_definitions/production/mnt_close.yaml, response.envelope
[^r23]: 04_service_definitions/production/mnt_save.yaml, procedures
[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 63, Step by step
[^r21]: 04_service_definitions/production/mnt_save.yaml, auth
[^r22]: 04_service_definitions/production/mnt_save.yaml, request.fields
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 63, Step by step
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 63, mnt_get MAINTENANCE ORDER GET
[^r17]: 04_service_definitions/production/mnt_get.yaml, auth
[^r19]: 04_service_definitions/production/mnt_get.yaml, response
[^r18]: 04_service_definitions/production/mnt_get.yaml, request
[^r29]: 04_service_definitions/production/mnt_get.yaml, errors
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 64, Step by step
[^r25]: 04_service_definitions/production/mnt_search.yaml, whole file
[^r27]: 04_service_definitions/production/mnt_search.yaml, response.envelope
[^r26]: 04_service_definitions/production/mnt_search.yaml, request.fields
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 63, mnt_search MAINTENANCE ORDER LIST
[^r28]: 04_service_definitions/production/mnt_search.yaml, common_errors
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 64, Closing a completed order:
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 63, mnt_close MAINTENANCE ORDER CLOSE
[^r11]: 04_service_definitions/production/mnt_close.yaml, service: mnt_close
[^r12]: 04_service_definitions/production/mnt_close.yaml, request.fields
[^r14]: 04_service_definitions/production/mnt_close.yaml, errors
[^r15]: 04_service_definitions/production/mnt_close.yaml, common_errors
