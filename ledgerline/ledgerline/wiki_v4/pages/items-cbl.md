---
title: "CBL-* items"
type: "item-family"
slug: "items-cbl"
summary: "Inventory balances, production usage, and stock status across Manchester and Leeds stores for the CBL family of internal bike wiring and cables."
audience: "staff"
status: "current"
sources: ["05_master_data/Stock_on_hand_2026-10-26_0900.xlsx", "06_transactions/stock_ledger_2026-Q3.csv"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Family Code | CBL |
| Description | Internal cables and wiring harnesses |
| Primary Warehouse | WH-MAN-STR |
| Secondary Warehouse | WH-LDS-STR |
| Status | current |

The CBL item family covers internal bicycle cabling, wiring looms, and component harnesses connecting motors, displays, brakes, shifters, lights, and sensors. Stock is predominantly held at Manchester Stores (WH-MAN-STR) with selective distribution at Leeds Stores (WH-LDS-STR) as recorded in [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]][^r1][^r10]. Across the third quarter of 2026, high-volume sensor, light, motor, and torque cables underwent steady drawdown to fulfill production work orders recorded in [[data-stock-ledger-2026-q3|stock_ledger_2026-Q3]][^r18][^r21][^r25][^r30].

## Stock on hand

As of 26 October 2026 at 09:00 GMT, inventory levels across the CBL family are:

* **CBL-MTR-01**: 3,439 units on hand, 447 allocated, and 0 on order at WH-MAN-STR[^r1].
* **CBL-MTR-02**: 167 units on hand, 15 allocated, and 0 on order at WH-MAN-STR[^r2].
* **CBL-DSP-01**: 178 units on hand, 43 allocated, and 200 on order at WH-MAN-STR[^r3].
* **CBL-DSP-02**: 78 units on hand, 4 allocated, and 0 on order at WH-MAN-STR[^r4].
* **CBL-BRK-01**: 1,429 units on hand, 12 allocated, and 0 on order at WH-MAN-STR[^r5].
* **CBL-BRK-02**: 11 units on hand, 0 allocated, and 0 on order at WH-MAN-STR[^r6].
* **CBL-SHF-01**: 699 units on hand, 20 allocated, and 0 on order at WH-MAN-STR[^r7].
* **CBL-SHF-02**: 955 units on hand, 3 allocated, and 0 on order at WH-MAN-STR[^r8].
* **CBL-HSG-01**: 21 units on hand, 2 allocated, and 0 on order at WH-MAN-STR[^r9].
* **CBL-HSG-02**: 4,269 units on hand and 337 allocated at WH-MAN-STR, and 639 units on hand with 0 allocated at WH-LDS-STR[^r10].
* **CBL-SNS-01**: 13,888 units on hand and 352 allocated at WH-MAN-STR, and 3,651 units on hand with 0 allocated at WH-LDS-STR[^r11].
* **CBL-SNS-02**: 17,044 units on hand, 925 allocated, and 9,000 on order at WH-MAN-STR, alongside 4,010 units on hand with 0 allocated at WH-LDS-STR[^r12].
* **CBL-TRQ-01**: 475 units on hand, 153 allocated, and 800 on order at WH-MAN-STR[^r13].
* **CBL-TRQ-02**: 1,377 units on hand, 93 allocated, and 800 on order at WH-MAN-STR, and 458 units on hand with 0 allocated at WH-LDS-STR[^r14].
* **CBL-LGT-01**: 5,906 units on hand, 733 allocated, and 2,500 on order at WH-MAN-STR[^r15].
* **CBL-LGT-02**: 8 units on hand, 2 allocated, and 10 on order at WH-MAN-STR[^r16].

## Production consumption (Q3 2026)

Ledger transactions during Q3 2026 show heavy usage of CBL lines across assembly operations at WH-MAN-STR:

