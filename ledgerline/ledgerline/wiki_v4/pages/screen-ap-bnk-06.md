---
title: "AP-BNK-06 Supplier Bank Details Entry"
type: "screen"
slug: "screen-ap-bnk-06"
summary: "Ledgerline screen for maintaining, verifying, and blocking vendor settlement bank particulars under Accounts payable."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-AP-004 Supplier Bank Detail Changes v2.0.pdf", "03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/accounts_payable/bnk_block.xml", "04_service_definitions/accounts_payable/bnk_get.xml", "04_service_definitions/accounts_payable/bnk_save.xml", "04_service_definitions/accounts_payable/bnk_search.xml", "04_service_definitions/accounts_payable/bnk_verify.xml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | AP-BNK-06 |
| Title | Supplier Bank Details Entry |
| Module | Accounts payable > Supplier bank |
| Roles | AP-CLERK, AP-MGR, FIN-CTRL, SYS-ADMIN |
| Status | current |

Screen AP-BNK-06 is used by the Northbridge Cycles finance department to maintain, review, verify, and block settlement bank particulars for vendors serving the Manchester plant and Leeds unit [^r3]. Located under Accounts payable > Supplier bank, access is authorized for roles AP-CLERK, AP-MGR, FIN-CTRL, and SYS-ADMIN [^r9]. Any amendment saved against an existing verified account clears its verification flag and places a payment hold under warning W-BNK-120 until verification is formally completed [^r2][^r7]. Recording a verification call via service `bnk_verify` requires all mandatory text details to be completed to clear payment holds [^r1][^r2].

| Field | Value |
|---|---|
| Screen code | AP-BNK-06 [^r3] |
| Navigation | Accounts payable > Supplier bank [^r9] |
| Authorized roles | AP-CLERK, AP-MGR, FIN-CTRL, SYS-ADMIN [^r9] |

## Fields

Screen AP-BNK-06 contains the following fields [^r4][^r5]:

* **SUP CD** (`sup_cd`, string): Mandatory supplier code [^r4][^r10].
* **ACCT NAME** (`acct_name`, string): Mandatory settlement account name [^r4][^r10].
* **SORT CD** (`sort_cd`): Optional bank sort code [^r4][^r5][^r10].
* **ACCT NO** (`acct_no`): Optional bank account number [^r4][^r5][^r10].
* **IBAN** (`iban`): Optional International Bank Account Number [^r4][^r5][^r10].
* **BIC** (`bic`): Optional Bank Identifier Code [^r4][^r5][^r10].
* **REASON** (`reason`): Optional text field for block or update justification [^r4][^r5][^r10][^r12].
* **STATUS** (`status`): Optional account status field [^r4][^r5][^r10].

## Keys and services

Screen AP-BNK-06 interacts with the Ledgerline system using interface key actions and services grouped under [[services-ap-bnk|AP bnk services]] [^r6]:

* **Search** (F2 / Enter): Invokes read service `bnk_search` to list supplier bank records [^r6][^r17][^r19].
* **Get**: Invokes read service `bnk_get` to retrieve an existing record [^r6][^r13][^r19].
* **Save** (F8): Invokes write service `bnk_save` to commit account fields including supplier code, account name, sort code, account number, IBAN, and BIC [^r6][^r14][^r19].
* **Verify**: Invokes write service `bnk_verify` with parameter `sup_cd` to record verification and release holds [^r1][^r6][^r18][^r19].
* **Block**: Invokes write service `bnk_block` using `sup_cd` and optional `reason` to block vendor payment settlement [^r6][^r12][^r19].

## Messages

The screen raises the following errors and warnings during processing [^r8][^r11]:

* `ERR-BNK-0001`: Raised when essential settlement fields are missing or bank details are not found ([[err-bnk-0001|ERR-BNK-0001 Missing mandatory banking fields]]) [^r8][^r11].
* `ERR-BNK-0118`: Raised when modulus, clearing code, or IBAN check digits fail validation ([[err-bnk-0118|ERR-BNK-0118 Modulus check or clearing code validation failed]]) [^r8][^r11][^r16].
* `ERR-BNK-0125`: Raised when a call-back is not recorded, modulus checks fail, or the record is locked by concurrent processes ([[err-bnk-0125|ERR-BNK-0125 Record locked by another user or concurrent payment process]]) [^r8][^r11].
* `ERR-SUP-0030`: Raised when the supplier code does not exist or is marked for deletion ([[err-sup-0030|ERR-SUP-0030]]) [^r8][^r11].
* `W-BNK-120`: Warning stating 'BANK DETAILS CHANGED, PAYMENTS HELD UNTIL VERIFIED', triggered on saving bank amendments and holding payments until `bnk_verify` is executed [^r2][^r7][^r11][^r15].

## See also

* [[sop-ap-004|SOP-AP-004 Supplier Bank Detail Changes]]
* [[services-ap-bnk|AP bnk services]]
* [[errors-bnk|Errors BNK]]
* [[errors-sup|ERR-SUP Error Codes]]
* [[screen-ap-pay-03|AP-PAY-03 Payment Run]]
* [[screen-pur-sup-03|PUR-SUP-03 Supplier Enquiry]]

## References

[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 22, Supplier Bank Details (AP-BNK-06)
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 4, AP-BNK-06 SUPPLIER BANK DETAILS ENTRY
[^r2]: 02_procedures/SOP-AP-004 Supplier Bank Detail Changes v2.0.pdf, p. 3, §5. Procedure
[^r7]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 24, Messages
[^r1]: 02_procedures/SOP-AP-004 Supplier Bank Detail Changes v2.0.pdf, p. 4, What to check on the screen
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 22, §8. Supplier Bank Details (AP-BNK-06)
[^r5]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 23, Screen layout and fields
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 4, AP-BNK-06 SUPPLIER BANK DETAILS ENTRY
[^r12]: 04_service_definitions/accounts_payable/bnk_block.xml, wsdl:documentation
[^r6]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 25, Worked example
[^r17]: 04_service_definitions/accounts_payable/bnk_search.xml, wsdl:documentation
[^r19]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 4, AP-BNK-06 SUPPLIER BANK DETAILS ENTRY
[^r13]: 04_service_definitions/accounts_payable/bnk_get.xml, wsdl:documentation
[^r14]: 04_service_definitions/accounts_payable/bnk_save.xml, wsdl:documentation
[^r18]: 04_service_definitions/accounts_payable/bnk_verify.xml, wsdl:documentation
[^r8]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 24, Messages
[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 5, AP-BNK-06 SUPPLIER BANK DETAILS ENTRY
[^r16]: 04_service_definitions/accounts_payable/bnk_save.xml, ll:errors
[^r15]: 04_service_definitions/accounts_payable/bnk_save.xml, ll:errors
