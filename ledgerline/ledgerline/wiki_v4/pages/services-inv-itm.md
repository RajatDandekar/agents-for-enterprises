---
title: "INV itm services"
type: "service-group"
slug: "services-inv-itm"
summary: "Inventory module services for creating, modifying, blocking, and maintaining unit of measure conversions for item master records on screen INV-ITM-01."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/itm_block.yaml", "04_service_definitions/inventory/itm_save.yaml", "04_service_definitions/inventory/itm_uom_conv.yaml", "04_service_definitions/inventory/itm_update.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| service_group | services-inv-itm |
| module | INV |
| screen | screen-inv-itm-01 |
| services | itm_save, itm_update, itm_block, itm_uom_conv |
| protocol | HTTP POST (/ll72/svc/*) |
| auth | Session token (X-LL-Session) |
| status | current |

The `services-inv-itm` service group comprises the core inventory write services in Ledgerline ERP 7.2 responsible for maintaining item records on screen [[screen-inv-itm-01|INV-ITM-01]][^r8][^r12][^r27]. These services handle creating item records, updating item parameters, blocking items from operational transactions, and maintaining secondary unit of measure conversion factors[^r2][^r3][^r4][^r5]. All endpoints in this group execute underlying database stored procedures via HTTP POST requests authenticated by a session token in the `X-LL-Session` header and require an authorised user role[^r13][^r15][^r18][^r20][^r23][^r28].

| Field | Value |
|---|---|
| Group code | `services-inv-itm` |
| Module | INV |
| Screen | [[screen-inv-itm-01|INV-ITM-01]] |
| Services | `itm_save`, `itm_update`, `itm_block`, `itm_uom_conv` |
| Introduced | Ledgerline 7.0 |
| Authentication | Session token (`X-LL-Session`) |
| Response envelope | `rc` ('S \| W \| E'), `err_cd`, `msg`, `data` |

## Services

### itm_save

The `itm_save` (ITEM MASTER SAVE) service creates a new item record, verifying entries against database tables, updating the system audit log, and clearing the entry buffer[^r2]. It is an INV write service introduced in Ledgerline 7.0 exposed at endpoint `POST /ll72/svc/itm_save`, executing stored procedure `sp_itm_save` on screen [[screen-inv-itm-01|INV-ITM-01]][^r8][^r17][^r18][^r20].

* **Required fields:** `itm_cd` (ITEM CD), `descr` (DESCRIPTION), `uom_cd` (UOM), and `category` (CATEGORY)[^r8][^r19].
* **Optional fields:** `cell_safety` (LITHIUM CELL 0/1; integer) and `reorder_lvl` (REORDER LVL; integer)[^r8][^r19].
* **Errors:** Specific error [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE), alongside common system errors ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER)[^r20][^r21].
* **Source file:** `04_service_definitions/inventory/itm_save.yaml`[^r17].

### itm_update

The `itm_update` (ITEM MASTER UPDATE) service modifies an existing item master record on screen [[screen-inv-itm-01|INV-ITM-01]] and executes stored procedure `sp_itm_update`[^r3][^r9][^r27][^r31]. It is accessible via endpoint `POST /ll72/svc/itm_update` and requires a valid session token in `X-LL-Session` with an authorised role[^r28].

* **Required fields:** `itm_cd` (string)[^r9][^r29].
* **Optional fields:** `descr` (string), `uom_cd` (string), `category` (string), and `cell_safety` (integer, lithium cell 0/1)[^r9][^r29].
* **Errors:** [[err-itm-0001|ERR-ITM-0001]] (ITEM MASTER NOT FOUND), [[err-itm-0801|ERR-ITM-0801]], and [[err-itm-0011|ERR-ITM-0011]], along with common system errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503[^r1][^r9][^r30][^r31].
* **Source file:** `04_service_definitions/inventory/itm_update.yaml`[^r27].

### itm_block

The `itm_block` (ITEM MASTER BLOCK) service sets an active item record as internally inactive for operational transactions on screen [[screen-inv-itm-01|INV-ITM-01]] by executing stored procedure `sp_itm_block`[^r4][^r10][^r12][^r15]. It is exposed at endpoint `POST /ll72/svc/itm_block` and requires session token authentication via `X-LL-Session`[^r12][^r13].

* **Required fields:** `itm_cd` (ITM CD; string)[^r10][^r14].
* **Optional fields:** `reason` (REASON; string)[^r10][^r14].
* **Errors:** [[err-itm-0001|ERR-ITM-0001]] (ITEM MASTER NOT FOUND) and [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE)[^r1][^r10][^r16].
* **Source file:** `04_service_definitions/inventory/itm_block.yaml`[^r12].

### itm_uom_conv

The `itm_uom_conv` (ITEM MASTER UOM CONV) service records unit conversion parameters in the secondary inventory conversion table for an item on screen [[screen-inv-itm-01|INV-ITM-01]] via stored procedure `sp_itm_uom_conv`[^r5][^r11][^r22]. It operates at endpoint `POST /ll72/svc/itm_uom_conv` and requires session token authorization[^r22][^r23].

* **Required fields:** `itm_cd` (ITEM CD; string), `from_uom` (FROM UOM; string), `to_uom` (TO UOM; string), and `factor` (FACTOR; float)[^r11][^r24].
* **Optional fields:** None[^r11][^r24].
* **Errors:** [[err-itm-0001|ERR-ITM-0001]] (ITEM MASTER NOT FOUND) and [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE), as well as common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503[^r1][^r7][^r11][^r25][^r26].
* **Source file:** `04_service_definitions/inventory/itm_uom_conv.yaml`[^r22].

## Versions and conflicts

* **Superseded manual procedures:** In current Ledgerline 7.2.3 documentation and service definitions, services execute with structured API envelopes and parameters[^r8][^r9][^r10][^r11][^r20]. Under superseded manual MAN-INV-72 v7.2.2 (2024-06-10), `itm_save` validated keys and committed new stock records, `itm_update` modified descriptions and reorder levels, and `itm_uom_conv` committed alternative unit conversion multipliers (`superseded`)[^r32][^r33].
* **UOM mutability on update:** Technical manual MAN-SVC-72 v7.2.3 and service definition `itm_update.yaml` accept `uom_cd` as an optional input field[^r9][^r29]. Conversely, user manual MAN-INV-72 v7.2.3 states that `itm_update` does not allow changes to the primary UOM (`contradiction`)[^r3].
* **itm_block mandatory reason and error codes:** The user manual worked example states that `itm_block` requires an explanatory entry in the REASON field and raises [[err-itm-0801|ERR-ITM-0801]] if omitted[^r6]. In contrast, service definition `itm_block.yaml` and reference MAN-SVC-72 document `reason` as an optional field and list only [[err-itm-0001|ERR-ITM-0001]] and [[err-itm-0011|ERR-ITM-0011]] as valid specific errors (`contradiction`)[^r10][^r14][^r16].

## See also

* [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]]
* [[errors-itm|ERR-ITM error codes]]
* [[err-itm-0001|ERR-ITM-0001: Item code already exists in Item Master]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[err-itm-0801|ERR-ITM-0801: Conversion factor invalid or calculation mismatch between units of measure]]
* [[items-bat|BAT-* items]]
* [[services-inv-adj|INV adj services]]
* [[services-inv-whs|INV whs services]]

## References

[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 18, itm_save ITEM MASTER SAVE
[^r12]: 04_service_definitions/inventory/itm_block.yaml, whole file
[^r27]: 04_service_definitions/inventory/itm_update.yaml, service: itm_update
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 41, Creating a new item master record
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 42, Updating an existing item record
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 42, Blocking an item from operational use
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 42, Maintaining unit of measure conversions
[^r13]: 04_service_definitions/inventory/itm_block.yaml, whole file
[^r15]: 04_service_definitions/inventory/itm_block.yaml, whole file
[^r18]: 04_service_definitions/inventory/itm_save.yaml, endpoint
[^r20]: 04_service_definitions/inventory/itm_save.yaml, response.envelope
[^r23]: 04_service_definitions/inventory/itm_uom_conv.yaml, endpoint
[^r28]: 04_service_definitions/inventory/itm_update.yaml, service: itm_update
[^r17]: 04_service_definitions/inventory/itm_save.yaml, service
[^r19]: 04_service_definitions/inventory/itm_save.yaml, request.fields
[^r21]: 04_service_definitions/inventory/itm_save.yaml, errors
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 19, itm_update ITEM MASTER UPDATE
[^r31]: 04_service_definitions/inventory/itm_update.yaml, errors
[^r29]: 04_service_definitions/inventory/itm_update.yaml, request.fields
[^r1]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 11
[^r30]: 04_service_definitions/inventory/itm_update.yaml, response.envelope
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 19, itm_block ITEM MASTER BLOCK
[^r14]: 04_service_definitions/inventory/itm_block.yaml, request
[^r16]: 04_service_definitions/inventory/itm_block.yaml, errors
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 19, itm_uom_conv ITEM MASTER UOM CONV
[^r22]: 04_service_definitions/inventory/itm_uom_conv.yaml, service: itm_uom_conv
[^r24]: 04_service_definitions/inventory/itm_uom_conv.yaml, request.fields
[^r7]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 44, Worked example: Item Master
[^r25]: 04_service_definitions/inventory/itm_uom_conv.yaml, errors
[^r26]: 04_service_definitions/inventory/itm_uom_conv.yaml, common_errors
[^r32]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 19, Step by step
[^r33]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 19, Step by step
[^r6]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 44, Worked example: Item Master
