---
title: "INV lot services"
type: "service-group"
slug: "services-inv-lot"
summary: "Ledgerline Inventory module services for creating, querying, tracing, holding, and releasing item lot and serial records on screen INV-LOT-10."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/lot_get.yaml", "04_service_definitions/inventory/lot_hold.yaml", "04_service_definitions/inventory/lot_release.yaml", "04_service_definitions/inventory/lot_save.yaml", "04_service_definitions/inventory/lot_search.yaml", "04_service_definitions/inventory/lot_trace.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | INV (Inventory) |
| Screen | INV-LOT-10 |
| Available since | Ledgerline 7.2.0 |
| Operations | lot_save, lot_get, lot_search, lot_trace, lot_hold, lot_release |
| Authentication | X-LL-Session header and authorised role |

The INV lot service group manages the registration, retrieval, lifecycle status, and genealogy tracking of tracked lots and serial numbers within Ledgerline ERP [^r1][^r4][^r13]. Mapped primarily to screen [[screen-inv-lot-10|INV-LOT-10]], these services allow warehouse operators to search lot registers, place materials on hold to block allocation, release cleared stock, and trace component consumption across work and sales orders [^r2][^r4][^r5][^r6][^r13]. All endpoints operate over HTTP POST, require an `X-LL-Session` authentication token header, enforce role-based access, and return a standard envelope containing return code `rc`, `err_cd`, `msg`, and `data` [^r14][^r16][^r19][^r21].

## Services

### lot_save

The `lot_save` service (title `LOT / SERIAL SAVE`) is an Inventory write service available since Ledgerline 7.2.0 at endpoint `POST /ll72/svc/lot_save` [^r28]. It validates submitted lot details against the item master and vendor ledgers, executing stored procedure `sp_lot_save` on screen [[screen-inv-lot-10|INV-LOT-10]] to commit changes [^r3][^r7][^r34]. Calling the service requires session authentication in the `X-LL-Session` header and an authorised role [^r29].

* **Required fields**: `itm_cd` (ITEM CD, string), `lot_no` (LOT/SERIAL, string) [^r7][^r30].
* **Optional fields**: `sup_cd` (SUP CD, string), `mfg_dt` (MFG DT, date), `grn_no` (GRN NO, string) [^r7][^r30].
* **Errors**: Specific errors include [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE) and [[err-sup-0030|ERR-SUP-0030]] (SUPPLIER NOT FOUND) [^r7][^r32]. Common errors include ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r33].
* **Source file**: `04_service_definitions/inventory/lot_save.yaml` [^r28].

### lot_get

The `lot_get` service (title `LOT / SERIAL GET`) is an Inventory read service available since Ledgerline 7.2.0 at endpoint `POST /ll72/svc/lot_get` [^r8][^r13]. Linked to screen [[screen-inv-lot-10|INV-LOT-10]], it retrieves recorded lot attributes including `SUP CD`, `MFG DT`, `GRN NO`, and `STATUS` [^r1][^r13]. Access requires an `X-LL-Session` token and an authorised role [^r14].

* **Required fields**: `lot_no` (string) [^r8][^r15].
* **Optional fields**: None [^r8][^r15].
* **Errors**: Specific error [[err-lot-0001|ERR-LOT-0001]] (LOT / SERIAL NOT FOUND) [^r8][^r17]. Common errors include ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r17].
* **Source file**: `04_service_definitions/inventory/lot_get.yaml` [^r13].

### lot_search

The `lot_search` service (title `LOT / SERIAL LIST`) is an Inventory read service active since version 7.2.0 at endpoint `POST /ll72/svc/lot_search` [^r35]. Mapped to screen [[screen-inv-lot-10|INV-LOT-10]], it opens a list window displaying all matching recorded lot and serial numbers [^r2][^r9][^r35]. It requires an `X-LL-Session` header and an authorised role [^r36].

* **Required fields**: None [^r9][^r37].
* **Optional fields**: `itm_cd` (ITEM CD, string), `lot_no` (LOT/SERIAL, string), `sup_cd` (SUP CD, string), `status` (STATUS, string) [^r9][^r37].
* **Errors**: Specific error [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE) [^r9][^r39]. Common errors include ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r40].
* **Source file**: `04_service_definitions/inventory/lot_search.yaml` [^r35].

### lot_trace

The `lot_trace` service (title `LOT / SERIAL TRACE`) is an Inventory read service introduced in version 7.2.0 at endpoint `POST /ll72/svc/lot_trace` [^r10][^r41]. Associated with screen [[screen-inv-lot-10|INV-LOT-10]], it returns the complete movement genealogy of a lot or serial number from receipt on a GRN through warehouse storage, work order consumption, and sales order dispatch [^r4][^r10][^r41]. Access requires an authorised role and an `X-LL-Session` token [^r42].

* **Required fields**: `lot_no` (LOT NO, string) [^r10][^r43].
* **Optional fields**: None [^r10][^r43].
* **Errors**: Specific error [[err-lot-0001|ERR-LOT-0001]] (LOT / SERIAL NOT FOUND) [^r10][^r45]. Common errors include ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r45].
* **Source file**: `04_service_definitions/inventory/lot_trace.yaml` [^r41].

### lot_hold

The `lot_hold` service (title `LOT / SERIAL HOLD`) is an Inventory write service introduced in version 7.2.0 at endpoint `POST /ll72/svc/lot_hold` [^r18]. Operating on screen [[screen-inv-lot-10|INV-LOT-10]], it executes stored procedure `sp_lot_hold` to update a lot's `STATUS` to held, preventing allocation or picking for works orders and sales orders [^r5][^r11][^r20]. Invocation requires role-based authorisation and an `X-LL-Session` authentication token [^r19].

