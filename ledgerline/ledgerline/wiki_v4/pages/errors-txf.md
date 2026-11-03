---
title: "Stock Transfer Error Codes (ERR-TXF-*)"
type: "error-list"
slug: "errors-txf"
summary: "Ledgerline error codes with prefix ERR-TXF raised during stock transfer entry, posting, saving, and cancellation."
audience: "staff"
status: "current"
sources: ["07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx", "03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "04_service_definitions/inventory/txf_cancel.yaml", "04_service_definitions/inventory/txf_get.yaml", "04_service_definitions/inventory/txf_post.yaml", "04_service_definitions/inventory/txf_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

Stock transfer error codes prefixed with `ERR-TXF-*` are emitted by Ledgerline inventory services and screen [[screen-inv-trf-04|INV-TRF-04 Stock Transfer Entry]][^r7]. They handle validation, concurrency, status checks, and data integrity across the [[services-inv-txf|INV txf services]] group[^r11][^r13][^r14][^r16]. In current operational service definitions and the [[data-data-dictionary|data dictionary]], these codes reflect specific record and field constraints[^r1][^r2][^r3][^r4][^r5].

### ERR-TXF-0001

* **Message:** STOCK TRANSFER NOT FOUND[^r1][^r11][^r13][^r14]
* **Cause:** Raised during transfer retrieval operations or attempts to execute actions on nonexistent transfer records[^r11][^r13][^r14].
* **Remedy:** Verify the specified transfer number exists before re-attempting the operation.
* **Raised by:** Service `txf_get`[^r13], `txf_post`[^r14], and `txf_cancel`[^r11].

### ERR-TXF-0007

* **Message:** STOCK TRANSFER NOT IN DRAFT (<status>)[^r2][^r15]
* **Cause:** An attempt is made to post a stock transfer that is not currently in draft status[^r15].
* **Remedy:** Ensure the transfer is in draft status before posting[^r15].
* **Raised by:** Service `txf_post`[^r15].

### ERR-TXF-0201

* **Message:** QTY MUST BE > 0[^r3][^r16]
* **Cause:** The quantity specified for the stock transfer is less than or equal to zero during save operations[^r3][^r16].
* **Remedy:** Enter a positive quantity greater than zero.
* **Raised by:** Service `txf_save`[^r16].

### ERR-TXF-0310

* **Message:** FROM AND TO WAREHOUSE ARE THE SAME[^r4][^r17]
* **Cause:** The destination warehouse matches the source warehouse on the transfer save request[^r4][^r17].
* **Remedy:** Select distinct source and destination warehouses.
* **Raised by:** Service `txf_save`[^r17].

### ERR-TXF-0801

* **Message:** STOCK TRANSFER CLOSED (<status>)[^r5][^r12]
* **Cause:** An action is attempted on a stock transfer record that is already closed[^r5][^r12].
* **Remedy:** Verify the transfer status and avoid re-processing closed records[^r5][^r12].
* **Raised by:** Service `txf_cancel`[^r12].

## Versions and conflicts

* **ERR-TXF-0001 message and meaning:** Under current service definitions and [[man-dd-72-all|data dictionary]] definitions, ERR-TXF-0001 is "STOCK TRANSFER NOT FOUND" raised by `txf_get`, `txf_post`, and `txf_cancel`[^r1][^r11][^r13][^r14]. In user manual [[man-inv-72|MAN-INV-72]], it is documented as raised by `txf_save` when mandatory fields ITEM CD, FROM WHS, TO WHS, or QTY are omitted[^r6]. Kind: `contradiction`[^r1][^r6][^r11][^r13][^r14].
* **ERR-TXF-0007 meaning:** Under the data dictionary and `txf_post` service definition, ERR-TXF-0007 represents "STOCK TRANSFER NOT IN DRAFT (<status>)"[^r2][^r15]. In MAN-INV-72, it is documented as raised when FROM WHS and TO WHS specify identical locations on screen INV-TRF-04[^r7]. Kind: `contradiction`[^r2][^r7][^r15].
* **ERR-TXF-0201 meaning:** The data dictionary and `txf_save` definition define ERR-TXF-0201 as "QTY MUST BE > 0"[^r3][^r16]. MAN-INV-72 documents it as raised when a transfer record is locked by another network user editing or updating the specified TXF NO[^r8]. Kind: `contradiction`[^r3][^r8][^r16].
* **ERR-TXF-0310 meaning:** The data dictionary and `txf_save` definition define ERR-TXF-0310 as "FROM AND TO WAREHOUSE ARE THE SAME"[^r4][^r17]. MAN-INV-72 documents it as indicating the selected transfer has already been posted or cancelled and cannot be altered[^r9]. Kind: `contradiction`[^r4][^r9][^r17].
* **ERR-TXF-0801 meaning:** The data dictionary and `txf_cancel` service definition define ERR-TXF-0801 as "STOCK TRANSFER CLOSED (<status>)"[^r5][^r12]. MAN-INV-72 documents it as a general posting failure in STOCK TRANSFER POST or an invalid cancellation attempt on an already committed or cancelled transfer[^r10]. Kind: `contradiction`[^r5][^r10][^r12].

## See also

* [[screen-inv-trf-04|INV-TRF-04 Stock Transfer Entry]]
* [[services-inv-txf|INV txf services]]
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]
* [[data-data-dictionary|Ledgerline_7.2_tables_and_fields]]
* [[errors-adj|Stock Adjustment Error Codes (ERR-ADJ-*)]]
* [[errors-cnt|Stock Count Error Codes (ERR-CNT-*)]]

## References

[^r7]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 5, Messages
[^r11]: 04_service_definitions/inventory/txf_cancel.yaml, errors
[^r13]: 04_service_definitions/inventory/txf_get.yaml, errors
[^r14]: 04_service_definitions/inventory/txf_post.yaml, errors
[^r16]: 04_service_definitions/inventory/txf_save.yaml, errors
[^r1]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-TXF-0001, SHEET Error codes
[^r2]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-TXF-0007, SHEET Error codes
[^r3]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-TXF-0201, SHEET Error codes
[^r4]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-TXF-0310, SHEET Error codes
[^r5]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-TXF-0801, SHEET Error codes
[^r15]: 04_service_definitions/inventory/txf_post.yaml, errors
[^r17]: 04_service_definitions/inventory/txf_save.yaml, errors
[^r12]: 04_service_definitions/inventory/txf_cancel.yaml, errors
[^r6]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 5, Messages
[^r8]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 5, Messages
[^r9]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 5, Messages
[^r10]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 5, Messages
