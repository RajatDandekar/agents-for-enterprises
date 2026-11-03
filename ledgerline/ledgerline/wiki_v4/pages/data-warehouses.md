---
title: "Warehouses"
type: "data-source"
slug: "data-warehouses"
summary: "Master reference of active and closed warehouse codes across Manchester and Leeds operating units in Ledgerline."
audience: "staff"
status: "current"
sources: ["05_master_data/Warehouses.csv", "01_policies/POL-BAT-004 Battery Safety and Handling Policy v1.2.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Dataset | Warehouses.csv |
| Location | 05_master_data/Warehouses.csv |
| Key column | whs_cd |
| Row count | 10 |
| Operating units | NBC-MAN-01, NBC-LDS-01 |
| Status | current |

The warehouse master dataset defines all active and legacy warehouse locations used by Northbridge Cycles in Ledgerline across operating units NBC-MAN-01 and NBC-LDS-01 [^r1][^r2][^r3]. It establishes functional divisions for general stores, quality quarantine holds, finished goods, return-to-vendor stock, and maintenance spares [^r1][^r2][^r3]. Two legacy Manchester codes remain recorded in the master with status CLOSED to prevent historic transaction errors [^r4][^r5].

### What it holds
The file catalogs Northbridge Cycles' 10 warehouse entities across its manufacturing and assembly sites [^r1]. For operating unit NBC-MAN-01 in Manchester, the active warehouses are WH-MAN-STR (Manchester main stores, STORES), WH-MAN-QC (Manchester quality hold, QUALITY), WH-MAN-FG (Manchester finished goods, FG), WH-MAN-RTV (Manchester returns to supplier, RTV), and WH-MAN-MRO (Manchester maintenance spares, MRO) [^r2]. For operating unit NBC-LDS-01 in Leeds, the active warehouses are WH-LDS-STR (Leeds stores, STORES), WH-LDS-QC (Leeds quality hold, QUALITY), and WH-LDS-FG (Leeds finished goods, FG) [^r3].

Closed locations retained in the master comprise WH-MAN-OLD (Ardwick overflow store, closed in 2017) and WH-MAN-BAT (the Ledgerline 6.x Battery store, merged into WH-MAN-STR in 2019) [^r4][^r5]. Under [[pol-bat-004|POL-BAT-004]], WH-MAN-BAT must never be used for receipts of [[items-bat|BAT-* items]], which must instead be booked directly into WH-MAN-STR across bin zones BAT-Z1 to BAT-Z4 [^r4][^r6].

### Columns
The dataset contains four columns [^r1]:
* `whs_cd`: unique warehouse code [^r1].
* `name`: descriptive warehouse name [^r1].
* `ou_cd`: operating unit code (`NBC-MAN-01` or `NBC-LDS-01`) [^r1][^r2][^r3].
* `kind`: functional classification (`STORES`, `QUALITY`, `FG`, `RTV`, `MRO`, or `CLOSED`) [^r1][^r2][^r4].

### How to look up a row
Look up rows in `05_master_data/Warehouses.csv` using the warehouse code column `whs_cd` [^r1].

### Size
The dataset contains 10 rows and 4 columns [^r1].

## See also
* [[items-bat]]
* [[pol-bat-004]]
* [[screen-qa-ncr-02]]

## References

[^r1]: 05_master_data/Warehouses.csv, sheet csv, SHEET csv
[^r2]: 05_master_data/Warehouses.csv, sheet csv, row WH-MAN-STR, ALL 10 ROWS
[^r3]: 05_master_data/Warehouses.csv, sheet csv, row WH-LDS-STR, ALL 10 ROWS
[^r4]: 05_master_data/Warehouses.csv, sheet csv, row WH-MAN-BAT, ALL 10 ROWS
[^r5]: 05_master_data/Warehouses.csv, sheet csv, row WH-MAN-OLD, ALL 10 ROWS
[^r6]: 01_policies/POL-BAT-004 Battery Safety and Handling Policy v1.2.pdf, p. 2, §2. Storage
