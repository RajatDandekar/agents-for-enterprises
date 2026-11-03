---
title: "Payment terms"
type: "data-source"
slug: "data-payment-terms"
summary: "Master data source defining standard Ledgerline purchasing payment term codes, durations, descriptions, and legacy usage status."
audience: "staff"
status: "current"
sources: ["05_master_data/Payment terms.csv", "07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | data-payment-terms |
| type | data-source |
| file | 05_master_data/Payment terms.csv |
| key column | pt_cd |
| columns | pt_cd, descr, days |
| rows | 8 |
| status | current |

The Payment terms master file defines the available payment term codes used across Ledgerline purchasing transactions as of 26 October 2026 [^r1]. It provides standardized payment credit windows and baseline due date calculations, including advance payments, standard net periods, and month-end terms [^r1][^r2][^r6]. The master records eight codes in total, distinguishing active purchasing terms from legacy terms marked 'do not use' [^r1][^r9].

| Field | Value |
|---|---|
| Code | data-payment-terms |
| File | `05_master_data/Payment terms.csv` |
| Primary Key | `pt_cd` |
| Columns | `pt_cd`, `descr`, `days` |
| Record Count | 8 |
| Status | Current |

## What it holds

The file holds the master reference table of payment term codes, their text descriptions, and their duration in days used by purchasing workflows such as [[services-pur-po|PUR po services]] [^r1]. Standard documented options in the purchasing data dictionary [[man-dd-72|MAN-DD-72]] include ADV (advance payment), N30 (net 30 days), N45 (net 45 days), and N60 (net 60 days from invoice) [^r10]. The full master table defines eight records [^r1]:
* `ADV`: Advance terms with 0 days [^r2].
* `N7`: Net 7 days [^r3].
* `N15`: Net 15 days [^r4].
* `N30`: Net 30 days [^r5].
* `EOM30`: 30 days end of month with a duration of 30 days [^r6].
* `N45`: Net 45 days [^r7].
* `N60`: Net 60 days [^r8].
* `N90`: Legacy term designated 'do not use', with a duration of 90 days [^r9].

## Columns

The dataset contains three columns across all rows [^r1]:
* `pt_cd`: The primary payment term code identifier (e.g., ADV, N30, N90) [^r1][^r2][^r5][^r9].
* `descr`: The text description of the term, including legacy status annotations where applicable [^r1][^r9].
* `days`: The payment duration in days [^r1].

## How to look up a row

Look up records using the primary key `pt_cd` in `05_master_data/Payment terms.csv` [^r1].

## Size

The file contains 8 rows across 3 columns [^r1].

## Versions and conflicts

* **In force today**: The master data source defines eight distinct codes: ADV, N7, N15, N30, EOM30, N45, N60, and N90 (marked legacy and 'do not use') [^r1][^r9].
* **Alternative documentation**: [[man-dd-72|MAN-DD-72]] lists only N30, N45, N60, and ADV as purchasing payment term options in Ledgerline [^r10].
* **Sources and dates**: `05_master_data/Payment terms.csv` (current) [^r1]; `MAN-DD-72 v7.2.3` (2025-01-15), p. 2, §8 [^r10].
* **Kind**: `superseded` (the master table provides the full system code list, while MAN-DD-72 lists an abbreviated subset).

## See also

* [[data-tax-codes|Tax codes]]
* [[man-dd-72|MAN-DD-72 Ledgerline ERP 7.2 Data Dictionary, Purchasing]]
* [[services-pur-po|PUR po services]]

## References

[^r1]: 05_master_data/Payment terms.csv, sheet csv, SHEET csv
[^r2]: 05_master_data/Payment terms.csv, sheet csv, row ADV, ALL 8 ROWS
[^r6]: 05_master_data/Payment terms.csv, sheet csv, row EOM30, ALL 8 ROWS
[^r9]: 05_master_data/Payment terms.csv, sheet csv, row N90, ALL 8 ROWS
[^r10]: 07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf, p. 2, §8. Payment terms
[^r3]: 05_master_data/Payment terms.csv, sheet csv, row N7, ALL 8 ROWS
[^r4]: 05_master_data/Payment terms.csv, sheet csv, row N15, ALL 8 ROWS
[^r5]: 05_master_data/Payment terms.csv, sheet csv, row N30, ALL 8 ROWS
[^r7]: 05_master_data/Payment terms.csv, sheet csv, row N45, ALL 8 ROWS
[^r8]: 05_master_data/Payment terms.csv, sheet csv, row N60, ALL 8 ROWS
