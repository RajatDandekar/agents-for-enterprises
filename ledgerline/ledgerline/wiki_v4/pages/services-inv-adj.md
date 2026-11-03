---
title: "INV adj services"
type: "service-group"
slug: "services-inv-adj"
summary: "Inventory adjustment service group in Ledgerline ERP for creating, retrieving, approving, posting, and cancelling stock adjustment records on screen INV-ADJ-05."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/adj_approve.yaml", "04_service_definitions/inventory/adj_cancel.yaml", "04_service_definitions/inventory/adj_get.yaml", "04_service_definitions/inventory/adj_post.yaml", "04_service_definitions/inventory/adj_save.yaml", "04_service_definitions/inventory/adj_search.yaml", "04_service_definitions/service_index.csv"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | Inventory (INV) |
| Object | Stock Adjustment (ADJ) |
| Screen | INV-ADJ-05 |
| Available since | Ledgerline ERP 7.0 |
| Service count | 6 |

The stock adjustment service group provides the backend procedures for managing inventory adjustments in the Ledgerline ERP Inventory (INV) module [^r13][^r34]. Linked directly to screen [[screen-inv-adj-05|INV-ADJ-05]], these services support creating, searching, retrieving, approving, posting, and cancelling adjustment transactions [^r1][^r2][^r3][^r4][^r5][^r6][^r13]. Available since Ledgerline version 7.0, each service endpoint requires authentication via a session token passed in the `X-LL-Session` header and is restricted to authorised user roles [^r13][^r14][^r24][^r34][^r35].

## Services

### adj_save
The `adj_save` service (STOCK ADJUSTMENT SAVE) validates line item details, writes a stock adjustment record, assigns an ADJ NO, and leaves the document in unapproved status [^r1]. It executes stored procedure `sp_adj_save` via endpoint `POST /ll72/svc/adj_save` [^r7][^r35][^r37]. The standard response envelope contains `rc` ("S | W | E"), `err_cd`, `msg`, and `data` [^r37].

* **Required fields**: `itm_cd` (str, ITEM CD), `whs_cd` (str, WHS CD), `qty` (int, QTY (+/-)), and `reason_cd` (str, REASON CD) [^r7][^r36].
* **Optional fields**: `remarks` (str, REMARKS) [^r36].
* **Errors**: [[errors-adj|ERR-ADJ-0201]] ("QTY MUST BE > 0"), [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE), ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r7][^r38].
* **Source file**: `04_service_definitions/inventory/adj_save.yaml` [^r34].

### adj_get
The `adj_get` service (STOCK ADJUSTMENT GET) is a read service that retrieves an existing stock adjustment record by document number for display on screen [[screen-inv-adj-05|INV-ADJ-05]] [^r2][^r8][^r24]. It is invoked at endpoint `POST /ll72/svc/adj_get` and returns a standard envelope with `rc` (S | W | E), `err_cd`, `msg`, and `data` [^r24][^r26].

* **Required fields**: `adj_no` (str, ADJ NO) [^r8][^r25].
* **Optional fields**: None [^r25].
* **Errors**: ERR-ADJ-0001 (STOCK ADJUSTMENT NOT FOUND), ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r8][^r27][^r28].
* **Source file**: `04_service_definitions/inventory/adj_get.yaml` [^r24].

### adj_search
The `adj_search` service executes the STOCK ADJUSTMENT LIST read functionality to look up existing adjustment records across criteria such as warehouse, item, quantity, or status [^r3][^r9][^r39]. It is accessed via endpoint `POST /ll72/svc/adj_search` and returns an envelope with `rc` ('S | W | E'), `err_cd`, `msg`, and `data` [^r39][^r42].

