---
title: "PR_extract_2026"
type: "data-source"
slug: "data-pr-extract-2026"
summary: "Transaction extract and register report of purchase requisitions raised between January and October 2026 across four requisition types."
audience: "staff"
status: "current"
sources: ["06_transactions/PR_extract_2026.csv", "06_transactions/reports/Purchase Request Register Jan-Oct 2026 (printed).pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| File | PR_extract_2026.csv |
| Report code | PUR-R005 |
| System | Ledgerline ERP 7.2 |
| Period | 2026-01-02 to 2026-10-26 |
| Row count | 4,416 data rows |
| Status | Current |

The 2026 purchase requisition extract and register cover requisitions raised in Ledgerline ERP 7.2 from 2026-01-02 to 2026-10-26 [^r1][^r6]. As of 26 October 2026, the dataset captures operational demand across four requisition types routed to three destination warehouses [^r1][^r2][^r4]. It provides the transaction-level audit trail supporting purchase requisition processing under [[sop-pur-002|SOP-PUR-002]].

## What it holds

The extract contains transactional data for all purchase requisitions entered during the 2026 calendar year up to 26 October 2026 [^r1]. Requisitions are classified into four types: MRO, SRV, STD, and TRF [^r2][^r8]. Records track six distinct requisition statuses: AP, CL, CN, DR, PA, and RJ [^r3][^r9]. Deliveries are routed to three destination warehouses: WH-LDS-STR, WH-MAN-MRO, and WH-MAN-STR [^r4]. Within the extract, 3,142 records have an approver recorded across eight distinct approving users [^r5].

A corresponding printed report, PUR-R005 (Ledgerline ERP 7.2 Purchase Request Register), covers the period 01-01-2026 to 26-10-2026 and was generated on 26-10-2026 at 05:40 [^r6].

## Columns

The CSV extract contains 13 columns [^r1].

The PUR-R005 register report formats these transactions under nine visible column headers [^r7]:
* PR NO [^r7]
* DATE [^r7]
* TYPE [^r7]
* ITEM CD [^r7]
* QTY [^r7]
* EST VALUE [^r7]
* CC [^r7]
* ST [^r7]
* BY [^r7]

## How to look up a row

Individual records in the extract and register are identified by the purchase requisition number (PR NO) [^r7]. Specific line items are tracked using the item code (ITEM CD) and associated cost centre (CC) [^r7].

## Size

The CSV file contains 4,416 data rows across 13 columns [^r1]. Exactly 3,142 of these requisitions record an approving user [^r5].

## See also

* [[sop-pur-002|SOP-PUR-002 Purchase Request to Purchase Order]]

## References

[^r1]: 06_transactions/PR_extract_2026.csv, sheet csv, SHEET csv
[^r6]: 06_transactions/reports/Purchase Request Register Jan-Oct 2026 (printed).pdf, p. 1
[^r2]: 06_transactions/PR_extract_2026.csv, sheet csv, SHEET csv
[^r4]: 06_transactions/PR_extract_2026.csv, sheet csv, SHEET csv
[^r8]: 06_transactions/reports/Purchase Request Register Jan-Oct 2026 (printed).pdf, p. 1
[^r3]: 06_transactions/PR_extract_2026.csv, sheet csv, SHEET csv
[^r9]: 06_transactions/reports/Purchase Request Register Jan-Oct 2026 (printed).pdf, p. 1
[^r5]: 06_transactions/PR_extract_2026.csv, sheet csv, SHEET csv
[^r7]: 06_transactions/reports/Purchase Request Register Jan-Oct 2026 (printed).pdf, p. 1
