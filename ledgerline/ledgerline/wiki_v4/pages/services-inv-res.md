---
title: "INV res services"
type: "service-group"
slug: "services-inv-res"
summary: "Ledgerline ERP 7.2 inventory service group managing stock reservation creation, lookup, search, and cancellation via screen INV-RES-12."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/res_cancel.yaml", "04_service_definitions/inventory/res_get.yaml", "04_service_definitions/inventory/res_save.yaml", "04_service_definitions/inventory/res_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | INV |
| Object | res (Stock Reservation) |
| Screen | INV-RES-12 |
| Services | res_save, res_get, res_search, res_cancel |
| Protocol | POST |
| Endpoint Base | /ll72/svc/ |
| Available Since | Ledgerline ERP 7.0 |
| Status | Current |

The `services-inv-res` service group provides the core stock reservation operations under module INV for Ledgerline ERP 7.2 [^r10]. Executed from screen [[screen-inv-res-12|INV-RES-12]], these services handle creating, querying, searching, and cancelling reservations against unreserved inventory balances [^r1][^r2][^r5]. All endpoints operate over HTTP POST, require caller authentication via session token header `X-LL-Session` with an authorised role, and return a standardised envelope with fields `rc`, `err_cd`, `msg`, and `data` [^r11][^r13][^r18][^r20][^r23][^r26][^r30][^r32].

## Services

### res_save (STOCK RESERVATION SAVE)
* **Description**: A write service available since version 7.0 that validates warehouse balances against free unreserved stock and commits the reservation via stored procedure `sp_res_save` on screen [[screen-inv-res-12|INV-RES-12]] [^r2][^r6][^r22][^r25].
* **Endpoint**: `POST /ll72/svc/res_save` [^r23].
* **Authentication**: Requires header `X-LL-Session` and a role permitted for the service [^r23].
* **Required fields**: `itm_cd` (str, ITEM CD), `whs_cd` (str, WHS CD), and `qty` (int, QTY) [^r6][^r24].
* **Optional fields**: `wo_no` (str, WO NO) [^r6][^r24].
* **Specific errors**: [[err-res-0201|ERR-RES-0201]] (QTY MUST BE > 0), [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE) [^r27].
* **Common errors**: ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r28].
* **Source file**: `04_service_definitions/inventory/res_save.yaml` [^r22][^r28].

### res_get (STOCK RESERVATION GET)
* **Description**: A read service available since version 7.0 that retrieves and populates ITEM CD, WHS CD, QTY, WO NO, STATUS, and REASON for a specified reservation number on screen [[screen-inv-res-12|INV-RES-12]] [^r3][^r7][^r17].
* **Endpoint**: `POST /ll72/svc/res_get` [^r18].
* **Authentication**: Requires header `X-LL-Session` and a role permitted for the service [^r18].
* **Required fields**: `res_no` (str, RES NO) [^r7][^r19].
* **Optional fields**: None [^r19].
* **Specific errors**: [[err-res-0001|ERR-RES-0001]] (STOCK RESERVATION NOT FOUND) [^r7][^r20].
* **Common errors**: ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r21].
* **Source file**: `04_service_definitions/inventory/res_get.yaml` [^r17][^r21].

### res_search (STOCK RESERVATION LIST)
* **Description**: A read service available since version 7.0 that lists matching stock reservations from partial search criteria on screen [[screen-inv-res-12|INV-RES-12]] [^r4][^r8][^r29].
* **Endpoint**: `POST /ll72/svc/res_search` [^r29].
* **Authentication**: Requires header `X-LL-Session` and a role permitted for the service [^r30].
* **Required fields**: None [^r31].
* **Optional fields**: `itm_cd` (str, ITEM CD), `whs_cd` (str, WHS CD), `qty` (int, QTY), and `status` (str, STATUS) [^r8][^r31].
* **Specific errors**: [[err-res-0201|ERR-RES-0201]] (QTY MUST BE > 0), [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE) [^r8][^r33].
* **Common errors**: ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r34].
* **Source file**: `04_service_definitions/inventory/res_search.yaml` [^r29][^r34].

