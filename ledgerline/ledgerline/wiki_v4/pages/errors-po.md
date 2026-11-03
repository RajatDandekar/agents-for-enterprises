---
title: "ERR-PO Error Codes"
type: "error-list"
slug: "errors-po"
summary: "Reference list of ERR-PO error codes raised across Ledgerline purchase order services, including message text, causes, and remedies."
audience: "staff"
status: "mixed"
sources: ["07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx", "03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf", "03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/old/Ledgerline 7.0 Purchasing Manual (2015).pdf", "04_service_definitions/purchase/po_amend.yaml", "04_service_definitions/purchase/po_approve.yaml", "04_service_definitions/purchase/po_cancel.yaml", "04_service_definitions/purchase/po_get.yaml", "04_service_definitions/purchase/po_reject.yaml", "04_service_definitions/purchase/po_release.yaml", "04_service_definitions/purchase/po_save.yaml", "04_service_definitions/purchase/pr_approve.yaml", "08_release_notes/RN-7.2.3-P1 Ledgerline Patch Notes.pdf", "11_training/QRC-03 ERR-PO-0412 quick fix.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-PO |
| Module | Purchasing (PO) |
| System | Ledgerline ERP 7.2 |
| Status | Current |

The ERR-PO series comprises system error codes raised by Ledgerline ERP 7.2 during purchase order processing [^r1][^r20]. These errors validate order headers, line items, approval status, direct order thresholds, and requisition linkage across purchase order entry, amendment, approval, and release services [^r20][^r24][^r27][^r72]. Resolving these errors ensures that purchase transactions strictly comply with requisition requirements, supplier tax classifications, and system status workflows [^r23][^r26][^r30].

### ERR-PO-0001
* **Message**: `PO NOT FOUND` [^r1][^r20].
* **Cause**: The purchase order number entered does not exist within the system [^r20][^r58].
* **Remedy**: Verify the purchase order number before re-executing the operation [^r20][^r58].
* **Raised by**: `po_get`, `po_approve`, `po_release`, `po_amend`, `po_cancel`, `grn_save`, and `inv_save` [^r20][^r63][^r65][^r67][^r69][^r71].

### ERR-PO-0105
* **Message**: `NEED DATE IN PAST` [^r2][^r21].
* **Cause**: The need-by date specified on the purchase order header or line is set to a date before today [^r2][^r21][^r54].
* **Remedy**: Adjust the need date to the current date or a future date [^r21][^r54].
* **Raised by**: `po_save` [^r21][^r73].

### ERR-PO-0201
* **Message**: `QTY MUST BE > 0` [^r3][^r22].
* **Cause**: The line quantity entered on the purchase order is zero or negative [^r22][^r53][^r73].
* **Remedy**: Enter a positive line quantity greater than zero [^r22][^r53].
* **Raised by**: `po_save` [^r22][^r73].

### ERR-PO-0412
* **Message**: `TAX CODE DOES NOT MATCH SUPPLIER COUNTRY [<country_code>]` [^r4][^r81].
* **Cause**: The tax code entered on the purchase order header or line does not match the supplier country recorded in the supplier master record, such as applying a UK tax code to an overseas supplier or vice versa [^r23][^r47][^r81][^r82].
* **Remedy**: Ensure the tax code aligns with the supplier's country, using reverse-charge `-RC` codes for non-UK suppliers [^r47][^r81].
* **Raised by**: `po_save` [^r23][^r76].
* **Details**: See [[err-po-0412]].

### ERR-PO-0602
* **Message**: `SOURCE PR MANDATORY FOR STD PO` [^r5][^r24].
* **Cause**: A standard purchase order (`STD`) is saved without referencing an approved source purchase requisition [^r24][^r50][^r74].
* **Remedy**: Populate a valid, approved purchase requisition reference in the source PR field [^r24][^r50].
* **Raised by**: `po_save` [^r24][^r74].

### ERR-PO-0603
* **Message**: `SOURCE PR NOT APPROVED (<status>)` [^r6][^r25].
* **Cause**: The referenced source purchase requisition is not in approved status `AP` [^r25][^r51][^r74].
* **Remedy**: Ensure the referenced requisition is fully approved before linking it to the standard purchase order [^r25][^r51].
* **Raised by**: `po_save` [^r25][^r74].

### ERR-PO-0604
* **Message**: `ITEM/QTY NOT AS PER PR` [^r7][^r26].
* **Cause**: The purchase order line item differs from the source requisition or the ordered quantity exceeds the requisition quantity [^r26][^r52][^r74].
* **Remedy**: Align the purchase order part number and order quantity with the lines approved on the source purchase requisition [^r26][^r52].
* **Raised by**: `po_save` [^r26][^r74].

### ERR-PO-0610
* **Message**: `DIRECT PO LIMIT 50000 EXCEEDED, RAISE PR` [^r8][^r27].
* **Cause**: A direct order (`DIR`) exceeds the gross value limit of 50,000 [^r27][^r48][^r75].
* **Remedy**: Raise a purchase requisition on [[screen-pur-pr-01|PUR-PR-01]] rather than entering a direct purchase order [^r27][^r48].
* **Raised by**: `po_save` [^r27][^r75].
* **Details**: See [[err-po-0610]].

### ERR-PO-0611
* **Message**: `DIR PO CANNOT REFER PR` [^r9][^r28].
* **Cause**: A source purchase request reference is populated on a direct order (`DIR`) [^r28][^r49][^r75].
* **Remedy**: Clear the source requisition reference field, or change the purchase order type from `DIR` to `STD` [^r28][^r49].
* **Raised by**: `po_save` [^r28][^r75].

### ERR-PO-0702
* **Message**: `PO NOT PENDING APPROVAL (<status>)` [^r10][^r66].
* **Cause**: An approval or rejection action is attempted on a purchase order that is not in pending approval status `PA` [^r29][^r56][^r66][^r70].
* **Remedy**: Verify the current order status and only submit approval or rejection against orders currently in `PA` status [^r29][^r56].
* **Raised by**: `po_approve` and `po_reject` [^r29][^r66][^r70].

### ERR-PO-0715
* **Message**: `DOCUMENT NOT IN RELEASABLE STATUS (<status>)` [^r11][^r72].
* **Cause**: A purchase order release is attempted on a document that is not in approved status `AP` [^r30][^r55][^r72].
* **Remedy**: Obtain the necessary approvals so the order reaches `AP` status before executing document release [^r30][^r55].
* **Raised by**: `po_release` [^r30][^r72].

### ERR-PO-0801
* **Message**: `PO CLOSED (<status>)` [^r12][^r64].
* **Cause**: An amendment or cancellation operation is attempted on a purchase order that is in cancelled (`CN`), rejected (`RJ`), or closed (`CL`) status [^r31][^r57][^r64][^r68].
* **Remedy**: Closed, rejected, or cancelled orders cannot be modified or re-cancelled; raise a new order if required [^r31][^r57].
* **Raised by**: `po_amend` and `po_cancel` [^r31][^r64][^r68].
* **Details**: See [[err-po-0801]].

## Versions and conflicts

* **ERR-PO-0412 message text and validation**: Under current Ledgerline 7.2 releases, ERR-PO-0412 validates the tax code against the supplier country and displays `TAX CODE DOES NOT MATCH SUPPLIER COUNTRY [<country_code>]` [^r4][^r23][^r47][^r81]. In superseded Ledgerline ERP 7.0 documentation, the error produced `TAX REGION DOES NOT MATCH SUPPLIER STATE` in the screen status bar when the tax code region conflicted with the supplier state [^r83] (kind: `superseded`).

## See also

* [[err-po-0412|ERR-PO-0412 TAX CODE DOES NOT MATCH SUPPLIER COUNTRY]]
* [[err-po-0610|ERR-PO-0610 Direct order exceeds maximum allowed value]]
* [[err-po-0801|ERR-PO-0801 Order in CN, RJ or CL status cannot be amended]]
* [[services-pur-po|PUR po services]]
* [[screen-pur-po-01|PUR-PO-01 Purchase Order Entry]]
* [[screen-pur-poa-04|PUR-POA-04 Purchase Order Approval]]
* [[screen-pur-pom-06|PUR-POM-06 Purchase Order Amendment]]
* [[screen-pur-por-05|PUR-POR-05 Purchase Order Release]]
* [[screen-pur-pr-01|PUR-PR-01 Purchase Request Entry]]
* [[data-tax-codes|Tax codes]]

## References

[^r1]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PO-0001, SHEET Error codes
[^r20]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 17, ERR-PO-0001
[^r24]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 18, ERR-PO-0602
[^r27]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 18, ERR-PO-0610
[^r72]: 04_service_definitions/purchase/po_release.yaml, errors
[^r23]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 17, ERR-PO-0412
[^r26]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 18, ERR-PO-0604
[^r30]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 18, ERR-PO-0715
[^r58]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 11, §17.15 ERR-PO-0001 PO not found
[^r63]: 04_service_definitions/purchase/po_amend.yaml, errors
[^r65]: 04_service_definitions/purchase/po_approve.yaml, errors
[^r67]: 04_service_definitions/purchase/po_cancel.yaml, errors
[^r69]: 04_service_definitions/purchase/po_get.yaml, errors
[^r71]: 04_service_definitions/purchase/po_release.yaml, errors
[^r2]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PO-0105, SHEET Error codes
[^r21]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 17, ERR-PO-0105
[^r54]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 11, §17.11 ERR-PO-0105 and ERR-PR-0105 Need date in past
[^r73]: 04_service_definitions/purchase/po_save.yaml, errors
[^r3]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PO-0201, SHEET Error codes
[^r22]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 17, ERR-PO-0201
[^r53]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 11, §17.10 ERR-PO-0201 Quantity must be more than zero
[^r4]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PO-0412, SHEET Error codes
[^r81]: 08_release_notes/RN-7.2.3-P1 Ledgerline Patch Notes.pdf, p. 2, §2. Changes
[^r47]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 10, §17.2 ERR-PO-0412 Tax code does not match supplier country
[^r82]: 11_training/QRC-03 ERR-PO-0412 quick fix.pdf, p. 1, Steps
[^r76]: 04_service_definitions/purchase/po_save.yaml, errors
[^r5]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PO-0602, SHEET Error codes
[^r50]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 10, §17.7 ERR-PO-0602 Source PR mandatory for STD PO
[^r74]: 04_service_definitions/purchase/po_save.yaml, errors
[^r6]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PO-0603, SHEET Error codes
[^r25]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 18, ERR-PO-0603
[^r51]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 11, §17.8 ERR-PO-0603 Source PR not approved
[^r7]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PO-0604, SHEET Error codes
[^r52]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 11, §17.9 ERR-PO-0604 Item or quantity not as per PR
[^r8]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PO-0610, SHEET Error codes
[^r48]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 10, §17.4 ERR-PO-0610 Direct PO limit exceeded, raise PR
[^r75]: 04_service_definitions/purchase/po_save.yaml, errors
[^r9]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PO-0611, SHEET Error codes
[^r28]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 18, ERR-PO-0611
[^r49]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 10, §17.5 ERR-PO-0611 Direct PO cannot refer PR
[^r10]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PO-0702, SHEET Error codes
[^r66]: 04_service_definitions/purchase/po_approve.yaml, errors
[^r29]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 18, ERR-PO-0702
[^r56]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 11, §17.13 ERR-PO-0702 PO not pending approval
[^r70]: 04_service_definitions/purchase/po_reject.yaml, errors
[^r11]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PO-0715, SHEET Error codes
[^r55]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 11, §17.12 ERR-PO-0715 Document not in releasable status
[^r12]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PO-0801, SHEET Error codes
[^r64]: 04_service_definitions/purchase/po_amend.yaml, errors
[^r31]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 18, ERR-PO-0801
[^r57]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 11, §17.14 ERR-PO-0801 PO closed
[^r68]: 04_service_definitions/purchase/po_cancel.yaml, errors
[^r83]: 03_ledgerline_manuals/old/Ledgerline 7.0 Purchasing Manual (2015).pdf, p. 3, §17. Messages
