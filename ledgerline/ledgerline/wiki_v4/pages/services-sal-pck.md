---
title: "SAL pck services"
type: "service-group"
slug: "services-sal-pck"
summary: "Ledgerline 7.2 service group for sales pick list entry, retrieval, search, and confirmation on screen SAL-PCK-04."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/sales/pck_confirm.yaml", "04_service_definitions/sales/pck_get.yaml", "04_service_definitions/sales/pck_save.yaml", "04_service_definitions/sales/pck_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | SAL |
| Screen | [[screen-sal-pck-04|SAL-PCK-04]] |
| Version introduced | 7.0 |
| Protocol | HTTP POST |
| Authentication | Session token (X-LL-Session) |
| Status | current |

The `services-sal-pck` group provides the Ledgerline ERP 7.2 services for managing sales pick lists under the sales (`SAL`) module [^r6][^r10]. Available since release 7.0, these services handle creating pick lists, querying headers and line allocations, listing pick lists by filter criteria, and confirming picked stock [^r1][^r2][^r3][^r4][^r10]. All services in this group are invoked via HTTP POST endpoints authenticated with a session token and correspond to user actions on screen [[screen-sal-pck-04|SAL-PCK-04]] [^r5][^r11][^r17][^r23][^r28].

## Services

### pck_save

The `pck_save` service is a write service titled PICK LIST SAVE that saves pick list records and allocates inventory lines [^r1][^r6][^r22]. Invoked on screen [[screen-sal-pck-04|SAL-PCK-04]] via key F8 or endpoint `POST /ll72/svc/pck_save`, it executes database stored procedure `sp_pck_save` to validate the sales order against the warehouse and assign a generated `PCK NO` reference [^r1][^r5][^r6][^r23][^r25]. Callers must pass a session token in header `X-LL-Session` with an authorised role [^r23].

* **Required fields**: `so_no` (`SO NO`), `whs_cd` (`WHS CD`) [^r24].
* **Optional fields**: None [^r24].
* **Errors**: Common errors include `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (`<FIELD>` MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD `<FIELD>` / BAD VALUE FOR `<FIELD>`), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r26]. The response envelope returns `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r25].
* **Source file**: `04_service_definitions/sales/pck_save.yaml` [^r22].

### pck_get

The `pck_get` service is a read service titled PICK LIST GET that retrieves an existing pick list header and line details by its `PCK NO` identifier [^r2][^r7][^r16]. Invoked on screen [[screen-sal-pck-04|SAL-PCK-04]] via key F3 or endpoint `POST /ll72/svc/pck_get`, it executes without a stored procedure [^r5][^r7][^r16]. Callers must authenticate with a session token in header `X-LL-Session` and possess an authorised role [^r17].

* **Required fields**: `pck_no` (`PCK NO`) [^r7][^r18].
* **Optional fields**: None [^r18].
* **Errors**: Returns specific error `ERR-PCK-0001` (PICK LIST NOT FOUND) when the record is missing [^r7][^r20]. Common errors include `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (`<FIELD>` MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD `<FIELD>` / BAD VALUE FOR `<FIELD>`), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r21]. The response envelope returns `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r19].
* **Source file**: `04_service_definitions/sales/pck_get.yaml` [^r16].

### pck_search

The `pck_search` service is a read service titled PICK LIST LIST that searches and lists pick lists matching selection criteria [^r3][^r8][^r27]. Invoked on screen [[screen-sal-pck-04|SAL-PCK-04]] via Search (F2/Enter) or endpoint `POST /ll72/svc/pck_search`, it executes without a stored procedure [^r5][^r8][^r28]. Requests require an `X-LL-Session` header token and appropriate role authorisation [^r28].

