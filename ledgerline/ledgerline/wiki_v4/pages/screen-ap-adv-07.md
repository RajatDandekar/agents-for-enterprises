---
title: "AP-ADV-07 Advance Payment Entry"
type: "screen"
slug: "screen-ap-adv-07"
summary: "Ledgerline screen for recording and approving advance payments against purchase orders for Manchester production parts."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/accounts_payable/adv_adjust.yaml", "04_service_definitions/accounts_payable/adv_approve.yaml", "04_service_definitions/accounts_payable/adv_get.yaml", "04_service_definitions/accounts_payable/adv_save.yaml", "04_service_definitions/accounts_payable/adv_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | AP-ADV-07 |
| Name | Advance Payment Entry |
| Menu path | Accounts payable > Advance payment |
| Authorized roles | AP-CLERK, AP-MGR, FIN-CTRL, SYS-ADMIN |
| Key services | adv_save, adv_get, adv_search, adv_approve, adv_adjust |

Screen AP-ADV-07 is the Ledgerline interface used to record, retrieve, and authorise advance payments against purchase orders for production parts at Manchester [^r7]. Located under menu path Accounts payable > Advance payment, it is authorised for roles AP-CLERK, AP-MGR, FIN-CTRL, and SYS-ADMIN [^r2][^r11]. Entering an advance requires matching the payment amount to the vendor's pro-forma invoice, and upon saving, the system automatically assigns an advance number [^r7][^r8].

| Field | Detail |
|---|---|
| Screen code | AP-ADV-07 |
| Name | Advance Payment Entry |
| Menu path | Accounts payable > Advance payment |
| Authorized roles | AP-CLERK, AP-MGR, FIN-CTRL, SYS-ADMIN |
| Key services | [[services-ap-adv\|adv_save]], adv_get, adv_search, adv_approve, adv_adjust |

## Fields

Active data fields on AP-ADV-07 comprise supplier and purchase order references alongside payment figures [^r1]:

* **SUP CD** (`sup_cd`, string): Mandatory supplier code [^r1][^r12].
* **PO NO** (`po_no`, string): Mandatory purchase order number [^r1][^r12].
* **AMOUNT** (`amount`, float): Mandatory payment value, which must match the vendor's pro-forma invoice [^r1][^r8][^r12].
* **ADV NO** (`adv_no`, string): Mandatory system-generated advance identifier [^r1][^r12].
* **STATUS** (`status`, string): System-maintained status indicating the stage of the advance record [^r1][^r12].
* **COMMENT** (`comment`, string): Optional open text field [^r1][^r12].

Data entry requires entering SUP CD, PO NO, AMOUNT, and COMMENT [^r8]. Supported search filters for query operations comprise `sup_cd`, `po_no`, `amount`, and `status` [^r20].

## Keys and services

AP-ADV-07 operates through a set of background read and write services mapped to function keys [^r2][^r13]:

* **Save (F8)**: Invokes write service `adv_save` to validate the supplier and purchase order, generate `adv_no`, and save the record [^r3][^r13][^r18].
* **Get (F3)**: Invokes read service `adv_get` to retrieve advance payment records using mandatory key `adv_no` [^r13][^r17].
* **Search (F2 / Enter)**: Invokes read service `adv_search` (`POST /ll72/svc/adv_search`) to retrieve lists of advance payments filtered by criteria [^r13][^r19][^r20].
* **Approve (F9)**: Invokes write service `adv_approve` (`POST /ll72/svc/adv_approve`) to validate approval authority, ensure the advance does not exceed the remaining purchase order commitment, and set status to approved [^r4][^r13][^r16].
* **Adjust**: Invokes write service `adv_adjust` (`POST /ll72/svc/adv_adjust`) using `adv_no`—and optionally `sup_cd`, `po_no`, and `amount`—to alter the amount or comment before authorisation, releasing commitment on the purchase order if permitted by status [^r5][^r9][^r13][^r15].

## Messages

The screen presents standard error codes during validation and authorization failures [^r6][^r10]:

