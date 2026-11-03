---
title: "INV-CNT-06 Stock Count Entry"
type: "screen"
slug: "screen-inv-cnt-06"
summary: "Ledgerline screen for freezing bin ranges, entering physical counts, and posting or cancelling stock count batches."
audience: "staff"
status: "mixed"
sources: ["02_procedures/SOP-INV-003 Stock Count v1.2.pdf", "03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/cnt_cancel.yaml", "04_service_definitions/inventory/cnt_entry.yaml", "04_service_definitions/inventory/cnt_freeze.yaml", "04_service_definitions/inventory/cnt_get.yaml", "04_service_definitions/inventory/cnt_post.yaml", "04_service_definitions/inventory/cnt_save.yaml", "04_service_definitions/inventory/cnt_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| screen | INV-CNT-06 |
| title | Stock Count Entry |
| module | Inventory |
| menu | Inventory > Stock count |
| status | current |

Screen INV-CNT-06 (Stock Count Entry) is the Ledgerline interface used to manage physical inventory and cycle count operations [^r3][^r12]. Accessible via Inventory > Stock count, the screen enables stores clerks to freeze inventory across designated bin ranges, record actual item counts, and execute final adjustment postings or cancellations [^r3][^r5][^r6][^r7][^r8]. Prior to issuing count sheets, operators must ensure the designated zone is locked and that no pending transactions remain open in the count area [^r1][^r2].

## Fields

Screen INV-CNT-06 includes the following mandatory entry fields:
* WHS CD (`whs_cd`): Warehouse code for the count location [^r4][^r12][^r22].
* CYCLE/ANNUAL (`cnt_type`): Count classification type [^r4][^r12][^r22][^r23].
* COUNT DT (`cnt_dt`): Scheduled count date [^r4][^r12][^r22].
* CNT NO (`cnt_no`): Stock count batch reference number [^r4][^r12][^r18].
* ITEM CD (`itm_cd`): Inventory item code being recorded [^r4][^r12][^r18].
* QTY COUNTED (`qty`): Physical count quantity recorded [^r4][^r12][^r18].
* REASON (`reason`): Mandatory reason code for count adjustments or cancellations [^r4][^r12][^r16].

Clerks can enter unexpected components directly into the line entry grid using ITEM CD, which registers the item against the designated bin [^r10].

## Keys and services

Screen INV-CNT-06 interacts with the following backend services in [[services-inv-cnt]]:
* `cnt_save`: Creates and saves stock count header records with warehouse code, count type, count date, and optional bin ranges [^r14][^r22].
* `cnt_get`: Retrieves an existing stock count record using endpoint POST `/ll72/svc/cnt_get` and parameter `cnt_no` [^r14][^r20].
* `cnt_search`: Searches and lists count batches filtered by warehouse, count type, status, and starting bin [^r15][^r23].
* `cnt_freeze`: Places temporary movement locks across bins within the specified BIN FROM and BIN TO range [^r5][^r19].
* `cnt_entry`: Opens the line entry sub-form to submit counted quantities against `cnt_no` and `itm_cd` [^r6][^r17][^r18].
* `cnt_post`: Executes final posting, releases bin freezes, updates stock balance adjustment records, and closes the count [^r7][^r21]. Once posted, adjustments cannot be reversed automatically from the screen [^r11].
* `cnt_cancel`: Cancels an unposted count batch using `cnt_no` and `reason`, immediately releasing bin locks and clearing count sheets [^r8][^r9][^r16].

## Messages

Screen INV-CNT-06 can raise the following system errors and warnings:
* `ERR-CNT-0001`: Stock Count Not Found [^r13].
* `ERR-CNT-0007`: Stock Count Not In Draft (<Status>) [^r13].
* `ERR-CNT-0105`: Date In Past [^r13].
* `ERR-CNT-0201`: Qty Must Be > 0 [^r13].
* [[err-cnt-0230]]: Open Transactions In Count Area [^r1][^r13].
* [[err-cnt-0240]]: Variance Above Tolerance, Recount Required [^r13].
* `ERR-CNT-0801`: Stock Count Closed (<Status>) [^r13].
* [[err-itm-0011]]: Item Not Found Or Inactive [^r13].
* `W-CNT-241`: Variance Noted, Within Tolerance [^r13].

## Versions and conflicts

Under MAN-INV-72 v7.2.3 and MAN-SCR-72 v7.2.3, the mandatory fields for screen INV-CNT-06 explicitly include warehouse code (`whs_cd`), alongside `cnt_type`, `cnt_dt`, `cnt_no`, `itm_cd`, `qty`, and `reason` [^r4][^r12]. Under the superseded MAN-INV-72 v7.2.2 (dated 2024-06-10), `whs_cd` was omitted from the listed mandatory screen fields (`superseded`) [^r25].

## See also

* [[err-cnt-0230|ERR-CNT-0230 Area has open transactions]]
* [[err-cnt-0240|ERR-CNT-0240 Cycle Count Value Variance Exceeds Tolerance]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[errors-cnt|Stock Count Error Codes (ERR-CNT-*)]]
* [[screen-inv-adj-05|INV-ADJ-05 Stock Adjustment Entry]]
* [[screen-inv-ccp-14|INV-CCP-14 Cycle Count Plan Entry]]
* [[services-inv-cnt|INV cnt services]]

## References

[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 11, §5. Stock Count (INV-CNT-06)
[^r12]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 13, INV-CNT-06 STOCK COUNT ENTRY
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 12, Freezing inventory:
[^r6]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 12, Entering count results:
[^r7]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 12, Posting or cancelling the count:
[^r8]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 12, Posting or cancelling the count:
[^r1]: 02_procedures/SOP-INV-003 Stock Count v1.2.pdf, p. 3, §5. Procedure
[^r2]: 02_procedures/SOP-INV-003 Stock Count v1.2.pdf, p. 4, What to check on the screen
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 11, §5. Stock Count (INV-CNT-06)
[^r22]: 04_service_definitions/inventory/cnt_save.yaml, cnt_save
[^r23]: 04_service_definitions/inventory/cnt_search.yaml, whole file
[^r18]: 04_service_definitions/inventory/cnt_entry.yaml, request.fields
[^r16]: 04_service_definitions/inventory/cnt_cancel.yaml, service: cnt_cancel
[^r10]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 13, Tips
[^r14]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 11, cnt_save STOCK COUNT SAVE
[^r20]: 04_service_definitions/inventory/cnt_get.yaml, whole file
[^r15]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 12, cnt_search STOCK COUNT LIST
[^r19]: 04_service_definitions/inventory/cnt_freeze.yaml, service: cnt_freeze
[^r17]: 04_service_definitions/inventory/cnt_entry.yaml, whole file
[^r21]: 04_service_definitions/inventory/cnt_post.yaml, service: cnt_post
[^r11]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 13, Tips
[^r9]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 14, Questions users ask
[^r13]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 13, INV-CNT-06 STOCK COUNT ENTRY
[^r25]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 6, §5. Stock Count (INV-CNT-06)
