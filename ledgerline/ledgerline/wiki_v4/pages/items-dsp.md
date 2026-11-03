---
title: "DSP-* items"
type: "item-family"
slug: "items-dsp"
summary: "Display modules (DSP-01 through DSP-04) used in e-bike sub-assemblies, including stock balances at WH-MAN-STR and lithium coin cell tracking."
audience: "staff"
status: "current"
sources: ["05_master_data/Stock_on_hand_2026-10-26_0900.xlsx", "06_transactions/reports/Item master listing 2026-10 (printed).pdf", "06_transactions/stock_ledger_2026-Q3.csv"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Family code | DSP-* |
| Description | Displays |
| Item count | 4 |
| Primary location | WH-MAN-STR |
| Regulated components | DSP-02 (coin cell / LC 1) |

The DSP-* item family covers display units used in Northbridge Cycles production assemblies, comprising four distinct parts from DSP-01 to DSP-04 [^r1][^r2]. As of 26 October 2026, stock is maintained at warehouse location WH-MAN-STR, supporting ongoing production issues to manufacturing work orders [^r1][^r3]. Item DSP-02 is a colour TFT display equipped with an internal coin cell requiring dangerous goods classification (LC 1), whereas DSP-01, DSP-03, and DSP-04 are non-lithium display assemblies with LC set to 0 [^r2].

## Items and specifications

The family includes four item codes recorded in the master catalogue [^r1][^r2]:
* **DSP-01**: Monochrome LCD display with LC flag set to 0 [^r2][^r4].
* **DSP-02**: Colour TFT display containing an integrated coin cell, flagged with LC 1 [^r2].
* **DSP-03**: Display assembly with LC flag set to 0 [^r1][^r2].
* **DSP-04**: Display assembly with LC flag set to 0 [^r1][^r2].

Detailed configuration data and master parameters for each code are referenced in [[data-item-master|ITEM_MASTER_2026-10-26]] [^r2].

## Inventory and stock movements

Current balances recorded in [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]] at WH-MAN-STR as of 26 October 2026, 09:00 GMT [^r1]:
* **DSP-01**: 1,090 on hand (313 allocated) [^r1].
* **DSP-02**: 158 on hand (10 allocated, 50 on order) [^r1].
* **DSP-03**: 21,992 on hand (180 allocated, 9,000 on order) [^r1].
* **DSP-04**: 664 on hand (91 allocated) [^r1].

Historical stock movement across Q3 2026 recorded in [[data-stock-ledger-2026-q3|stock_ledger_2026-Q3]] reflects progressive consumption by production work orders at WH-MAN-STR [^r3][^r4][^r5][^r6][^r7][^r8][^r9][^r10]:
* **DSP-01**: Opened Q3 on 2026-07-01 at 6,830 units, drew down to 4,691 units by the end of July 2026, and stood at 4,602 units on 2026-08-03 before reaching 1,090 units at the close of September 2026 [^r3][^r4].
* **DSP-03**: Opened on 2026-07-01 with 65,649 units; initial July issues included 648 units to WO/2026/07553 and 518 units to WO/2026/03003 [^r5]. Consecutive issues reduced on-hand balances from 63,339 units to 35,298 units into early September 2026, closing at 21,992 units on 2026-09-30 after an issue to WO/2026/04200 [^r6][^r7].
* **DSP-04**: Opened Q3 on 2026-07-01 with 4,485 units, fell to 3,039 units by 2026-08-04 following an issue of 37 units against WO/2026/04077, and reached an ending balance of 664 units on 2026-09-30 after an issue of 24 units against WO/2026/04110 [^r8][^r9][^r10].

Warehouse material issues and stock maintenance functions are administered through [[services-pur-stk|PUR stk services]].

## See also

* [[data-item-master|ITEM_MASTER_2026-10-26]]
* [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]
* [[data-stock-ledger-2026-q3|stock_ledger_2026-Q3]]
* [[services-pur-stk|PUR stk services]]
* [[items-ctl|CTL-* items]]
* [[items-cbl|CBL-* items]]
* [[items-bat|BAT-* items]]

## References

[^r1]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row DSP-03@WH-MAN-STR, SHEET Stock
[^r2]: 06_transactions/reports/Item master listing 2026-10 (printed).pdf, row DSP-02, p. 2, LEDGERLINE ERP 7.2 REPORT INV-R001 ITEM MASTER LISTING
[^r3]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 4021, sheet csv
[^r4]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 4022, SHEET csv
[^r5]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 4078, SHEET csv
[^r6]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 4082, SHEET csv
[^r7]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 4167, SHEET csv
[^r8]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 4168, SHEET csv
[^r9]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 4201, SHEET csv
[^r10]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 4257, SHEET csv
