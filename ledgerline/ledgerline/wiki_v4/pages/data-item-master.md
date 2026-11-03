---
title: "ITEM_MASTER_2026-10-26"
type: "data-source"
slug: "data-item-master"
summary: "Item master extract covering 2,182 active and inactive part numbers, category lookups, UOM definitions, and Ledgerline 6 legacy cross-references."
audience: "staff"
status: "mixed"
sources: ["05_master_data/ITEM_MASTER_2026-10-26.xlsx", "05_master_data/old/item_master_export_2025-03.csv", "08_release_notes/RN-7.0 Ledgerline Release Notes.pdf", "06_transactions/reports/Item master listing 2026-10 (printed).pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Source file | 05_master_data/ITEM_MASTER_2026-10-26.xlsx |
| Screen | INV-ITM-01 |
| Operating unit | NBC-MAN-01 |
| Extracted by | JFLETCHER |
| Extract date | 2026-10-26 09:00 |
| Item count | 2,182 data rows |

The item master extract is the central catalogue of parts, assemblies, and finished goods for operating unit NBC-MAN-01 generated from [[screen-inv-itm-01|INV-ITM-01]] on 26 October 2026 at 09:00 by JFLETCHER[^r1]. It provides planning, costing, classification, compliance, and legacy code mappings across 2,182 items[^r2]. In addition to master records, it contains reference sheets for valid item categories, units of measure, and migration cross-references from Ledgerline 6[^r2][^r5][^r13][^r25].

## What it holds

The workbook `05_master_data/ITEM_MASTER_2026-10-26.xlsx` holds the complete part records and lookup tables for manufacturing and purchasing operations[^r1][^r2]. Master records assign items to specific buyers, including [[user-eclarke|ECLARKE]], [[user-hnakamura|HNAKAMURA]], [[user-kmensah|KMENSAH]], and [[user-lmoreno|LMORENO]][^r4]. It flags hazardous lithium components using the `cell_safety` attribute, which is controlled exclusively by Quality[^r3]. The system also generates printed overview report INV-R001 (Item Master Listing), which surfaces key planning parameters and flags lithium cells under column LC[^r28][^r29].

## Columns

The workbook contains four sheets[^r2][^r5][^r13][^r25]:

### Sheet: Items
The primary sheet contains 2,182 data rows across 18 columns covering identification, classification, planning, costing, compliance, legacy Ledgerline 6 references, and audit timestamps[^r2]. The corresponding printed Ledgerline ERP 7.2 report INV-R001 presents items using the columns ITEM CD, DESCRIPTION, UOM, CAT, ACT, LC, ROL, ADI, and LEGACY[^r28][^r29].

### Sheet: Categories
The `Categories` sheet contains 2 columns (`category` and `meaning`) across 7 distinct category codes used to classify parts across the business[^r5]:
* `RAW`: Raw material and bought-in major parts[^r6].
* `COMPONENTS`: Components[^r7].
* `SPARES`: Spares and battery packs[^r8].
* `PACKING`: Packing material[^r9].
* `MRO`: Maintenance, repair and operations[^r10].
* `CONSUMABLES`: Consumables[^r11].
* `FINISHED`: Finished e-bikes[^r12].

### Sheet: UOM
The `UOM` sheet holds 11 rows across two columns (`uom_cd` and `meaning`)[^r13]:
* `NOS`: Numbers (pieces)[^r14].
* `KG`: Kilograms[^r15].
* `PR`: Pair[^r16].
* `SET`: Set[^r17].
* `MTR`: Metres[^r18].
* `ROL`: Roll[^r19].
* `BOX`: Box[^r20].
* `BAG`: Bag[^r21].
* `PKT`: Packet[^r22].
* `HRS`: Hours (services)[^r23].
* `EA`: Each (from Ledgerline 6.x, having the same meaning as `NOS`)[^r24].

### Sheet: Legacy code map
The `Legacy code map` sheet contains 1,556 data rows mapping pre-2015 Ledgerline 6 legacy part numbers following the `NBnnnnnn` pattern to Ledgerline 7 item codes established during the 2015 migration and maintained since[^r25][^r26][^r27]. Its columns are `legacy_cd`, `itm_cd`, and `descr`, each containing 1,556 distinct filled entries[^r26]. These legacy codes are also stored in the dedicated legacy code field of the main part master record alongside the general part description[^r27].

## How to look up a row

* In sheet `Items`, look up records using the primary key `itm_cd` (or legacy identifier via the `Legacy code map` sheet)[^r2][^r26].
* In sheet `Categories`, look up category codes using `category`[^r5].
* In sheet `UOM`, look up unit of measure codes using `uom_cd`[^r13].
* In sheet `Legacy code map`, look up previous Ledgerline 6 part numbers using `legacy_cd` or match modern codes via `itm_cd`[^r26].

## Size

* Sheet `Items`: 2,182 data rows across 18 columns[^r2].
* Sheet `Categories`: 7 data rows across 2 columns[^r5].
* Sheet `UOM`: 11 data rows across 2 columns[^r13].
* Sheet `Legacy code map`: 1,556 data rows across 3 columns[^r25][^r26].

## Versions and conflicts

* **Record count and schema expansion**: Today's active master extract (`ITEM_MASTER_2026-10-26.xlsx`) contains 2,182 data rows across 18 columns[^r2]. The superseded March 2025 export (`05_master_data/old/item_master_export_2025-03.csv`) contained 1,650 data rows across 8 columns (`itm_cd`, `descr`, `uom_cd`, `category`, `active`, `cell_safety`, `reorder_lvl`, and `avg_daily_issue`)[^r30]. (Kind: `superseded`)
* **Historic planning parameters**: The superseded March 2025 CSV export recorded active part `BAT-500` with category `SPARES`, `cell_safety` 1, reorder level 2,500, and average daily issue 600[^r31]; refurbished pack `BAT-500-R` with active 1, `cell_safety` 1, reorder level 0, and average daily issue 0[^r32]; and legacy model `BAT-400-OLD` as inactive (`active` 0) with `cell_safety` 1, reorder level 0, and average daily issue 0[^r33]. Readers must refer to the current 26 October 2026 workbook for binding planning parameters[^r1][^r2]. (Kind: `superseded`)

## See also

* [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]]
* [[topic-item-categories|Item Categories]]
* [[data-units-of-measure|Units of measure]]
* [[rn-7-0|RN-7.0 Ledgerline ERP 7.0 Release Notes]]
* [[items-bat|BAT-* items]]
* [[user-eclarke|Emma Clarke (ECLARKE)]]
* [[user-hnakamura|Hana Nakamura (HNAKAMURA)]]
* [[user-kmensah|Kwame Mensah (KMENSAH)]]
* [[user-lmoreno|Luis Moreno (LMORENO)]]

