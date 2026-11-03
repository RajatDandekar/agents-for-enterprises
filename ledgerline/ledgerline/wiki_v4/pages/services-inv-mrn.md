---
title: "INV mrn services"
type: "service-group"
slug: "services-inv-mrn"
summary: "Ledgerline inventory services for creating, retrieving, searching, posting, and cancelling material issue records on screen INV-MRN-08."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/mrn_cancel.yaml", "04_service_definitions/inventory/mrn_get.yaml", "04_service_definitions/inventory/mrn_post.yaml", "04_service_definitions/inventory/mrn_save.yaml", "04_service_definitions/inventory/mrn_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| module | INV |
| screen | INV-MRN-08 |
| available_since | 7.0 |
| endpoint_prefix | /ll72/svc/ |
| services_count | 5 |

The material issue service group covers the backend Ledgerline services managing material requisitions and issue notes for production consumption on screen [[screen-inv-mrn-08|INV-MRN-08]][^r1][^r6]. These services handle the full lifecycle of material issues, from creating draft issues and retrieving issue records to committing movements against works order work-in-progress and cancelling unposted requisitions[^r1][^r2][^r3][^r4]. All services run under the `INV` module, execute over HTTP POST endpoints prefixed with `/ll72/svc/`, and require a valid session token in header `X-LL-Session` alongside an authorized user role[^r11][^r12][^r17][^r18][^r22][^r23][^r27][^r28][^r33][^r34][^r35].

## Services

### mrn_save

Service `mrn_save` is a write service titled `MATERIAL ISSUE SAVE` associated with screen [[screen-inv-mrn-08|INV-MRN-08]] that creates or updates a draft material issue record and assigns sequential `MRN NO` values[^r1][^r6][^r27]. It sets record status to draft, decrements temporary allocations, and validates work order, item, stock, and warehouse values[^r1]. It executes backend stored procedure `sp_mrn_save` via endpoint `POST /ll72/svc/mrn_save` and returns the standard envelope containing `rc`, `err_cd`, `msg`, and `data`[^r6][^r27][^r30].

* **Required fields:** `wo_no` (string, `WO NO`), `itm_cd` (string, `ITEM CD`), `qty` (integer, `QTY`)[^r6][^r29].
* **Optional fields:** `whs_cd` (string, `WHS CD`)[^r6][^r29].
* **Errors:** ERR-MRN-0201 (`QTY MUST BE > 0`), [[err-itm-0011|ERR-ITM-0011]] (`ITEM NOT FOUND OR INACTIVE`), ERR-STK-0102 (`INSUFFICIENT STOCK (<available>)`), ERR-WO-0007 (`WORK ORDER NOT RELEASED`)[^r6][^r31]. Common errors include ERR-SEC-0001 (`ACCESS DENIED`), ERR-SYS-0421 (`<FIELD> MANDATORY`), ERR-SYS-0422 (`UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>`), and ERR-SYS-0503 (`SERVER BUSY, TRY LATER`)[^r32].
* **Source file:** `04_service_definitions/inventory/mrn_save.yaml`[^r27].

### mrn_get

Service `mrn_get` is a read service titled `MATERIAL ISSUE GET` associated with screen [[screen-inv-mrn-08|INV-MRN-08]] that retrieves a single material issue record by reference number[^r4][^r7][^r17]. It is available since version 7.0 via endpoint `POST /ll72/svc/mrn_get` and returns a response envelope with `rc`, `err_cd`, `msg`, and `data`[^r17][^r20].

* **Required fields:** `mrn_no` (string, `MRN NO`)[^r7][^r19].
* **Optional fields:** None[^r19].
* **Errors:** ERR-MRN-0001 (`MATERIAL ISSUE NOT FOUND`)[^r4][^r7][^r21]. Common errors include ERR-SEC-0001 (`ACCESS DENIED`), ERR-SYS-0421 (`<FIELD> MANDATORY`), ERR-SYS-0422 (`UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>`), and ERR-SYS-0503 (`SERVER BUSY, TRY LATER`)[^r21].
* **Source file:** `04_service_definitions/inventory/mrn_get.yaml`[^r17].

