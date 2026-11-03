---
title: "ERR-WO error codes"
type: "error-list"
slug: "errors-wo"
summary: "Catalogue of Ledgerline production work order error codes (ERR-WO-*), detailing message definitions, service triggers, remedies, and documentation discrepancies across module services."
audience: "staff"
status: "current"
sources: ["07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx", "03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "04_service_definitions/production/wo_cancel.yaml", "04_service_definitions/production/wo_close.yaml", "04_service_definitions/production/wo_get.yaml", "04_service_definitions/production/wo_release.yaml", "04_service_definitions/production/wo_save.yaml", "04_service_definitions/production/wo_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-WO |
| Module | Production (PRD) |
| System | Ledgerline ERP 7.2 |
| Reference table | Error codes |
| Source services | [[services-prd-wo|PRD wo services]] |
| Owner | Production |

This page catalogues the `ERR-WO-*` error codes raised by the Ledgerline ERP 7.2 Production module across the [[services-prd-wo|PRD wo services]] family and on screen [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]][^r1][^r7]. These codes govern work order creation, searching, release, cancellation, and closure validation[^r13][^r15][^r17][^r18][^r21][^r23]. Significant discrepancies exist between the backend service definitions and the [[man-prd-72|MAN-PRD-72]] user manual regarding message text and triggers[^r1][^r7].

| Field | Value |
|---|---|
| Prefix | ERR-WO |
| Module | Production (PRD) |
| System | Ledgerline ERP 7.2 |
| Reference table | Error codes |
| Source services | [[services-prd-wo|PRD wo services]] |
| Owner | Production |

### ERR-WO-0001
* **Message:** WORK ORDER NOT FOUND[^r1][^r13][^r15][^r17][^r18]
* **Cause:** The requested work order number does not exist or cannot be located in the database[^r13][^r17][^r18].
* **Remedy:** Verify the work order number (`wo_no`) entered on the screen or request payload and confirm the order exists before retrying[^r13][^r17].
* **Raised by:** `wo_cancel`[^r13], `wo_close`[^r15], `wo_get`[^r17], `wo_release`[^r18].

### ERR-WO-0007
* **Message:** WORK ORDER NOT RELEASED[^r2] / WORK ORDER NOT IN DRAFT (`<status>`)[^r19]
* **Cause:** An operation expected the work order to be released, or an attempt was made to release a work order that is not currently in draft status[^r2][^r19].
* **Remedy:** Check the current lifecycle status of the work order and ensure it is in draft status before calling release[^r19].
* **Raised by:** `wo_release`[^r19].

### ERR-WO-0105
* **Message:** DATE IN PAST[^r3][^r22][^r24]
* **Cause:** The work order start date is configured with a date in the past[^r22].
* **Remedy:** Set the start date (`START DT`) to the current date or a future date[^r22].
* **Raised by:** `wo_save`[^r22], `wo_search`[^r24].

### ERR-WO-0201
* **Message:** QTY MUST BE > 0[^r4][^r21][^r23]
* **Cause:** The entered work order quantity is zero or negative[^r21].
* **Remedy:** Enter a positive numeric value greater than zero in the quantity (`QTY`) field[^r21].
* **Raised by:** `wo_save`[^r21], `wo_search`[^r23].

### ERR-WO-0310
* **Message:** COMPONENT SHORTAGE (`<itm_cd>`)[^r5][^r20]
* **Cause:** Required bill of materials components for the item are unavailable in stock during release[^r20].
* **Remedy:** Check inventory levels for the flagged component item code, replenish stock, or expedite incoming allocations as outlined in [[err-wo-0310|ERR-WO-0310]][^r20].
* **Raised by:** `wo_release`[^r20].

### ERR-WO-0801
* **Message:** WORK ORDER CLOSED (`<status>`)[^r6][^r14][^r16]
* **Cause:** An operation was attempted on a work order that has already been closed[^r14][^r16].
* **Remedy:** Select an open work order; closed orders cannot be cancelled or modified[^r14][^r16].
* **Raised by:** `wo_cancel`[^r14], `wo_close`[^r16].

## Versions and conflicts

