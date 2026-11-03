---
title: "INV-LOT-10 Lot / Serial Entry"
type: "screen"
slug: "screen-inv-lot-10"
summary: "Ledgerline screen for creating, searching, tracing, quarantining, and releasing lot and serial number records."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/lot_get.yaml", "04_service_definitions/inventory/lot_hold.yaml", "04_service_definitions/inventory/lot_release.yaml", "04_service_definitions/inventory/lot_save.yaml", "04_service_definitions/inventory/lot_search.yaml", "04_service_definitions/inventory/lot_trace.yaml", "08_release_notes/RN-7.2.0 Ledgerline Release Notes.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | INV-LOT-10 |
| name | Lot / Serial Entry |
| module | Inventory |
| menu path | Inventory > Lot / |
| introduced | Ledgerline 7.2.0 |
| status | current |

INV-LOT-10 is the Ledgerline inventory screen used to maintain traceable lot records and individual serial numbers across stock holdings at Manchester and Leeds [^r1][^r25]. Introduced in Ledgerline 7.2.0, it is mandatory for serial entry on every battery pack line prior to posting stock receipts, internal transfers, and works order issues [^r12][^r21]. The screen allows warehouse and quality staff to trace complete movement histories from goods receipt to finished bicycle assembly, place batches on quality hold, and release cleared lots back to active inventory [^r3][^r4][^r5][^r23].

| Field | Value |
|---|---|
| Screen Code | INV-LOT-10 |
| Name | Lot / Serial Entry |
| Module | Inventory |
| Navigation | Inventory > Lot / |
| Introduced | Ledgerline 7.2.0 |
| Status | Current |

## Fields

Screen INV-LOT-10 contains the following header and detail fields [^r1][^r10]:

* **ITEM CD (`itm_cd`)**: Mandatory item identifier [^r1][^r10].
* **LOT/SERIAL (`lot_no`)**: Mandatory lot or serial number identifier [^r1][^r10].
* **SUP CD (`sup_cd`)**: Optional supplier code associated with the received lot [^r1][^r10].
* **MFG DT (`mfg_dt`)**: Optional manufacturing date [^r1][^r10].
* **GRN NO (`grn_no`)**: Optional goods received note reference number [^r1][^r10].
* **STATUS (`status`)**: Optional status indicator (e.g. active or quarantined) [^r1][^r5][^r10].
* **REASON (`reason`)**: Optional explanation field, populated with quarantine details when placing a lot on hold and cleared upon release [^r1][^r4][^r9][^r10].
* **COMMENT (`comment`)**: Optional notes field used to record inspector initials, defect details on hold, or clearance inspection notes on release [^r1][^r5][^r7][^r10].

## Keys and services

INV-LOT-10 interacts with the [[services-inv-lot|INV lot services]] group through the following actions and keyboard shortcuts [^r11][^r12]:

* **lot_search (F2 / Enter)**: Read service (`POST /ll72/svc/lot_search`) that queries lot and serial records matching parameters `itm_cd`, `lot_no`, `sup_cd`, and `status` [^r11][^r18][^r19].
* **lot_get (F3)**: Read service (`POST /ll72/svc/lot_get`) that retrieves an existing record using mandatory field `lot_no` alongside `itm_cd` [^r2][^r11][^r13].
* **lot_save (F8)**: Write service (`POST /ll72/svc/lot_save`) that saves lot and serial records and commits status updates [^r8][^r9][^r11][^r17].
* **lot_trace**: Read service (`POST /ll72/svc/lot_trace`) that displays an item's complete movement history linking original goods receipt note through to work order consumption, assembly, and sales order dispatch [^r3][^r8][^r11][^r20][^r23].
* **lot_hold**: Write service (`POST /ll72/svc/lot_hold`) executed via stored procedure `sp_lot_hold` using mandatory `lot_no` and optional `reason` to restrict a lot from work orders and sales orders [^r4][^r8][^r11][^r14][^r15].
* **lot_release (F9)**: Write service (`POST /ll72/svc/lot_release`) used to clear quarantine restrictions and return `status` to active [^r5][^r9][^r11][^r16].

External feeds and warehouse intake files for battery packs must supply the full serial array for each transaction line; missing serials cause the import service to reject the entire batch and write to the interface log [^r24]. Inventory transaction services also validate each serial number against a central register to prevent duplicates and block postings where the entered serial count does not match the line total [^r22].

