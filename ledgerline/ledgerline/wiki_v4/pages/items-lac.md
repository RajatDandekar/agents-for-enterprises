---
title: "LAC-* items"
type: "item-family"
slug: "items-lac"
summary: "Raw material lacquer codes (LAC-*) covering colour coating stocks at Manchester stores and procurement for Leeds assembly."
audience: "staff"
status: "current"
sources: ["05_master_data/Stock_on_hand_2026-10-26_0900.xlsx", "06_transactions/PO_extract_2026-01_to_2026-10.xlsx"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code prefix | LAC |
| category | Raw materials (lacquers and coatings) |
| primary warehouse | WH-MAN-STR |
| items tracked | LAC-BLK, LAC-BLU, LAC-GRN, LAC-GRY, LAC-RED, LAC-SLV, LAC-WHT |
| status | current |

The `LAC-*` item family covers production lacquers and frame coatings stored at WH-MAN-STR and procured for assembly operations[^r1][^r8]. As of 26 October 2026 at 09:00 GMT, inventory is tracked across seven colour variants, with major holdings in red, blue, and white lacquer stocks[^r1][^r4][^r5][^r6]. Bulk procurement supplies assembly requirements, including historical deliveries booked to [[cc-lds-prd-01|LDS-PRD-01 Leeds assembly]][^r8].

## Stock on hand

Stock balances recorded as of 26 October 2026 at 09:00 across warehouse WH-MAN-STR comprise[^r1][^r2][^r3][^r4][^r5][^r6][^r7]:

* **LAC-BLK** (black lacquer): 323 units on hand, 9 units allocated[^r1].
* **LAC-BLU** (blue lacquer): 9,025 units on hand, 11 units allocated[^r5].
* **LAC-GRN** (green lacquer): 32 units on hand, 0 units allocated[^r2].
* **LAC-GRY** (grey lacquer): 169 units on hand, 6 units allocated[^r7].
* **LAC-RED** (red lacquer): 23,104 units on hand, 2,393 units allocated[^r4].
* **LAC-SLV** (silver lacquer): 22 units on hand, 0 units allocated[^r3].
* **LAC-WHT** (white lacquer): 3,168 units on hand, 121 units allocated[^r6].

Detailed stock balances and allocations are maintained in [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]][^r1].

## Procurement

Purchase orders for lacquer materials specify bulk quantities measured in kilograms[^r8]. Under PO/2026/00262, issued on 27 February 2026, Northbridge ordered 9,000 KG of LAC-RED at £7.91 per KG from supplier MF-BIR-1041 for [[cc-lds-prd-01|LDS-PRD-01 Leeds assembly]][^r8].

## See also

* [[cc-lds-prd-01|LDS-PRD-01 Leeds assembly]]
* [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]
* [[items-frm|FRM-* items]]
* [[services-pur-stk|PUR stk services]]

## References

[^r1]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row LAC-BLK@WH-MAN-STR, SHEET Stock
[^r8]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-02, row PO/2026/00262, SHEET 2026-02
[^r4]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row LAC-RED@WH-MAN-STR, SHEET Stock
[^r5]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row LAC-BLU@WH-MAN-STR, SHEET Stock
[^r6]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row LAC-WHT@WH-MAN-STR, SHEET Stock
[^r2]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row LAC-GRN@WH-MAN-STR, SHEET Stock
[^r3]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row LAC-SLV@WH-MAN-STR, SHEET Stock
[^r7]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row LAC-GRY@WH-MAN-STR, SHEET Stock
