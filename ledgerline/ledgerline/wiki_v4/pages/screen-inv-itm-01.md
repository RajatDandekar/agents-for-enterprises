---
title: "INV-ITM-01 Item Master Entry"
type: "screen"
slug: "screen-inv-itm-01"
summary: "Ledgerline screen INV-ITM-01 maintains item definitions, units of measure, conversion factors, safety compliance flags, and blocking reason controls."
audience: "staff"
status: "mixed"
sources: ["05_master_data/ITEM_MASTER_2026-10-26.xlsx", "03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/itm_block.yaml", "04_service_definitions/inventory/itm_save.yaml", "04_service_definitions/inventory/itm_uom_conv.yaml", "04_service_definitions/inventory/itm_update.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | INV-ITM-01 |
| Module | Inventory |
| Menu path | Inventory > Item master |
| Save key | F8 |
| Status | Current |

Screen INV-ITM-01 manages item definitions, covering identification, classification, planning, costing, compliance, and legacy code audit data [^r1]. It is accessed through the menu path Inventory > Item master and is powered by the [[services-inv-itm|itm services]] group [^r2]. Marking battery assemblies and cell packs using the safety flag ensures dispatch docks generate mandatory hazardous goods transport paperwork [^r5][^r6].

| Property | Value |
|---|---|
| Screen Code | INV-ITM-01 [^r2] |
| Screen Name | ITEM MASTER ENTRY [^r9] |
| Module | Inventory [^r2] |
| Menu Path | Inventory > Item master [^r2] |
| Primary Key | F8 (itm_save) [^r10] |

## Fields

Screen INV-ITM-01 contains the following master fields:
* `itm_cd` (ITEM CD): Mandatory item code identifier [^r3][^r9].
* `descr` (DESCRIPTION): Item description; designated mandatory in application manual MAN-INV-72, but not marked mandatory in screen guide MAN-SCR-72 [^r3][^r9].
* `uom_cd` (UOM): Mandatory stocking unit of measure [^r3][^r9].
* `category` (CATEGORY): Mandatory classification category [^r3][^r9].
* `cell_safety` (LITHIUM CELL (0/1)): Optional flag where 1 designates battery assemblies, cell packs (such as [[items-bat|BAT-* items]]), or complete bicycles containing cells, while 0 designates mechanical parts, non-electric frames, hardware, and inert components [^r3][^r5][^r9]. Setting this field to 0 or leaving it blank prevents the generation of hazardous goods transport documentation at dispatch [^r6].
* `reorder_lvl` (REORDER LVL): Optional reorder level [^r3][^r9].
* `reason` (REASON): Optional reason text, populated when retiring an obsolete component [^r3][^r8][^r9].

For defining bulk-to-issue ratios, the unit of measure conversion sub-dialog uses three mandatory fields:
* `from_uom` (FROM UOM): Mandatory source unit of measure [^r4][^r7][^r9].
* `to_uom` (TO UOM): Mandatory target unit of measure [^r4][^r7][^r9].
* `factor` (FACTOR): Mandatory floating-point conversion factor [^r4][^r7][^r9].

## Keys and services

* **F8**: Triggers the `itm_save` write service to create and save new item master records [^r10][^r11][^r13].
* **itm_update button**: Invokes write service `itm_update` using fields `itm_cd`, `descr`, `uom_cd`, `category`, and `cell_safety` [^r10][^r11][^r15].
* **itm_block button**: Invokes write service `itm_block` using fields `itm_cd` and `reason` to retire obsolete items from active use [^r8][^r10][^r11][^r12]. Retiring an obsolete part requires clicking `itm_block`, entering a value in `reason`, and clicking `itm_update` [^r8].
* **itm_uom_conv button**: Opens the unit of measure conversion function and invokes write service `itm_uom_conv` using `itm_cd`, `from_uom`, `to_uom`, and `factor` [^r7][^r10][^r11][^r14].

## Messages

The screen raises error codes from [[errors-itm|ERR-ITM error codes]] during validation and service execution:
* [[err-itm-0001|ERR-ITM-0001]]: Triggered if the item code already exists in the Item Master during creation [^r10].
* [[err-itm-0011|ERR-ITM-0011]]: Triggered if the specified item code is missing, inactive, or closed when attempting modifications [^r10].
* [[err-itm-0801|ERR-ITM-0801]]: Triggered when a conversion factor is invalid or a calculation mismatch occurs between units of measure [^r10].

## Versions and conflicts

* **Field requirement for `descr`** (`contradiction`): Current system documentation contains a contradiction regarding whether `descr` is mandatory. MAN-INV-72 v7.2.3 (2025-01-15) lists `descr` as mandatory, whereas MAN-SCR-72 v7.2.3 (2025-01-15) lists `descr` without the mandatory flag, requiring only `itm_cd`, `uom_cd`, and `category` [^r3][^r9].
* **Prior documentation version** (`superseded`): In MAN-INV-72 v7.2.2 (2024-06-10), screen INV-ITM-01 had identical field mandates (`itm_cd`, `descr`, `uom_cd`, `category`), UOM conversion inputs (`from_uom`, `to_uom`, `factor`), and `itm_block` retirement procedures using `reason` [^r16][^r17][^r18]. This manual version was superseded by MAN-INV-72 v7.2.3 on 2025-01-15 [^r2][^r3][^r4][^r8].

## See also

* [[services-inv-itm|INV itm services]]
* [[errors-itm|ERR-ITM error codes]]
* [[err-itm-0001|ERR-ITM-0001: Item code already exists in Item Master]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[err-itm-0801|ERR-ITM-0801: Conversion factor invalid or calculation mismatch between units of measure]]
* [[items-bat|BAT-* items]]

## References

[^r1]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Items, row title rows, title rows
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 40, §13. Item Master (INV-ITM-01)
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 41, Creating a new item master record
[^r6]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 44, Worked example: Item Master
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 15, INV-ITM-01 ITEM MASTER ENTRY
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 15, INV-ITM-01 ITEM MASTER ENTRY
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 40, §13. Item Master (INV-ITM-01)
[^r8]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 44, Worked example: Item Master
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 40, §13. Item Master (INV-ITM-01)
[^r7]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 44, Worked example: Item Master
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 18, itm_save ITEM MASTER SAVE
[^r13]: 04_service_definitions/inventory/itm_save.yaml, service
[^r15]: 04_service_definitions/inventory/itm_update.yaml, service: itm_update
[^r12]: 04_service_definitions/inventory/itm_block.yaml, whole file
[^r14]: 04_service_definitions/inventory/itm_uom_conv.yaml, screen: INV-ITM-01
[^r16]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 18, §13. Item Master (INV-ITM-01)
[^r17]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 18, §13. Item Master (INV-ITM-01)
[^r18]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 19, Step by step
