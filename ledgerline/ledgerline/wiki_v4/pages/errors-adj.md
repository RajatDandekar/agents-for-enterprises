---
title: "Stock Adjustment Error Codes (ERR-ADJ-*)"
type: "error-list"
slug: "errors-adj"
summary: "Ledgerline error codes under prefix ERR-ADJ- raised during stock adjustment processing, approvals, and inventory balance validations."
audience: "staff"
status: "current"
sources: ["07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx", "03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "04_service_definitions/inventory/adj_approve.yaml", "04_service_definitions/inventory/adj_cancel.yaml", "04_service_definitions/inventory/adj_get.yaml", "04_service_definitions/inventory/adj_post.yaml", "04_service_definitions/inventory/adj_save.yaml", "04_service_definitions/inventory/adj_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-ADJ- |
| Module | ADJ (Inventory Adjustment) |
| Applicable system | Ledgerline ERP 7.2 |
| Manual | MAN-INV-72 |

The ERR-ADJ-* error codes are raised by Ledgerline ERP 7.2 when creating, updating, posting, or approving inventory stock adjustments [^r1][^r11][^r19]. As of 26 October 2026, these codes enforce document state validation, authorization boundaries, and quantity constraints across the adjustment services [^r2][^r4][^r13][^r19]. They are primarily encountered on screen [[screen-inv-adj-05|INV-ADJ-05 Stock Adjustment Entry]] and through the [[services-inv-adj|INV adj services]] group [^r6][^r11][^r19].

### ERR-ADJ-0001

* **Message**: `STOCK ADJUSTMENT NOT FOUND` [^r11][^r16][^r17]
* **Cause**: The adjustment document number entered cannot be found in the database or does not exist [^r1][^r6].
* **Remedy**: Verify the stock adjustment document number and re-enter or locate the valid adjustment reference before retrying [^r6].
* **Raised by**: Raised by the ADJ module and service endpoints `adj_approve`, `adj_cancel`, `adj_get`, and `adj_post` [^r1][^r11][^r14][^r16][^r17].

### ERR-ADJ-0007

* **Message**: `STOCK ADJUSTMENT NOT IN DRAFT (<status>)` [^r12][^r18]
* **Cause**: The selected adjustment document is not in draft status, meaning its current state (such as already posted or voided) does not permit the requested action or modification [^r2][^r7][^r12][^r18].
* **Remedy**: Select a document that is in draft state or create a new adjustment document if further changes are required [^r7].
* **Raised by**: Raised by the ADJ module and service endpoints `adj_approve` and `adj_post` [^r2][^r12][^r18].

### ERR-ADJ-0201

* **Message**: `QTY MUST BE > 0` [^r19][^r20]
* **Cause**: The adjustment quantity entered is not greater than 0, or is formatted invalidly in the quantity entry field [^r3][^r8][^r19][^r20].
* **Remedy**: Enter a non-zero number greater than 0, formatting negative adjustments with a standard minus sign without spaces as required by the interface [^r3][^r8][^r19].
* **Raised by**: Raised by the ADJ module and service endpoints `adj_save` and `adj_search` [^r3][^r19][^r20].

### ERR-ADJ-0420

* **Message**: `ADJUSTMENT ABOVE STORES LIMIT, NEEDS PLANT HEAD` [^r13]
* **Cause**: The stock adjustment exceeds the role limit for Stores and requires Plant Head approval, or a negative adjustment exceeds available physical stock in the warehouse location [^r4][^r9][^r13].
* **Remedy**: Route the document to the Plant Head for approval or check recorded warehouse stock availability before adjusting [^r4][^r9][^r13].
* **Raised by**: Raised by the ADJ module and service endpoint `adj_approve` [^r4][^r13].

### ERR-ADJ-0801

* **Message**: `STOCK ADJUSTMENT CLOSED (<status>)` [^r15]
* **Cause**: An action was attempted on a stock adjustment that is already closed, or the entered `REASON CD` is not recognised by the parameter tables [^r5][^r10][^r15].
* **Remedy**: Confirm that the adjustment is open, or verify and select a valid reason code defined in the system tables [^r5][^r10].
* **Raised by**: Raised by the ADJ module and service endpoint `adj_cancel` [^r5][^r15].

## Versions and conflicts

* **ERR-ADJ-0420 definition**: Today's system service definition and data dictionary define ERR-ADJ-0420 as `ADJUSTMENT ABOVE STORES LIMIT, NEEDS PLANT HEAD`, raised when an adjustment exceeds the Stores role limit and requires Plant Head approval [^r4][^r13]. Conversely, [[man-inv-72|MAN-INV-72]] (v7.2.3, 15 January 2025) lists ERR-ADJ-0420 as an error indicating that a negative adjustment quantity exceeds the total available physical stock recorded in the warehouse location [^r9]. Kind: `contradiction`.
* **ERR-ADJ-0801 definition**: Today's system service definition and data dictionary define ERR-ADJ-0801 as `STOCK ADJUSTMENT CLOSED (<status>)`, raised when attempting an action on an already-closed adjustment [^r5][^r15]. [[man-inv-72|MAN-INV-72]] (v7.2.3, 15 January 2025) lists ERR-ADJ-0801 as being raised when an unrecognised value is entered in the `REASON CD` field [^r10]. Kind: `contradiction`.

## See also

* [[screen-inv-adj-05|INV-ADJ-05 Stock Adjustment Entry]]
* [[services-inv-adj|INV adj services]]
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]
* [[data-data-dictionary|Ledgerline_7.2_tables_and_fields]]
* [[errors-cnt|Stock Count Error Codes (ERR-CNT-*)]]
* [[errors-itm|ERR-ITM error codes]]
* [[errors-apr|Errors APR]]

## References

[^r1]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-ADJ-0001, SHEET Error codes
[^r11]: 04_service_definitions/inventory/adj_approve.yaml, errors
[^r19]: 04_service_definitions/inventory/adj_save.yaml, errors
[^r2]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-ADJ-0007, SHEET Error codes
[^r4]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-ADJ-0420, SHEET Error codes
[^r13]: 04_service_definitions/inventory/adj_approve.yaml, errors
[^r6]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 9, Messages
[^r16]: 04_service_definitions/inventory/adj_get.yaml, errors
[^r17]: 04_service_definitions/inventory/adj_post.yaml, errors
[^r14]: 04_service_definitions/inventory/adj_cancel.yaml, errors
[^r12]: 04_service_definitions/inventory/adj_approve.yaml, errors
[^r18]: 04_service_definitions/inventory/adj_post.yaml, errors
[^r7]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 9, Messages
[^r20]: 04_service_definitions/inventory/adj_search.yaml, errors
[^r3]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-ADJ-0201, SHEET Error codes
[^r8]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 9, Messages
[^r9]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 9, Messages
[^r15]: 04_service_definitions/inventory/adj_cancel.yaml, errors
[^r5]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-ADJ-0801, SHEET Error codes
[^r10]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 9, Messages