* **Required fields**: None [^r29].
* **Optional fields**: `so_no` (`SO NO`), `whs_cd` (`WHS CD`), `status` (`STATUS`) [^r8][^r29].
* **Errors**: Common errors include `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (`<FIELD>` MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD `<FIELD>` / BAD VALUE FOR `<FIELD>`), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r31]. The response envelope returns `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r30].
* **Source file**: `04_service_definitions/sales/pck_search.yaml` [^r27].

### pck_confirm

The `pck_confirm` service is a write service titled PICK LIST CONFIRM that commits gathered pick quantities, sets pick list `STATUS` to confirmed, locks the `COMMENT` field, and closes lines against further allocation [^r4][^r9][^r10]. Invoked on screen [[screen-sal-pck-04|SAL-PCK-04]] via key F9 or endpoint `POST /ll72/svc/pck_confirm`, it executes database stored procedure `sp_pck_confirm` [^r5][^r9][^r11][^r14]. Requests require an `X-LL-Session` token and an authorized user role [^r11].

* **Required fields**: `pck_no` (`PCK NO`) [^r9][^r12].
* **Optional fields**: `comment` (`COMMENT`) [^r9][^r12].
* **Errors**: Returns specific errors `ERR-PCK-0001` (PICK LIST NOT FOUND) and `ERR-PCK-0007` (PICK LIST NOT IN DRAFT (`<status>`)) [^r9][^r14]. Common errors include `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r15]. The response envelope returns `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r13].
* **Source file**: `04_service_definitions/sales/pck_confirm.yaml` [^r10].

## See also

* [[screen-sal-pck-04|SAL-PCK-04 Pick List Entry]]
* [[screen-sal-so-01|SAL-SO-01 Sales Order]]
* [[services-sal-so|SAL so services]]
* [[services-sal-alc|SAL alc services]]
* [[services-sal-dlv|SAL dlv services]]

## References

[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 42, pck_save PICK LIST SAVE
[^r10]: 04_service_definitions/sales/pck_confirm.yaml, service: pck_confirm
[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 19, Screen layout and fields
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 19, Screen layout and fields
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 19, Screen layout and fields
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 19, Screen layout and fields
[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 37, SAL-PCK-04 PICK LIST ENTRY
[^r11]: 04_service_definitions/sales/pck_confirm.yaml, auth
[^r17]: 04_service_definitions/sales/pck_get.yaml, auth
[^r23]: 04_service_definitions/sales/pck_save.yaml, endpoint
[^r28]: 04_service_definitions/sales/pck_search.yaml, endpoint
[^r22]: 04_service_definitions/sales/pck_save.yaml, service: pck_save
[^r25]: 04_service_definitions/sales/pck_save.yaml, response
[^r24]: 04_service_definitions/sales/pck_save.yaml, request
[^r26]: 04_service_definitions/sales/pck_save.yaml, common_errors
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 43, pck_get PICK LIST GET
[^r16]: 04_service_definitions/sales/pck_get.yaml, service
[^r18]: 04_service_definitions/sales/pck_get.yaml, request.fields
[^r20]: 04_service_definitions/sales/pck_get.yaml, errors
[^r21]: 04_service_definitions/sales/pck_get.yaml, common_errors
[^r19]: 04_service_definitions/sales/pck_get.yaml, response.envelope
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 43, pck_search PICK LIST LIST
[^r27]: 04_service_definitions/sales/pck_search.yaml, service: pck_search
[^r29]: 04_service_definitions/sales/pck_search.yaml, request.fields
[^r31]: 04_service_definitions/sales/pck_search.yaml, common_errors
[^r30]: 04_service_definitions/sales/pck_search.yaml, response.envelope
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 43, pck_confirm PICK LIST CONFIRM
[^r14]: 04_service_definitions/sales/pck_confirm.yaml, errors
[^r12]: 04_service_definitions/sales/pck_confirm.yaml, request.fields
[^r15]: 04_service_definitions/sales/pck_confirm.yaml, common_errors
[^r13]: 04_service_definitions/sales/pck_confirm.yaml, response.envelope