### mrn_search

Service `mrn_search` is a read service titled `MATERIAL ISSUE LIST` associated with screen [[screen-inv-mrn-08|INV-MRN-08]] used to query and list material issue records matching criteria such as works order numbers[^r5][^r8][^r33]. It is accessible via endpoint `POST /ll72/svc/mrn_search` since version 7.0 and populates standard response envelope fields `rc`, `err_cd`, `msg`, and `data`[^r34][^r37].

* **Required fields:** None[^r8][^r36].
* **Optional fields:** `wo_no` (string, `WO NO`), `itm_cd` (string, `ITEM CD`), `qty` (integer, `QTY`), `status` (string, `STATUS`)[^r8][^r36].
* **Errors:** ERR-MRN-0201 (`QTY MUST BE > 0`), [[err-itm-0011|ERR-ITM-0011]] (`ITEM NOT FOUND OR INACTIVE`)[^r8][^r38]. Common errors include ERR-SEC-0001 (`ACCESS DENIED`), ERR-SYS-0421 (`<FIELD> MANDATORY`), ERR-SYS-0422 (`UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>`), and ERR-SYS-0503 (`SERVER BUSY, TRY LATER`)[^r39].
* **Source file:** `04_service_definitions/inventory/mrn_search.yaml`[^r33].

### mrn_post

Service `mrn_post` is a write service titled `MATERIAL ISSUE POST` associated with screen [[screen-inv-mrn-08|INV-MRN-08]] that commits a material issue movement, decrements warehouse inventory stock balances, debits works order WIP accounts, and transitions record status to posted[^r2][^r9][^r22]. It executes database stored procedure `sp_mrn_post` via endpoint `POST /ll72/svc/mrn_post`[^r9][^r23][^r25].

* **Required fields:** `mrn_no` (string, `MRN NO`)[^r9][^r24].
* **Optional fields:** `comment` (string, `COMMENT`)[^r9][^r24].
* **Errors:** ERR-MRN-0001 (`MATERIAL ISSUE NOT FOUND`), ERR-MRN-0007 (`MATERIAL ISSUE NOT IN DRAFT (<status>)`)[^r3][^r9][^r26]. Common errors include ERR-SEC-0001 (`ACCESS DENIED`), ERR-SYS-0421 (`<FIELD> MANDATORY`), ERR-SYS-0422 (`UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>`), and ERR-SYS-0503 (`SERVER BUSY, TRY LATER`)[^r26].
* **Source file:** `04_service_definitions/inventory/mrn_post.yaml`[^r22].

### mrn_cancel

Service `mrn_cancel` is a write service titled `MATERIAL ISSUE CANCEL` associated with screen [[screen-inv-mrn-08|INV-MRN-08]] that cancels an unposted material issue record and releases any temporary stock reservations[^r3][^r10][^r11]. It executes stored procedure `sp_mrn_cancel` via endpoint `POST /ll72/svc/mrn_cancel`[^r10][^r11][^r14]. Attempting to cancel an already committed record fails with error conditions[^r3].

* **Required fields:** `mrn_no` (string, `MRN NO`), `reason` (string, `REASON`)[^r10][^r13].
* **Optional fields:** None[^r10][^r13].
* **Errors:** ERR-MRN-0001 (`MATERIAL ISSUE NOT FOUND`), ERR-MRN-0801 (`MATERIAL ISSUE CLOSED (<status>)`)[^r10][^r15]. It also reports ERR-MRN-0007 if invoked against a committed record[^r3]. Common errors include ERR-SEC-0001 (`ACCESS DENIED`), ERR-SYS-0421 (`<FIELD> MANDATORY`), ERR-SYS-0422 (`UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>`), and ERR-SYS-0503 (`SERVER BUSY, TRY LATER`)[^r16].
* **Source file:** `04_service_definitions/inventory/mrn_cancel.yaml`[^r11].

## Versions and conflicts