* **Required fields**: None [^r41].
* **Optional fields**: `itm_cd` (str, ITEM CD), `whs_cd` (str, WHS CD), `qty` (int, QTY (+/-)), and `status` (str, STATUS) [^r9][^r41].
* **Errors**: [[errors-adj|ERR-ADJ-0201]] ('QTY MUST BE > 0'), [[err-itm-0011|ERR-ITM-0011]] ('ITEM NOT FOUND OR INACTIVE'), ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 ('<FIELD> MANDATORY'), ERR-SYS-0422 ('UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>'), and ERR-SYS-0503 ('SERVER BUSY, TRY LATER') [^r43][^r44].
* **Source file**: `04_service_definitions/inventory/adj_search.yaml` [^r39].

### adj_approve
The `adj_approve` service (STOCK ADJUSTMENT APPROVE) evaluates line value thresholds against the calling operator's profile and marks the adjustment document as authorised [^r4][^r13]. It is invoked at endpoint `POST /ll72/svc/adj_approve` and executes stored procedure `sp_adj_approve` [^r10][^r13][^r16].

* **Required fields**: `adj_no` (str, ADJ NO) [^r10][^r15].
* **Optional fields**: `comment` (str, COMMENT) [^r15].
* **Errors**: ERR-ADJ-0001 (STOCK ADJUSTMENT NOT FOUND), ERR-ADJ-0007 (STOCK ADJUSTMENT NOT IN DRAFT (<status>)), [[err-apr-0003|ERR-APR-0003]] (SELF APPROVAL NOT ALLOWED), [[err-apr-0004|ERR-APR-0004]] (VALUE ABOVE YOUR LIMIT), ERR-ADJ-0420 (ADJUSTMENT ABOVE [[role-stores|STORES]] LIMIT, NEEDS [[role-plant-head|PLANT HEAD]]), ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r10][^r17][^r18].
* **Source file**: `04_service_definitions/inventory/adj_approve.yaml` [^r13].

### adj_post
The `adj_post` write service (STOCK ADJUSTMENT POST) executes stored procedure `sp_adj_post` to lock the document, update perpetual inventory balances, generate stock ledger movements, and create nominal journal entries [^r5][^r11][^r29]. It is invoked at endpoint `POST /ll72/svc/adj_post` and outputs an envelope with `rc` ('S | W | E'), `err_cd`, `msg`, and `data` [^r30][^r32].

* **Required fields**: `adj_no` (str, ADJ NO) [^r11][^r31].
* **Optional fields**: `comment` (str, COMMENT) [^r11][^r31].
* **Errors**: ERR-ADJ-0001 (STOCK ADJUSTMENT NOT FOUND), ERR-ADJ-0007 (STOCK ADJUSTMENT NOT IN DRAFT (<status>)), ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r11][^r33].
* **Source file**: `04_service_definitions/inventory/adj_post.yaml` [^r29].

### adj_cancel
The `adj_cancel` write service (STOCK ADJUSTMENT CANCEL) executes procedure `sp_adj_cancel` via endpoint `POST /ll72/svc/adj_cancel` to void an unposted stock adjustment record, preventing ledger updates and permanently locking the document against edits [^r6][^r12][^r19][^r23]. Its response envelope provides `rc` ('S | W | E'), `err_cd`, `msg`, and `data` [^r22].

* **Required fields**: `adj_no` (str, ADJ NO) and `reason` (str, REASON) [^r12][^r21].
* **Optional fields**: None [^r21].
* **Errors**: ERR-ADJ-0001 (STOCK ADJUSTMENT NOT FOUND), ERR-ADJ-0801, ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r12][^r20][^r22].
* **Source file**: `04_service_definitions/inventory/adj_cancel.yaml` [^r19].

## Versions and conflicts

* **Superseded inventory manual description**: Under the current [[man-inv-72|MAN-INV-72]] v7.2.3 manual and individual YAML service definitions, the six adjustment services are maintained with active parameter definitions and validations [^r1][^r10][^r13][^r24]. Earlier documentation in MAN-INV-72 v7.2.2 (dated 2024-06-10) covered the same six services and validation errors in §4 before being superseded [^r46]. (Type: `superseded`).

## See also

