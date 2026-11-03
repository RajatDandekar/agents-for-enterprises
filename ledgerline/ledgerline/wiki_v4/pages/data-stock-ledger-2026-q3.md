---
title: "stock_ledger_2026-Q3"
type: "data-source"
slug: "data-stock-ledger-2026-q3"
summary: "Transaction extract recording 12,549 warehouse stock movements and running balances at WH-MAN-STR across 140 items during Q3 2026."
audience: "staff"
status: "current"
sources: ["06_transactions/stock_ledger_2026-Q3.csv"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Source file | 06_transactions/stock_ledger_2026-Q3.csv |
| Format | CSV |
| Rows | 12,549 |
| Columns | 7 |
| Warehouse | WH-MAN-STR |
| Period | Q3 2026 (2026-07-01 to 2026-09-30) |
| Distinct items | 140 |

The Q3 2026 stock ledger extract records inventory transactions and running balance positions at Northbridge Cycles for warehouse WH-MAN-STR[^r2][^r4]. Covering 81 distinct dates and 140 item codes, it tracks stock intake from goods receipt notes, issues to production work orders, and opening balances between 1 July 2026 and 30 September 2026[^r1][^r2][^r9]. It provides the audit trail for inventory quantities across [[items-acc|ACC-* items]] and [[items-bat|BAT-* items]] during the third quarter of 2026[^r3][^r23].

## What it holds

The file documents inventory transactions including opening balance entries (`OPENING`), goods receipts (`GRN`), and production issues (`ISS`)[^r2][^r4]. Every recorded movement applies specifically to warehouse WH-MAN-STR[^r2][^r7].

Key stock movements documented in the ledger include:
* Opening positions as of 1 July 2026: ACC-BSK opened at 12,433 units[^r3]; ACC-CGD opened at 14,788 units[^r6]; ACC-KS2 opened at 9,372 units under reference `Q3 OPENING`[^r9]; ACC-KST opened at 66,797 units under reference `Q3 OPENING`[^r14]; ACC-RCC opened at 66,340 units under reference `Q3 OPENING`[^r17]; BAT-375 opened at 15,432 units under reference `Q3 OPENING`[^r23]; BAT-418 opened at 5,600 units under reference `Q3 OPENING`[^r26]; and BAT-500 opened at 30,196 units under reference `Q3 OPENING`[^r27].
* Interim issues and receipts: On 10 July 2026, an issue of -87 units of ACC-KS2 against work order WO/2026/06811 reduced stock to 8,634[^r11]. On 15 July 2026, an issue of 715 units of ACC-RCC for WO/2026/07967 reduced stock to 59,174[^r19]. On 19 July 2026, warehouse WH-MAN-STR received GRN/2026/29632 for 1,800 units of BAT-500, setting the balance to 25,527[^r30]. On 3 August 2026, issues of 697 and 591 units of ACC-RCC for WO/2026/07261 and WO/2026/06859 dropped stock to 51,246[^r20]. On 12 August 2026, an issue of 381 units of ACC-KST to WO/2026/07144 brought the balance to 44,527[^r15]. By 27 August 2026, issues of BAT-375 against production work orders brought stock down to 8,432 following an issue of 103 units for WO/2026/04002[^r24]. On 11 September 2026, an issue of -38 units of ACC-KS2 for WO/2026/06776 resulted in a balance of 4,903[^r12]. By 22 September 2026, production issues reduced ACC-RCC stock to 29,906 following an issue of 386 units for WO/2026/04041[^r21].
* Closing balances on 30 September 2026: ACC-BSK stood at 1,124 following September work order issues[^r5]; ACC-CGD reached 3,565 after an issue of 127 units under WO/2026/04192[^r8]; ACC-KS2 finished at 3,935 after an issue of 49 units against WO/2026/06057[^r13]; ACC-KST ended at 20,304 after an issue of -339 units for WO/2026/04371[^r18]; ACC-RCC concluded at 25,972 after an issue of 547 units against WO/2026/03848[^r22]; and BAT-418 closed at 1,982 after issues for WO/2026/04080 (-57 units) and WO/2026/03534 (-43 units)[^r28].

## Columns

The dataset contains seven columns across each row[^r1][^r29]:
* `dt`: Transaction date (spanning 81 distinct dates across Q3 2026)[^r1][^r2].
* `itm_cd`: Item code (covering 140 distinct items)[^r1][^r10].
* `whs_cd`: Warehouse identifier (WH-MAN-STR across all rows)[^r1][^r25].
* `txn`: Transaction classification, including GRN, ISS, and OPENING[^r2][^r16].
* `qty`: Movement quantity (positive for receipts and opening entries, negative for issues)[^r1][^r11][^r30].
* `ref`: Reference string, such as `Q3 OPENING`, purchase receipt identifiers (e.g., GRN/2026/29632), or production work orders (e.g., WO/2026/04192)[^r8][^r9][^r30].
* `balance`: Cumulative running stock quantity remaining at WH-MAN-STR following the transaction[^r1][^r11].

## How to look up a row

Locate rows by filtering on `itm_cd` for the relevant part code, then sorting chronologically by `dt` to follow the movement history and observe changes in `balance`[^r1][^r10]. Individual transactions can also be verified by filtering on document numbers in the `ref` column, such as specific work order identifiers or GRN references[^r8][^r30].

## Size

The file contains 12,549 data rows covering 140 item codes across 81 distinct transaction dates[^r1][^r2].

## See also

* [[items-acc]]
* [[items-bat]]

## References

[^r2]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, SHEET csv
[^r4]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, SHEET csv
[^r1]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, SHEET csv
[^r9]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 170, SHEET csv
[^r3]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2026-07-01, SHEET csv
[^r23]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 430, SHEET csv
[^r7]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, SHEET csv
[^r6]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 87, SHEET csv
[^r14]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 257, SHEET csv
[^r17]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 348, SHEET csv
[^r26]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 514
[^r27]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 601
[^r11]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row row 182, SHEET csv
[^r19]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 362
[^r30]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 622, SHEET csv
[^r20]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 378
[^r15]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 301, SHEET csv
[^r24]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 481, SHEET csv
[^r12]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row row 241, SHEET csv
[^r21]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 421
[^r5]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 86, SHEET csv
[^r8]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 169, SHEET csv
[^r13]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 256, SHEET csv
[^r18]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 347, SHEET csv
[^r22]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 429, SHEET csv
[^r28]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 600
[^r29]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, SHEET csv
[^r10]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, SHEET csv
[^r25]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv
[^r16]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, SHEET csv
