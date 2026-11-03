---
title: "BRK-* items"
type: "item-family"
slug: "items-brk"
summary: "Braking components family covering disc pads, calipers, rotors, levers, and hoses used across e-bike production models."
audience: "staff"
status: "mixed"
sources: ["05_master_data/BOM_master_2026.xlsx", "05_master_data/ITEM_MASTER_2026-10-26.xlsx", "05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx", "05_master_data/Stock_on_hand_2026-10-26_0900.xlsx", "05_master_data/old/item_master_export_2025-03.csv", "06_transactions/PO_extract_2026-01_to_2026-10.xlsx", "06_transactions/reports/Item master listing 2026-10 (printed).pdf", "06_transactions/reports/PO register 2026-04 (printed).pdf", "06_transactions/stock_ledger_2026-Q3.csv", "99_scans/2023_stock_count_sheet_MAN_aisle_B.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | BRK-* |
| family | Braking components |
| buyer | ECLARKE |
| valuation_standard | £9.40 (BRK-PAD-01) |
| hs_code | 8714.99 (BRK-PAD-01) |
| primary_supplier | PB-MAN-0017 |
| status | current |

The `BRK-*` item family encompasses braking system components, including disc brake pad pairs, calipers, rotors, levers, and hydraulic hoses across Northbridge Cycles production models. Disc brake pad pair `BRK-PAD-01` serves as a core assembly component scheduled at line 110 across multiple e-bike frames. Procurement is overseen by buyer [[user-eclarke|ECLARKE]], backed by an active rate contract with Pennine Brakes (`PB-MAN-0017`) through 31 March 2027.

| Field | Value |
|---|---|
| Family code | `BRK-*` |
| Primary buyer | [[user-eclarke|ECLARKE]] |
| Key supplier | `PB-MAN-0017` |
| Lead days (BRK-PAD-01) | 21 |
| Reorder level (BRK-PAD-01) | 12,000 |
| Average daily issue (BRK-PAD-01) | 3,500 |

## Components and bill of materials usage

Component `BRK-PAD-01` (legacy code `NB104402`) is assigned to line 110 of bill of materials assemblies for parent frames such as `FG-ANC-L-BLU` with a quantity of 2 NOS and 2% scrap [^r1][^r5][^r6][^r21]. It is also scheduled at line 110 at a quantity of 2 NOS on models `FG-DEA-XL-BLU`, `FG-MED-M-SLV`, and `FG-MED-L-BLK` [^r2]. Additional line 110 schedules specify 2 NOS on models `FG-MED-XL-SLV`, `FG-IRK-S-BLK`, `FG-IRK-S-BLU`, `FG-IRK-L-BLK`, and `FG-IRK-L-BLU` [^r3]. On assembly `FG-TAM-M-GRN`, `BRK-PAD-01` is configured at line 110 with a quantity of 2 NOS and 0% scrap [^r4]. In the March 2023 stock count, `BRK-PAD-01` was recorded in bin B-01-01 at Manchester Main Stores with a physical count of 2,400 units [^r51].

## Master data and pricing

Standard cost for `BRK-PAD-01` is £9.40, with HS code 8714.99 and assigned buyer [[user-eclarke|ECLARKE]] [^r5]. Supplier `PB-MAN-0017` holds a 2026–27 rate contract for `BRK-PAD-01` at £9.40 per unit valid from 1 April 2026 to 31 March 2027 [^r7].

Purchase orders raised for the family include:
* `PO/2026/00515` placed on 20 April 2026 by [[user-hnakamura|HNAKAMURA]] with `PB-MAN-0017` for 70,000 units of `BRK-PAD-01` at £9.40 (£789,600.00 gross under VAT20-UK) for Leeds assembly cost centre [[cc-lds-prd-01|LDS-PRD-01]] [^r18][^r22].
* `PO/2026/00537` placed in April 2026 for 9,000 units of caliper `BRK-CAL-02` from `BB-NEW-1113` at a unit rate of £55.43 [^r19].
* `PO/2026/00556` placed on 27 April 2026 for 7,500 units of `BRK-PAD-02` at a rate of £54.01 [^r20].
* `PO/2026/00557` placed on 27 April 2026 by [[user-lmoreno|LMORENO]] with `PB-MAN-0017` for 35,000 units of `BRK-PAD-01` at £9.40 (£394,800.00 gross under VAT20-UK) for cost centre [[cc-prd-05|PRD-05]] [^r20][^r23].

## Stock levels and inventory movements

As of 26 October 2026 at 09:00, stock on hand across warehouses stands at:
* `BRK-PAD-01`: 26,000 units on hand, 0 allocated, and 0 on order at `WH-MAN-STR` [^r8].
* `BRK-PAD-02`: 2,933 units on hand and 369 allocated at `WH-MAN-STR`, with 876 units on hand at `WH-LDS-STR` [^r11].
* `BRK-ROT-180`: 21,130 units on hand and 280 allocated at `WH-MAN-STR` [^r9].
* `BRK-ROT-160`: 4,368 units on hand and 1,405 allocated at `WH-MAN-STR` [^r9].
* `BRK-CAL-02`: 13,339 units on hand and 1,575 allocated at `WH-MAN-STR` [^r10].
* `BRK-CAL-03`: 351 units on hand and 30 allocated at `WH-MAN-STR`, with 317 units on hand at `WH-LDS-STR` [^r10].
* `BRK-LEV-01`: 126 units on hand, 20 allocated, and 0 on order at `WH-MAN-STR` [^r12].
* `BRK-LEV-02`: 18 units on hand, 0 allocated, and 10 on order at `WH-MAN-STR` [^r13].
* `BRK-LEV-03`: 266 units on hand, 0 allocated, and 100 on order at `WH-MAN-STR`, plus 75 units on hand at `WH-LDS-STR` [^r14].
* `BRK-HOS-160`: 374 units on hand, 22 allocated, and 0 on order at `WH-MAN-STR` [^r15].
* `BRK-HOS-180`: 9 units on hand, 1 allocated, and 0 on order at `WH-MAN-STR` [^r16].
* `BRK-HOS-203`: 9,015 units on hand, 26 allocated, and 2,500 on order at `WH-MAN-STR` [^r17].

During Q3 2026 at `WH-MAN-STR`, `BRK-PAD-01` had an opening balance of 96,707 units on 1 July 2026, received two bulk receipts of 52,500 units under GRN/2026/29644 on 20 July 2026 and GRN/2026/29715 on 1 August 2026, moved from 71,742 to 67,868 units between 15 July and 8 September 2026 through continuous issues, and closed September at 26,000 units after issuing 2,053 units to WO/2026/05114 [^r35][^r36][^r37][^r38]. 

`BRK-PAD-02` opened Q3 at 14,697 units on 1 July 2026, falling to 9,728 units by 6 August 2026, and further reducing from 9,542 units on 7 August to 2,933 units by 30 September 2026 [^r39][^r40]. `BRK-PAD-03` held 4,139 units on 1 July 2026, declining to 3,784 on 10 July, 1,163 on 15 September, and closing at 491 units on 30 September 2026 following an issue of 48 units to WO/2026/04369 [^r41][^r42][^r43].

`BRK-CAL-02` held an opening balance of 39,779 units on 1 July 2026, received 4,500 units on 3 July 2026 under GRN/2026/29535, stood at 23,800 units on 10 August 2026, and received 13,500 units on 23 September 2026 via GRN/2026/29953 to raise stock from 3,929 to 17,429 units [^r24][^r25][^r26][^r27]. `BRK-CAL-03` opened Q3 at 3,529 units, received receipts of 800 units each on 8 August (GRN/2026/29752), 17 August (GRN/2026/29808), and 25 August (GRN/2026/29848), dropped to 1,852 units on 3 September 2026, and closed 30 September 2026 at 351 units [^r28][^r29][^r30][^r31].

`BRK-HOS-203` opened Q3 at 20,156 units, declined to 15,185 units by 10 August 2026, and reached 9,015 units on 30 September 2026 [^r32][^r33][^r34]. `BRK-ROT-160` opened at 44,764 units, moved to 24,154 units on 13 August 2026, and reached 23,597 units on 14 August 2026 [^r44][^r45]. `BRK-ROT-180` opened Q3 at 53,831 units on 1 July 2026, fell to 44,395 units by 17 July, received 13,500 units on 18 August 2026 via GRN/2026/29816, fell to 29,011 units on 15 September and 27,969 units on 16 September, and concluded September at 21,130 units [^r46][^r47][^r48][^r49][^r50].

## Versions and conflicts

* **Superseded item master export**: Today's master data records `BRK-PAD-01` under item family `BRK-*` with lead days 21, reorder level 12,000, average daily issue 3,500, standard cost £9.40, and buyer [[user-eclarke|ECLARKE]] [^r5][^r21]. The older March 2025 item master export catalogued `BRK-PAD-01` under category `COMPONENTS` with `active` flag 1 and `cell_safety` flag 0 [^r52]. Kind: `superseded`.

## See also

* [[data-item-master|ITEM_MASTER_2026-10-26]]
* [[data-bom-master|BOM_master_2026]]
* [[data-rate-contracts|Rate Contracts 2025-26 and 2026-27]]
* [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]
* [[data-po-extract-2026|PO_extract_2026-01_to_2026-10]]
* [[user-eclarke|Emma Clarke (ECLARKE)]]
* [[user-hnakamura|Hana Nakamura (HNAKAMURA)]]
* [[user-lmoreno|Luis Moreno (LMORENO)]]
* [[cc-lds-prd-01|LDS-PRD-01 Leeds assembly]]
* [[cc-prd-05|PRD-05 City e-bike line, regular production]]
* [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]]

