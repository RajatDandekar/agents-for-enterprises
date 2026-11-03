---
title: "Stock Count Error Codes (ERR-CNT-*)"
type: "error-list"
slug: "errors-cnt"
summary: "Reference catalogue of stock count error codes (ERR-CNT-*) and warning codes raised across Ledgerline inventory counting services."
audience: "staff"
status: "current"
sources: ["07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx", "03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "04_service_definitions/inventory/cnt_cancel.yaml", "04_service_definitions/inventory/cnt_entry.yaml", "04_service_definitions/inventory/cnt_freeze.yaml", "04_service_definitions/inventory/cnt_get.yaml", "04_service_definitions/inventory/cnt_post.yaml", "04_service_definitions/inventory/cnt_save.yaml", "08_release_notes/RN-7.2.2 Ledgerline Release Notes.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-CNT-* |
| Module | Inventory (CNT) |
| Governing Manual | MAN-INV-72 |
| Underlying Services | services-inv-cnt |

This page catalogues the error and warning codes with the `ERR-CNT-*` prefix raised by Ledgerline's stock count module (CNT) and related [[services-inv-cnt|inventory counting services]][^r1]. These codes enforce validation across count creation, line entry on [[screen-inv-cnt-06|INV-CNT-06 Stock Count Entry]], area freezing, cancellation, and final posting according to [[sop-inv-003|SOP-INV-003]][^r8][^r10][^r13][^r18]. Understanding these validations ensures counting procedures adhere to Northbridge Cycles' inventory control standards without interrupting operations[^r5][^r20].

### ERR-CNT-0001
* **Message**: STOCK COUNT NOT FOUND[^r10][^r12][^r17][^r18]
* **Cause**: Raised by module CNT when the specified stock count identifier is not found in the system, or when an invalid or missing stock count number `cnt_no` is submitted[^r1][^r10][^r12][^r14][^r17][^r18]. Manual [[man-inv-72|MAN-INV-72]] additionally notes header establishment failure due to an invalid warehouse code `WHS CD` or missing mandatory parameters before executing `STOCK COUNT SAVE`[^r8].
* **Remedy**: Verify the count reference number `cnt_no` exists in the count register, or provide all mandatory header parameters including a valid warehouse code before saving[^r8][^r10][^r12].
* **Raised by**: `cnt_cancel`[^r10], `cnt_entry`[^r12], `cnt_freeze`[^r14], `cnt_get`[^r17], `cnt_post`[^r18], `cnt_save`[^r8].

### ERR-CNT-0007
* **Message**: STOCK COUNT NOT IN DRAFT (<status>)[^r19]
* **Cause**: Raised by module CNT when an operation requires the count to be in draft status, but the current record is in a non-draft state[^r2][^r15][^r19]. Manual [[man-inv-72|MAN-INV-72]] describes this as warehouse freeze failure where the system cannot lock the requested bin range via `STOCK COUNT FREEZE` due to background stock movements[^r9].
* **Remedy**: Confirm that the stock count is still in draft status before triggering freeze or posting actions, and verify background stock movements have ceased across the target bins[^r9][^r15][^r19].
* **Raised by**: `cnt_freeze`[^r15], `cnt_post`[^r19].

### ERR-CNT-0105
* **Message**: DATE IN PAST[^r22]
* **Cause**: Raised by module CNT when the count date is set in the past[^r3][^r22].
* **Remedy**: Ensure the entered count date is set to the current date or a future scheduled count date[^r3][^r22].
* **Raised by**: `cnt_save`[^r22].

### ERR-CNT-0201
* **Message**: QTY MUST BE > 0[^r13]
* **Cause**: Raised by module CNT when the count quantity entered for an item is not greater than 0, such as zero or negative values[^r4][^r13].
* **Remedy**: Enter a valid positive count quantity on [[screen-inv-cnt-06|INV-CNT-06]][^r4][^r13].
* **Raised by**: `cnt_entry`[^r13].

### ERR-CNT-0230
* **Message**: Open transactions in count area[^r5]
* **Cause**: Raised by module CNT when open inventory transactions exist within the specified count area or bin range during freezing[^r5][^r16].
* **Remedy**: Clear, post, or cancel all pending warehouse transactions in the targeted count area before running `cnt_freeze`[^r5][^r16]. Detailed procedural instructions are provided on [[err-cnt-0230|ERR-CNT-0230 Area has open transactions]].
* **Raised by**: `cnt_freeze`[^r16].

### ERR-CNT-0240
* **Message**: VARIANCE ABOVE TOLERANCE, RECOUNT REQUIRED[^r20]
* **Cause**: Raised by module CNT when the counted inventory value variance exceeds the defined system tolerance parameter `INV.CNT_TOL_PCT`, preventing posting[^r6][^r20][^r23].
* **Remedy**: Initiate a recount of the affected items to resolve the discrepancy or obtain the required managerial approval before posting[^r6][^r20][^r23]. See [[err-cnt-0240|ERR-CNT-0240 Cycle Count Value Variance Exceeds Tolerance]] for recount workflows.
* **Raised by**: `cnt_post`[^r20].

### ERR-CNT-0801
* **Message**: STOCK COUNT CLOSED (<status>)[^r11]
* **Cause**: Raised by module CNT when an action or cancellation is attempted on a stock count that is already closed[^r7][^r11].
* **Remedy**: Do not attempt updates or cancellation on finalized or closed counts; initiate a new count if further adjustments are required[^r7][^r11].
* **Raised by**: `cnt_cancel`[^r11].

### W-CNT-241
* **Message**: VARIANCE NOTED, WITHIN TOLERANCE[^r21]
* **Cause**: Informational warning raised during stock count posting when a variance exists between recorded stock and counted quantities, but the variance remains within acceptable tolerance limits[^r21].
* **Remedy**: Review line discrepancies for auditing; posting is permitted to proceed without recount[^r21].
* **Raised by**: `cnt_post`[^r21].

## Versions and conflicts

* **Contradiction on ERR-CNT-0001**: In [[data-data-dictionary|data dictionary tables]] and service YAML definitions (`cnt_get`, `cnt_entry`, `cnt_post`, `cnt_cancel`, `cnt_freeze`), ERR-CNT-0001 is defined as "STOCK COUNT NOT FOUND" when an invalid or nonexistent count number is supplied[^r1][^r10][^r12][^r14][^r17][^r18]. In [[man-inv-72|MAN-INV-72]] (v7.2.3, 2025-01-15), ERR-CNT-0001 is described as count header establishment failure from missing parameters or an invalid warehouse code during save[^r8].
* **Contradiction on ERR-CNT-0007**: In [[data-data-dictionary|data dictionary tables]] and service YAML definitions (`cnt_freeze`, `cnt_post`), ERR-CNT-0007 indicates "STOCK COUNT NOT IN DRAFT (<status>)"[^r2][^r15][^r19]. In [[man-inv-72|MAN-INV-72]] (v7.2.3, 2025-01-15), ERR-CNT-0007 is documented as warehouse freeze failure caused by background stock movements locking bin ranges[^r9].

## See also

* [[err-cnt-0230|ERR-CNT-0230 Area has open transactions]]
* [[err-cnt-0240|ERR-CNT-0240 Cycle Count Value Variance Exceeds Tolerance]]
* [[errors-adj|Stock Adjustment Error Codes (ERR-ADJ-*)]]
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]
* [[rn-7-2-2|RN-7.2.2 Ledgerline ERP 7.2.2 Release Notes]]
* [[screen-inv-cnt-06|INV-CNT-06 Stock Count Entry]]
* [[services-inv-cnt|INV cnt services]]
* [[sop-inv-003|SOP-INV-003 Stock Count (cycle and annual)]]

