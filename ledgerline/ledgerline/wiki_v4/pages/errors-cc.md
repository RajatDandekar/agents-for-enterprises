---
title: "Cost Centre Error Codes (ERR-CC-*)"
type: "error-list"
slug: "errors-cc"
summary: "Reference catalogue of cost centre error codes (ERR-CC-*) raised across finance, purchasing, admin, and production services in Ledgerline ERP 7.2."
audience: "staff"
status: "current"
sources: ["07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx", "02_procedures/SOP-FIN-001 Cost Centre Open and Close v1.1.pdf", "04_service_definitions/accounts_payable/exp_save.yaml", "04_service_definitions/accounts_payable/pcs_save.yaml", "04_service_definitions/admin/bud_save.yaml", "04_service_definitions/admin/bud_transfer.yaml", "04_service_definitions/admin/cc_close.yaml", "04_service_definitions/admin/cc_reopen.yaml", "04_service_definitions/admin/cc_save.yaml", "04_service_definitions/production/mnt_save.yaml", "04_service_definitions/production/wo_save.yaml", "04_service_definitions/purchase/bud_check.yaml", "04_service_definitions/purchase/cc_get.yaml", "04_service_definitions/purchase/pr_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-CC |
| Module | CC (Cost Centre) |
| System | Ledgerline ERP 7.2 |
| Status | Current |

This catalogue lists the ERR-CC-* error codes raised by the Ledgerline CC module and associated services across administration, accounts payable, purchasing, and production. These errors occur when cost centre records cannot be found, when actions are attempted against closed cost centres, or when open commitments prevent cost centre closure. Resolving these issues requires verifying cost centre codes or clearing outstanding transactions according to standard financial procedures.

### ERR-CC-0001: COST CENTRE NOT FOUND
* **Message**: `COST CENTRE NOT FOUND` [^r9][^r13]
* **Cause**: The CC module raises ERR-CC-0001 when a requested cost centre is not found [^r1].
* **Remedy**: Verify the cost centre identifier against the system records and ensure the code is valid before reattempting administration actions.
* **Raised by**: Raised during cost centre operations by [[services-adm-cc|cc_close]] and [[services-adm-cc|cc_reopen]] [^r9][^r13].

### ERR-CC-0009: COST CENTRE NOT FOUND
* **Message**: `COST CENTRE NOT FOUND` [^r5][^r6][^r7][^r8][^r10][^r14][^r15][^r16][^r17][^r18][^r19][^r20]
* **Cause**: Module CC raises this error when a referenced cost centre is not found or does not exist in the master records [^r1][^r17][^r19].
* **Remedy**: Confirm that the entered cost centre code is active and correctly typed on the originating document or service payload.
* **Raised by**: Raised by expense claim saving in [[services-ap-exp|exp_save]], petty cash saving in [[services-ap-pcs|pcs_save]], budget operations in [[services-adm-bud|bud_save]] and [[services-adm-bud|bud_transfer]], administration services [[services-adm-cc|cc_close]], [[services-adm-cc|cc_reopen]], and [[services-adm-cc|cc_save]], maintenance order saving in [[services-prd-mnt|mnt_save]], work order entry in [[services-prd-wo|wo_save]], budget validation in [[services-pur-bud|bud_check]], lookup requests in [[services-pur-cc|cc_get]], and purchase request saving in [[services-pur-pr|pr_save]] [^r5][^r6][^r7][^r8][^r10][^r14][^r15][^r16][^r17][^r18][^r19][^r20]. Links to detailed entry: [[err-cc-0009]].

### ERR-CC-0310: OPEN DOCUMENTS ON COST CENTRE
* **Message**: `OPEN DOCUMENTS ON COST CENTRE` [^r11]
* **Cause**: The CC module raises ERR-CC-0310 when attempting to close or modify a cost centre that still has open documents [^r2]. This occurs during cost centre closure when active commitments such as open purchase requisitions, incomplete purchase orders, or unposted goods receipts remain assigned to the cost centre [^r4].
* **Remedy**: Review, complete, cancel, or reassign all pending commitments, including requisitions, orders, and receipts, prior to executing cost centre closure under [[sop-fin-001|SOP-FIN-001 Cost Centre Open and Close]] [^r4].
* **Raised by**: Raised by [[services-adm-cc|cc_close]] [^r11]. Links to detailed entry: [[err-cc-0310|ERR-CC-0310 Cost centre has open documents]].

### ERR-CC-0801: COST CENTRE CLOSED (&lt;status&gt;)
* **Message**: `COST CENTRE CLOSED (<status>)` [^r12]
* **Cause**: Module CC raises ERR-CC-0801 when the cost centre is closed [^r3]. It is encountered by the system when an action targets a cost centre that is already closed [^r12].
* **Remedy**: Reopen the cost centre using appropriate administrative services or designate an active cost centre for the transaction.
* **Raised by**: Raised by [[services-adm-cc|cc_close]] [^r12].

## See also
* [[data-data-dictionary|Ledgerline_7.2_tables_and_fields]]
* [[man-dd-72-all|MAN-DD-72-ALL Ledgerline ERP 7.2 Data Dictionary: all]]
* [[sop-fin-001|SOP-FIN-001 Cost Centre Open and Close]]
* [[services-adm-cc|ADM cc services]]
* [[err-cc-0009|ERR-CC-0009]]
* [[err-cc-0310|ERR-CC-0310 Cost centre has open documents]]
* [[errors-bud|ERR-BUD error codes]]
* [[errors-pr|ERR-PR Error Codes]]
* [[errors-wo|ERR-WO error codes]]

## References

[^r9]: 04_service_definitions/admin/cc_close.yaml, errors
[^r13]: 04_service_definitions/admin/cc_reopen.yaml, errors
[^r1]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-CC-0001, SHEET Error codes
[^r5]: 04_service_definitions/accounts_payable/exp_save.yaml, errors
[^r6]: 04_service_definitions/accounts_payable/pcs_save.yaml, errors
[^r7]: 04_service_definitions/admin/bud_save.yaml, errors
[^r8]: 04_service_definitions/admin/bud_transfer.yaml, errors
[^r10]: 04_service_definitions/admin/cc_close.yaml, errors
[^r14]: 04_service_definitions/admin/cc_reopen.yaml, errors
[^r15]: 04_service_definitions/admin/cc_save.yaml, errors
[^r16]: 04_service_definitions/production/mnt_save.yaml, errors
[^r17]: 04_service_definitions/production/wo_save.yaml, errors
[^r18]: 04_service_definitions/purchase/bud_check.yaml, errors
[^r19]: 04_service_definitions/purchase/cc_get.yaml, errors
[^r20]: 04_service_definitions/purchase/pr_save.yaml, errors
[^r11]: 04_service_definitions/admin/cc_close.yaml, errors
[^r2]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-CC-0310, SHEET Error codes
[^r4]: 02_procedures/SOP-FIN-001 Cost Centre Open and Close v1.1.pdf, p. 3, Common mistakes
[^r12]: 04_service_definitions/admin/cc_close.yaml, errors
[^r3]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-CC-0801, SHEET Error codes