## References

[^r1]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-L-BLU
[^r5]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Items, row BRK-PAD-01, first 5 rows, then the 10 rows whose key appears in the narrative documents
[^r6]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Legacy code map, row NB104402, SHEET Legacy code map
[^r21]: 06_transactions/reports/Item master listing 2026-10 (printed).pdf, row BRK-PAD-01, p. 1, LEDGERLINE ERP 7.2 REPORT INV-R001 ITEM MASTER LISTING
[^r2]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-DEA-XL-BLU
[^r3]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-MED-XL-SLV, SHEET BOM
[^r4]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row 3280, SHEET BOM
[^r51]: 99_scans/2023_stock_count_sheet_MAN_aisle_B.pdf, p. 1, ANNUAL STOCK COUNT 2023 MANCHESTER MAIN STORES
[^r7]: 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx, sheet 2026-27, row PB-MAN-0017/BRK-PAD-01/2026-04-01, SHEET 2026-27
[^r18]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-04, row PO/2026/00515, SHEET 2026-04
[^r22]: 06_transactions/reports/PO register 2026-04 (printed).pdf, row PO/2026/00515, p. 3, PUR-R010 PURCHASE ORDER REGISTER
[^r19]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-04, row PO/2026/00537, SHEET 2026-04
[^r20]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-04, row PO/2026/00557, SHEET 2026-04
[^r23]: 06_transactions/reports/PO register 2026-04 (printed).pdf, row PO/2026/00557, p. 4, PUR-R010 PURCHASE ORDER REGISTER
[^r8]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BRK-PAD-01@WH-MAN-STR, SHEET Stock
[^r11]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BRK-PAD-02@WH-MAN-STR, SHEET Stock
[^r9]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BRK-ROT-180@WH-MAN-STR, SHEET Stock
[^r10]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BRK-CAL-02@WH-MAN-STR, SHEET Stock
[^r12]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BRK-LEV-01@WH-MAN-STR, SHEET Stock
[^r13]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BRK-LEV-02@WH-MAN-STR, SHEET Stock
[^r14]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BRK-LEV-03@WH-MAN-STR, SHEET Stock
[^r15]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BRK-HOS-160@WH-MAN-STR, SHEET Stock
[^r16]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BRK-HOS-180@WH-MAN-STR, SHEET Stock
[^r17]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BRK-HOS-203@WH-MAN-STR, SHEET Stock
[^r35]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row row 1668, SHEET csv
[^r36]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1686, csv
[^r37]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1682, csv
[^r38]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1763, SHEET csv
[^r39]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1764, SHEET csv
[^r40]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1802
[^r41]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1861
[^r42]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row row 1862, key 2026-07-13, csv
[^r43]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1937, SHEET csv
[^r24]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1399
[^r25]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1402
[^r26]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1441
[^r27]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1487, SHEET csv
[^r28]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1497, SHEET csv
[^r29]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1542, csv
[^r30]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1561, csv
[^r31]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1585, SHEET csv
[^r32]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1586, SHEET csv
[^r33]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1621, SHEET csv
[^r34]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row row 1667, SHEET csv
[^r44]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1981, SHEET csv
[^r45]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2026-08-14, csv
[^r46]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2026-07-17, csv
[^r47]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2071
[^r48]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2101
[^r49]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2103, csv
[^r50]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2117, csv
[^r52]: 05_master_data/old/item_master_export_2025-03.csv, sheet csv, row BRK-PAD-01, SHEET csv
