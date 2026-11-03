---
title: "CON-* items"
type: "item-family"
slug: "items-con"
summary: "CON-* workshop and assembly consumables inventory, stock levels, and open orders at warehouse WH-MAN-STR as of 26 October 2026."
audience: "staff"
status: "current"
sources: ["05_master_data/Stock_on_hand_2026-10-26_0900.xlsx"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | CON-* |
| type | item-family |
| category | Consumables |
| primary_location | WH-MAN-STR |
| status | current |
| as_of | 2026-10-26 09:00 GMT |

The `CON-*` family covers workshop and assembly consumables used across manufacturing and maintenance operations at Northbridge Cycles. As of 26 October 2026 at 09:00 GMT, all recorded stock for this family is held at warehouse location `WH-MAN-STR` with zero quantities currently allocated against production orders. Active replenishment is underway for nitrile gloves and threadlock, while protective sleeves show critically low stock levels.

| Item code | Description | Warehouse | On hand | Allocated | On order |
|---|---|---|---|---|---|
| code | description | warehouse | on_hand | allocated | on_order |
| `CON-GLV-01` | Nitrile gloves | WH-MAN-STR | 25 | 0 | 10 |
| `CON-WIP-01` | Consumable wipes | WH-MAN-STR | 715 | 0 | 0 |
| `CON-GRS-01` | Grease | WH-MAN-STR | 505 | 0 | 0 |
| `CON-THR-01` | Threadlock | WH-MAN-STR | 649 | 0 | 200 |
| `CON-SLV-01` | Protective sleeves | WH-MAN-STR | 3 | 0 | 0 |
| `CON-ESD-01` | ESD protection item | WH-MAN-STR | 30 | 0 | 0 |

## Stock on hand

At 26 October 2026 09:00, nitrile gloves `CON-GLV-01` at warehouse `WH-MAN-STR` have 25 on hand, 0 allocated, and 10 on order.[^r1] Consumable wipes `CON-WIP-01` at warehouse `WH-MAN-STR` have 715 on hand, 0 allocated, and 0 on order.[^r2] Assembly grease `CON-GRS-01` at warehouse `WH-MAN-STR` has 505 on hand, 0 allocated, and 0 on order.[^r3] Threadlock `CON-THR-01` at warehouse `WH-MAN-STR` has 649 on hand, 0 allocated, and 200 on order.[^r4] Protective sleeves `CON-SLV-01` at warehouse `WH-MAN-STR` have 3 on hand, 0 allocated, and 0 on order.[^r5] Electrostatic discharge protection item `CON-ESD-01` at warehouse `WH-MAN-STR` has 30 on hand, 0 allocated, and 0 on order.[^r6]

Stock figures can be verified against the structured inventory export in [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]. Inventory movement transactions and queries are managed via [[services-pur-stk|PUR stk services]].

## See also

* [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]
* [[services-pur-stk|PUR stk services]]
* [[items-fst|FST-* items]]
* [[items-pnt|PNT-* items]]
* [[items-mnt|MNT-* items]]
* [[items-pkg|PKG-* items]]

## References

[^r1]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CON-GLV-01@WH-MAN-STR, SHEET Stock
[^r2]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CON-WIP-01@WH-MAN-STR, SHEET Stock
[^r3]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CON-GRS-01@WH-MAN-STR, SHEET Stock
[^r4]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CON-THR-01@WH-MAN-STR, SHEET Stock
[^r5]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CON-SLV-01@WH-MAN-STR, SHEET Stock
[^r6]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CON-ESD-01@WH-MAN-STR, SHEET Stock
