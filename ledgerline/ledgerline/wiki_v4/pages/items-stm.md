---
title: "STM-* items"
type: "item-family"
slug: "items-stm"
summary: "Stem component items (STM-*), covering inventory levels, allocations, and open purchase orders across warehouses as of 26 October 2026."
audience: "staff"
status: "current"
sources: ["05_master_data/Stock_on_hand_2026-10-26_0900.xlsx"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | STM- |
| Family | Stems |
| Active items | STM-60, STM-70, STM-80, STM-90, STM-100 |
| Primary warehouse | WH-MAN-STR |
| Secondary warehouse | WH-LDS-STR |
| As of | 2026-10-26 09:00 GMT |

The `STM-*` family comprises bicycle stem components stocked for production and assembly at Northbridge Cycles. As of 26 October 2026 at 09:00 GMT, inventory is held primarily at warehouse WH-MAN-STR, with additional stock for STM-80 positioned at WH-LDS-STR [^r1][^r2][^r3][^r4][^r5]. Across the five tracked variants (STM-60 through STM-100), only STM-90 has units currently on order [^r1][^r2][^r3][^r4][^r5].

## Inventory status

Stock balances and allocation figures taken from [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]] as of 26 October 2026 at 09:00 GMT:

| Item code | Warehouse | On hand | Allocated | On order |
|---|---|---|---|---|
| STM-60 | WH-MAN-STR | 2,361 | 495 | 0 |
| STM-70 | WH-MAN-STR | 182 | 87 | 0 |
| STM-80 | WH-MAN-STR | 1,714 | 228 | 0 |
| STM-80 | WH-LDS-STR | 472 | 0 | 0 |
| STM-90 | WH-MAN-STR | 104 | 13 | 200 |
| STM-100 | WH-MAN-STR | 1,029 | 0 | 0 |

At 09:00 on 26 October 2026, stock for stem STM-60 at WH-MAN-STR was 2,361 on hand, 495 allocated, and 0 on order [^r1]. At the same time, stem STM-70 at WH-MAN-STR recorded 182 units on hand, 87 allocated, and 0 on order [^r2].

Item STM-80 is distributed across two facilities, holding 1,714 units on hand with 228 allocated at WH-MAN-STR, alongside 472 units on hand with 0 allocated at WH-LDS-STR, and has 0 on order at both sites [^r3]. Item STM-90 has 104 units on hand, 13 allocated, and 200 on order at WH-MAN-STR [^r4]. Item STM-100 holds 1,029 units on hand, 0 allocated, and 0 on order at WH-MAN-STR [^r5].

## See also

* [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]
* [[services-pur-stk|PUR stk services]]
* [[items-hbr|HBR-* items]]
* [[items-frm|FRM-* items]]

## References

[^r1]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row STM-60@WH-MAN-STR, SHEET Stock
[^r2]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row STM-70@WH-MAN-STR, SHEET Stock
[^r3]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row STM-80@WH-MAN-STR, SHEET Stock
[^r4]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row STM-90@WH-MAN-STR, SHEET Stock
[^r5]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row STM-100@WH-MAN-STR, SHEET Stock
