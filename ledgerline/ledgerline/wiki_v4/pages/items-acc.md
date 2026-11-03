---
title: "ACC-* items"
type: "item-family"
slug: "items-acc"
summary: "Inventory balances, stock ledger movements, and purchase orders for Northbridge Cycles' ACC-* accessory component family across warehouse locations."
audience: "staff"
status: "current"
sources: ["05_master_data/Stock_on_hand_2026-10-26_0900.xlsx", "06_transactions/PO_extract_2026-01_to_2026-10.xlsx", "06_transactions/stock_ledger_2026-Q3.csv"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ACC |
| Description | Accessories and ancillary components |
| Primary Stores | WH-MAN-STR, WH-LDS-STR |
| Active Items | ACC-BSK, ACC-CGD, ACC-KS2, ACC-KST, ACC-LCK, ACC-MDG, ACC-MDW, ACC-RCC, ACC-RCK |
| Status | Current |

The ACC-* item family covers accessory components used in bicycle manufacturing and assembly at Northbridge Cycles, including baskets, chain guards, kickstands, and racks. As of 26 October 2026, inventory is primarily held at the Manchester store WH-MAN-STR, with additional stock of select rack items located at Leeds store WH-LDS-STR [^r1][^r2][^r3].

## Stock on hand

Stock levels across Northbridge storage locations recorded on 26 October 2026 are tracked in [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]] [^r1][^r3]:

* **ACC-BSK**: 1,124 units on hand, 695 units allocated, and 2,500 units on order at WH-MAN-STR [^r9].
* **ACC-CGD**: 3,565 units on hand, 271 units allocated, and 2,500 units on order at WH-MAN-STR [^r7].
* **ACC-KS2**: 3,935 units on hand, 291 units allocated, and 0 units on order at WH-MAN-STR [^r6].
* **ACC-KST**: 20,304 units on hand, 417 units allocated, and 0 units on order at WH-MAN-STR [^r5].
* **ACC-LCK**: 29 units on hand, 2 units allocated, and 10 units on order at WH-MAN-STR [^r8].
* **ACC-MDG**: 29 units on hand, 0 units allocated, and 0 units on order at WH-MAN-STR [^r1].
* **ACC-MDW**: 46 units on hand, 28 units allocated, and 0 units on order at WH-MAN-STR [^r2].
* **ACC-RCC**: 25,972 units on hand, 507 units allocated, and 9,000 units on order at WH-MAN-STR [^r4].
* **ACC-RCK**: 103 units on hand and 13 units allocated at WH-MAN-STR, alongside 77 units on hand and 0 units allocated at WH-LDS-STR [^r3].

## Consumption and transactions

Production issues during Q3 2026 drew down Manchester store balances across high-volume accessory lines:

* **ACC-BSK** (Basket): Opened Q3 2026 on 1 July 2026 with 12,433 units under transaction reference Q3 OPENING [^r11]. Regular production work order issues reduced the balance to 4,361 units by 1 September 2026 [^r12], concluding September 2026 at 1,124 units [^r13].
* **ACC-CGD** (Chain guard): Recorded a balance of 14,788 units on 1 July 2026, falling to 10,119 units by 5 August 2026 [^r14]. Further work order issues drew stock down from 9,935 units on 6 August 2026 to 3,565 units by 30 September 2026 [^r15]. Additionally, purchase order PO/2026/00762 ordered 5,000 units from ACP-CAR-0712 at £46.70 each for [[cc-lds-prd-01|LDS-PRD-01 Leeds assembly]] [^r10].
* **ACC-KS2** (Kickstand component): Opened on 1 July 2026 with 9,372 units, which was reduced through work orders such as WO/2026/06168 and WO/2026/05469 [^r16]. The balance stood at 8,634 units on 10 July 2026 after issuing 87 units to WO/2026/06811 [^r17], reached 4,903 units on 11 September 2026 after an issue of 38 units to WO/2026/06776 [^r18], and closed Q3 on 30 September 2026 at 3,935 units [^r19].
* **ACC-KST**: Began Q3 on 1 July 2026 with 66,797 units [^r20]. Continuous issues through August and September 2026 brought stock down from 43,818 units on 13 August 2026 to 20,304 units on 30 September 2026 [^r21].
* **ACC-RCC**: Opened on 1 July 2026 with 66,340 units, reaching 59,889 units on 14 July 2026 [^r22]. Issues between 15 July and 22 September 2026 reduced the balance from 59,174 to 29,906 units [^r23]. On 30 September 2026, issues of 697 units for WO/2026/07804 and 547 units for WO/2026/03848 brought the balance to 25,972 units [^r24].

## See also

* [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]
* [[cc-lds-prd-01|cc-lds-prd-01: LDS-PRD-01 Leeds assembly]]
* [[items-fg|items-fg: FG-* items]]
* [[services-pur-stk|services-pur-stk: PUR stk services]]

## References

[^r1]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row ACC-MDG@WH-MAN-STR, SHEET Stock
[^r2]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row ACC-MDW@WH-MAN-STR, SHEET Stock
[^r3]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row ACC-RCK@WH-MAN-STR, SHEET Stock
[^r9]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row ACC-BSK@WH-MAN-STR, SHEET Stock
[^r7]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row ACC-CGD@WH-MAN-STR, SHEET Stock
[^r6]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row ACC-KS2@WH-MAN-STR, SHEET Stock
[^r5]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row ACC-KST@WH-MAN-STR, SHEET Stock
[^r8]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row ACC-LCK@WH-MAN-STR, SHEET Stock
[^r4]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row ACC-RCC@WH-MAN-STR, SHEET Stock
[^r11]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2026-07-01, SHEET csv
[^r12]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2026-09-01, SHEET csv
[^r13]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 86, SHEET csv
[^r14]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 121, SHEET csv
[^r15]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 122, SHEET csv
[^r10]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-06, row PO/2026/00762, SHEET 2026-06
[^r16]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 170, SHEET csv
[^r17]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row row 182, SHEET csv
[^r18]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row row 241, SHEET csv
[^r19]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 256, SHEET csv
[^r20]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 257, SHEET csv
[^r21]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 302, SHEET csv
[^r22]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 361, SHEET csv
[^r23]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 421
[^r24]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 428, SHEET csv
