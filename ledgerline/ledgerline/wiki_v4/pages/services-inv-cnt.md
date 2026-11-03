---
title: "INV cnt services"
type: "service-group"
slug: "services-inv-cnt"
summary: "Ledgerline inventory count services supporting stock count creation, freeze, entry, search, posting, and cancellation on screen INV-CNT-06."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/cnt_cancel.yaml", "04_service_definitions/inventory/cnt_entry.yaml", "04_service_definitions/inventory/cnt_freeze.yaml", "04_service_definitions/inventory/cnt_get.yaml", "04_service_definitions/inventory/cnt_post.yaml", "04_service_definitions/inventory/cnt_save.yaml", "04_service_definitions/inventory/cnt_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | INV |
| Object | cnt |
| Screen | INV-CNT-06 |
| Endpoint base | /ll72/svc/ |
| Ledgerline version | 7.2.3 |
| Status | current |

The `cnt` service group manages physical inventory counts within Ledgerline's Inventory (INV) module on screen [[screen-inv-cnt-06|INV-CNT-06]][^r13][^r27][^r32]. Operating via write and read endpoints introduced in version 7.0, it coordinates the complete cycle count and annual count workflow from document initialisation and bin freezing through line entry, posting, and cancellation[^r5][^r6][^r7][^r9][^r10][^r20][^r49]. All endpoints require a session token passed in the `X-LL-Session` header and enforce role-based access control[^r21][^r28][^r33][^r38][^r44][^r50][^r56].

## Services

### cnt_save

Initialises a new stock count header and creates a unique document reference in `CNT NO`[^r5]. Available since Ledgerline 7.0, it executes database procedure `sp_cnt_save` via `POST /ll72/svc/cnt_save` linked to [[screen-inv-cnt-06|INV-CNT-06]][^r13][^r48][^r49][^r54].

* **Required fields**: `whs_cd` (warehouse code), `cnt_type` (`CYCLE` or `ANNUAL`), and `cnt_dt` (count date)[^r13][^r51].
* **Optional fields**: `bin_from` and `bin_to`[^r51].
* **Errors**: [[errors-cnt|ERR-CNT-0105]] (raised if `cnt_dt` is in the past), `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503`[^r4][^r13][^r53].
* **Source file**: `04_service_definitions/inventory/cnt_save.yaml`[^r48].

### cnt_get

Retrieves an existing stock count record on [[screen-inv-cnt-06|INV-CNT-06]] using endpoint `POST /ll72/svc/cnt_get`[^r8][^r14][^r37]. It operates as a read service introduced in version 7.0[^r37].

* **Required fields**: `cnt_no`[^r14][^r39].
* **Optional fields**: none[^r39].
* **Errors**: [[errors-cnt|ERR-CNT-0001]] (stock count not found), `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503`[^r14][^r41][^r42].
* **Source file**: `04_service_definitions/inventory/cnt_get.yaml`[^r37].

### cnt_search

Enables browsing open counts via the `STOCK COUNT LIST` view on [[screen-inv-cnt-06|INV-CNT-06]][^r8][^r15][^r55]. It is a read service operating via `POST /ll72/svc/cnt_search` introduced in Ledgerline 7.0[^r15][^r55][^r56].

* **Required fields**: none[^r15][^r57].
* **Optional fields**: `whs_cd`, `cnt_type` (`CYCLE` or `ANNUAL`), `bin_from`, and `status`[^r15][^r57].
* **Errors**: `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503`[^r59].
* **Source file**: `04_service_definitions/inventory/cnt_search.yaml`[^r55].

### cnt_freeze

Locks inventory movements across the bin range configured in `BIN FROM` and `BIN TO`[^r6]. It runs database stored procedure `sp_cnt_freeze` via write endpoint `POST /ll72/svc/cnt_freeze` on [[screen-inv-cnt-06|INV-CNT-06]][^r17][^r32][^r36].

* **Required fields**: `cnt_no`[^r17][^r34].
* **Optional fields**: `comment`[^r17][^r34].
* **Errors**: [[errors-cnt|ERR-CNT-0001]], [[errors-cnt|ERR-CNT-0007]] (raised if count is not in Draft status), [[err-cnt-0230|ERR-CNT-0230]] (raised if open transactions exist in the count area), `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503`[^r1][^r17].
* **Source file**: `04_service_definitions/inventory/cnt_freeze.yaml`[^r32].

