---
title: "Ledgerline ERP 7.2 Code Lists Reference"
type: "data-source"
slug: "data-code-lists"
summary: "Reference dataset defining standard Ledgerline ERP 7.2 enumeration codes across document statuses, supplier statuses, purchase order types, and service return codes."
audience: "staff"
status: "current"
sources: ["07_data_dictionary/code_lists.csv"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Dataset | code_lists.csv |
| Location | 07_data_dictionary/code_lists.csv |
| Format | CSV |
| Lists | doc_status, sup_status, po_type, rc |
| Status | Current |

The `code_lists.csv` reference file defines standard enumeration codes and their operational meanings within Ledgerline ERP 7.2 [^r1]. It provides authoritative lookup values for document lifecycles, supplier ordering statuses, purchase order classifications, and service execution return codes [^r1]. As of 26 October 2026, transactions and service calls across the purchasing module evaluate against these list definitions [^r1][^r3].

| Field | Value |
|---|---|
| Dataset | `code_lists.csv` |
| Location | `07_data_dictionary/code_lists.csv` |
| Format | CSV |
| Defined lists | `doc_status`, `sup_status`, `po_type`, `rc` |
| Total entries | 14 rows |
| Status | Current |

## What it holds

The dataset standardises enumeration codes across four system lists: `doc_status`, `sup_status`, `po_type`, and `rc` [^r1].

* **doc_status**: Controls the workflow state of procurement documents, specifying `DR` (Draft), `PA` (Pending approval), `AP` (Approved), `RL` (Released), `RJ` (Rejected), `CN` (Cancelled), and `CL` (Closed) [^r2].
* **sup_status**: Dictates vendor ordering eligibility, where `ACTIVE` permits ordering and `BLOCKED` refuses order creation with [[err-sup-0031|ERR-SUP-0031]] [^r3].
* **po_type**: Categorises purchase orders into `STD` (orders placed against an approved request) and `DIR` (direct orders placed without a request, grossed up to the direct-order limit) [^r4].
* **rc**: Standardises service return codes returned by API calls, comprising `S` (Success), `W` (Success with warning), and `E` (Error) [^r5].

## Columns

The CSV file defines standard list values using the following structure [^r1]:

* `list_name`: The identifier of the enumeration group (`doc_status`, `sup_status`, `po_type`, or `rc`) [^r1].
* `code`: The system key or abbreviation stored in database records and transaction payloads [^r1][^r2].
* `meaning`: The functional definition or full label assigned to the code [^r1][^r2].

## How to look up a row

Filter by `list_name` to isolate the target enumeration group, then match on `code` to retrieve the functional meaning [^r1]. For instance, looking up `BLOCKED` under `sup_status` reveals that orders placed with the vendor are rejected [^r3].

## Size

The file contains 14 rows across the four defined lists [^r2][^r3][^r4][^r5].

## See also

* [[err-sup-0031|ERR-SUP-0031 Supplier is blocked]]
* [[errors-sup|ERR-SUP Error Codes]]
* [[services-pur-po|PUR po services]]

## References

[^r1]: 07_data_dictionary/code_lists.csv, sheet csv, row columns, SHEET csv
[^r3]: 07_data_dictionary/code_lists.csv, sheet csv, row sup_status, ALL 14 ROWS
[^r2]: 07_data_dictionary/code_lists.csv, sheet csv, row doc_status, ALL 14 ROWS
[^r4]: 07_data_dictionary/code_lists.csv, sheet csv, row po_type, ALL 14 ROWS
[^r5]: 07_data_dictionary/code_lists.csv, sheet csv, row rc, ALL 14 ROWS