* [[err-sup-0030]]: Raised when a supplier is blocked or not found [^r6][^r14].
* [[err-adv-0001]]: Raised for missing input fields or when an advance payment record is not found [^r6][^r14].
* [[err-adv-0007]]: Raised when the purchase order does not match the supplier code, the purchase order is closed, or the advance record is not in draft status [^r6][^r14].
* [[err-apr-0003]]: Raised for insufficient authority or when self-approval is attempted [^r6][^r14].
* [[err-apr-0004]]: Raised when the advance amount exceeds the unbilled commitment on the purchase order or exceeds the user's approval limit [^r6][^r14].

## Versions and conflicts

* **Initial status upon saving**: MAN-AP-72 p. 27 states that saving via `adv_save` sets the status to entered [^r3]. However, MAN-AP-72 p. 29 states that `adv_save` saves the entry as pending [^r9].
* **Field optionality**: MAN-AP-72 p. 26 defines ADV NO as mandatory and STATUS as system-maintained [^r1]. MAN-SCR-72 p. 4 lists ADV NO alongside mandatory fields, but marks STATUS as optional [^r12].
* **Message descriptions**: MAN-AP-72 p. 28 documents ERR-ADV-0001 for missing fields, ERR-ADV-0007 for PO supplier mismatch or closed status, ERR-APR-0003 for insufficient authority, and ERR-APR-0004 for amount exceeding unbilled commitment [^r6]. In contrast, MAN-SCR-72 p. 4 lists ERR-ADV-0001 as "Advance Payment Not Found", ERR-ADV-0007 as "Advance Payment Not In Draft (<Status>)", ERR-APR-0003 as "Self Approval Not Allowed", and ERR-APR-0004 as "Value Above Your Limit" [^r14].

## See also

* [[services-ap-adv|AP adv services]]
* [[services-pur-po|PUR po services]]
* [[screen-ap-inv-01|AP-INV-01 Supplier Invoice Entry]]
* [[screen-ap-pay-03|AP-PAY-03 Payment Run]]
* [[err-adv-0001|ERR-ADV-0001 Missing or invalid advance payment fields]]
* [[err-adv-0007|ERR-ADV-0007 Purchase order supplier mismatch or closed]]
* [[err-apr-0003|ERR-APR-0003 Self-approval not permitted]]
* [[err-apr-0004|ERR-APR-0004 Advance amount exceeds PO unbilled commitment]]
* [[err-sup-0030|ERR-SUP-0030]]
* [[errors-sup|ERR-SUP Error Codes]]

## References

[^r7]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 29, Advance Payment (AP-ADV-07)
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 26, §9. Advance Payment (AP-ADV-07)
[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 4, AP-ADV-07 ADVANCE PAYMENT ENTRY
[^r8]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 29, Advance Payment (AP-ADV-07)
[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 26, §9. Advance Payment (AP-ADV-07)
[^r12]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 4, AP-ADV-07 ADVANCE PAYMENT ENTRY
[^r20]: 04_service_definitions/accounts_payable/adv_search.yaml, request.fields
[^r13]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 4, AP-ADV-07 ADVANCE PAYMENT ENTRY
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 27, Step by step
[^r18]: 04_service_definitions/accounts_payable/adv_save.yaml, screen
[^r17]: 04_service_definitions/accounts_payable/adv_get.yaml, whole file
[^r19]: 04_service_definitions/accounts_payable/adv_search.yaml, service: adv_search
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 27, Step by step
[^r16]: 04_service_definitions/accounts_payable/adv_approve.yaml, screen: AP-ADV-07
[^r5]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 28, Tips
[^r9]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 29, Advance Payment (AP-ADV-07)
[^r15]: 04_service_definitions/accounts_payable/adv_adjust.yaml, screen
[^r6]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 28, Messages
[^r10]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 29, Advance Payment (AP-ADV-07)
[^r14]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 4, AP-ADV-07 ADVANCE PAYMENT ENTRY
