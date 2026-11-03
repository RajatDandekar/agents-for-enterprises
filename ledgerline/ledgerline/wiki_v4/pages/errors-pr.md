---
title: "ERR-PR Error Codes"
type: "error-list"
slug: "errors-pr"
summary: "Reference list of ERR-PR error codes raised by Ledgerline 7.2 purchase requisition services and tables."
audience: "staff"
status: "current"
sources: ["07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx", "04_service_definitions/purchase/pr_get.yaml", "04_service_definitions/purchase/pr_save.yaml", "04_service_definitions/purchase/pr_submit.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code prefix | ERR-PR |
| Module | PR (Purchase Requisition) |
| System | Ledgerline ERP 7.2 |
| Status | current |

The `ERR-PR-*` series comprises system error codes raised by Ledgerline ERP 7.2 during purchase requisition operations. These messages enforce document existence, valid workflow status transitions, and forward-looking need dates across requisition screens and backend services. Requisitions failing these validation checks are halted until the requisition record is corrected or exists in the expected state.

### ERR-PR-0001

* **Message:** `PR NOT FOUND` [^r1][^r5]
* **Cause:** The requested purchase requisition record does not exist in the system [^r1][^r5].
* **Remedy:** Verify the requisition identifier and confirm the record has been created before retrieving or submitting it.
* **Raised by:** Service `pr_get` [^r5], service `pr_submit` [^r7], and module PR [^r1].

### ERR-PR-0007

* **Message:** `PR NOT IN DRAFT (<status>)` [^r2][^r8]
* **Cause:** Attempting to modify or submit a purchase requisition that is not currently in draft status [^r2][^r8].
* **Remedy:** Ensure the purchase requisition is in draft status before applying modifications or attempting submission [^r2][^r8].
* **Raised by:** Service `pr_submit` [^r8] and module PR [^r2].

### ERR-PR-0008

* **Message:** `PR NOT PENDING (<status>)` [^r3]
* **Cause:** A requisition approval action was attempted on a purchase requisition that is not in pending status [^r3].
* **Remedy:** Check the current workflow status of the purchase requisition prior to executing approval actions [^r3].
* **Raised by:** Module PR [^r3].

### ERR-PR-0105

* **Message:** `NEED DATE IN PAST` [^r4][^r6]
* **Cause:** A purchase request is submitted or saved with a need date prior to today [^r4][^r6].
* **Remedy:** Update the line or header need date to today or a future date before saving or submitting [^r4][^r6].
* **Raised by:** Service `pr_save` [^r6] and module PR [^r4].

## See also

* [[services-pur-pr|PUR pr services]]
* [[screen-pur-pr-01|PUR-PR-01 Purchase Request Entry]]
* [[man-dd-72-all|MAN-DD-72-ALL Ledgerline ERP 7.2 Data Dictionary: all]]
* [[data-data-dictionary|Ledgerline_7.2_tables_and_fields]]
* [[topic-status-codes|Document Status Codes]]
* [[errors-po|ERR-PO Error Codes]]

## References

[^r1]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PR-0001, SHEET Error codes
[^r5]: 04_service_definitions/purchase/pr_get.yaml, errors
[^r7]: 04_service_definitions/purchase/pr_submit.yaml, errors
[^r2]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PR-0007, SHEET Error codes
[^r8]: 04_service_definitions/purchase/pr_submit.yaml, errors
[^r3]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PR-0008, SHEET Error codes
[^r4]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PR-0105, SHEET Error codes
[^r6]: 04_service_definitions/purchase/pr_save.yaml, errors
