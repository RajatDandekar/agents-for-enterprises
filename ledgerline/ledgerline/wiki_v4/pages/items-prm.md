---
title: "PRM-* items"
type: "item-family"
slug: "items-prm"
summary: "Stock levels, allocations and open orders for PRM-* primer coating items across Manchester and Leeds stores."
audience: "staff"
status: "current"
sources: ["05_master_data/Stock_on_hand_2026-10-26_0900.xlsx"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Family prefix | PRM |
| Description | Primers |
| Storage locations | WH-MAN-STR, WH-LDS-STR |
| Active items | PRM-BLK, PRM-BLU, PRM-GRN, PRM-GRY, PRM-RED, PRM-SLV, PRM-WHT |
| Data source | [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]] |

The `PRM-*` item family covers primer paints and coatings used in production across Northbridge Cycles facilities. As of 26 October 2026 09:00, stock is held predominantly at WH-MAN-STR with secondary balances at WH-LDS-STR, recorded in [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]][^r1][^r3]. Inventory levels range from high-volume colours like blue and white down to single-digit balances for silver and grey[^r3][^r5][^r6][^r7].

## Stock on hand

| Item code | Description | Warehouse | On hand | Allocated | On order |
|---|---|---|---|---|---|
| PRM-BLK | Black primer | WH-MAN-STR | 29 | 1 | 0 |
| PRM-BLU | Blue primer | WH-MAN-STR | 31,441 | 2,409 | 9,000 |
| PRM-BLU | Blue primer | WH-LDS-STR | 3,684 | — | — |
| PRM-GRN | Green primer | WH-MAN-STR | 165 | 0 | 50 |
| PRM-GRY | Grey primer | WH-MAN-STR | 12 | 1 | 0 |
| PRM-RED | Red primer | WH-MAN-STR | 17 | 0 | 0 |
| PRM-SLV | Silver primer | WH-MAN-STR | 2 | — | — |
| PRM-SLV | Silver primer | WH-LDS-STR | 4 | — | — |
| PRM-WHT | White primer | WH-MAN-STR | 1,264 | 112 | 400 |
| PRM-WHT | White primer | WH-LDS-STR | 82 | — | — |

Black primer PRM-BLK holds 29 units on hand and 1 allocated at WH-MAN-STR as of 26 October 2026 09:00[^r1]. Green primer PRM-GRN has 165 units on hand, 0 allocated, and 50 on order at WH-MAN-STR[^r2]. Silver primer PRM-SLV has 2 units on hand at WH-MAN-STR and 4 units on hand at WH-LDS-STR[^r3]. Red primer PRM-RED has 17 units on hand and 0 allocated at WH-MAN-STR[^r4]. Blue primer PRM-BLU maintains 31,441 units on hand, 2,409 allocated, and 9,000 on order at WH-MAN-STR, alongside 3,684 units on hand at WH-LDS-STR[^r5]. White primer PRM-WHT has 1,264 units on hand, 112 allocated, and 400 on order at WH-MAN-STR, with an additional 82 units on hand at WH-LDS-STR[^r6]. Grey primer PRM-GRY holds 12 units on hand and 1 allocated at WH-MAN-STR[^r7].

## See also

* [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]
* [[items-pnt|PNT-* items]]
* [[items-lac|LAC-* items]]
* [[services-pur-stk|PUR stk services]]

## References

[^r1]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row PRM-BLK@WH-MAN-STR, SHEET Stock
[^r3]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row PRM-SLV@WH-MAN-STR, SHEET Stock
[^r5]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row PRM-BLU@WH-MAN-STR, SHEET Stock
[^r6]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row PRM-WHT@WH-MAN-STR, SHEET Stock
[^r7]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row PRM-GRY@WH-MAN-STR, SHEET Stock
[^r2]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row PRM-GRN@WH-MAN-STR, SHEET Stock
[^r4]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row PRM-RED@WH-MAN-STR, SHEET Stock
