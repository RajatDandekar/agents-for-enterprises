---
title: "BEL-* items"
type: "item-family"
slug: "items-bel"
summary: "Bicycle bells including standard bell BEL-STD-01 used across finished bike BOMs, stocked at Manchester Stores, and procured by buyer Emma Clarke."
audience: "staff"
status: "mixed"
sources: ["05_master_data/BOM_master_2026.xlsx", "05_master_data/ITEM_MASTER_2026-10-26.xlsx", "05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx", "05_master_data/Stock_on_hand_2026-10-26_0900.xlsx", "05_master_data/old/item_master_export_2025-03.csv", "06_transactions/PO_extract_2026-01_to_2026-10.xlsx", "06_transactions/reports/Item master listing 2026-10 (printed).pdf", "06_transactions/stock_ledger_2026-Q3.csv", "99_scans/2023_stock_count_sheet_MAN_aisle_B.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Family code | BEL |
| Description | Bicycle bells |
| Buyer | ECLARKE |
| Primary warehouse | WH-MAN-STR |
| Standard item | BEL-STD-01 |
| Unit of measure | NOS |
| Active items | 4 |

The `BEL-*` item family comprises bicycle bells installed across multiple Northbridge Cycles finished bicycle ranges.[^r1][^r5] As of 26 October 2026, the primary production component is `BEL-STD-01`, which is managed by buyer [[user-eclarke|Emma Clarke (ECLARKE)]] and holds an active rate contract with supplier PB-MAN-0017 at £6.80 per unit.[^r6][^r8] Current stock on hand across all bell variants is maintained at warehouse WH-MAN-STR, where `BEL-STD-01` holds 8,000 units against a reorder level of 12,000 units.[^r6][^r9][^r10][^r11][^r12]

| Code | Description | Standard cost | Reorder level | Average daily issue | Lead days | Legacy code | Buyer |
|---|---|---|---|---|---|---|---|
| `BEL-STD-01` | Bell, standard | £6.80 | 12,000 | 3,500 | 21 | NB104373 | [[user-eclarke|ECLARKE]] |

## Bill of materials usage

Standard bell `BEL-STD-01` is specified at BOM line 210 in quantity 1 NOS for finished good parents across multiple bike lines, tracked in the [[data-bom-master|BOM master]]:[^r1][^r2]

* Ancoats models including `FG-ANC-M-RED` (0% scrap), `FG-ANC-M-BLU` (1% scrap), `FG-ANC-XL-RED` (0% scrap), and `FG-ANC-L-SLV` (0% scrap).[^r1][^r2]
* Deansgate models including `FG-DEA-M-GRN` (0% scrap).[^r2]
* Medlock trekking models including `FG-MED-S-BLU` (0.50% scrap) and `FG-MED-XL-RED` (line 210, 1 NOS).[^r3][^r4]
* Irk models including `FG-IRK-S-BLK` and `FG-IRK-L-GRN` (line 210, 1 NOS).[^r4]
* Tame and Roch e-bike models including `FG-TAM-M-BLK`, `FG-TAM-M-RED`, `FG-TAM-L-GRN`, `FG-TAM-L-SLV`, `FG-ROC-S-BLK`, and `FG-ROC-S-SLV` (line 210, 1 NOS).[^r5]

## Stock and warehouse storage

As of 26 October 2026 at 09:00, stock on hand recorded in [[data-stock-on-hand|Stock on hand]] at warehouse WH-MAN-STR is:[^r9][^r10][^r11][^r12]

* `BEL-STD-01`: 8,000 on hand, 0 allocated, 0 on order.[^r9]
* `BEL-STD-02`: 24 on hand, 2 allocated, 0 on order.[^r10]
* `BEL-STD-03`: 273 on hand, 0 allocated, 0 on order.[^r11]
* `BEL-STD-04`: 3,444 on hand, 30 allocated, 0 on order.[^r12]

Historical warehouse count records show `BEL-STD-01` located in bin B-01-02 at Manchester Main Stores, where 1,150 units were counted on 25 March 2023.[^r23]

During Q3 2026, stock ledger movements at WH-MAN-STR showed continuous consumption for assembly work orders:[^r17][^r18][^r19][^r20][^r21][^r22]
* `BEL-STD-01` opened Q3 on 1 July 2026 with 181,687 units, declining to 117,421 units by 4 August 2026 and closing Q3 on 30 September 2026 at 8,000 units.[^r17][^r18]
* `BEL-STD-04` opened Q3 on 1 July 2026 with 9,213 units, dropping to 9,032 units on 2 July 2026 after issues to work orders WO/2026/05952 (-49 units) and WO/2026/06310 (-39 units), continuing downward through July and August to 5,036 units, then from 4,958 units on 4 September 2026 to 3,444 units on 30 September 2026.[^r19][^r20][^r21][^r22]

## Purchasing and contracts

Standard bell `BEL-STD-01` is covered under a 2026-27 rate contract in [[data-rate-contracts|Rate Contracts 2025-26 and 2026-27]] held by supplier PB-MAN-0017 at £6.80 per unit, valid from 2026-04-01 to 2027-03-31.[^r8]

Purchase orders placed in 2026 include:
* `PO/2026/00257` (February 2026): 600 units of `BEL-STD-03` at £27.30 per unit from supplier UCP-UTR-0971 under cost centre [[cc-prd-02|PRD-02]].[^r13]
* `PO/2026/00715` (29 May 2026): 52,500 units of `BEL-STD-01` at £6.80 per unit from PB-MAN-0017.[^r14]
* `PO/2026/01131` (September 2026): 30,000 units of `BEL-STD-01` at £6.80 per unit from PB-MAN-0017, totalling £244,800.00 gross.[^r15]

## Versions and conflicts

* **Superseded item master export**: The current active [[data-item-master|ITEM_MASTER_2026-10-26]] and report INV-R001 record `BEL-STD-01` as an active standard bell component with standard cost £6.80, reorder level 12,000, average daily issue 3,500, lead days 21, and legacy code NB104373.[^r6][^r7][^r16] In the superseded March 2025 item master export (`05_master_data/old/item_master_export_2025-03.csv`), `BEL-STD-01` had category COMPONENTS, active flag 1, and cell_safety flag 0 (`superseded`).[^r24]

## See also

* [[data-item-master|ITEM_MASTER_2026-10-26]]
* [[data-bom-master|BOM_master_2026]]
* [[data-rate-contracts|Rate Contracts 2025-26 and 2026-27]]
* [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]
* [[items-fg|FG-* items]]
* [[user-eclarke|Emma Clarke (ECLARKE)]]
* [[cc-prd-02|PRD-02 Deansgate step-through line]]

## References

[^r1]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-M-RED
[^r5]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row 3252, SHEET BOM
[^r6]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Items, row BEL-STD-01, first 5 rows, then the 10 rows whose key appears in the narrative documents
[^r8]: 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx, sheet 2026-27, row PB-MAN-0017/BEL-STD-01/2026-04-01, SHEET 2026-27
[^r9]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BEL-STD-01@WH-MAN-STR, SHEET Stock
[^r10]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BEL-STD-02@WH-MAN-STR, SHEET Stock
[^r11]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BEL-STD-03@WH-MAN-STR, SHEET Stock
[^r12]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BEL-STD-04@WH-MAN-STR, SHEET Stock
[^r2]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-L-SLV
[^r3]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-MED-S-BLU
[^r4]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-MED-XL-RED, SHEET BOM
[^r23]: 99_scans/2023_stock_count_sheet_MAN_aisle_B.pdf, p. 1, ANNUAL STOCK COUNT 2023 MANCHESTER MAIN STORES
[^r17]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1048, SHEET csv
[^r18]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1137
[^r19]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1138
[^r20]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1141
[^r21]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1142, SHEET csv
[^r22]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1202, csv
[^r13]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-02, row PO/2026/00257, SHEET 2026-02
[^r14]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-05, row PO/2026/00715, SHEET 2026-05
[^r15]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-09, row PO/2026/01131, ALL 50 ROWS
[^r7]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Legacy code map, row NB104373, SHEET Legacy code map
[^r16]: 06_transactions/reports/Item master listing 2026-10 (printed).pdf, row BEL-STD-01, p. 1, LEDGERLINE ERP 7.2 REPORT INV-R001 ITEM MASTER LISTING
[^r24]: 05_master_data/old/item_master_export_2025-03.csv, sheet csv, row BEL-STD-01, SHEET csv
