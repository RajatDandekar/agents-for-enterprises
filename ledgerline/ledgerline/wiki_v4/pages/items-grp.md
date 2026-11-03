---
title: "GRP-* items"
type: "item-family"
slug: "items-grp"
summary: "Handlebar grips family, covering GRP-ERG items with stock balances across Manchester and Leeds stores and purchasing activity."
audience: "staff"
status: "current"
sources: ["05_master_data/Stock_on_hand_2026-10-26_0900.xlsx", "06_transactions/PO_extract_2026-01_to_2026-10.xlsx", "06_transactions/reports/PO register 2026-03 (printed).pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Family code | GRP |
| Family description | Handlebar grips |
| Tracked items | GRP-ERG-01, GRP-ERG-02, GRP-ERG-03 |
| Primary storage | WH-MAN-STR, WH-LDS-STR |
| Status | current |

The `GRP-*` item family encompasses handlebar grips used across Northbridge Cycles assembly operations, including ergonomic variants GRP-ERG-01, GRP-ERG-02, and GRP-ERG-03 [^r1][^r2][^r3]. As of 26 October 2026, stock is maintained primarily at Manchester Central Stores (WH-MAN-STR) and Leeds Stores (WH-LDS-STR) [^r1][^r2][^r3]. Recorded procurement includes an attempt to source GRP-ERG-01 for Leeds assembly in March 2026 that was rejected [^r4][^r5].

## Family items and inventory

As of 26 October 2026 at 09:00 GMT, inventory levels in [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]] for the `GRP-*` family are:

* **GRP-ERG-01**: At WH-MAN-STR, there are 711 units on hand, 25 allocated, and 200 on order [^r1].
* **GRP-ERG-02**: At WH-MAN-STR, there are 10,343 units on hand, 541 allocated, and 0 on order [^r2]. At WH-LDS-STR, there are 1,115 units on hand, 0 allocated, and 0 on order [^r2].
* **GRP-ERG-03**: At WH-MAN-STR, there are 681 units on hand, 5 allocated, and 0 on order [^r3].

## Procurement history

On 23 March 2026, direct purchase order PO/2026/00377 was raised for 300 PR of ergonomic grips GRP-ERG-01 at a unit rate of 37.69 (gross 13,568.40) from supplier Bilbao Accessories S.L. (BA-BIL-0566) for cost centre [[cc-lds-prd-01|LDS-PRD-01]] [^r4][^r5]. The order was rejected with status RJ by [[user-hnakamura|Hana Nakamura (HNAKAMURA)]] [^r4][^r5]. Transactions are recorded in [[data-po-extract-2026|PO_extract_2026-01_to_2026-10]] [^r4].

## See also

* [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]
* [[data-po-extract-2026|PO_extract_2026-01_to_2026-10]]
* [[cc-lds-prd-01|LDS-PRD-01 Leeds assembly]]
* [[user-hnakamura|Hana Nakamura (HNAKAMURA)]]

## References

[^r1]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row GRP-ERG-01@WH-MAN-STR, SHEET Stock
[^r2]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row GRP-ERG-02@WH-MAN-STR, SHEET Stock
[^r3]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row GRP-ERG-03@WH-MAN-STR, SHEET Stock
[^r4]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-03, row PO/2026/00377, PURCHASE ORDERS CREATED 2026-03 (po_hdr + po_line)
[^r5]: 06_transactions/reports/PO register 2026-03 (printed).pdf, p. 3, REPORT PUR-R010