* **ERR-WO-0001 definition:** Today, the backend YAML service definitions and the [[data-data-dictionary|data dictionary]] define ERR-WO-0001 as `WORK ORDER NOT FOUND` raised by `wo_cancel`, `wo_close`, `wo_get`, and `wo_release` when a work order does not exist[^r1][^r13][^r15][^r17][^r18]. In contrast, [[man-prd-72|MAN-PRD-72]] (v7.2.3, 2025-01-15, p. 6) documents ERR-WO-0001 as `Work order save failed` raised by `wo_save` due to omitted header fields or database locks[^r7] (`contradiction`).
* **ERR-WO-0007 definition:** In the data dictionary and service definitions, ERR-WO-0007 represents `WORK ORDER NOT RELEASED` / `WORK ORDER NOT IN DRAFT (<status>)` raised by `wo_release` when releasing a non-draft order[^r2][^r19]. [[man-prd-72|MAN-PRD-72]] documents ERR-WO-0007 as `Mandatory fields missing` when `ITEM CD`, `QTY`, `START DT`, `WORK CENTRE`, or `CC CD` are left empty during save[^r8] (`contradiction`).
* **ERR-WO-0105 definition:** Service definitions and the data dictionary specify ERR-WO-0105 as `DATE IN PAST` raised by `wo_save` and `wo_search` when start dates are set in the past[^r3][^r22][^r24]. [[man-prd-72|MAN-PRD-72]] documents ERR-WO-0105 as `Insufficient component stock for release` raised by `wo_release` during warehouse reservation shortages[^r9] (`contradiction`).
* **ERR-WO-0201 definition:** Service definitions and the data dictionary specify ERR-WO-0201 as `QTY MUST BE > 0` raised by `wo_save` and `wo_search` for non-positive quantities[^r4][^r21][^r23]. [[man-prd-72|MAN-PRD-72]] documents ERR-WO-0201 as `Work order cannot be closed with open transactions` raised by `wo_close` for unposted material movements, open shop-floor bookings, or unresolved inspection records[^r10] (`contradiction`).
* **ERR-WO-0310 definition:** Service definitions and the data dictionary define ERR-WO-0310 as `COMPONENT SHORTAGE (<itm_cd>)` raised by `wo_release` when BOM components are unavailable[^r5][^r20]. [[man-prd-72|MAN-PRD-72]] documents ERR-WO-0310 as `Cancellation reason required` raised by `wo_cancel` when the `REASON` field is blank[^r11] (`contradiction`).
* **ERR-WO-0801 definition:** Service definitions and the data dictionary define ERR-WO-0801 as `WORK ORDER CLOSED (<status>)` raised by `wo_cancel` and `wo_close` when operating on closed orders[^r6][^r14][^r16]. [[man-prd-72|MAN-PRD-72]] documents ERR-WO-0801 as `Invalid status transition` for invalid state actions such as releasing a closed order or modifying a cancelled order[^r12] (`contradiction`).

## See also

* [[err-wo-0310|ERR-WO-0310 Component Shortage on Work Order Release]]
* [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]
* [[services-prd-wo|PRD wo services]]
* [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]]
* [[data-data-dictionary|Ledgerline_7.2_tables_and_fields]]
* [[sop-prd-001|SOP-PRD-001 Work Order Release and Backflush]]

## References

[^r1]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-WO-0001, SHEET Error codes
[^r7]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 6, Messages
[^r13]: 04_service_definitions/production/wo_cancel.yaml, errors
[^r15]: 04_service_definitions/production/wo_close.yaml, errors
[^r17]: 04_service_definitions/production/wo_get.yaml, errors
[^r18]: 04_service_definitions/production/wo_release.yaml, errors
[^r21]: 04_service_definitions/production/wo_save.yaml, errors
[^r23]: 04_service_definitions/production/wo_search.yaml, errors
[^r2]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-WO-0007, SHEET Error codes
[^r19]: 04_service_definitions/production/wo_release.yaml, errors
[^r3]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-WO-0105, SHEET Error codes
[^r22]: 04_service_definitions/production/wo_save.yaml, errors
[^r24]: 04_service_definitions/production/wo_search.yaml, errors
[^r4]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-WO-0201, SHEET Error codes
[^r5]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-WO-0310, SHEET Error codes
[^r20]: 04_service_definitions/production/wo_release.yaml, errors
[^r6]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-WO-0801, SHEET Error codes
[^r14]: 04_service_definitions/production/wo_cancel.yaml, errors
[^r16]: 04_service_definitions/production/wo_close.yaml, errors
[^r8]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 6, Messages
[^r9]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 6, Messages
[^r10]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 6, Messages
[^r11]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 6, Messages
[^r12]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 6, Messages