### res_cancel (STOCK RESERVATION CANCEL)
* **Description**: A write service available since version 7.0 that releases reserved stock back to available inventory via stored procedure `sp_res_cancel` on screen [[screen-inv-res-12|INV-RES-12]], verifying that parts have not already been drawn down by stores issues [^r5][^r9][^r10][^r14].
* **Endpoint**: `POST /ll72/svc/res_cancel` [^r11].
* **Authentication**: Requires header `X-LL-Session` and a role permitted for the service [^r11].
* **Required fields**: `res_no` (str, RES NO) and `reason` (str, REASON) [^r9][^r12].
* **Optional fields**: None [^r12].
* **Specific errors**: [[err-res-0001|ERR-RES-0001]] (STOCK RESERVATION NOT FOUND), [[err-res-0801|ERR-RES-0801]] (STOCK RESERVATION CLOSED (<status>)) [^r9][^r15].
* **Common errors**: ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r16].
* **Source file**: `04_service_definitions/inventory/res_cancel.yaml` [^r10][^r16].

## Versions and conflicts

* **Reservation workflow validation**: Today, in [[man-inv-72|MAN-INV-72]] v7.2.3 (effective 2025-01-15), `res_save` validates warehouse balances against free unreserved stock, `res_cancel` checks whether reserved stock has been drawn down by stores issues prior to release, and `res_search` filters by item, warehouse, quantity, or status [^r1][^r2][^r4][^r5][^r8]. Under superseded manual MAN-INV-72 v7.2.2 (2024-06-10), `res_save` generated RES NO and set STATUS to hold stock, `res_cancel` simply returned held stock to free inventory, and `res_search` retrieved reservations across the works order [^r35][^r36][^r37] (`superseded`).

## See also

* [[screen-inv-res-12|screen-inv-res-12]]: Screen INV-RES-12 Stock Reservation Entry
* [[man-inv-72|man-inv-72]]: MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory
* [[errors-res|errors-res]]: ERR-RES Stock Reservation Error Codes
* [[err-res-0001|err-res-0001]]: ERR-RES-0001 General reservation validation failure
* [[err-res-0201|err-res-0201]]: ERR-RES-0201 Insufficient unreserved stock available
* [[err-res-0801|err-res-0801]]: ERR-RES-0801 Cancellation rejected
* [[err-itm-0011|err-itm-0011]]: ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE

## References

[^r10]: 04_service_definitions/inventory/res_cancel.yaml, whole file
[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 33, §11. Stock Reservation (INV-RES-12)
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 36, Worked example
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 34, Step by step
[^r11]: 04_service_definitions/inventory/res_cancel.yaml, whole file
[^r13]: 04_service_definitions/inventory/res_cancel.yaml, response.envelope
[^r18]: 04_service_definitions/inventory/res_get.yaml, endpoint
[^r20]: 04_service_definitions/inventory/res_get.yaml, response
[^r23]: 04_service_definitions/inventory/res_save.yaml, res_save
[^r26]: 04_service_definitions/inventory/res_save.yaml, response.envelope
[^r30]: 04_service_definitions/inventory/res_search.yaml, auth
[^r32]: 04_service_definitions/inventory/res_search.yaml, response.envelope
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 17, res_save STOCK RESERVATION SAVE
[^r22]: 04_service_definitions/inventory/res_save.yaml, res_save
[^r25]: 04_service_definitions/inventory/res_save.yaml, procedures
[^r24]: 04_service_definitions/inventory/res_save.yaml, request.fields
[^r27]: 04_service_definitions/inventory/res_save.yaml, errors
[^r28]: 04_service_definitions/inventory/res_save.yaml, common_errors
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 34, Step by step
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 18, res_get STOCK RESERVATION GET
[^r17]: 04_service_definitions/inventory/res_get.yaml, service
[^r19]: 04_service_definitions/inventory/res_get.yaml, request.fields
[^r21]: 04_service_definitions/inventory/res_get.yaml, common_errors
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 34, Step by step
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 18, res_search STOCK RESERVATION LIST
[^r29]: 04_service_definitions/inventory/res_search.yaml, service: res_search
[^r31]: 04_service_definitions/inventory/res_search.yaml, request.fields
[^r33]: 04_service_definitions/inventory/res_search.yaml, errors
[^r34]: 04_service_definitions/inventory/res_search.yaml, common_errors
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 18, res_cancel STOCK RESERVATION CANCEL
[^r14]: 04_service_definitions/inventory/res_cancel.yaml, procedures
[^r12]: 04_service_definitions/inventory/res_cancel.yaml, request.fields
[^r15]: 04_service_definitions/inventory/res_cancel.yaml, errors
[^r16]: 04_service_definitions/inventory/res_cancel.yaml, common_errors
[^r35]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 15, Step by step
[^r36]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 16, Messages
[^r37]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 16, Messages
