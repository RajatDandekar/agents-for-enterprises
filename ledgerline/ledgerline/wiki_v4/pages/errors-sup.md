---
title: "ERR-SUP Error Codes"
type: "error-list"
slug: "errors-sup"
summary: "Ledgerline error codes with prefix ERR-SUP, covering missing supplier codes, blocked supplier accounts, and duplicate VAT registration validation."
audience: "staff"
status: "current"
sources: ["07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx", "07_data_dictionary/code_lists.csv", "01_policies/POL-SUP-003 Supplier Policy v2.3.pdf", "03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf", "04_service_definitions/accounts_payable/adv_adjust.yaml", "04_service_definitions/accounts_payable/adv_save.yaml", "04_service_definitions/accounts_payable/bnk_block.xml", "04_service_definitions/accounts_payable/bnk_save.xml", "04_service_definitions/accounts_payable/bnk_verify.xml", "04_service_definitions/accounts_payable/crn_save.yaml", "04_service_definitions/accounts_payable/dbn_save.yaml", "04_service_definitions/accounts_payable/pay_propose.xml", "04_service_definitions/accounts_payable/sbal_ageing.yaml", "04_service_definitions/accounts_payable/sbal_query.yaml", "04_service_definitions/accounts_payable/sbal_stmt.yaml", "04_service_definitions/accounts_payable/sup_pay_hold.yaml", "04_service_definitions/accounts_payable/sup_pay_release.yaml", "04_service_definitions/inventory/csg_save.yaml", "04_service_definitions/inventory/lot_save.yaml", "04_service_definitions/purchase/po_fetch.yaml", "04_service_definitions/purchase/sup_cert_upload.yaml", "04_service_definitions/purchase/sup_create.yaml", "04_service_definitions/purchase/sup_get.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-SUP |
| Module | Purchasing / Accounts Payable / Inventory |
| System | Ledgerline ERP 7.2 |
| Reference manual | MAN-ERR-72 |
| Total codes | 3 |

The `ERR-SUP` error family validates supplier identifiers, master record availability, and tax registration integrity across Ledgerline ERP 7.2 [^r1][^r2][^r3]. These errors are raised across purchasing, accounts payable, and inventory modules when records are unrecognised, accounts are set to blocked status, or duplicate onboarding attempts occur [^r4][^r5][^r6][^r10]. Resolving them requires confirming master record existence, verifying activation status, or addressing duplicate tax registrations [^r10][^r11][^r12].

### [[err-sup-0030|ERR-SUP-0030]]

* **Message:** `SUPPLIER NOT FOUND` [^r1][^r10]
* **Cause:** The entered supplier identifier does not exist in the master file or accounts payable ledger, has been purged, is archived or deleted, or cannot be resolved with the provided vendor code [^r8][^r9][^r10][^r13]. On [[screen-ap-crn-05|AP-CRN-05]], it represents an unrecognised or inactive supplier code, while on [[screen-ap-pay-03|AP-PAY-03]] it indicates missing bank sorting codes, account numbers, or electronic payment flags for selected vendors [^r7].
* **Remedy:** Search for valid suppliers using the F2 lookup key or navigate to [[screen-pur-sup-03|PUR-SUP-03]] to verify the code and account status before retrying the transaction [^r10].
* **Raised by:** [[services-pur-sup|sup_get]] [^r10][^r34], `sup_cert_upload` [^r10][^r32], [[services-pur-po|po_fetch]] [^r10][^r31], `po_save` [^r10], `lot_save` [^r10][^r30], `pkg_save` [^r10], `csg_save` [^r10][^r29], `csg_settle` [^r10], [[services-ap-inv|inv_save]] [^r10], [[services-ap-dbn|dbn_save]] [^r10][^r22], [[services-ap-crn|crn_save]] [^r10][^r21], [[services-ap-pay|pay_propose]] [^r10][^r23], [[services-ap-adv|adv_adjust]] [^r16], `adv_save` [^r17], [[services-ap-bnk|bnk_block]] [^r18], `bnk_save` [^r19], `bnk_verify` [^r20], [[services-ap-sbal|sbal_ageing]] [^r24], `sbal_query` [^r25], `sbal_stmt` [^r26], [[services-ap-sup|sup_pay_hold]] [^r27], and `sup_pay_release` [^r28].

### [[err-sup-0031|ERR-SUP-0031]]

* **Message:** `SUPPLIER NOT ACTIVE` [^r2][^r11]
* **Cause:** An operator attempted to create a transaction or raise a new purchase order against a supplier whose master status is `BLOCKED` [^r4][^r5][^r11][^r14].
* **Remedy:** Check the supplier master status and initiate required unblocking procedures in accordance with purchasing policy before attempting further purchasing transactions [^r5][^r14].
* **Raised by:** `po_save` [^r11].

### [[err-sup-0118|ERR-SUP-0118]]

* **Message:** `VAT NO ALREADY REGISTERED` [^r3][^r12]
* **Cause:** An attempt was made to onboard or create a supplier record using a VAT registration number that already exists for an active or recorded vendor in the system [^r6][^r12][^r15].
* **Remedy:** Review existing supplier records to prevent duplicate vendor accounts and confirm the correct registration details for the trading entity [^r6][^r15].
* **Raised by:** `sup_create` [^r12][^r33].

## See also

* [[err-sup-0030|ERR-SUP-0030]]
* [[err-sup-0031|ERR-SUP-0031 Supplier is blocked]]
* [[err-sup-0118|ERR-SUP-0118 VAT number already registered]]
* [[errors-po|ERR-PO Error Codes]]
* [[errors-bnk|Errors BNK]]
* [[screen-pur-sup-03|PUR-SUP-03 Supplier Enquiry]]
* [[screen-pur-sup-01|PUR-SUP-01 Supplier Master Create]]
* [[screen-pur-po-01|PUR-PO-01 Purchase Order Entry]]
* [[screen-ap-pay-03|AP-PAY-03 Payment Run]]
* [[services-pur-sup|PUR sup services]]
* [[data-data-dictionary|Ledgerline_7.2_tables_and_fields]]

## References

[^r1]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-SUP-0030, SHEET Error codes
[^r2]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-SUP-0031, SHEET Error codes
[^r3]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-SUP-0118, SHEET Error codes
[^r4]: 07_data_dictionary/code_lists.csv, sheet csv, row sup_status, ALL 14 ROWS
[^r5]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 2, §5. Blocking and unblocking
[^r6]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 2, §6. Duplicate suppliers
[^r10]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 25, ERR-SUP-0030 SUPPLIER NOT FOUND
[^r11]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 25, ERR-SUP-0031 SUPPLIER NOT ACTIVE
[^r12]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 25, ERR-SUP-0118 VAT NO ALREADY REGISTERED
[^r8]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 31, Messages
[^r9]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 60, Messages
[^r13]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 11, §17.16 ERR-SUP-0030 Supplier not found
[^r7]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 21, Messages
[^r34]: 04_service_definitions/purchase/sup_get.yaml, errors
[^r32]: 04_service_definitions/purchase/sup_cert_upload.yaml, errors
[^r31]: 04_service_definitions/purchase/po_fetch.yaml, errors
[^r30]: 04_service_definitions/inventory/lot_save.yaml, errors
[^r29]: 04_service_definitions/inventory/csg_save.yaml, errors
[^r22]: 04_service_definitions/accounts_payable/dbn_save.yaml, errors
[^r21]: 04_service_definitions/accounts_payable/crn_save.yaml, errors
[^r23]: 04_service_definitions/accounts_payable/pay_propose.xml, ll:errors
[^r16]: 04_service_definitions/accounts_payable/adv_adjust.yaml, errors
[^r17]: 04_service_definitions/accounts_payable/adv_save.yaml, errors
[^r18]: 04_service_definitions/accounts_payable/bnk_block.xml, ll:errors
[^r19]: 04_service_definitions/accounts_payable/bnk_save.xml, ll:errors
[^r20]: 04_service_definitions/accounts_payable/bnk_verify.xml, ll:errors
[^r24]: 04_service_definitions/accounts_payable/sbal_ageing.yaml, errors
[^r25]: 04_service_definitions/accounts_payable/sbal_query.yaml, errors
[^r26]: 04_service_definitions/accounts_payable/sbal_stmt.yaml, errors
[^r27]: 04_service_definitions/accounts_payable/sup_pay_hold.yaml, errors
[^r28]: 04_service_definitions/accounts_payable/sup_pay_release.yaml, errors
[^r14]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 11, §17.17 ERR-SUP-0031 Supplier not active
[^r15]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 11, §17.18 ERR-SUP-0118 VAT number already registered
[^r33]: 04_service_definitions/purchase/sup_create.yaml, errors
