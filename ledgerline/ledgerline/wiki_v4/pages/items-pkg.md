---
title: "PKG-* items"
type: "item-family"
slug: "items-pkg"
summary: "Packaging family (PKG-*) covering protective materials, tapes, pallets, and required UN lithium battery handling labels across assembly BOMs."
audience: "staff"
status: "mixed"
sources: ["05_master_data/BOM_master_2026.xlsx", "05_master_data/ITEM_MASTER_2026-10-26.xlsx", "05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx", "05_master_data/Stock_on_hand_2026-10-26_0900.xlsx", "05_master_data/old/item_master_export_2025-03.csv", "01_policies/POL-BAT-004 Battery Safety and Handling Policy v1.2.pdf", "11_training/QRC-07 Lithium battery labels.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code_prefix | PKG- |
| description | Packaging materials and handling labels |
| buyer | HNAKAMURA |
| category | PACKING |
| status | current |

The `PKG-*` item family encompasses packaging supplies, protective materials, and mandatory compliance labels used in warehouse handling and finished bicycle assembly pack lines [^r1][^r10][^r13]. The primary active compliance item in this family is `PKG-LBL-UN`, the lithium battery handling label affixed to all parcels containing battery packs as mandated by transport safety rules [^r8][^r14][^r15]. As of 26 October 2026, stock for packaging items is held at warehouse `WH-MAN-STR`, with procurement managed under buyer [[user-hnakamura|HNAKAMURA]] [^r8][^r10][^r12].

## Packaging items and stock

According to [[data-item-master|ITEM_MASTER_2026-10-26]], `PKG-LBL-UN` is defined as a lithium battery handling label with a standard cost of £6.44, a reorder level of 560, an average daily issue of 40, lead days of 56, and buyer [[user-hnakamura|HNAKAMURA]] [^r8]. Supplier `HP-WIG-0928` holds rate contract `RC/2025/390` in [[data-rate-contracts|Rate Contracts 2025-26 and 2026-27]] for `PKG-LBL-UN` at £6.44 per unit, valid from 2026-04-01 to 2027-03-31 [^r9].

Stock balances recorded in [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]] at `WH-MAN-STR` as of 26 October 2026 09:00 are:
* `PKG-LBL-UN`: 1,166 units on hand [^r12].
* `PKG-FOAM-01`: 27,029 units on hand [^r10].
* `PKG-TAPE-01`: 80 units on hand, with 50 units on order [^r11].
* `PKG-CRN-01`: 248 units on hand, with 200 units on order [^r13].
* `PKG-WRAP-01`: 34 units on hand [^r13].
* `PKG-PAL-01`: 32 units on hand [^r13].

## Bill of materials usage

In [[data-bom-master|BOM_master_2026]], `PKG-LBL-UN` is utilised across packaging lines 360, 370, and 380 for assembly of finished goods [[items-fg|FG-*]] [^r1][^r4][^r6]. The label appears in quantities ranging between 1 and 8 units per assembly [^r5]. For example, parent `FG-DEA-S-SLV` lists `PKG-LBL-UN` on three consecutive lines: line 360 (quantity 4 NOS, 0.50% scrap), line 370 (quantity 1 NOS, 1% scrap), and line 380 (quantity 3 NOS, 0% scrap) [^r2]. Across Sprint finished goods, `PKG-LBL-UN` is specified at line 370 or line 380 in quantities between 3 and 7 NOS [^r7].

## Transport and labelling requirements

Under [[pol-bat-004|POL-BAT-004]], `PKG-LBL-UN` is the lithium battery handling label that must be affixed flat and clearly visible to every parcel containing a battery pack [^r14]. Quick reference guide QRC-07 specifies that `PKG-LBL-UN` must be marked with either designation UN3480 or UN3481 depending on the shipment packaging [^r15].

## Versions and conflicts

* **Unit of measure discrepancy in BOM master**: Today's BOM master specifies `PKG-LBL-UN` with unit of measure `NOS` on certain parent models and lines (such as `FG-DEA-L-SLV` line 360, `FG-DEA-L-RED` lines 370 and 380, and `FG-MED-S-SLV` line 380), but specifies `ROL` on others (such as `FG-DEA-M-RED` line 360 and `FG-DEA-L-BLU` line 380) (`contradiction`: [[data-bom-master|BOM_master_2026]], sheet BOM) [^r1][^r3][^r4][^r5][^r6].
* **Historical item master attributes**: In the superseded March 2025 export, `PKG-LBL-UN` ('Label, lithium battery handling') was recorded with category `PACKING`, active flag 1, cell_safety flag 0, reorder level 560, and average daily issue 40 (`superseded`: `05_master_data/old/item_master_export_2025-03.csv`) [^r16].

## See also

* [[data-bom-master|BOM_master_2026]]
* [[data-item-master|ITEM_MASTER_2026-10-26]]
* [[data-rate-contracts|Rate Contracts 2025-26 and 2026-27]]
* [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]
* [[items-bat|BAT-* items]]
* [[items-fg|FG-* items]]
* [[pol-bat-004|POL-BAT-004 Battery Safety and Handling Policy]]
* [[user-hnakamura|Hana Nakamura (HNAKAMURA)]]

## References

[^r1]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-M-RED
[^r10]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row PKG-FOAM-01@WH-MAN-STR, SHEET Stock
[^r13]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row PKG-CRN-01@WH-MAN-STR, SHEET Stock
[^r8]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Items, row PKG-LBL-UN, first 5 rows, then the 10 rows whose key appears in the narrative documents
[^r14]: 01_policies/POL-BAT-004 Battery Safety and Handling Policy v1.2.pdf, p. 4, §4. Transport
[^r15]: 11_training/QRC-07 Lithium battery labels.pdf, p. 1, Selecting the correct designation
[^r12]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row PKG-LBL-UN@WH-MAN-STR, SHEET Stock
[^r9]: 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx, sheet 2026-27, row HP-WIG-0928/PKG-LBL-UN/2026-04-01, SHEET 2026-27
[^r11]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row PKG-TAPE-01@WH-MAN-STR, SHEET Stock
[^r4]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-IRK-S-GRN, SHEET BOM
[^r6]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-SPR-M-RED, SHEET BOM
[^r5]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row 4142, SHEET BOM
[^r2]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-DEA-S-SLV
[^r7]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row 5055, SHEET BOM
[^r3]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-DEA-M-RED
[^r16]: 05_master_data/old/item_master_export_2025-03.csv, sheet csv, row PKG-LBL-UN, SHEET csv