## References

[^r1]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Items, row title rows, title rows
[^r2]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Items, SHEET Items
[^r5]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Categories, SHEET Categories
[^r13]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet UOM, PART 3 of 4 (sheet UOM)
[^r25]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Legacy code map, SHEET Legacy code map
[^r4]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Items, columns
[^r3]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Items, row title rows, title rows
[^r28]: 06_transactions/reports/Item master listing 2026-10 (printed).pdf, p. 1, LEDGERLINE ERP 7.2 REPORT INV-R001 ITEM MASTER LISTING
[^r29]: 06_transactions/reports/Item master listing 2026-10 (printed).pdf, p. 1, LEDGERLINE ERP 7.2 REPORT INV-R001 ITEM MASTER LISTING
[^r6]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Categories, row RAW, SHEET Categories
[^r7]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Categories, row COMPONENTS, SHEET Categories
[^r8]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Categories, row SPARES, SHEET Categories
[^r9]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Categories, row PACKING, SHEET Categories
[^r10]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Categories, row MRO, SHEET Categories
[^r11]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Categories, row CONSUMABLES, SHEET Categories
[^r12]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Categories, row FINISHED, SHEET Categories
[^r14]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet UOM, row NOS, PART 3 of 4 (sheet UOM)
[^r15]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet UOM, row KG, PART 3 of 4 (sheet UOM)
[^r16]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet UOM, row PR, PART 3 of 4 (sheet UOM)
[^r17]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet UOM, row SET, PART 3 of 4 (sheet UOM)
[^r18]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet UOM, row MTR, PART 3 of 4 (sheet UOM)
[^r19]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet UOM, row ROL, PART 3 of 4 (sheet UOM)
[^r20]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet UOM, row BOX, PART 3 of 4 (sheet UOM)
[^r21]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet UOM, row BAG, PART 3 of 4 (sheet UOM)
[^r22]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet UOM, row PKT, PART 3 of 4 (sheet UOM)
[^r23]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet UOM, row HRS, PART 3 of 4 (sheet UOM)
[^r24]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet UOM, row EA, PART 3 of 4 (sheet UOM)
[^r26]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Legacy code map, SHEET Legacy code map
[^r27]: 08_release_notes/RN-7.0 Ledgerline Release Notes.pdf, p. 4, §3. Details
[^r30]: 05_master_data/old/item_master_export_2025-03.csv, sheet csv, SHEET csv
[^r31]: 05_master_data/old/item_master_export_2025-03.csv, sheet csv, row BAT-500, SHEET csv
[^r32]: 05_master_data/old/item_master_export_2025-03.csv, sheet csv, row BAT-500-R, SHEET csv
[^r33]: 05_master_data/old/item_master_export_2025-03.csv, sheet csv, row BAT-400-OLD, SHEET csv
