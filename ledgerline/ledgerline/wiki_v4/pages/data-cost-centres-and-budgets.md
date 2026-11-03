---
title: "Cost Centres and Budgets FY2026-27"
type: "data-source"
slug: "data-cost-centres-and-budgets"
summary: "Master workbook for Northbridge cost centres, Q4 budget allocations, committed spend, and multi-period budget tracking."
audience: "staff"
status: "current"
sources: ["05_master_data/Cost Centres and Budgets FY2026-27.xlsx"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Source file | 05_master_data/Cost Centres and Budgets FY2026-27.xlsx |
| Type | Master and register extract |
| Status | Current |
| Operating units | NBC-MAN-01, NBC-LDS-01 |
| Cost centres count | 28 |
| Sheets | Cost centres, Budgets 2026-Q4, All periods |

The Cost Centres and Budgets FY2026-27 workbook is the structured master file defining Northbridge Cycles' cost centres and their budget positions [^r1][^r4]. It maintains master metadata across two operating units, provides current 2026-Q4 budget allocations and committed spend balances in GBP, and records historical and multi-period budget tracking [^r2][^r4][^r6]. As of Monday 26 October 2026 at 09:00 GMT, it serves as the reference data source for cost centre validity, operational statuses, and spending limits across Ledgerline transactions [^r3][^r4].

## What it holds
The workbook holds three primary sheets:
* **Cost centres**: The master list of all 28 registered cost centres across operating units `NBC-MAN-01` and `NBC-LDS-01`, recording the code, name, operational status, closure date where relevant, owner, and operating unit [^r1][^r2]. Three status values exist across the register: `OPEN`, `CLOSED`, and `PLANNED`, with five cost centres carrying recorded closure dates [^r3].
* **Budgets 2026-Q4**: The current quarter budget tracking sheet as at 26 October 2026 09:00, covering 23 cost centres and setting out allocated budget amounts, committed spend (defined as the gross value of approved and pending purchase orders), and available remaining balances in GBP [^r4][^r5].
* **All periods**: The complete multi-period register spanning 213 rows of periodic budget allocations and committed figures [^r6]. Examples for 2026-Q4 include [[cc-mnt-01|MNT-01 Plant maintenance]] with a budget of 300,000 and committed expenditure of 45,000, [[cc-adm-01|ADM-01 Administration]] with a budget of 200,000 and committed expenditure of 20,000, and [[cc-prd-03|PRD-03 Cargo e-bike line]] with a budget of 800,000 and committed spending of 120,000 [^r7][^r8][^r9].

## Columns
### Sheet: Cost centres
* `cc_cd`: The primary cost centre identifier code [^r1].
* `name`: Cost centre description [^r1].
* `status`: Operational status (`OPEN`, `CLOSED`, or `PLANNED`) [^r1][^r3].
* `closed_on`: Recorded closure date for discontinued cost centres [^r1][^r3].
* `owner`: Assigned manager or cost centre owner [^r1].
* `ou_cd`: Operating unit code (`NBC-MAN-01` or `NBC-LDS-01`) [^r1][^r2].

### Sheet: Budgets 2026-Q4
* `cc_cd`: Cost centre code [^r5].
* `amount`: Total budget amount in GBP [^r4][^r5].
* `committed`: Gross value of approved and pending orders in GBP [^r4][^r5].
* `available`: Remaining available balance in GBP [^r4][^r5].

### Sheet: All periods
* `line`: Sequential line identifier [^r6].
* `cc_cd`: Cost centre code [^r6].
* `period`: Fiscal period (e.g., `2026-Q4`) [^r6][^r7].
* `amount`: Period budget amount in GBP [^r6][^r7].
* `committed`: Period committed expenditure in GBP [^r6][^r7].

## How to look up a row
* In the **Cost centres** sheet, search or filter by the unique cost centre code in column `cc_cd` (such as `MNT-01` or `ADM-01`) [^r1][^r7][^r8].
* In the **Budgets 2026-Q4** sheet, look up by column `cc_cd` to retrieve the active budget, committed spend, and remaining balance [^r4][^r5].
* In the **All periods** sheet, locate rows using the composite key of `cc_cd` and `period` (for example, `MNT-01/2026-Q4` or `PRD-03/2026-Q4`) [^r6][^r7][^r9].

## Size
* **Cost centres**: 28 data rows across 6 columns [^r1].
* **Budgets 2026-Q4**: 23 cost centre rows across 4 columns [^r4][^r5].
* **All periods**: 213 data rows across 5 columns [^r6].

## See also
* [[cc-adm-01|ADM-01 Administration]]
* [[cc-cap-2025|CAP-2025 Capital projects 2025-26]]
* [[cc-cap-2026|CAP-2026 Capital projects 2026-27]]
* [[cc-fin-01|FIN-01 Finance]]
* [[cc-hr-01|HR-01 Human resources]]
* [[cc-hse-01|HSE-01 Health, safety and environment]]
* [[cc-it-01|IT-01 IT]]
* [[cc-lds-adm-01|LDS-ADM-01 Leeds administration]]
* [[cc-lds-log-01|LDS-LOG-01 Leeds stores]]
* [[cc-lds-prd-01|LDS-PRD-01 Leeds assembly]]
* [[cc-log-01|LOG-01 Stores and logistics]]
* [[cc-mnt-01|MNT-01 Plant maintenance]]
* [[cc-mnt-02|MNT-02 Leeds maintenance]]
* [[cc-prd-01|PRD-01 Ancoats city line (2016-2022)]]
* [[cc-prd-02|PRD-02 Deansgate step-through line]]
* [[cc-prd-03|PRD-03 Cargo e-bike line]]
* [[cc-prd-04|PRD-04 Medlock trekking line]]
* [[cc-prd-05|PRD-05 City e-bike line, regular production]]
* [[cc-prd-06|PRD-06 Tame folding line]]
* [[cc-prd-07|PRD-07 Spring launch run]]
* [[cc-prd-08|PRD-08 Roch mountain line (opens 2027)]]
* [[cc-prd-09|PRD-09 Battery refurbishment]]
* [[cc-prd-5|PRD-5 City line (6.x code, do not use)]]
* [[cc-qa-01|QA-01 Quality]]
* [[cc-sal-01|SAL-01 Sales UK]]
* [[cc-sal-02|SAL-02 Sales Europe]]
* [[cc-sal-03|SAL-03 Warranty and service]]
* [[cc-rnd-01|RND-01 Product development]]

## References

[^r1]: 05_master_data/Cost Centres and Budgets FY2026-27.xlsx, sheet Cost centres, SHEET Cost centres
[^r4]: 05_master_data/Cost Centres and Budgets FY2026-27.xlsx, sheet Budgets 2026-Q4, SHEET Budgets 2026-Q4
[^r2]: 05_master_data/Cost Centres and Budgets FY2026-27.xlsx, sheet Cost centres, SHEET Cost centres
[^r6]: 05_master_data/Cost Centres and Budgets FY2026-27.xlsx, sheet All periods, SHEET All periods
[^r3]: 05_master_data/Cost Centres and Budgets FY2026-27.xlsx, sheet Cost centres, SHEET Cost centres
[^r5]: 05_master_data/Cost Centres and Budgets FY2026-27.xlsx, sheet Budgets 2026-Q4, SHEET Budgets 2026-Q4
[^r7]: 05_master_data/Cost Centres and Budgets FY2026-27.xlsx, sheet All periods, row MNT-01/2026-Q4, SHEET All periods
[^r8]: 05_master_data/Cost Centres and Budgets FY2026-27.xlsx, sheet All periods, row ADM-01/2026-Q4, SHEET All periods
[^r9]: 05_master_data/Cost Centres and Budgets FY2026-27.xlsx, sheet All periods, row PRD-03/2026-Q4, SHEET All periods
