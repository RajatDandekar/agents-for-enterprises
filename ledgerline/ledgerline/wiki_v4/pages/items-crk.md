---
title: "CRK-* items"
type: "item-family"
slug: "items-crk"
summary: "Crankset item family including CRK-170 and CRK-175 stock balances, allocations, purchase orders, and Q3 2026 manufacturing consumption history."
audience: "staff"
status: "current"
sources: ["05_master_data/Stock_on_hand_2026-10-26_0900.xlsx", "06_transactions/stock_ledger_2026-Q3.csv"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code prefix | CRK |
| Family | Cranksets |
| Managed warehouse | WH-MAN-STR |
| Tracked items | CRK-170, CRK-175 |
| Status | current |

The `CRK-*` family comprises crankset components stocked primarily at the main manufacturing store (`WH-MAN-STR`). As of 26 October 2026, the active codes recorded in stock are CRK-170 and CRK-175, supporting ongoing bicycle assembly work orders. Both items maintain active purchase orders to replenish warehouse inventory against regular production issues.

## Stock positions

According to the master snapshot in [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]], stock levels across the family at WH-MAN-STR as of 09:00 on 26 October 2026 stand as follows:

* **CRK-170**: 160 units on hand, 44 allocated, and 200 on order[^r1].
* **CRK-175**: 2,461 units on hand, 99 allocated, and 800 on order[^r2].

## Transaction history

Transaction movements for the family during the third quarter of 2026 are tracked in [[data-stock-ledger-2026-q3|stock_ledger_2026-Q3]]. On 2026-07-01, item CRK-175 opened Q3 2026 with a balance of 6,261 units at WH-MAN-STR[^r3]. The item was issued continuously to work orders throughout July and August 2026, reaching a balance of 4,198 units at WH-MAN-STR by 2026-08-20 after an issue of 58 units against work order WO/2026/07842[^r4]. Q3 production consumption concluded on 2026-09-30 with a stock balance of 2,461 units at WH-MAN-STR following an issue of 50 units for work order WO/2026/07226[^r5].

## See also

* [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]
* [[data-stock-ledger-2026-q3|stock_ledger_2026-Q3]]
* [[items-bbr|BBR-* items]]
* [[items-chn|CHN-* items]]
* [[items-pdl|PDL-* items]]
* [[services-pur-stk|PUR stk services]]

## References

[^r1]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CRK-170@WH-MAN-STR, SHEET Stock
[^r2]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CRK-175@WH-MAN-STR, SHEET Stock
[^r3]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3191
[^r4]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3241
[^r5]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3282
