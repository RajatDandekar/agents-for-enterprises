---
title: "CST-* items"
type: "item-family"
slug: "items-cst"
summary: "Cassette sprockets across 8-speed to 11-speed variants, detailing stock balances and Q3 2026 consumption."
audience: "staff"
status: "current"
sources: ["05_master_data/Stock_on_hand_2026-10-26_0900.xlsx", "06_transactions/stock_ledger_2026-Q3.csv"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code prefix | CST- |
| Family description | Cassette sprockets |
| Primary storage | WH-MAN-STR, WH-LDS-STR |
| Active items | CST-8S-1136, CST-9S-1136, CST-10S-1136, CST-11S-1136 |
| Stock status date | 2026-10-26 09:00 GMT |

The `CST-*` item family covers cassette sprockets utilized across Northbridge Cycles drivetrain assemblies, ranging from 8-speed to 11-speed variants. As of 26 October 2026 at 09:00 GMT, inventory is primarily concentrated in warehouse WH-MAN-STR, with high availability in 8-speed and 9-speed units alongside critical lower balances in 10-speed and 11-speed specifications [^r1][^r2][^r3][^r4]. Production demand during Q3 2026 drew steadily on these components for manufacturing work orders [^r7][^r11]. Detailed ledger movement and inventory extracts are maintained in [[data-stock-ledger-2026-q3|stock_ledger_2026-Q3]] and [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]] [^r1][^r5].

## Inventory status

As of 09:00 GMT on 26 October 2026, stock-on-hand positions across locations are:

* **CST-8S-1136**: 2,835 units on hand, 15 allocated, and 0 on order at WH-MAN-STR [^r1].
* **CST-9S-1136**: 7,880 units on hand, 61 allocated, and 2,500 on order at WH-MAN-STR, with an additional 729 units on hand, 0 allocated, and 0 on order at WH-LDS-STR [^r2].
* **CST-10S-1136**: 20 units on hand, 2 allocated, and 0 on order at WH-MAN-STR [^r3].
* **CST-11S-1136**: 23 units on hand, 2 allocated, and 10 on order at WH-MAN-STR [^r4].

## Consumption and replenishment history

During Q3 2026, transactions in [[data-stock-ledger-2026-q3|stock_ledger_2026-Q3]] recorded active production issues from WH-MAN-STR:

* **CST-8S-1136**: Opened Q3 on 2026-07-01 with a balance of 3,333 units [^r5]. Regular issues reduced the balance to 2,417 units by 2026-07-20 following an issue of 30 units against work order WO/2026/07990 [^r6]. Ongoing production consumption pushed stock down to a low of 275 units on 3 September 2026 [^r7]. Two replenishment receipts of 1,800 units each were booked via GRN/2026/29896 on 4 September 2026 and GRN/2026/29945 on 18 September 2026 [^r8]. Continued daily work order issues brought the closing balance to 2,835 units on 30 September 2026 [^r9].
* **CST-9S-1136**: Opened on 1 July 2026 with 19,725 units at WH-MAN-STR and underwent regular production issues through July and August 2026 [^r10]. Balances declined from 13,224 units on 18 August to 7,880 units on 30 September 2026 due to continuous work order withdrawals [^r11].

## See also

* [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]
* [[data-stock-ledger-2026-q3|stock_ledger_2026-Q3]]
* [[items-chn|CHN-* items]]
* [[items-drl|DRL-* items]]
* [[items-shf|SHF-* items]]
* [[items-crk|CRK-* items]]

## References

[^r1]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CST-8S-1136@WH-MAN-STR, SHEET Stock
[^r2]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CST-9S-1136@WH-MAN-STR, SHEET Stock
[^r3]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CST-10S-1136@WH-MAN-STR, SHEET Stock
[^r4]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CST-11S-1136@WH-MAN-STR, SHEET Stock
[^r7]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3348, csv
[^r11]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3422, SHEET csv
[^r5]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3283
[^r6]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3301
[^r8]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3361, csv
[^r9]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3375
[^r10]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3376
