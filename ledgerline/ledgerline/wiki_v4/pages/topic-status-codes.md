---
title: "Document Status Codes"
type: "topic"
slug: "topic-status-codes"
summary: "Standard document lifecycle status codes in Ledgerline ERP 7.2 defining record progression across modules."
audience: "staff"
status: "current"
sources: ["07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| System | Ledgerline ERP 7.2 |
| Topic | Standard Document Status Codes |
| Data dictionary | [[data-data-dictionary|Ledgerline_7.2_tables_and_fields]] |

Document status codes represent the lifecycle progression of transactional and master records within Ledgerline ERP 7.2 [^r1]. As of 26 October 2026, standard document processing across modules relies on a unified seven-state status model [^r1]. These codes govern record readiness, approval state, release availability, and closure tracking [^r1].

## Standard Status Codes

Ledgerline ERP 7.2 defines seven standard status codes across system tables [^r1]:

* `DR`: Draft [^r1].
* `PA`: Pending approval [^r1].
* `AP`: Approved [^r1].
* `RL`: Released [^r1].
* `RJ`: Rejected [^r1].
* `CN`: Cancelled [^r1].
* `CL`: Closed [^r1].

## See also

* [[data-data-dictionary|Ledgerline_7.2_tables_and_fields]]
* [[man-dd-72-all|MAN-DD-72-ALL Ledgerline ERP 7.2 Data Dictionary: all]]
* [[errors-po|ERR-PO Error Codes]]
* [[errors-pr|ERR-PR Error Codes]]

## References

[^r1]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Status codes, SHEET Status codes