### cnt_entry

Inputs physical count results for individual items into the sub-form on [[screen-inv-cnt-06|INV-CNT-06]][^r7][^r16]. It invokes stored procedure `sp_cnt_entry` via write endpoint `POST /ll72/svc/cnt_entry`[^r16][^r27][^r30].

* **Required fields**: `cnt_no` (count number), `itm_cd` (item code), and positive integer `qty` (quantity counted)[^r16][^r29].
* **Optional fields**: none[^r29].
* **Errors**: [[errors-cnt|ERR-CNT-0001]], [[errors-cnt|ERR-CNT-0201]] (raised if quantity entered is zero or negative), [[err-itm-0011|ERR-ITM-0011]], `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503`[^r3][^r16][^r31].
* **Source file**: `04_service_definitions/inventory/cnt_entry.yaml`[^r27].

### cnt_post

Evaluates count lines against book balance snapshots, releases bin movement locks, writes adjustment entries to stock balances, and closes the count document[^r9]. Invoked from [[screen-inv-cnt-06|INV-CNT-06]], it runs stored procedure `sp_cnt_post` via write endpoint `POST /ll72/svc/cnt_post`[^r18][^r43][^r47].

* **Required fields**: `cnt_no`[^r18][^r45].
* **Optional fields**: `comment`[^r18][^r45].
* **Errors**: [[errors-cnt|ERR-CNT-0001]], [[errors-cnt|ERR-CNT-0007]] (raised if count is not in Draft or pending status), [[err-cnt-0240|ERR-CNT-0240]] (raised if variance exceeds tolerance requiring a recount, if discrepancy requires supervisor sign-off, or if variance exceeds the `INV.CNT_TOL_PCT` threshold of 1.5% by value), warning `W-CNT-241`, `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503`[^r2][^r12][^r18].
* **Source file**: `04_service_definitions/inventory/cnt_post.yaml`[^r43].

### cnt_cancel

Clears count sheets, releases bin locks, and marks document status as cancelled[^r10][^r11]. Operating on [[screen-inv-cnt-06|INV-CNT-06]], it invokes backend procedure `sp_cnt_cancel` through write endpoint `POST /ll72/svc/cnt_cancel`[^r19][^r20][^r21][^r24].

* **Required fields**: `cnt_no` and `reason`[^r19][^r22].
* **Optional fields**: none[^r22].
* **Errors**: [[errors-cnt|ERR-CNT-0001]], [[errors-cnt|ERR-CNT-0801]] (raised if the count is closed or linked transactions prevent cancellation), `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503`[^r11][^r19][^r25][^r26].
* **Source file**: `04_service_definitions/inventory/cnt_cancel.yaml`[^r20].

## Versions and conflicts

* **Current version (Ledgerline 7.2.3, 2025-01-15)**: The current operational service group for physical counts comprises `cnt_save`, `cnt_get`, `cnt_search`, `cnt_freeze`, `cnt_entry`, `cnt_post`, and `cnt_cancel` on screen [[screen-inv-cnt-06|INV-CNT-06]], governed by the endpoints and error responses documented in v7.2.3 manuals and service definitions[^r1][^r2][^r3][^r4][^r5][^r6][^r7][^r8][^r9][^r10][^r11][^r12][^r13][^r14][^r15][^r16][^r17][^r18][^r19][^r20][^r27][^r32][^r37][^r43][^r48][^r55].
* **Superseded version (Ledgerline 7.2.2, 2024-06-10)**: Section 5 of superseded manual `MAN-INV-72` v7.2.2 detailed the stock count service list and error catalog (`ERR-CNT-0001`, `ERR-CNT-0007`, `ERR-CNT-0105`, `ERR-CNT-0201`, `ERR-CNT-0230`, `ERR-CNT-0240`, `ERR-CNT-0801`, `ERR-ITM-0011`, and `W-CNT-241`) prior to the v7.2.3 documentation baseline[^r60]. Kind: `superseded`[^r60].

## See also

* [[screen-inv-cnt-06|INV-CNT-06 Stock Count Entry]]
* [[errors-cnt|Stock Count Error Codes (ERR-CNT-*)]]
* [[err-cnt-0230|ERR-CNT-0230 Area has open transactions]]
* [[err-cnt-0240|ERR-CNT-0240 Cycle Count Value Variance Exceeds Tolerance]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[services-inv-adj|INV adj services]]
* [[services-inv-ccp|INV ccp services]]
* [[screen-inv-ccp-14|INV-CCP-14 Cycle Count Plan Entry]]