* **Housing cable CBL-HSG-02**: Opened Q3 on 2026-07-01 with 10,704 units at WH-MAN-STR[^r17]. Regular work order issues reduced the balance to 8,076 by 2026-08-10[^r18]. Drawdowns continued from 8,004 units on 2026-08-11 down to 4,269 units on 2026-09-30[^r19].
* **Light cable CBL-LGT-01**: Held an opening balance of 17,085 units on 2026-07-01, immediately issuing against work orders WO/2026/07777 and WO/2026/07532[^r20]. Stock drew down from 16,622 on 2026-07-03 to 8,800 on 2026-09-04[^r21], finishing September 2026 at 5,906 units following issue WO/2026/04726[^r22].
* **Motor cable CBL-MTR-01**: Opened Q3 with 22,739 units at WH-MAN-STR on 2026-07-01[^r23]. Issues throughout July and early August reduced the balance to 14,527 on 2026-08-06[^r24], declining steadily from 14,374 later that day down to 3,439 units by 2026-09-30[^r25].
* **Sensor cable CBL-SNS-01**: Began Q3 on 2026-07-01 with 33,586 units at WH-MAN-STR[^r26]. Repeated production issues lowered inventory from 31,482 on 2026-07-10 to 18,328 on 2026-09-14[^r27], reaching 13,888 units on 2026-09-30[^r28].
* **Sensor cable CBL-SNS-02**: Started Q3 on 2026-07-01 with 60,327 units at WH-MAN-STR[^r29]. Following regular issues in late Q3, stock closed September 2026 at 17,044 units[^r30].
* **Torque sensor cable CBL-TRQ-01**: Opened Q3 on 2026-07-01 with 4,161 units before being drawn for work orders including WO/2026/05397 and WO/2026/05427[^r31]. Issues reduced stock from 3,601 units on 2026-07-14 to 1,035 units on 2026-09-15[^r32], and further dropped from 992 on 2026-09-16 to 475 on 2026-09-30[^r33].
* **Torque sensor cable CBL-TRQ-02**: Opened with 4,965 units on 2026-07-01 at WH-MAN-STR, dropping to 3,089 units by 2026-08-20[^r34]. Repeated issues through August and September concluded with a closing balance of 1,377 units on 2026-09-30[^r35].

## See also

* [[data-stock-on-hand|Stock on hand register]]
* [[data-stock-ledger-2026-q3|Stock ledger 2026-Q3]]
* [[items-mtr|MTR-* items]]
* [[items-dsp|DSP-* items]]
* [[items-brk|BRK-* items]]
* [[items-shf|SHF-* items]]
* [[items-lgt|LGT-* items]]
* [[items-con|CON-* items]]
* [[services-pur-stk|PUR stock services]]

## References

[^r1]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CBL-MTR-01@WH-MAN-STR, SHEET Stock
[^r10]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CBL-HSG-02@WH-MAN-STR, SHEET Stock
[^r18]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2161, csv
[^r21]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2026-07-03, SHEET csv
[^r25]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2392
[^r30]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2568, SHEET csv
[^r2]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CBL-MTR-02@WH-MAN-STR, SHEET Stock
[^r3]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CBL-DSP-01@WH-MAN-STR, SHEET Stock
[^r4]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CBL-DSP-02@WH-MAN-STR, SHEET Stock
[^r5]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CBL-BRK-01@WH-MAN-STR, SHEET Stock
[^r6]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CBL-BRK-02@WH-MAN-STR, SHEET Stock
[^r7]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CBL-SHF-01@WH-MAN-STR, SHEET Stock
[^r8]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CBL-SHF-02@WH-MAN-STR, SHEET Stock
[^r9]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CBL-HSG-01@WH-MAN-STR, SHEET Stock
[^r11]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CBL-SNS-01@WH-MAN-STR, SHEET Stock
[^r12]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CBL-SNS-02@WH-MAN-STR, SHEET Stock
[^r13]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CBL-TRQ-01@WH-MAN-STR, SHEET Stock
[^r14]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CBL-TRQ-02@WH-MAN-STR, SHEET Stock
[^r15]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CBL-LGT-01@WH-MAN-STR, SHEET Stock
[^r16]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CBL-LGT-02@WH-MAN-STR, SHEET Stock
[^r17]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2118, csv
[^r19]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2217, csv
[^r20]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2218, csv
[^r22]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2304
[^r23]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2305
[^r24]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2341
[^r26]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2393
[^r27]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row row 2402, key 2026-07-10, SHEET csv
[^r28]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row row 2480, csv
[^r29]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row row 2481, csv
[^r31]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2569, SHEET csv
[^r32]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2582
[^r33]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2026-09-16, SHEET csv
[^r34]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2026-08-20, SHEET csv
[^r35]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2742, SHEET csv
