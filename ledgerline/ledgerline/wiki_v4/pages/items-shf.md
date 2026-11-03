---
title: "SHF-* items"
type: "item-family"
slug: "items-shf"
summary: "Item family for gear shifters (SHF-*), tracking warehouse stock levels across locations and historical purchase order procurement."
audience: "staff"
status: "current"
sources: ["05_master_data/Stock_on_hand_2026-10-26_0900.xlsx", "06_transactions/PO_extract_2026-01_to_2026-10.xlsx"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Family code | SHF |
| Description | Shifters |
| Stock locations | WH-MAN-STR, WH-LDS-STR |
| Items recorded | SHF-8S, SHF-9S, SHF-10S, SHF-11S |

The SHF-* item family covers Northbridge Cycles' gear shifter components used across assembly operations. As of 26 October 2026, stock is held at both the Manchester central store (WH-MAN-STR) and the Leeds store (WH-LDS-STR) across 8-speed, 9-speed, 10-speed, and 11-speed variants [^r1][^r2][^r3][^r4]. Active open replenishment orders are currently placed for SHF-10S and SHF-11S units [^r3][^r4].

## Stock on hand

Stock levels across warehouse locations recorded at 09:00 on 26 October 2026 in [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]] are as follows:

* **SHF-8S**: WH-MAN-STR holds 3,057 on hand, 481 allocated, and 0 on order [^r1].
* **SHF-9S**: WH-MAN-STR holds 144 on hand, 65 allocated, and 0 on order; WH-LDS-STR holds 324 on hand, 0 allocated, and 0 on order [^r2].
* **SHF-10S**: WH-MAN-STR holds 7,194 on hand, 1,195 allocated, and 4,000 on order; WH-LDS-STR holds 532 on hand, 0 allocated, and 0 on order [^r3].
* **SHF-11S**: WH-MAN-STR holds 783 on hand, 49 allocated, and 200 on order [^r4].

Detailed lookups and reorder parameters are maintained in [[data-stock-on-hand]]. Stock ledger services are managed via [[services-pur-stk]].

## Procurement history

Purchase order PO/2026/00716 procured 800 units of shifter SHF-9S from supplier SG-BIR-0177 at a unit price of 10.03 for cost centre [[cc-prd-03|PRD-03 Cargo e-bike line]] [^r5].

## See also

* [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]
* [[services-pur-stk|PUR stk services]]
* [[cc-prd-03|PRD-03 Cargo e-bike line]]
* [[items-drl|DRL-* items]]
* [[items-cst|CST-* items]]
* [[items-chn|CHN-* items]]

## References

[^r1]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SHF-8S@WH-MAN-STR, SHEET Stock
[^r2]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SHF-9S@WH-MAN-STR, SHEET Stock
[^r3]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SHF-10S@WH-MAN-STR, SHEET Stock
[^r4]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SHF-11S@WH-MAN-STR, SHEET Stock
[^r5]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-05, row PO/2026/00716, SHEET 2026-05