## References

[^r13]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 11, cnt_save STOCK COUNT SAVE
[^r27]: 04_service_definitions/inventory/cnt_entry.yaml, whole file
[^r32]: 04_service_definitions/inventory/cnt_freeze.yaml, service: cnt_freeze
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 12, Initiating a new count header:
[^r6]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 12, Freezing inventory:
[^r7]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 12, Entering count results:
[^r9]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 12, Posting or cancelling the count:
[^r10]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 12, Posting or cancelling the count:
[^r20]: 04_service_definitions/inventory/cnt_cancel.yaml, service: cnt_cancel
[^r49]: 04_service_definitions/inventory/cnt_save.yaml, cnt_save
[^r21]: 04_service_definitions/inventory/cnt_cancel.yaml, endpoint
[^r28]: 04_service_definitions/inventory/cnt_entry.yaml, whole file
[^r33]: 04_service_definitions/inventory/cnt_freeze.yaml, auth
[^r38]: 04_service_definitions/inventory/cnt_get.yaml, auth
[^r44]: 04_service_definitions/inventory/cnt_post.yaml, endpoint / auth
[^r50]: 04_service_definitions/inventory/cnt_save.yaml, auth
[^r56]: 04_service_definitions/inventory/cnt_search.yaml, whole file
[^r48]: 04_service_definitions/inventory/cnt_save.yaml, cnt_save
[^r54]: 04_service_definitions/inventory/cnt_save.yaml, procedures
[^r51]: 04_service_definitions/inventory/cnt_save.yaml, request.fields
[^r4]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 5, ERR-CNT-0105
[^r53]: 04_service_definitions/inventory/cnt_save.yaml, errors
[^r8]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 12, Entering count results:
[^r14]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 11, cnt_get STOCK COUNT GET
[^r37]: 04_service_definitions/inventory/cnt_get.yaml, whole file
[^r39]: 04_service_definitions/inventory/cnt_get.yaml, request.fields
[^r41]: 04_service_definitions/inventory/cnt_get.yaml, errors
[^r42]: 04_service_definitions/inventory/cnt_get.yaml, common_errors
[^r15]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 12, cnt_search STOCK COUNT LIST
[^r55]: 04_service_definitions/inventory/cnt_search.yaml, whole file
[^r57]: 04_service_definitions/inventory/cnt_search.yaml, request.fields
[^r59]: 04_service_definitions/inventory/cnt_search.yaml, common_errors
[^r17]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 12, cnt_freeze STOCK COUNT FREEZE
[^r36]: 04_service_definitions/inventory/cnt_freeze.yaml, procedures
[^r34]: 04_service_definitions/inventory/cnt_freeze.yaml, request.fields
[^r1]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 5, ERR-CNT-0230
[^r16]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 12, cnt_entry STOCK COUNT ENTRY
[^r30]: 04_service_definitions/inventory/cnt_entry.yaml, response
[^r29]: 04_service_definitions/inventory/cnt_entry.yaml, request.fields
[^r3]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 5, ERR-CNT-0201
[^r31]: 04_service_definitions/inventory/cnt_entry.yaml, errors
[^r18]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 12, cnt_post STOCK COUNT POST
[^r43]: 04_service_definitions/inventory/cnt_post.yaml, service: cnt_post
[^r47]: 04_service_definitions/inventory/cnt_post.yaml, procedures
[^r45]: 04_service_definitions/inventory/cnt_post.yaml, request.fields
[^r2]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 5, ERR-CNT-0240
[^r12]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 14, Questions users ask
[^r11]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 14, Questions users ask
[^r19]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 12, cnt_cancel STOCK COUNT CANCEL
[^r24]: 04_service_definitions/inventory/cnt_cancel.yaml, procedures
[^r22]: 04_service_definitions/inventory/cnt_cancel.yaml, request.fields
[^r25]: 04_service_definitions/inventory/cnt_cancel.yaml, errors
[^r26]: 04_service_definitions/inventory/cnt_cancel.yaml, common_errors
[^r60]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 5, §5. Stock Count (INV-CNT-06)
