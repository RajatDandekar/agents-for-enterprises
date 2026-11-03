---
title: "INV scr services"
type: "service-group"
slug: "services-inv-scr"
summary: "Ledgerline INV scrap services supporting creation, enquiry, approval, and posting of scrap notes on screen INV-SCR-16."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/scr_approve.yaml", "04_service_definitions/inventory/scr_get.yaml", "04_service_definitions/inventory/scr_post.yaml", "04_service_definitions/inventory/scr_save.yaml", "04_service_definitions/inventory/scr_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | INV |
| Screen | INV-SCR-16 |
| Services | scr_save, scr_get, scr_search, scr_approve, scr_post |
| Introduced | Ledgerline ERP 7.0 |
| Protocol | POST (/ll72/svc/*) |
| Session header | X-LL-Session |

The INV scrap service group handles scrap note lifecycle actions in Ledgerline ERP, including saving draft notes, retrieving records, listing existing notes, authorising write-offs, and final posting [^r1][^r2][^r3][^r4][^r5]. All five services operate under module INV against screen [[screen-inv-scr-16|INV-SCR-16]] via HTTP POST endpoints introduced in Ledgerline 7.0 [^r6][^r12][^r18][^r23][^r30][^r35]. Every service call requires a valid session token passed in the `X-LL-Session` header and an authenticated role permitted to run the service [^r13][^r19][^r24][^r31][^r35]. Responses adhere to a standard envelope containing return code `rc` (`S | W | E`), error code `err_cd`, uppercase message `msg`, and payload `data` [^r15][^r21][^r26][^r33].

## Services

### scr_save
The `scr_save` service (SCRAP NOTE SAVE) creates a scrap document, issues a sequence number into SCR NO, and assigns draft status via stored procedure `sp_scr_save` [^r1][^r7][^r30][^r34]. Accessed on screen [[screen-inv-scr-16|INV-SCR-16]] (keyboard shortcut F8) and via endpoint `POST /ll72/svc/scr_save`, it validates the specified item, warehouse, and quantity codes [^r1][^r6][^r31].
* **Required fields**: `itm_cd` (ITEM CD, string), `whs_cd` (WHS CD, string), `qty` (QTY, integer), and `reason_cd` (REASON CD, string) [^r7][^r32].
* **Optional fields**: None [^r32].
* **Errors**: Specific errors include [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE) and ERR-SCR-0201 (QTY MUST BE > 0) [^r7][^r34]. Common errors are ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r30].
* **Source file**: `04_service_definitions/inventory/scr_save.yaml` [^r30].

### scr_get
The `scr_get` service (SCRAP NOTE GET) is a read service that retrieves an existing scrap record by reference number on screen [[screen-inv-scr-16|INV-SCR-16]] (F3) via endpoint `POST /ll72/svc/scr_get` [^r2][^r6][^r8][^r18].
* **Required fields**: `scr_no` (SCR NO, string) [^r8][^r20].
* **Optional fields**: None [^r20].
* **Errors**: Returns [[errors-scr|ERR-SCR-0001]] (SCRAP NOTE NOT FOUND) or ERR-SCR-0007 if locked by another user, as well as common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r2][^r8][^r22].
* **Source file**: `04_service_definitions/inventory/scr_get.yaml` [^r18].

### scr_search
The `scr_search` service (SCRAP NOTE LIST) is a read service that queries existing scrap records matching specified filters on screen [[screen-inv-scr-16|INV-SCR-16]] (F2/Enter) via endpoint `POST /ll72/svc/scr_search` [^r3][^r6][^r9][^r35].
* **Required fields**: None [^r36].
* **Optional fields**: `itm_cd` (string), `whs_cd` (string), `qty` (integer), and `status` (string) [^r9][^r36].
* **Errors**: Can return domain errors [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE) and ERR-SCR-0201 (QTY MUST BE > 0), alongside common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r9][^r37][^r38].
* **Source file**: `04_service_definitions/inventory/scr_search.yaml` [^r35].

### scr_approve
The `scr_approve` service (SCRAP NOTE APPROVE) validates supervisor authorization, applies formal approval, locks scrap fields, and invokes stored procedure `sp_scr_approve` on screen [[screen-inv-scr-16|INV-SCR-16]] (F9) via endpoint `POST /ll72/svc/scr_approve` [^r4][^r6][^r10][^r12][^r15].
* **Required fields**: `scr_no` (SCR NO, string) [^r10][^r14].
* **Optional fields**: `comment` (COMMENT, string) [^r14].
* **Errors**: Returns domain errors [[errors-scr|ERR-SCR-0001]] (SCRAP NOTE NOT FOUND), ERR-SCR-0007 (SCRAP NOTE NOT IN DRAFT (<status>)), [[err-apr-0003|ERR-APR-0003]] (SELF APPROVAL NOT ALLOWED), and [[err-apr-0004|ERR-APR-0004]] (VALUE ABOVE YOUR LIMIT), in addition to common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r4][^r10][^r16][^r17].
* **Source file**: `04_service_definitions/inventory/scr_approve.yaml` [^r12].

### scr_post
The `scr_post` service (SCRAP NOTE POST) verifies location stock balances, flags STATUS as posted, updates general ledger scrap and inventory accounts, and reduces physical stock via stored procedure `sp_scr_post` on screen [[screen-inv-scr-16|INV-SCR-16]] (F9) via endpoint `POST /ll72/svc/scr_post` [^r5][^r6][^r11][^r23][^r27].
* **Required fields**: `scr_no` (SCR NO, string) [^r11][^r25].
* **Optional fields**: `comment` (COMMENT, string) [^r11][^r25].
* **Errors**: Returns [[errors-scr|ERR-SCR-0001]] (SCRAP NOTE NOT FOUND), ERR-SCR-0007 (SCRAP NOTE NOT IN DRAFT (<status>)), or ERR-SCR-0201 if unapproved or if the accounting period is closed, alongside common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r5][^r11][^r28][^r29].
* **Source file**: `04_service_definitions/inventory/scr_post.yaml` [^r23].

## Versions and conflicts

Today's rule under MAN-INV-72 v7.2.3 (2025-01-15) establishes that `scr_save` assigns draft status, `scr_approve` performs supervisor authorization and locks record fields, and `scr_post` reduces physical stock balances and updates inventory and scrap general ledger accounts [^r1][^r4][^r5]. Under superseded manual MAN-INV-72 v7.2.2 (2024-06-10), `scr_save` set a provisional STATUS, `scr_approve` updated STATUS to authorised, and `scr_post` permanently wrote off stock balances [^r39][^r40] (`superseded`).

## See also
* [[screen-inv-scr-16|INV-SCR-16 Scrap Note Entry]]
* [[errors-scr|ERR-SCR Scrap Error Codes]]
* [[err-apr-0003|ERR-APR-0003 Self-approval not permitted]]
* [[err-apr-0004|ERR-APR-0004 Advance amount exceeds PO unbilled commitment]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[services-inv-adj|INV adj services]]
* [[services-inv-itm|INV itm services]]
* [[services-inv-mrn|INV mrn services]]
* [[services-inv-stk|INV stk services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 61, Screen Layout and Fields
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 61, Screen Layout and Fields
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 61, Screen Layout and Fields
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 61, Screen Layout and Fields
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 61, Screen Layout and Fields
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 19, INV-SCR-16 SCRAP NOTE ENTRY
[^r12]: 04_service_definitions/inventory/scr_approve.yaml, service: scr_approve
[^r18]: 04_service_definitions/inventory/scr_get.yaml, service: scr_get
[^r23]: 04_service_definitions/inventory/scr_post.yaml, service: scr_post
[^r30]: 04_service_definitions/inventory/scr_save.yaml, whole file
[^r35]: 04_service_definitions/inventory/scr_search.yaml, service: scr_search
[^r13]: 04_service_definitions/inventory/scr_approve.yaml, auth
[^r19]: 04_service_definitions/inventory/scr_get.yaml, auth
[^r24]: 04_service_definitions/inventory/scr_post.yaml, endpoint
[^r31]: 04_service_definitions/inventory/scr_save.yaml, whole file
[^r15]: 04_service_definitions/inventory/scr_approve.yaml, response.envelope
[^r21]: 04_service_definitions/inventory/scr_get.yaml, response.envelope
[^r26]: 04_service_definitions/inventory/scr_post.yaml, response.envelope
[^r33]: 04_service_definitions/inventory/scr_save.yaml, response.envelope
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 23, scr_save SCRAP NOTE SAVE
[^r34]: 04_service_definitions/inventory/scr_save.yaml, errors
[^r32]: 04_service_definitions/inventory/scr_save.yaml, request.fields
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 23, scr_get SCRAP NOTE GET
[^r20]: 04_service_definitions/inventory/scr_get.yaml, request.fields
[^r22]: 04_service_definitions/inventory/scr_get.yaml, errors
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 23, scr_search SCRAP NOTE LIST
[^r36]: 04_service_definitions/inventory/scr_search.yaml, request.fields
[^r37]: 04_service_definitions/inventory/scr_search.yaml, errors
[^r38]: 04_service_definitions/inventory/scr_search.yaml, common_errors
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 23, scr_approve SCRAP NOTE APPROVE
[^r14]: 04_service_definitions/inventory/scr_approve.yaml, request.fields
[^r16]: 04_service_definitions/inventory/scr_approve.yaml, errors
[^r17]: 04_service_definitions/inventory/scr_approve.yaml, common_errors
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 24, scr_post SCRAP NOTE POST
[^r27]: 04_service_definitions/inventory/scr_post.yaml, procedures
[^r25]: 04_service_definitions/inventory/scr_post.yaml, request.fields
[^r28]: 04_service_definitions/inventory/scr_post.yaml, errors
[^r29]: 04_service_definitions/inventory/scr_post.yaml, common_errors
[^r39]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 26, Step by step
[^r40]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 26, Step by step
