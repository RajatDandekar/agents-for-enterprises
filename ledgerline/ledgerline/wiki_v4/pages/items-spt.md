---
title: "SPT-* items"
type: "item-family"
slug: "items-spt"
summary: "Stock levels, allocations, and open orders across warehouse locations for Northbridge Cycles' SPT-* item family as of 26 October 2026."
audience: "staff"
status: "current"
sources: ["05_master_data/Stock_on_hand_2026-10-26_0900.xlsx"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code prefix | SPT- |
| Family name | SPT-* items |
| Status | Current |
| Data source | [[data-stock-on-hand|Stock on Hand]] |

The `SPT-*` item family encompasses inventory tracked across Northbridge Cycles warehouse facilities including Manchester (`WH-MAN-STR`) and Leeds (`WH-LDS-STR`)[^r1][^r3]. As of 26 October 2026 at 09:00 GMT, stock positions for active items in this family range from low-volume components to high-turnover lines carrying substantial on-order replenishments[^r1][^r2]. Detailed inventory figures and balances are recorded in the central [[data-stock-on-hand|stock register]][^r1][^r2][^r3].

## Stock positions

Inventory balances across warehouse locations for `SPT-*` items stand as follows:

* **SPT-01**: Holds 11 units on hand and 1 unit allocated at `WH-MAN-STR`, with an additional 4 units on hand and 0 allocated at `WH-LDS-STR`[^r1].
* **SPT-02**: Holds 8,379 units on hand, 628 units allocated, and 2,500 units on order at `WH-MAN-STR`[^r2].
* **SPT-03**: Holds 173 units on hand and 15 units allocated at `WH-MAN-STR`, alongside 84 units on hand and 0 allocated at `WH-LDS-STR`[^r3].

For transaction operations or inventory inquiries, inventory services are processed via [[services-pur-stk|PUR stk services]].

## See also

* [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]
* [[services-pur-stk|PUR stk services]]
* [[items-spr|SPR-* items]]

## References

[^r1]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPT-01@WH-MAN-STR, SHEET Stock
[^r3]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPT-03@WH-MAN-STR, SHEET Stock
[^r2]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPT-02@WH-MAN-STR, SHEET Stock
