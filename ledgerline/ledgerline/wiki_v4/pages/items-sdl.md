---
title: "SDL-* items"
type: "item-family"
slug: "items-sdl"
summary: "Stock balances, procurement history, and purchase order records for the SDL saddle and seating item family across Northbridge warehouses."
audience: "staff"
status: "current"
sources: ["05_master_data/Stock_on_hand_2026-10-26_0900.xlsx", "06_transactions/PO_extract_2026-01_to_2026-10.xlsx"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Family code | SDL |
| Description | Saddles and seating components |
| Status | Current |
| Managed locations | WH-MAN-STR, WH-LDS-STR |
| Known items | SDL-01, SDL-02, SDL-03 |
| Primary supplier | HA-HAL-0842 |

The `SDL-*` item family encompasses saddle components used across Northbridge Cycles assembly and replacement operations. As of 26 October 2026, stock is maintained at Manchester stores (WH-MAN-STR) across parts SDL-01, SDL-02, and SDL-03, with inbound replenishment tracked through purchase orders to Manchester and Leeds stores (WH-LDS-STR). Major volume procurement is sourced from supplier HA-HAL-0842.

## Stock positions

Stock balances recorded as of 26 October 2026 at 09:00 GMT for warehouse WH-MAN-STR are detailed in [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]:

| Item code | Location | On hand | Allocated | On order |
|---|---|---|---|---|
| SDL-01 | WH-MAN-STR | 4,152 | 2,245 | 0 |
| SDL-02 | WH-MAN-STR | 25 | 1 | 10 |
| SDL-03 | WH-MAN-STR | 2,992 | 146 | 800 |

SDL-01 holds 4,152 units on hand, 2,245 allocated, and 0 on order at WH-MAN-STR [^r1]. SDL-02 has 25 units on hand, 1 allocated, and 10 on order at WH-MAN-STR [^r2]. SDL-03 has 2,992 units on hand, 146 allocated, and 800 on order at WH-MAN-STR [^r3].

## Procurement and orders

Purchase orders placed for the `SDL-*` family include transactions with supplier HA-HAL-0842:

* On 2026-06-05, purchase order PO/2026/00749 was created for 9,000 units of SDL-01 from HA-HAL-0842 at a unit rate of £38.49, totaling a gross value of £415,692.00 [^r4].
* Under purchase order PO/2026/00839, 13,500 NOS of SDL-01 were ordered from supplier HA-HAL-0842 at a unit rate of 38.49 for delivery to WH-LDS-STR [^r5].

## See also

* [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]
* [[services-pur-stk|PUR stk services]]
* [[items-frm|FRM-* items]]
* [[items-grp|GRP-* items]]
* [[items-acc|ACC-* items]]

## References

[^r1]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SDL-01@WH-MAN-STR, SHEET Stock
[^r2]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SDL-02@WH-MAN-STR, SHEET Stock
[^r3]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SDL-03@WH-MAN-STR, SHEET Stock
[^r4]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-06, row PO/2026/00749, SHEET 2026-06
[^r5]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-06, row PO/2026/00839, PURCHASE ORDERS CREATED 2026-06 (po_hdr + po_line). One line per order.
