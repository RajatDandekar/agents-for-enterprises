---
title: "ERR-RTV Return to Vendor Error Codes"
type: "error-list"
slug: "errors-rtv"
summary: "Catalogue of Ledgerline ERP 7.2 Return to Vendor error codes (ERR-RTV-*) raised across inventory RTV services and screens."
audience: "staff"
status: "current"
sources: ["07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx", "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "04_service_definitions/inventory/rtv_cancel.yaml", "04_service_definitions/inventory/rtv_get.yaml", "04_service_definitions/inventory/rtv_post.yaml", "04_service_definitions/inventory/rtv_save.yaml", "04_service_definitions/inventory/rtv_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-RTV |
| Module | Inventory (INV) |
| Reference manual | [[man-err-72|MAN-ERR-72]] |
| Data dictionary | [[man-dd-72-all|MAN-DD-72-ALL]] |

Error codes under the `ERR-RTV` prefix are returned by Ledgerline ERP 7.2 during inventory return to vendor operations, such as creating, posting, or cancelling return documents on [[screen-inv-rtv-07|INV-RTV-07 Return To Vendor Entry]][^r1][^r7]. They enforce transactional constraints such as receipt quantity caps, document lifecycle statuses, and invoice-matching boundaries established under [[sop-inv-002|SOP-INV-002 Returns to Vendor (RTV)]][^r4][^r5][^r8]. As of 26 October 2026, these messages govern operations handled by the [[services-inv-rtv|INV rtv services]][^r7][^r13].

### ERR-RTV-0001
* **Message**: `RETURN TO VENDOR NOT FOUND`[^r1][^r13][^r15][^r16]
* **Cause**: The return to vendor document key does not exist in the system[^r7].
* **Remedy**: Verify the RTV document number and retry the enquiry or operation[^r7][^r15].
* **Raised by**: Services `rtv_get`, `rtv_post`, and `rtv_cancel`[^r7][^r13][^r15][^r16].

### ERR-RTV-0007
* **Message**: `RETURN TO VENDOR NOT IN DRAFT (<status>)`[^r2][^r17]
* **Cause**: An operation requiring the RTV record to be in Draft or pending status was attempted on a document in a different status[^r8][^r17].
* **Remedy**: Confirm the current lifecycle status of the RTV document before attempting to post[^r8][^r17].
* **Raised by**: Service `rtv_post`[^r8][^r17].

### ERR-RTV-0201
* **Message**: `QTY MUST BE > 0`[^r3][^r18][^r21]
* **Cause**: The entered return-to-vendor quantity is zero or negative[^r9][^r18].
* **Remedy**: Enter a positive line quantity greater than zero[^r9][^r18].
* **Raised by**: Services `rtv_save` and `rtv_search`[^r9][^r18][^r21].

### ERR-RTV-0204
* **Message**: `QTY EXCEEDS QTY RECEIVED (<qty>)`[^r4][^r19]
* **Cause**: The return quantity entered on the line exceeds the quantity originally received on the referenced Goods Receipt Note (GRN)[^r4][^r10][^r19].
* **Remedy**: Reduce the RTV quantity so that it does not exceed the received GRN quantity[^r4][^r10][^r19].
* **Raised by**: Service `rtv_save`[^r10][^r19].

### ERR-RTV-0230
* **Message**: `GRN ALREADY INVOICED, RAISE DEBIT NOTE`[^r5][^r20]
* **Cause**: An attempt was made to save an RTV against a GRN that has already been matched and invoiced[^r5][^r11][^r20].
* **Remedy**: Refer to [[err-rtv-0230|ERR-RTV-0230]] and follow accounts payable procedures to raise a debit note instead of processing a direct stock return[^r5][^r11][^r20].
* **Raised by**: Service `rtv_save`[^r11][^r20].

### ERR-RTV-0801
* **Message**: `RETURN TO VENDOR CLOSED (<status>)`[^r6][^r14]
* **Cause**: A cancellation attempt was made on an RTV document that is already closed, cancelled, or rejected[^r6][^r12][^r14].
* **Remedy**: Check the RTV document status; closed or cancelled records cannot be cancelled again[^r12][^r14].
* **Raised by**: Service `rtv_cancel`[^r12][^r14].

## See also
* [[err-rtv-0230|ERR-RTV-0230 Invoice already posted against receipt]]
* [[services-inv-rtv|INV rtv services]]
* [[screen-inv-rtv-07|INV-RTV-07 Return To Vendor Entry]]
* [[sop-inv-002|SOP-INV-002 Returns to Vendor (RTV)]]
* [[man-err-72|MAN-ERR-72 Ledgerline ERP 7.2 Message and Error Code]]
* [[man-dd-72-all|MAN-DD-72-ALL Ledgerline ERP 7.2 Data Dictionary: all]]
* [[data-data-dictionary|Ledgerline_7.2_tables_and_fields]]

## References

[^r1]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-RTV-0001, SHEET Error codes
[^r7]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 21
[^r4]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-RTV-0204, SHEET Error codes
[^r5]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-RTV-0230, SHEET Error codes
[^r8]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 21
[^r13]: 04_service_definitions/inventory/rtv_cancel.yaml, errors
[^r15]: 04_service_definitions/inventory/rtv_get.yaml, errors
[^r16]: 04_service_definitions/inventory/rtv_post.yaml, errors
[^r2]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-RTV-0007, SHEET Error codes
[^r17]: 04_service_definitions/inventory/rtv_post.yaml, errors
[^r3]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-RTV-0201, SHEET Error codes
[^r18]: 04_service_definitions/inventory/rtv_save.yaml, errors
[^r21]: 04_service_definitions/inventory/rtv_search.yaml, errors
[^r9]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 21
[^r19]: 04_service_definitions/inventory/rtv_save.yaml, errors
[^r10]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 21
[^r20]: 04_service_definitions/inventory/rtv_save.yaml, errors
[^r11]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 21
[^r6]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-RTV-0801, SHEET Error codes
[^r14]: 04_service_definitions/inventory/rtv_cancel.yaml, errors
[^r12]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 22