* [[screen-inv-adj-05|screen-inv-adj-05 Stock Adjustment Entry]]
* [[errors-adj|errors-adj Stock Adjustment Error Codes]]
* [[man-inv-72|man-inv-72 Ledgerline ERP 7.2 User Manual: Inventory]]
* [[err-apr-0003|err-apr-0003 Self-approval not permitted]]
* [[err-apr-0004|err-apr-0004 Advance amount exceeds PO unbilled commitment]]
* [[err-itm-0011|err-itm-0011 ITEM NOT FOUND OR INACTIVE]]
* [[services-inv-cnt|services-inv-cnt Stock count services]]
* [[services-inv-itm|services-inv-itm Item services]]

## References

[^r13]: 04_service_definitions/inventory/adj_approve.yaml, service
[^r34]: 04_service_definitions/inventory/adj_save.yaml, whole file
[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 8, Creating a New Stock Adjustment Record
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 8, Retrieving an Existing Document
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 8, Retrieving an Existing Document
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 8, Approving an Adjustment
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 8, Posting an Adjustment to the Ledger
[^r6]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 9, Cancelling an Adjustment
[^r14]: 04_service_definitions/inventory/adj_approve.yaml, auth
[^r24]: 04_service_definitions/inventory/adj_get.yaml, whole file
[^r35]: 04_service_definitions/inventory/adj_save.yaml, whole file
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 10, adj_save STOCK ADJUSTMENT SAVE
[^r37]: 04_service_definitions/inventory/adj_save.yaml, response.envelope
[^r36]: 04_service_definitions/inventory/adj_save.yaml, request.fields
[^r38]: 04_service_definitions/inventory/adj_save.yaml, errors
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 10, adj_get STOCK ADJUSTMENT GET
[^r26]: 04_service_definitions/inventory/adj_get.yaml, response.envelope
[^r25]: 04_service_definitions/inventory/adj_get.yaml, request.fields
[^r27]: 04_service_definitions/inventory/adj_get.yaml, errors
[^r28]: 04_service_definitions/inventory/adj_get.yaml, common_errors
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 10, adj_search STOCK ADJUSTMENT LIST
[^r39]: 04_service_definitions/inventory/adj_search.yaml, service: adj_search
[^r42]: 04_service_definitions/inventory/adj_search.yaml, response
[^r41]: 04_service_definitions/inventory/adj_search.yaml, request
[^r43]: 04_service_definitions/inventory/adj_search.yaml, errors
[^r44]: 04_service_definitions/inventory/adj_search.yaml, common_errors
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 11, adj_approve STOCK ADJUSTMENT APPROVE
[^r16]: 04_service_definitions/inventory/adj_approve.yaml, procedures
[^r15]: 04_service_definitions/inventory/adj_approve.yaml, request.fields
[^r17]: 04_service_definitions/inventory/adj_approve.yaml, errors
[^r18]: 04_service_definitions/inventory/adj_approve.yaml, common_errors
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 11, adj_post STOCK ADJUSTMENT POST
[^r29]: 04_service_definitions/inventory/adj_post.yaml, service: adj_post
[^r30]: 04_service_definitions/inventory/adj_post.yaml, service: adj_post
[^r32]: 04_service_definitions/inventory/adj_post.yaml, response.envelope
[^r31]: 04_service_definitions/inventory/adj_post.yaml, request.fields
[^r33]: 04_service_definitions/inventory/adj_post.yaml, errors
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 11, adj_cancel STOCK ADJUSTMENT CANCEL
[^r19]: 04_service_definitions/inventory/adj_cancel.yaml, service: adj_cancel
[^r23]: 04_service_definitions/inventory/adj_cancel.yaml, procedures
[^r22]: 04_service_definitions/inventory/adj_cancel.yaml, response.envelope
[^r21]: 04_service_definitions/inventory/adj_cancel.yaml, request.fields
[^r20]: 04_service_definitions/inventory/adj_cancel.yaml, auth
[^r46]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 4, §4. Stock Adjustment (INV-ADJ-05)
