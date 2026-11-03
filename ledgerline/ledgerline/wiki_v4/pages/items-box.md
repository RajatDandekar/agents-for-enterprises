---
title: "BOX-* items"
type: "item-family"
slug: "items-box"
summary: "Item family for packing cartons including bike shipping, battery, and parts boxes across assembly lines."
audience: "staff"
status: "mixed"
sources: ["05_master_data/BOM_master_2026.xlsx", "05_master_data/ITEM_MASTER_2026-10-26.xlsx", "05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx", "05_master_data/Stock_on_hand_2026-10-26_0900.xlsx", "05_master_data/old/item_master_export_2025-03.csv", "06_transactions/PO_extract_2026-01_to_2026-10.xlsx", "06_transactions/reports/Item master listing 2026-10 (printed).pdf", "06_transactions/reports/PO register 2026-03 (printed).pdf", "06_transactions/stock_ledger_2026-Q3.csv", "99_scans/2023_stock_count_sheet_MAN_aisle_B.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code prefix | BOX-* |
| Category | PACKING |
| Buyer | ECLARKE |
| Primary store | WH-MAN-STR |
| Standard items | BOX-BIKE-01, BOX-BIKE-02, BOX-BIKE-03, BOX-BAT-01, BOX-BAT-02, BOX-PRT-01, BOX-PRT-02 |

The BOX-* item family covers rigid packaging cartons used for shipping complete bicycles, battery packs, and component parts [^r4][^r10][^r11]. Primary high-volume carton BOX-BIKE-01 is standard packaging across finished goods lines, with 60,000 units on hand at Manchester stores as of 26 October 2026 [^r1][^r2][^r7]. The items fall under category PACKING and are managed by buyer [[user-eclarke|Emma Clarke]] [^r4].

## Family items and specifications

The master carton for finished bicycles is BOX-BIKE-01 (legacy code NB104444), which has a standard cost of £21.50, a lead time of 21 days, a reorder level of 20,000 units, and an average daily issue of 6,000 units [^r4][^r5][^r13]. It is supplied under a 2026-27 rate contract by supplier IP-MAN-0055 at £21.50 per unit through 31 March 2027 [^r6]. Other packaging items in the family include secondary bicycle boxes BOX-BIKE-02 and BOX-BIKE-03, battery cartons BOX-BAT-01 and BOX-BAT-02, and component packaging BOX-PRT-01 and BOX-PRT-02 [^r8][^r9][^r10][^r11].

## Bill of materials allocation

Item BOX-BIKE-01 is specified on BOM line 350 with a standard quantity of 1 NOS across multiple finished bicycle models [^r1][^r2][^r3]. Recorded assembly allocations include [[items-fg|finished goods]] lines for Deansgate models FG-DEA-M-RED, FG-DEA-XL-GRN, and FG-DEA-XL-BLU; Medlock models FG-MED-S-BLK, FG-MED-M-BLU, and FG-MED-L-RED; Irk models FG-IRK-S-SLV, FG-IRK-L-RED, and FG-IRK-L-BLU; Tame models FG-TAM-M-GRN, FG-TAM-L-GRN, and FG-TAM-XL-RED; and Rochdale model FG-ROC-M-RED [^r1][^r2][^r3].

## Stock levels and inventory movements

As of 09:00 on 26 October 2026, recorded warehouse stock at WH-MAN-STR across the family stands at:
* BOX-BIKE-01: 60,000 units on hand, 0 allocated, 0 on order [^r7].
* BOX-BIKE-02: 11 units on hand, 0 allocated [^r8].
* BOX-BIKE-03: 139 units on hand, 0 allocated [^r9].
* BOX-BAT-01: 214 units on hand [^r10].
* BOX-BAT-02: 735 units on hand [^r10].
* BOX-PRT-01: 512 units on hand [^r11].
* BOX-PRT-02: 817 units on hand [^r11].

Carton BOX-BIKE-01 opened Q3 2026 with 333,025 units at WH-MAN-STR on 1 July 2026 and dropped to 315,014 units on 9 July 2026 [^r15]. Issues continued through July, August, and September 2026, reducing stock to 117,523 units on 10 September 2026, until a final issue of 4,089 units to work order WO/2026/05477 on 30 September 2026 closed the ledger at 60,000 units [^r16][^r17]. An earlier count at Manchester Main Stores on 25 March 2023 recorded 3,600 units of BOX-BIKE-01 in bin B-02-01 [^r18].

## Purchasing history

High-volume replenishment includes order PO/2026/01167 for 40,000 units of BOX-BIKE-01 placed with IP-MAN-0055 at £21.50 under cost centre [[cc-prd-07|PRD-07]] for delivery to WH-MAN-STR [^r12]. Battery box replenishment includes purchase order PO/2026/00389, issued on 24 March 2026 to Calder Cartons (CC-HUL-0411) for 400 units of BOX-BAT-02 at £18.89 (£9,067.20 gross), charged to cost centre [[cc-prd-02|PRD-02]] [^r14].

## Versions and conflicts

* **Superseded item master metadata**: Today's active master record defines BOX-BIKE-01 with category PACKING, standard cost £21.50, lead days 21, and buyer ECLARKE [^r4]. The superseded export from March 2025 tracked BOX-BIKE-01 under category PACKING with an active flag of 1, a cell safety flag of 0, reorder level 20,000, and average daily issue 6,000, but predates the full current procurement profile [^r19].

## See also

* [[data-item-master|ITEM_MASTER_2026-10-26]]
* [[data-bom-master|BOM_master_2026]]
* [[data-rate-contracts|Rate Contracts 2025-26 and 2026-27]]
* [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]
* [[data-po-extract-2026|PO_extract_2026-01_to_2026-10]]
* [[items-pkg|PKG-* items]]
* [[items-bat|BAT-* items]]
* [[cc-prd-07|PRD-07 Spring launch run]]
* [[cc-prd-02|PRD-02 Deansgate step-through line]]
* [[user-eclarke|Emma Clarke (ECLARKE)]]

## References

[^r4]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Items, row BOX-BIKE-01, first 5 rows, then the 10 rows whose key appears in the narrative documents
[^r10]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BOX-BAT-01@WH-MAN-STR, SHEET Stock
[^r11]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BOX-PRT-01@WH-MAN-STR, SHEET Stock
[^r1]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-DEA-M-RED
[^r2]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-IRK-S-SLV, SHEET BOM
[^r7]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BOX-BIKE-01@WH-MAN-STR, SHEET Stock
[^r5]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Legacy code map, row NB104444, SHEET Legacy code map
[^r13]: 06_transactions/reports/Item master listing 2026-10 (printed).pdf, row BOX-BIKE-01, p. 1, LEDGERLINE ERP 7.2 REPORT INV-R001 ITEM MASTER LISTING
[^r6]: 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx, sheet 2026-27, row IP-MAN-0055/BOX-BIKE-01/2026-04-01, SHEET 2026-27
[^r8]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BOX-BIKE-02@WH-MAN-STR, SHEET Stock
[^r9]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BOX-BIKE-03@WH-MAN-STR, SHEET Stock
[^r3]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row 3760, SHEET BOM
[^r15]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1314
[^r16]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2026-07-09
[^r17]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1398
[^r18]: 99_scans/2023_stock_count_sheet_MAN_aisle_B.pdf, p. 1, ANNUAL STOCK COUNT 2023 MANCHESTER MAIN STORES
[^r12]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-10, row PO/2026/01167, SHEET 2026-10
[^r14]: 06_transactions/reports/PO register 2026-03 (printed).pdf, p. 3, REPORT PUR-R010
[^r19]: 05_master_data/old/item_master_export_2025-03.csv, sheet csv, row BOX-BIKE-01, SHEET csv
