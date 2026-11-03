---
title: "Units of measure"
type: "data-source"
slug: "data-units-of-measure"
summary: "Reference catalogue of eleven standard Ledgerline units of measure (UOM) used across item master records and service lines."
audience: "staff"
status: "current"
sources: ["05_master_data/ITEM_MASTER_2026-10-26.xlsx", "05_master_data/Units of measure.csv"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Dataset | Units of measure |
| Primary key | uom_cd |
| Format | CSV / XLSX reference sheet |
| Row count | 11 |
| Legacy codes | EA (equivalent to NOS) |

The units of measure reference dataset defines the valid unit codes permitted across Northbridge Cycles' inventory and service lines in Ledgerline ERP [^r1][^r3]. Ledgerline maintains eleven standard units of measure covering discrete parts, bulk materials, packaging, and services [^r1][^r16]. The dataset is embedded as a reference sheet in [[data-item-master|ITEM_MASTER_2026-10-26]] and published as a standalone lookup file [^r1][^r4].

## What it holds

The dataset holds the definitive list of unit codes and their operational meanings used in ERP master data and transaction entry [^r4]. It includes standard countable units like NOS for numbers/pieces, bulk and physical dimensions such as KG, PR, SET, MTR, and ROL, packaging units like BOX, BAG, and PKT, and administrative or legacy codes [^r5][^r6][^r7][^r8][^r9][^r10][^r11][^r12][^r13]. Service items utilize the code HRS, which represents service hours [^r3][^r14][^r18]. The code EA represents "Each" and is retained as a legacy unit code carried over from Ledgerline 6.x that functions as an equivalent to NOS [^r2][^r15][^r17].

## Columns

The dataset contains two columns [^r4]:

* `uom_cd`: The primary unit of measure code (e.g. NOS, KG, HRS, EA) [^r1][^r4].
* `meaning`: The full text description of the unit of measure (e.g. Numbers (pieces), Kilograms, Hours (services), Each) [^r4][^r5][^r6][^r14][^r15].

## How to look up a row

Lookups are performed using the primary key `uom_cd` directly in `05_master_data/Units of measure.csv` or within the `UOM` sheet of `05_master_data/ITEM_MASTER_2026-10-26.xlsx` [^r1][^r4]. Values in transaction screens and entry forms such as [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]] validate against the codes in this table [^r1][^r4].

## Size

The file consists of 11 data rows across 2 columns [^r4].

## See also

* [[data-item-master|ITEM_MASTER_2026-10-26]]
* [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]]
* [[topic-item-categories|Item Categories]]

## References

[^r1]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet UOM, PART 3 of 4 (sheet UOM)
[^r3]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet UOM, row HRS, PART 3 of 4 (sheet UOM)
[^r16]: 05_master_data/Units of measure.csv, sheet csv, SHEET csv
[^r4]: 05_master_data/Units of measure.csv, sheet csv, SHEET csv
[^r5]: 05_master_data/Units of measure.csv, sheet csv, row NOS, SHEET csv
[^r6]: 05_master_data/Units of measure.csv, sheet csv, row KG, SHEET csv
[^r7]: 05_master_data/Units of measure.csv, sheet csv, row PR, SHEET csv
[^r8]: 05_master_data/Units of measure.csv, sheet csv, row SET, SHEET csv
[^r9]: 05_master_data/Units of measure.csv, sheet csv, row MTR, SHEET csv
[^r10]: 05_master_data/Units of measure.csv, sheet csv, row ROL, SHEET csv
[^r11]: 05_master_data/Units of measure.csv, sheet csv, row BOX, SHEET csv
[^r12]: 05_master_data/Units of measure.csv, sheet csv, row BAG, SHEET csv
[^r13]: 05_master_data/Units of measure.csv, sheet csv, row PKT, SHEET csv
[^r14]: 05_master_data/Units of measure.csv, sheet csv, row HRS, SHEET csv
[^r18]: 05_master_data/Units of measure.csv, sheet csv, row HRS, SHEET csv
[^r2]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet UOM, row EA, PART 3 of 4 (sheet UOM)
[^r15]: 05_master_data/Units of measure.csv, sheet csv, row EA, SHEET csv
[^r17]: 05_master_data/Units of measure.csv, sheet csv, row EA, SHEET csv