* **Today's rule:** In [[man-inv-72|MAN-INV-72]] v7.2.3, `mrn_save` populates `MRN NO` sequentially, validates `WO NO`, and checks against unreleased work orders (raising ERR-WO-0007), while `mrn_post` debits works order WIP balances alongside warehouse stock balance decrements[^r1][^r2][^r6].
* **Older rule:** In superseded manual [[man-inv-72|MAN-INV-72]] v7.2.2 (dated 2024-06-10), `mrn_save` documentation did not specify work order release validation, and `mrn_post` was described solely as committing movements directly to inventory records without explicit WIP balance updates[^r40][^r41].
* **Sources:** [[man-inv-72|MAN-INV-72]] v7.2.3 (2025-01-15) and [[man-inv-72|MAN-INV-72]] v7.2.2 (2024-06-10)[^r1][^r2][^r40][^r41].
* **Kind:** `superseded`[^r40][^r41].

## See also

* [[screen-inv-mrn-08|INV-MRN-08 Material Issue Entry]]
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]
* [[errors-mrn|ERR-MRN Error Code Reference]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[services-inv-stk|INV stk services]]
* [[services-inv-res|INV res services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 19, Step by step
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 14, mrn_save MATERIAL ISSUE SAVE
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 19, Step by step
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 20, Step by step
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 20, Messages
[^r11]: 04_service_definitions/inventory/mrn_cancel.yaml, service: mrn_cancel
[^r12]: 04_service_definitions/inventory/mrn_cancel.yaml, auth
[^r17]: 04_service_definitions/inventory/mrn_get.yaml, service: mrn_get
[^r18]: 04_service_definitions/inventory/mrn_get.yaml, auth
[^r22]: 04_service_definitions/inventory/mrn_post.yaml, service: mrn_post
[^r23]: 04_service_definitions/inventory/mrn_post.yaml, auth
[^r27]: 04_service_definitions/inventory/mrn_save.yaml, whole file
[^r28]: 04_service_definitions/inventory/mrn_save.yaml, auth
[^r33]: 04_service_definitions/inventory/mrn_search.yaml, service: mrn_search
[^r34]: 04_service_definitions/inventory/mrn_search.yaml, service: mrn_search
[^r35]: 04_service_definitions/inventory/mrn_search.yaml, auth
[^r30]: 04_service_definitions/inventory/mrn_save.yaml, response.envelope
[^r29]: 04_service_definitions/inventory/mrn_save.yaml, request.fields
[^r31]: 04_service_definitions/inventory/mrn_save.yaml, errors
[^r32]: 04_service_definitions/inventory/mrn_save.yaml, common_errors
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 14, mrn_get MATERIAL ISSUE GET
[^r20]: 04_service_definitions/inventory/mrn_get.yaml, response.envelope
[^r19]: 04_service_definitions/inventory/mrn_get.yaml, request.fields
[^r21]: 04_service_definitions/inventory/mrn_get.yaml, errors
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 20, Step by step
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 14, mrn_search MATERIAL ISSUE LIST
[^r37]: 04_service_definitions/inventory/mrn_search.yaml, response.envelope
[^r36]: 04_service_definitions/inventory/mrn_search.yaml, request.fields
[^r38]: 04_service_definitions/inventory/mrn_search.yaml, errors
[^r39]: 04_service_definitions/inventory/mrn_search.yaml, common_errors
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 14, mrn_post MATERIAL ISSUE POST
[^r25]: 04_service_definitions/inventory/mrn_post.yaml, procedures
[^r24]: 04_service_definitions/inventory/mrn_post.yaml, request
[^r26]: 04_service_definitions/inventory/mrn_post.yaml, errors
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 14, mrn_cancel MATERIAL ISSUE CANCEL
[^r14]: 04_service_definitions/inventory/mrn_cancel.yaml, procedures
[^r13]: 04_service_definitions/inventory/mrn_cancel.yaml, request.fields
[^r15]: 04_service_definitions/inventory/mrn_cancel.yaml, errors
[^r16]: 04_service_definitions/inventory/mrn_cancel.yaml, common_errors
[^r40]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 9, Step by step
[^r41]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 9, Step by step
