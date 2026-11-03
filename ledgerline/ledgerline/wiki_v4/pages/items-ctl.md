---
title: "CTL-* items"
type: "item-family"
slug: "items-ctl"
summary: "Active electronic motor controller components (CTL-01 to CTL-04) used in assembly production, detailing stock balances and reorder levels across stores."
audience: "staff"
status: "current"
sources: ["05_master_data/Stock_on_hand_2026-10-26_0900.xlsx", "06_transactions/reports/Item master listing 2026-10 (printed).pdf", "06_transactions/stock_ledger_2026-Q3.csv"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Item family | CTL |
| Category | COMPONENTS |
| Status | ACTIVE |
| Line category | LC 0 |
| Member count | 4 |
| Locations | WH-MAN-STR, WH-LDS-STR |

The CTL family covers electronic controller components used across Northbridge Cycles assembly lines, comprising items CTL-01 through CTL-04 [^r3]. All four items are configured as active components with line category LC 0 in the [[data-item-master|item master]] [^r3]. Inventory is held primarily at Manchester Stores (WH-MAN-STR), with secondary stocks for CTL-04 located at Leeds Stores (WH-LDS-STR) [^r1][^r2].

| Item code | Description category | Status | Line category | Reorder level (ROL) | WH-MAN-STR on hand (allocated) | WH-LDS-STR on hand (allocated) | On order |
|---|---|---|---|---|---|---|---|
| CTL-01 | COMPONENTS | ACTIVE | LC 0 | 12,600 | 24,800 (1,082) | — | 9,000 |
| CTL-02 | COMPONENTS | ACTIVE | LC 0 | 1,680 | 571 (333) | — | 0 |
| CTL-03 | COMPONENTS | ACTIVE | LC 0 | 280 | 500 (48) | — | 0 |
| CTL-04 | COMPONENTS | ACTIVE | LC 0 | 1,120 | 859 (183) | 330 (0) | 0 |

## Master data and parameters

All members of the CTL family are classified under the COMPONENTS item category with line category LC 0 [^r3]. Reorder levels (ROL) defined in the master catalog are 12,600 for CTL-01, 1,680 for CTL-02, 280 for CTL-03, and 1,120 for CTL-04 [^r3].

## Stock on hand

As of 26 October 2026 at 09:00 GMT, inventory in [[data-stock-on-hand|stock on hand]] is recorded as follows:
* **CTL-01**: 24,800 units on hand at WH-MAN-STR, with 1,082 units allocated and 9,000 units currently on order [^r1].
* **CTL-02**: 571 units on hand at WH-MAN-STR, with 333 units allocated [^r1].
* **CTL-03**: 500 units on hand at WH-MAN-STR, with 48 units allocated [^r1].
* **CTL-04**: 859 units on hand at WH-MAN-STR (183 allocated), and 330 units on hand at WH-LDS-STR (0 allocated) [^r2].

## Consumption history (Q3 2026)

Ledger activity in the [[data-stock-ledger-2026-q3|Q3 2026 stock ledger]] reflects substantial manufacturing issues against production work orders from WH-MAN-STR:
* **CTL-01**: Opened Q3 on 1 July 2026 with 68,317 units, decreasing through work order backflush issues to 59,146 units by 20 July 2026 [^r4]. Further work order production issues reduced stock from 58,635 units on 20 July 2026 to 29,322 units by 18 September 2026 [^r5]. It finished the quarter at 24,800 units following an issue of 339 units to WO/2026/03879 on 30 September 2026 [^r6].
* **CTL-02**: Opened Q3 on 1 July 2026 with 6,144 units [^r7]. Successive production issues lowered stock to 3,294 units by 17 August 2026 after 49 units were issued to WO/2026/03935 [^r8]. Ongoing work order drawdowns through August and September 2026 reduced the balance to 571 units on 30 September 2026 [^r9].
* **CTL-04**: Opened Q3 on 1 July 2026 with 4,721 units, dropping to 4,092 units by 16 July 2026 [^r10]. Continued work order issues reduced the balance from 4,056 units on 17 July 2026 to 1,489 units by 14 September 2026 [^r11]. An issue to WO/2026/07249 on 30 September 2026 brought the quarter-end WH-MAN-STR balance to 859 units [^r12].

## See also

* [[data-item-master|ITEM_MASTER_2026-10-26]]
* [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]
* [[data-stock-ledger-2026-q3|stock_ledger_2026-Q3]]
* [[items-bat|BAT-* items]]
* [[items-mtr|MTR-* items]]
* [[items-cbl|CBL-* items]]
* [[services-pur-stk|PUR stk services]]

## References

[^r3]: 06_transactions/reports/Item master listing 2026-10 (printed).pdf, row CTL-01, p. 2, LEDGERLINE ERP 7.2 REPORT INV-R001 ITEM MASTER LISTING
[^r1]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CTL-01@WH-MAN-STR, SHEET Stock
[^r2]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CTL-04@WH-MAN-STR, SHEET Stock
[^r4]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3481, SHEET csv
[^r5]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3482, csv
[^r6]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3551
[^r7]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3552
[^r8]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3601
[^r9]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3645, csv
[^r10]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3661, csv
[^r11]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3721, SHEET csv
[^r12]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3734, csv