* **Required fields**: `lot_no` (LOT NO, string) [^r11][^r20].
* **Optional fields**: `reason` (REASON, string) [^r11][^r20].
* **Errors**: Specific errors [[err-lot-0001|ERR-LOT-0001]] (LOT / SERIAL NOT FOUND) and [[err-lot-0301|ERR-LOT-0301]] (LOT ALREADY ON HOLD) [^r11][^r22].
* **Source file**: `04_service_definitions/inventory/lot_hold.yaml` [^r18].

### lot_release

The `lot_release` service (title `LOT / SERIAL RELEASE`) is an Inventory write service available since version 7.2.0 at endpoint `POST /ll72/svc/lot_release` [^r23]. Linked to screen [[screen-inv-lot-10|INV-LOT-10]], it executes stored procedure `sp_lot_release` to clear quarantine restrictions and restore lot `STATUS` to active and available [^r6][^r12][^r23]. It requires an `X-LL-Session` header and an authorised role [^r24].

* **Required fields**: `lot_no` (string) [^r12][^r25].
* **Optional fields**: `comment` (string) [^r12][^r25].
* **Errors**: Specific errors [[err-lot-0001|ERR-LOT-0001]] (LOT / SERIAL NOT FOUND) and [[err-lot-0007|ERR-LOT-0007]] (LOT / SERIAL NOT IN DRAFT (<status>)) [^r12][^r26]. Common errors include ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r27].
* **Source file**: `04_service_definitions/inventory/lot_release.yaml` [^r23].

## Versions and conflicts

* **Lot hold status update and fields**: Current documentation ([[man-inv-72|MAN-INV-72]] v7.2.3 and `lot_hold.yaml`) states that `lot_hold` updates lot `STATUS` to held, takes optional field `reason`, and locks stock against picking [^r5][^r20]. In superseded manual [[man-inv-72|MAN-INV-72]] v7.2.2 (10 June 2024), `lot_hold` set lot `STATUS` to quarantine after capturing notes in `REASON` and `COMMENT` [^r46]. Kind: `superseded`.

## See also

* [[screen-inv-lot-10|INV-LOT-10 Lot / Serial Entry]]
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]
* [[errors-lot|ERR-LOT Error Codes]]
* [[services-inv-itm|INV itm services]]
* [[services-inv-qch|INV qch services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 26, Retrieving an existing record:
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 27, Tracing item movement:
[^r13]: 04_service_definitions/inventory/lot_get.yaml, service
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 26, Retrieving an existing record:
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 27, Placing a lot on hold:
[^r6]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 27, Releasing a lot from quarantine:
[^r14]: 04_service_definitions/inventory/lot_get.yaml, auth
[^r16]: 04_service_definitions/inventory/lot_get.yaml, response.envelope
[^r19]: 04_service_definitions/inventory/lot_hold.yaml, whole file
[^r21]: 04_service_definitions/inventory/lot_hold.yaml, response
[^r28]: 04_service_definitions/inventory/lot_save.yaml, service: lot_save
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 27, Registering or amending lot information:
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 15, lot_save LOT / SERIAL SAVE
[^r34]: 04_service_definitions/inventory/lot_save.yaml, procedures
[^r29]: 04_service_definitions/inventory/lot_save.yaml, auth
[^r30]: 04_service_definitions/inventory/lot_save.yaml, request.fields
[^r32]: 04_service_definitions/inventory/lot_save.yaml, errors
[^r33]: 04_service_definitions/inventory/lot_save.yaml, common_errors
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 15, lot_get LOT / SERIAL GET
[^r15]: 04_service_definitions/inventory/lot_get.yaml, request.fields
[^r17]: 04_service_definitions/inventory/lot_get.yaml, errors
[^r35]: 04_service_definitions/inventory/lot_search.yaml, service
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 16, lot_search LOT / SERIAL LIST
[^r36]: 04_service_definitions/inventory/lot_search.yaml, auth
[^r37]: 04_service_definitions/inventory/lot_search.yaml, request.fields
[^r39]: 04_service_definitions/inventory/lot_search.yaml, errors
[^r40]: 04_service_definitions/inventory/lot_search.yaml, common_errors
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 16, lot_trace LOT / SERIAL TRACE
[^r41]: 04_service_definitions/inventory/lot_trace.yaml, whole file
[^r42]: 04_service_definitions/inventory/lot_trace.yaml, auth
[^r43]: 04_service_definitions/inventory/lot_trace.yaml, request
[^r45]: 04_service_definitions/inventory/lot_trace.yaml, errors
[^r18]: 04_service_definitions/inventory/lot_hold.yaml, whole file
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 16, lot_hold LOT / SERIAL HOLD
[^r20]: 04_service_definitions/inventory/lot_hold.yaml, request
[^r22]: 04_service_definitions/inventory/lot_hold.yaml, errors
[^r23]: 04_service_definitions/inventory/lot_release.yaml, lot_release
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 16, lot_release LOT / SERIAL RELEASE
[^r24]: 04_service_definitions/inventory/lot_release.yaml, lot_release
[^r25]: 04_service_definitions/inventory/lot_release.yaml, request.fields
[^r26]: 04_service_definitions/inventory/lot_release.yaml, errors
[^r27]: 04_service_definitions/inventory/lot_release.yaml, common_errors
[^r46]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 12, Step by step
