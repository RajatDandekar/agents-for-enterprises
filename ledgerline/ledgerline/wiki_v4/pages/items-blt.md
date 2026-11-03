---
title: "BLT-* items"
type: "item-family"
slug: "items-blt"
summary: "Inventory balances, warehouse allocations, and Q3 2026 consumption history for the BLT-* drive belt item family."
audience: "staff"
status: "current"
sources: ["05_master_data/Stock_on_hand_2026-10-26_0900.xlsx", "06_transactions/stock_ledger_2026-Q3.csv"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code prefix | BLT- |
| Family | Belt drives |
| Tracked items | BLT-118, BLT-122 |
| Primary warehouse | WH-MAN-STR |
| Secondary warehouse | WH-LDS-STR |
| Status | current |

The BLT-* item family comprises belt drive components used across Northbridge Cycles production assemblies, notably belt drives BLT-118 and BLT-122 [^r1][^r2]. As of 09:00 on 26 October 2026, inventory is held primarily at warehouse WH-MAN-STR with secondary reserves at WH-LDS-STR [^r1][^r2]. Active production work orders heavily consume BLT-118 stock, while BLT-122 maintains open purchase replenishment [^r1][^r2][^r4].

| Item code | Description | Warehouse | On hand | Allocated | On order |
|---|---|---|---|---|---|
| BLT-118 | Belt drive | WH-MAN-STR | 18,486 | 1,357 | 0 |
| BLT-118 | Belt drive | WH-LDS-STR | 4,847 | 0 | 0 |
| BLT-122 | Belt drive | WH-MAN-STR | 354 | 52 | 200 |

Detailed point-in-time stock quantities across all sites are recorded in [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]] [^r1][^r2].

## Stock ledger history

Transaction records from [[data-stock-ledger-2026-q3|stock_ledger_2026-Q3]] document heavy consumption of item BLT-118 at WH-MAN-STR throughout the third quarter of 2026 [^r3][^r4]. On 1 July 2026, BLT-118 recorded an opening balance of 59,883 units at WH-MAN-STR [^r3]. Regular production work order issues drew down this balance to 43,834 units by 7 August 2026 [^r3]. Between 10 August 2026 and 30 September 2026, ongoing consumption across dozens of work orders further reduced inventory at WH-MAN-STR to a quarter-ending balance of 18,486 units [^r4].

## See also

* [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]
* [[data-stock-ledger-2026-q3|stock_ledger_2026-Q3]]
* [[items-chn|CHN-* items]]
* [[items-crk|CRK-* items]]
* [[services-pur-stk|PUR stk services]]

## References

[^r1]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BLT-118@WH-MAN-STR, SHEET Stock
[^r2]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BLT-122@WH-MAN-STR, SHEET Stock
[^r4]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1313
[^r3]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 1228, csv
