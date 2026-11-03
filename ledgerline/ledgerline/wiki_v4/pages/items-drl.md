---
title: "DRL-* items"
type: "item-family"
slug: "items-drl"
summary: "Master inventory balances and Q3 2026 consumption movements for the DRL-* derailleur component family across Manchester and Leeds warehouses."
audience: "staff"
status: "current"
sources: ["05_master_data/Stock_on_hand_2026-10-26_0900.xlsx", "06_transactions/stock_ledger_2026-Q3.csv"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Family code | DRL-* |
| Description | Rear derailleurs (8-speed to 11-speed) |
| Stock tracking | [[data-stock-on-hand|Stock on hand]] & [[data-stock-ledger-2026-q3|Stock ledger]] |
| Primary locations | WH-MAN-STR, WH-LDS-STR |
| Status | Current |

The DRL-* item family encompasses Northbridge Cycles' rear derailleur components across multiple speed configurations, serving ongoing assembly and production requirements. Inventory is primarily stocked at the central store WH-MAN-STR, with secondary holdings for select variants maintained at WH-LDS-STR. Stock balances across all models reflect active drawdowns from work order issues through the third quarter of 2026, with zero quantities on order as of 26 October 2026.

| Field | Value |
|---|---|
| Family code | DRL-* |
| Description | Rear derailleurs (8-speed to 11-speed) |
| Stock tracking | [[data-stock-on-hand|Stock on hand]] & [[data-stock-ledger-2026-q3|Stock ledger]] |
| Primary locations | WH-MAN-STR, WH-LDS-STR |
| Status | Current |

## Stock on hand

As of 09:00 on 26 October 2026, stock levels recorded in [[data-stock-on-hand|Stock on hand]] are as follows:

* **DRL-8S**: WH-MAN-STR holds 633 units on hand, 69 allocated, and 0 on order [^r1].
* **DRL-9S**: WH-MAN-STR holds 1,338 units on hand, 271 allocated, and 0 on order, while WH-LDS-STR holds 237 units on hand, 0 allocated, and 0 on order [^r2].
* **DRL-10S**: WH-MAN-STR holds 3,837 units on hand, 281 allocated, and 0 on order, while WH-LDS-STR holds 324 units on hand, 0 allocated, and 0 on order [^r3].
* **DRL-11S**: WH-MAN-STR holds 889 units on hand, 121 allocated, and 0 on order [^r4].

## Movement history

The Q3 2026 transaction register in [[data-stock-ledger-2026-q3|stock_ledger_2026-Q3]] documents steady production drawdowns at WH-MAN-STR across active derailleur items:

* **DRL-9S**: Opened Q3 on 1 July 2026 with 6,890 units at WH-MAN-STR [^r11]. Regular production issues during July and August reduced the balance to 3,147 units by 31 August 2026 [^r12]. Further work order issues throughout September closed the month at 1,338 units on 30 September 2026 [^r13].
* **DRL-10S**: Held an opening balance of 9,122 units at WH-MAN-STR on 1 July 2026, which was drawn down through work order issues to 6,285 units by 20 August 2026 [^r5]. The balance continued to decrease from 6,211 units on 21 August 2026 to 3,837 units on 30 September 2026 via production work order issues [^r6].
* **DRL-11S**: Opened Q3 on 1 July 2026 with 4,724 units at WH-MAN-STR and dropped to 3,724 units by 24 July 2026 following multiple work order issues [^r7]. A drawdown of 63 units under work order WO/2026/06950 on 24 August 2026 left 2,534 units on hand [^r8]. An issue of 47 units for work order WO/2026/05725 on 25 September 2026 brought the balance to 1,084 units [^r9], and a final issue of 63 units on 30 September 2026 under work order WO/2026/03448 concluded the month at 889 units [^r10].

## See also

* [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]
* [[data-stock-ledger-2026-q3|stock_ledger_2026-Q3]]
* [[items-shf|SHF-* items]]
* [[items-chn|CHN-* items]]
* [[items-cst|CST-* items]]
* [[items-hgr|HGR-* items]]
* [[services-pur-stk|PUR stk services]]

## References

[^r1]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row DRL-8S@WH-MAN-STR, SHEET Stock
[^r2]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row DRL-9S@WH-MAN-STR, SHEET Stock
[^r3]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row DRL-10S@WH-MAN-STR, SHEET Stock
[^r4]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row DRL-11S@WH-MAN-STR, SHEET Stock
[^r11]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3906, SHEET csv
[^r12]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3961, SHEET csv
[^r13]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3989, sheet csv
[^r5]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3735, csv
[^r6]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3782, SHEET csv
[^r7]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3841, SHEET csv
[^r8]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3867
[^r9]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3901
[^r10]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3905, SHEET csv
