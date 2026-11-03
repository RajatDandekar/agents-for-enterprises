---
title: "INV-TRF-04 Stock Transfer Entry"
type: "screen"
slug: "screen-inv-trf-04"
summary: "INV-TRF-04 Stock Transfer Entry handles recording, searching, posting, and cancelling warehouse inventory transfers in Ledgerline."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/txf_cancel.yaml", "04_service_definitions/inventory/txf_get.yaml", "04_service_definitions/inventory/txf_post.yaml", "04_service_definitions/inventory/txf_save.yaml", "04_service_definitions/inventory/txf_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | INV-TRF-04 |
| Title | Stock Transfer Entry |
| Menu path | Inventory > Stock transfer |
| Roles | STORES, STORES-MGR, PUR-EXEC, SYS-ADMIN |
| Services | txf_save, txf_get, txf_search, txf_post, txf_cancel |

Screen INV-TRF-04 (Stock Transfer Entry) manages the transfer of inventory items between Northbridge warehouse locations in Ledgerline [^r1][^r6]. Found under Inventory > Stock transfer, it allows authorized staff to draft, search, commit, or cancel stock movement records [^r1][^r6][^r8]. Committed transactions write to ledger lines immediately and cannot be modified directly [^r4].

| Attribute | Details |
|---|---|
| Screen Code | INV-TRF-04 [^r1][^r6] |
| Screen Name | Stock Transfer Entry [^r6] |
| Navigation | Inventory > Stock transfer [^r1][^r6] |
| Authorized Roles | STORES, STORES-MGR, PUR-EXEC, SYS-ADMIN [^r6] |
| Associated Services | [[services-inv-txf|txf_save]], txf_get, txf_search, txf_post, txf_cancel [^r1][^r7][^r8] |

## Fields

When creating a new entry, TXF NO is left blank to allow the system to allocate a transfer number upon saving [^r3]. The source warehouse (FROM WHS) cannot match the destination warehouse (TO WHS) [^r3].

| Field Label | Field Name | Data Type | Requirement | Notes |
|---|---|---|---|---|
| ITEM CD | itm_cd | String | Mandatory | Target item code [^r2][^r6] |
| FROM WHS | from_whs | String | Mandatory | Source warehouse; cannot match destination warehouse [^r2][^r3][^r6] |
| TO WHS | to_whs | String | Mandatory | Destination warehouse; cannot match source warehouse [^r2][^r3][^r6] |
| QTY | qty | Integer | Mandatory | Transfer quantity [^r2][^r6] |
| TXF NO | txf_no | String | Mandatory | Transfer number; left blank on new entry for system allocation [^r2][^r3][^r6] |
| REASON | reason | String | Optional | Reason for transfer [^r2][^r6] |
| STATUS | status | String | Optional | Status of the transfer record [^r2][^r6] |
| COMMENT | comment | String | Optional | Additional transfer notes [^r2][^r6] |

## Keys and services

INV-TRF-04 links keyboard shortcuts and action buttons directly to backend [[services-inv-txf|txf]] services [^r7]:

* **Save (F8)**: Calls write service `txf_save` to record and allocate a transfer entry [^r3][^r7][^r12].
* **Get (F3)**: Calls read service `txf_get` (POST `/ll72/svc/txf_get`) using mandatory field `txf_no` to retrieve a specific record [^r7][^r10].
* **Search (F2 / Enter)**: Calls read service `txf_search` to query transfer records matching item code, source warehouse, destination warehouse, and status [^r7][^r13].
* **Post (F9)**: Calls `txf_post` (POST `/ll72/svc/txf_post`, invoking stored procedure `sp_txf_post`) to commit ledger movements [^r7][^r11]. Once posted, ledger lines cannot be altered, and any quantity discrepancy requires entering an inverse transfer [^r4].
* **Cancel (Shift+F8)**: Calls write service `txf_cancel` to run the STOCK TRANSFER CANCEL service, marking STATUS as cancelled without altering stock balances [^r5][^r7][^r9]. Cancellation is permitted only on unposted drafts [^r5].

## Messages

Screen INV-TRF-04 captures and returns the following system error codes [^r7]:

* `ERR-TXF-0201` [^r7]
* [[err-itm-0011|ERR-ITM-0011]] [^r7]
* `ERR-TXF-0310` [^r7]
* `ERR-STK-0102` [^r7]
* `ERR-TXF-0001` [^r7]
* `ERR-TXF-0007` [^r7]
* `ERR-TXF-0801` [^r7]

## Versions and conflicts

* **Status lifecycle updates**: Under current version 7.2.3, calling `txf_cancel` sets STATUS to cancelled on unposted drafts, whereas committed transfers lock ledger lines permanently [^r4][^r5]. In superseded manual v7.2.2 (dated 2024-06-10), saving with `txf_save` explicitly set STATUS to pending, and posting via `txf_post` updated STATUS to completed [^r16] (`superseded`).

## See also

* [[services-inv-txf|INV txf services]]
* [[errors-txf|Stock Transfer Error Codes (ERR-TXF-*)]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[screen-inv-whs-01|INV-WHS-01 Warehouse Master]]
* [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]]
* [[screen-inv-stk-03|INV-STK-03 Stock Val]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 3, §3. Stock Transfer (INV-TRF-04)
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 20, INV-TRF-04 STOCK TRANSFER ENTRY
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 9, §3. Inventory services
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 5, Step by step
[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 20, INV-TRF-04 STOCK TRANSFER ENTRY
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 4, Step by step
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 3, §3. Stock Transfer (INV-TRF-04)
[^r12]: 04_service_definitions/inventory/txf_save.yaml, screen
[^r10]: 04_service_definitions/inventory/txf_get.yaml, whole file
[^r13]: 04_service_definitions/inventory/txf_search.yaml, service
[^r11]: 04_service_definitions/inventory/txf_post.yaml, whole file
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 5, Step by step
[^r9]: 04_service_definitions/inventory/txf_cancel.yaml, whole file
[^r16]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 3, §3. Stock Transfer (INV-TRF-04)