## References

[^r1]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-CNT-0001, SHEET Error codes
[^r8]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 12, Messages
[^r10]: 04_service_definitions/inventory/cnt_cancel.yaml, errors
[^r13]: 04_service_definitions/inventory/cnt_entry.yaml, errors
[^r18]: 04_service_definitions/inventory/cnt_post.yaml, errors
[^r5]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-CNT-0230, SHEET Error codes
[^r20]: 04_service_definitions/inventory/cnt_post.yaml, errors
[^r12]: 04_service_definitions/inventory/cnt_entry.yaml, errors
[^r17]: 04_service_definitions/inventory/cnt_get.yaml, errors
[^r14]: 04_service_definitions/inventory/cnt_freeze.yaml, errors
[^r19]: 04_service_definitions/inventory/cnt_post.yaml, errors
[^r2]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-CNT-0007, SHEET Error codes
[^r15]: 04_service_definitions/inventory/cnt_freeze.yaml, errors
[^r9]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 12, Messages
[^r22]: 04_service_definitions/inventory/cnt_save.yaml, errors
[^r3]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-CNT-0105, SHEET Error codes
[^r4]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-CNT-0201, SHEET Error codes
[^r16]: 04_service_definitions/inventory/cnt_freeze.yaml, errors
[^r6]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-CNT-0240, SHEET Error codes
[^r23]: 08_release_notes/RN-7.2.2 Ledgerline Release Notes.pdf, p. 2, §2. Changes
[^r11]: 04_service_definitions/inventory/cnt_cancel.yaml, errors
[^r7]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-CNT-0801, SHEET Error codes
[^r21]: 04_service_definitions/inventory/cnt_post.yaml, errors
