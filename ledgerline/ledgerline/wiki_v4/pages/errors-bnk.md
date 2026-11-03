---
title: "Errors BNK"
type: "error-list"
slug: "errors-bnk"
summary: "Catalogue of Ledgerline ERP 7.2 BNK banking error and warning codes covering missing records, verification blocks, invalid IBANs, and call-back requirements."
audience: "staff"
status: "current"
sources: ["07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx", "03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "04_service_definitions/accounts_payable/bnk_save.xml", "04_service_definitions/accounts_payable/bnk_verify.xml", "04_service_definitions/accounts_payable/pay_approve.xml", "04_service_definitions/accounts_payable/pay_file.xml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | BNK (Banking / Accounts Payable) |
| System | Ledgerline ERP 7.2 |
| Applies to | Supplier bank maintenance and payment runs |
| Parent manual | MAN-AP-72, MAN-ERR-72 |

The BNK error list catalogues messages raised by Ledgerline ERP 7.2 during supplier bank account maintenance and payment run processing [^r6]. These codes prevent disbursement when bank accounts are missing, unverified, mathematically invalid, or lack mandatory verification controls [^r1][^r2][^r3][^r4][^r8]. As of 26 October 2026, handling these exceptions requires proper call-back documentation and verification workflows before supplier payments can proceed [^r4][^r6][^r8][^r10].

### ERR-BNK-0001
* **Message**: SUPPLIER BANK DETAILS NOT FOUND [^r6][^r7].
* **Cause**: Module BNK raises this code when supplier bank details are not found, or when no bank record matches the provided key [^r1][^r7].
* **Remedy**: Verify that bank details have been entered and exist for the supplier [^r1][^r7]. For detail, see [[err-bnk-0001]].
* **Raised by**: `bnk_get`, `bnk_verify`, and `bnk_block` [^r7][^r13].

### ERR-BNK-0101
* **Message**: BANK DETAILS NOT VERIFIED (<sup_cd>) [^r6][^r8][^r15][^r16].
* **Cause**: Module BNK raises this error when bank details are not verified for a supplier code, blocking payment approval or filing against unverified accounts [^r2][^r8][^r15][^r16]. Alternatively, it indicates that BANK CD does not match an active disbursement account in GL master tables or the selected account is suspended for outgoing payments [^r5].
* **Remedy**: Complete the verification workflow for the supplier's bank details or select an active disbursement account [^r2][^r5][^r8]. For detail, see [[err-bnk-0101]].
* **Raised by**: `pay_approve` and `pay_file` [^r8][^r15][^r16].

### ERR-BNK-0118
* **Message**: IBAN CHECK DIGITS INVALID [^r6][^r9][^r11].
* **Cause**: Module BNK raises this error when submitted IBAN check digits fail validation [^r3][^r9][^r11].
* **Remedy**: Check and re-enter the IBAN ensuring the country code, length, and check digits are correct [^r3][^r9]. For detail, see [[err-bnk-0118]].
* **Raised by**: `bnk_save` [^r9][^r11].

### ERR-BNK-0125
* **Message**: CALL-BACK NOT RECORDED [^r6][^r10][^r14].
* **Cause**: Module BNK raises this code when the required verification call-back has not been logged [^r4][^r10][^r14].
* **Remedy**: Record the verification call-back details prior to attempting bank record verification [^r4][^r10][^r14]. For detail, see [[err-bnk-0125]].
* **Raised by**: `bnk_verify` [^r10][^r14].

### W-BNK-120
* **Message**: BANK DETAILS CHANGED, PAYMENTS HELD UNTIL VERIFIED [^r6][^r12].
* **Cause**: Issued as a warning when saving supplier bank details that alter existing banking data [^r6][^r12].
* **Remedy**: Inform Accounts Payable that outgoing payments are held until verification is formally completed [^r6][^r12].
* **Raised by**: `bnk_save` [^r12].

## Versions and conflicts
* **ERR-BNK-0101 definition**: According to the Ledgerline 7.2 Data Dictionary, MAN-ERR-72, MAN-AP-72 §20, and service definitions `pay_approve.xml` and `pay_file.xml`, ERR-BNK-0101 represents "BANK DETAILS NOT VERIFIED (<sup_cd>)" and is triggered when payments are processed against unverified supplier bank records [^r2][^r6][^r8][^r15][^r16]. In contrast, MAN-AP-72 page 20 states that ERR-BNK-0101 indicates that BANK CD does not match an active disbursement account in GL master tables or the selected account is suspended [^r5] (`contradiction`).

## See also
* [[err-bnk-0001|ERR-BNK-0001]]
* [[err-bnk-0101|ERR-BNK-0101]]
* [[err-bnk-0118|ERR-BNK-0118]]
* [[err-bnk-0125|ERR-BNK-0125]]
* [[services-ap-bnk|AP bnk services]]
* [[services-ap-pay|AP pay services]]
* [[screen-ap-bnk-06|AP-BNK-06 Supplier Bank Details Entry]]
* [[screen-ap-pay-03|AP-PAY-03 Payment Run]]
* [[sop-ap-003|SOP-AP-003 Supplier Payment Run]]
* [[sop-ap-004|SOP-AP-004 Supplier Bank Detail Changes]]
* [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]]
* [[data-data-dictionary|Ledgerline_7.2_tables_and_fields]]

## References

[^r6]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 65, §20. Messages
[^r1]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-BNK-0001, SHEET Error codes
[^r2]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-BNK-0101, SHEET Error codes
[^r3]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-BNK-0118, SHEET Error codes
[^r4]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-BNK-0125, SHEET Error codes
[^r8]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 3, §2. Codes
[^r10]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 3, §2. Codes
[^r7]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 3, §2. Codes
[^r13]: 04_service_definitions/accounts_payable/bnk_verify.xml, ll:errors
[^r15]: 04_service_definitions/accounts_payable/pay_approve.xml, ll:errors
[^r16]: 04_service_definitions/accounts_payable/pay_file.xml, ll:errors
[^r5]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 20, Messages
[^r9]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 3, §2. Codes
[^r11]: 04_service_definitions/accounts_payable/bnk_save.xml, ll:errors
[^r14]: 04_service_definitions/accounts_payable/bnk_verify.xml, ll:errors
[^r12]: 04_service_definitions/accounts_payable/bnk_save.xml, ll:errors