## Messages

The screen raises the following validation error codes:

* **[[err-itm-0011|ERR-ITM-0011]]**: Raised when an item code is missing or inactive [^r6][^r11].
* **[[err-sup-0030|ERR-SUP-0030]]**: Raised on invalid supplier validation [^r11].
* **[[err-lot-0001|ERR-LOT-0001]]**: Raised when a duplicate lot or serial identifier is submitted [^r6][^r11].
* **[[err-lot-0007|ERR-LOT-0007]]**: Raised when a lot or serial number is not found for the specified item or is not in draft status [^r6][^r11].
* **[[err-lot-0301|ERR-LOT-0301]]**: Raised when a lot is locked by another transaction, has an invalid status transition, or is already on hold [^r6][^r11].

## Versions and conflicts

* **INV-LOT-10 manual coverage**: In force today, MAN-INV-72 v7.2.3 (pages 25–28) provides expanded screen documentation including worked examples for quality holds and quarantine releases, field navigation tips, and error message lists [^r1][^r6][^r7][^r8][^r9]. Earlier, the superseded MAN-INV-72 v7.2.2 (page 12) documented only high-level field descriptions and multi-site tracking across Manchester and Leeds (`superseded`) [^r25][^r26].

## See also

* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[err-lot-0001|ERR-LOT-0001 Duplicate lot or serial identifier]]
* [[err-lot-0007|ERR-LOT-0007 Lot or serial number not found]]
* [[err-lot-0301|ERR-LOT-0301 Lot locked or invalid status transition]]
* [[err-sup-0030|ERR-SUP-0030]]
* [[items-bat|BAT-* items]]
* [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]]
* [[screen-inv-qch-11|INV-QCH-11 Quality Hold Entry]]
* [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]
* [[screen-qa-btt-03|QA-BTT-03 Battery End-Of-Line Test Entry]]
* [[screen-qa-ncr-02|QA-NCR-02 Non-Conformance Report Entry]]
* [[services-inv-lot|INV lot services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 25, §9. Lot / Serial (INV-LOT-10)
[^r25]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 12, Lot / Serial (INV-LOT-10)
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 15, lot_save LOT / SERIAL SAVE
[^r21]: 08_release_notes/RN-7.2.0 Ledgerline Release Notes.pdf, p. 3, Inventory: Lot and serial tracking (INV-LOT-10), used for battery pack serials
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 27, Tracing item movement:
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 27, Placing a lot on hold:
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 27, Releasing a lot from quarantine:
[^r23]: 08_release_notes/RN-7.2.0 Ledgerline Release Notes.pdf, p. 3, Inventory: Lot and serial tracking (INV-LOT-10), used for battery pack serials
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 16, INV-LOT-10 LOT / SERIAL ENTRY
[^r9]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 28, Worked example: Lot / Serial
[^r7]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 28, Tips
[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 16, INV-LOT-10 LOT / SERIAL ENTRY
[^r18]: 04_service_definitions/inventory/lot_search.yaml, screen
[^r19]: 04_service_definitions/inventory/lot_search.yaml, request.fields
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 26, Retrieving an existing record:
[^r13]: 04_service_definitions/inventory/lot_get.yaml, screen
[^r8]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 28, Worked example: Lot / Serial
[^r17]: 04_service_definitions/inventory/lot_save.yaml, service: lot_save
[^r20]: 04_service_definitions/inventory/lot_trace.yaml, whole file
[^r14]: 04_service_definitions/inventory/lot_hold.yaml, whole file
[^r15]: 04_service_definitions/inventory/lot_hold.yaml, request
[^r16]: 04_service_definitions/inventory/lot_release.yaml, lot_release
[^r24]: 08_release_notes/RN-7.2.0 Ledgerline Release Notes.pdf, p. 3, Inventory: Lot and serial tracking (INV-LOT-10), used for battery pack serials
[^r22]: 08_release_notes/RN-7.2.0 Ledgerline Release Notes.pdf, p. 3, Inventory: Lot and serial tracking (INV-LOT-10), used for battery pack serials
[^r6]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 27, Messages
[^r26]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 12, §9. Lot / Serial (INV-LOT-10)
