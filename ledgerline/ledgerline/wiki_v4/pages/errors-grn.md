---
title: "Errors GRN Goods Receipt Note"
type: "error-list"
slug: "errors-grn"
summary: "Ledgerline error codes for goods receipt notes (ERR-GRN-*), detailing message texts, validation causes, remedies, and calling inventory services."
audience: "staff"
status: "current"
sources: ["07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx", "04_service_definitions/inventory/grn_get.yaml", "04_service_definitions/inventory/grn_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-GRN |
| Module | Inventory (INV) / Goods Receipt Note |
| Source | Data Dictionary & Service Definitions |
| Target Screens | screen-inv-grn-03 |
| Related Services | services-inv-grn |

The `ERR-GRN-*` error code series covers validation failures raised when creating, modifying, or retrieving goods receipt notes in Ledgerline ERP 7.2. These errors safeguard inventory integrity by preventing receipt against unreleased or completed purchase orders, blocking invalid quantities, and ensuring missing GRN records are detected. In everyday warehouse operations, they are encountered primarily through [[screen-inv-grn-03|INV-GRN-03]] and back-end inventory receipt services.

### ERR-GRN-0001: GRN NOT FOUND

* **Message:** `GRN NOT FOUND` [^r1][^r6]
* **Cause:** The requested Goods Receipt Note record does not exist in the GRN module [^r1][^r6].
* **Remedy:** Verify the GRN number entered and check whether the receipt record was saved or purged.
* **Raised by:** Service `grn_get` [^r6]; [[data-data-dictionary|Data Dictionary]] error code reference [^r1].

### ERR-GRN-0102: PO NOT RELEASED (<status>)

* **Message:** `PO NOT RELEASED (<status>)` [^r2][^r7]
* **Cause:** A goods receipt was attempted against a purchase order that is not in released status [^r2][^r7].
* **Remedy:** Ensure the purchase order has completed the required approval workflow and is in released status before booking the receipt (see [[err-grn-0102]]).
* **Raised by:** Service `grn_save` [^r7]; [[data-data-dictionary|Data Dictionary]] error code reference [^r2].

### ERR-GRN-0105: PO ALREADY FULLY RECEIVED

* **Message:** `PO ALREADY FULLY RECEIVED` [^r3][^r8]
* **Cause:** A receipt was attempted on a purchase order line or order that has no remaining open balance to receive [^r3][^r8].
* **Remedy:** Check the open order balance against previous receipts; if additional items have arrived, raise a supplementary purchase order or inspect line quantities.
* **Raised by:** Service `grn_save` [^r8]; [[data-data-dictionary|Data Dictionary]] error code reference [^r3].

### ERR-GRN-0201: QTY MUST BE > 0

* **Message:** `QTY MUST BE > 0` [^r4][^r9]
* **Cause:** A GRN line was submitted with a receipt quantity of zero or a negative value [^r4][^r9].
* **Remedy:** Enter a positive receipt quantity greater than zero on the GRN line.
* **Raised by:** Service `grn_save` [^r9]; [[data-data-dictionary|Data Dictionary]] error code reference [^r4].

### ERR-GRN-0204: QTY EXCEEDS PO BALANCE (<qty>)

* **Message:** `QTY EXCEEDS PO BALANCE (<qty>)` [^r5][^r10]
* **Cause:** The quantity entered for receipt exceeds the open balance remaining on the purchase order [^r5][^r10].
* **Remedy:** Adjust the receipt quantity to match the remaining open purchase order balance, or seek authorisation for over-receipt where permissible (see [[err-grn-0204]]).
* **Raised by:** Service `grn_save` [^r10]; [[data-data-dictionary|Data Dictionary]] error code reference [^r5].

## See also

* [[err-grn-0102|ERR-GRN-0102 Purchase order not released]]
* [[err-grn-0204|ERR-GRN-0204 Over-receipt exceeds order balance]]
* [[services-inv-grn|INV grn services]]
* [[screen-inv-grn-03|INV-GRN-03 Goods Receipt Note (Grn)]]
* [[errors-po|ERR-PO Error Codes]]
* [[errors-rtv|ERR-RTV Return to Vendor Error Codes]]
* [[sop-ap-001|SOP-AP-001 Three-Way Invoice Matching]]
* [[data-data-dictionary|Ledgerline_7.2_tables_and_fields]]

## References

[^r1]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-GRN-0001, SHEET Error codes
[^r6]: 04_service_definitions/inventory/grn_get.yaml, errors
[^r2]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-GRN-0102, SHEET Error codes
[^r7]: 04_service_definitions/inventory/grn_save.yaml, errors
[^r3]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-GRN-0105, SHEET Error codes
[^r8]: 04_service_definitions/inventory/grn_save.yaml, errors
[^r4]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-GRN-0201, SHEET Error codes
[^r9]: 04_service_definitions/inventory/grn_save.yaml, errors
[^r5]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-GRN-0204, SHEET Error codes
[^r10]: 04_service_definitions/inventory/grn_save.yaml, errors
