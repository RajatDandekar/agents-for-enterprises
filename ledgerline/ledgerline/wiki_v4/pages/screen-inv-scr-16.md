---
title: "INV-SCR-16 Scrap Note Entry"
type: "screen"
slug: "screen-inv-scr-16"
summary: "Ledgerline screen for creating, searching, approving, and posting inventory scrap notes to write off stock."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/scr_approve.yaml", "04_service_definitions/inventory/scr_get.yaml", "04_service_definitions/inventory/scr_post.yaml", "04_service_definitions/inventory/scr_save.yaml", "04_service_definitions/inventory/scr_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | INV-SCR-16 |
| Screen title | Scrap Note Entry |
| Module | Inventory |
| Navigation | Inventory > Scrap note |
| Primary roles | STORES, STORES-MGR, PUR-EXEC, SYS-ADMIN |
| Key services | scr_save, scr_get, scr_search, scr_approve, scr_post |

Screen INV-SCR-16 (Scrap Note Entry) is Ledgerline's interface under Inventory > Scrap note for recording, approving, and posting stock write-offs [^r1][^r7]. It is accessible to roles STORES, STORES-MGR, PUR-EXEC, and SYS-ADMIN [^r7]. Once a scrap note is approved, its core entry fields are locked against further modification [^r3].

| Field | Detail |
|---|---|
| Screen code | INV-SCR-16 [^r1] |
| Screen title | Scrap Note Entry [^r7] |
| Module | Inventory [^r1] |
| Navigation | Inventory > Scrap note [^r1][^r7] |
| Access roles | STORES, STORES-MGR, PUR-EXEC, SYS-ADMIN [^r7] |

## Fields

INV-SCR-16 captures mandatory and optional header and line attributes for scrap entries:

* **SCR NO (`scr_no`)**: Mandatory scrap reference number [^r1][^r7]. Leaving this field blank on initial entry prompts the system to allocate the next sequential scrap reference number and assign a draft status [^r2].
* **ITEM CD (`itm_cd`)**: Mandatory item code to be scrapped [^r1][^r7].
* **WHS CD (`whs_cd`)**: Mandatory warehouse location code where stock is held [^r1][^r7].
* **QTY (`qty`)**: Mandatory integer scrap quantity [^r1][^r7].
* **REASON CD (`reason_cd`)**: Mandatory scrap reason code [^r1][^r7].
* **STATUS (`status`)**: Optional status indicator [^r1][^r7].
* **COMMENT (`comment`)**: Optional descriptive comment [^r1][^r7].

## Keys and services

INV-SCR-16 connects to the [[services-inv-scr|INV scr services]] group across several function keys and actions:

* **Get (F3)**: Executes read service `scr_get` to retrieve scrap note records by reference number [^r8][^r9][^r12].
* **Search (F2 / Enter)**: Calls service `scr_search` (POST `/ll72/svc/scr_search`) to query scrap notes by item code, warehouse code, quantity, and status [^r8][^r9][^r15].
* **Save (F8)**: Invokes write service `scr_save` (POST `/ll72/svc/scr_save`) to generate or update scrap note records with mandatory item, warehouse, quantity, and reason codes [^r2][^r8][^r9][^r14].
* **Approve (F9)**: Calls write service `scr_approve` (POST `/ll72/svc/scr_approve`) via stored procedure `sp_scr_approve` to approve the scrap note and lock core fields [^r3][^r8][^r9][^r10].
* **Post (F9)**: Executes write service `scr_post` (POST `/ll72/svc/scr_post`) to finalize and post the scrap movement [^r8][^r9][^r13].

## Messages

The screen validates entries against the following system errors:

* [[err-itm-0011|ERR-ITM-0011]]: Returned when the specified item does not exist in the part master, is obsolete, or is flagged inactive for store movements [^r6][^r8].
* ERR-SCR-0001: Raised when the scrap quantity exceeds the available unallocated physical stock in the selected warehouse [^r4][^r8].
* ERR-SCR-0007: Raised when the scrap reason code is missing or invalid, or when another user locks the scrap record during retrieval [^r5][^r8].
* ERR-SCR-0201: Stock validation error checked by the interface [^r8].
* [[err-apr-0003|ERR-APR-0003]]: Returned during approval when self-approval is attempted [^r8][^r11].
* [[err-apr-0004|ERR-APR-0004]]: Returned during approval when the value exceeds the user's authorized approval limit [^r8][^r11].

## Versions and conflicts

* **Error definitions for ERR-SCR-0001 and ERR-SCR-0007**: Today, under v7.2.3, ERR-SCR-0001 indicates that scrap quantity exceeds unallocated warehouse stock, and ERR-SCR-0007 indicates an invalid reason code or record lock [^r4][^r5]. In superseded v7.2.2 (2024-06-10), ERR-SCR-0001 represented missing mandatory fields, ERR-SCR-0007 indicated a scrap note was not found, and ERR-SCR-0201 indicated insufficient stock (`superseded`) [^r18].
* **Approval error definitions**: Today, under v7.2.3, approval enforces limits via ERR-APR-0003 (self-approval not permitted) and ERR-APR-0004 (value above approval limit) [^r11]. In superseded v7.2.2 (2024-06-10), ERR-APR-0003 represented general missing approval permissions, and ERR-APR-0004 represented an already approved record (`superseded`) [^r18].

## See also

* [[services-inv-scr|INV scr services]]
* [[errors-scr|ERR-SCR Scrap Error Codes]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[err-apr-0003|ERR-APR-0003 Self-approval not permitted]]
* [[err-apr-0004|ERR-APR-0004 Advance amount exceeds PO unbilled commitment]]
* [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]]
* [[screen-inv-adj-05|INV-ADJ-05 Stock Adjustment Entry]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 60, §18. Scrap Note (INV-SCR-16)
[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 19, INV-SCR-16 SCRAP NOTE ENTRY
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 62, To approve a scrap note:
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 61, Step by step
[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 19, INV-SCR-16 SCRAP NOTE ENTRY
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 23, scr_approve SCRAP NOTE APPROVE
[^r12]: 04_service_definitions/inventory/scr_get.yaml, service: scr_get
[^r15]: 04_service_definitions/inventory/scr_search.yaml, service: scr_search
[^r14]: 04_service_definitions/inventory/scr_save.yaml, whole file
[^r10]: 04_service_definitions/inventory/scr_approve.yaml, service: scr_approve
[^r13]: 04_service_definitions/inventory/scr_post.yaml, service: scr_post
[^r6]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 63, Messages
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 63, Messages
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 63, Messages
[^r11]: 04_service_definitions/inventory/scr_approve.yaml, errors
[^r18]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 26, Messages
