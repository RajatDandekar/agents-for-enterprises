---
title: "Errors PAY"
type: "error-list"
slug: "errors-pay"
summary: "Reference list of PAY module error codes in Ledgerline ERP 7.2 for accounts payable payment runs and file processing."
audience: "staff"
status: "current"
sources: ["07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx", "03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "04_service_definitions/accounts_payable/pay_approve.xml", "04_service_definitions/accounts_payable/pay_cancel.xml", "04_service_definitions/accounts_payable/pay_file.xml", "04_service_definitions/accounts_payable/pay_get.xml", "04_service_definitions/accounts_payable/pay_propose.xml", "04_service_definitions/accounts_payable/pay_release.xml", "04_service_definitions/accounts_payable/pay_search.xml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-PAY |
| Module | PAY (Accounts Payable) |
| System | Ledgerline ERP 7.2 |
| Status | current |
| Source documents | MAN-AP-72, Ledgerline tables and XML service definitions |

This page catalogues the `ERR-PAY-*` error codes raised across payment run processing in Ledgerline ERP 7.2 [^r13]. These codes are generated during the proposal, approval, generation, release, and cancellation of accounts payable payment runs on screen [[screen-ap-pay-03|AP-PAY-03]] [^r13]. As of 26 October 2026, the underlying service schemas and data dictionary govern the system messages, while the user manual notes operational causes encountered in AP operations [^r1][^r13].

### ERR-PAY-0001

* **Message:** `PAYMENT RUN NOT FOUND` [^r1][^r13]
* **Cause:** The run number entered does not exist in the database, or in worked examples, no matched items were eligible for settlement [^r7].
* **Remedy:** Verify the payment run number or check that matched invoices are eligible for the run [^r7].
* **Raised by:** Services `pay_approve`, `pay_cancel`, `pay_file`, `pay_get`, and `pay_release` in [[services-ap-pay]] [^r14][^r17][^r18][^r20][^r22].

### ERR-PAY-0007

* **Message:** `PAYMENT RUN NOT IN DRAFT (<status>)` [^r2][^r13]
* **Cause:** A modification, cancellation, or release action was attempted on a payment run that is not in draft status, or proposal generation conflicted with concurrent proposals or locked batch routines [^r2][^r8][^r23].
* **Remedy:** Check the current status of the payment run before modifying, or ensure concurrent proposals against the bank account have completed [^r2][^r8].
* **Raised by:** Services `pay_approve` and `pay_release` [^r15][^r23].

### ERR-PAY-0105

* **Message:** `DATE IN PAST` [^r3][^r13]
* **Cause:** An invalid payment date in the past was supplied, or invoices within the due date threshold are locked by another uncompleted payment proposal [^r3][^r9][^r21].
* **Remedy:** Correct the payment date or release the locking payment proposal [^r3][^r9].
* **Raised by:** Services `pay_propose` and `pay_search` [^r21][^r24].

### ERR-PAY-0430

* **Message:** `RUN APPROVER SAME AS PROPOSER` [^r4][^r13]
* **Cause:** The user attempting to approve the payment run is identical to the proposer, violating segregation of duties; alternatively, the manual describes file write failures or ledger period locks during execution [^r4][^r10][^r16]. Detailed workflow and role handling are documented on [[err-pay-0430]].
* **Remedy:** Assign a different authorised user to approve the run, or verify network folder permissions and open accounting periods [^r4][^r10][^r16].
* **Raised by:** Service `pay_approve` [^r16].

### ERR-PAY-0440

* **Message:** `RUN NOT APPROVED` [^r5][^r13]
* **Cause:** File creation or processing was attempted on a payment run that has not received formal approval, or selection parameters produced an empty batch with no eligible liabilities [^r5][^r11][^r19].
* **Remedy:** Approve the payment run before generating clearing files, or review invoice query and hold statuses [^r5][^r11][^r19].
* **Raised by:** Service `pay_file` [^r19].

### ERR-PAY-0801

* **Message:** `PAYMENT RUN CLOSED (<status>)` [^r6][^r13]
* **Cause:** The requested action is invalid because the run has already been cancelled or closed, or actions were performed out of sequence [^r6][^r12][^r25].
* **Remedy:** Verify the run status on [[screen-ap-pay-03|AP-PAY-03]] and follow the proper approval sequence [^r12][^r25].
* **Raised by:** Service `pay_cancel` [^r25].

## Versions and conflicts

* **ERR-PAY-0430 meaning:** The [[data-data-dictionary|Ledgerline 7.2 data dictionary]] and service definition define the message as `RUN APPROVER SAME AS PROPOSER` to enforce segregation of duties [^r4][^r16]. [[man-ap-72|MAN-AP-72]] (15 January 2025) lists the message code text as `RUN APPROVER SAME AS PROPOSER` in §20, but describes the failure in section text as an inability of `pay_file` to write electronic clearing files to a network drive or underlying ledgers being locked for period closure [^r10][^r13] (`contradiction`).
* **ERR-PAY-0440 meaning:** The data dictionary and service definition define the code as `RUN NOT APPROVED` when attempting execution without approval [^r5][^r19]. [[man-ap-72|MAN-AP-72]] lists the code text as `RUN NOT APPROVED` in §20, but describes the runtime cause in section text as an empty payment batch with no eligible liabilities [^r11][^r13] (`contradiction`).
* **ERR-PAY-0105 meaning:** The data dictionary and XML service definitions assign the text `DATE IN PAST` [^r3][^r21][^r24]. [[man-ap-72|MAN-AP-72]] lists `DATE IN PAST` in §20, but narrative text links it to open invoices being locked by active proposals [^r9][^r13] (`contradiction`).
* **ERR-PAY-0007 meaning:** The data dictionary and service definitions assign `PAYMENT RUN NOT IN DRAFT (<status>)` [^r2][^r15][^r23]. [[man-ap-72|MAN-AP-72]] lists this text in §20, but describes proposal failure from concurrent proposals or locked supplier files [^r8][^r13] (`contradiction`).
* **ERR-PAY-0801 meaning:** The data dictionary and service definitions define `PAYMENT RUN CLOSED (<status>)` [^r6][^r25]. [[man-ap-72|MAN-AP-72]] lists this text in §20, but explains it as executing an invalid action for current status such as `pay_release` before `pay_approve` [^r12][^r13] (`contradiction`).
* **ERR-PAY-0001 meaning:** The data dictionary and service definitions define `PAYMENT RUN NOT FOUND` [^r1][^r14]. [[man-ap-72|MAN-AP-72]] lists this text in §20, but describes a worked example where no matched items were eligible for settlement [^r7][^r13] (`contradiction`).

## See also

* [[err-pay-0430]]: Detailed page for proposal approver cannot be proposer
* [[screen-ap-pay-03]]: Payment Run screen
* [[services-ap-pay]]: AP payment services reference
* [[man-ap-72]]: Ledgerline ERP 7.2 User Manual: Accounts Payable
* [[data-data-dictionary]]: Ledgerline 7.2 Tables and Fields reference
* [[errors-bnk]]: Bank module error codes
* [[errors-apr]]: Approval module error codes

## References

[^r13]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 66, §20. Messages
[^r1]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PAY-0001, SHEET Error codes
[^r7]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 20, Messages
[^r14]: 04_service_definitions/accounts_payable/pay_approve.xml, ll:errors
[^r17]: 04_service_definitions/accounts_payable/pay_cancel.xml, ll:errors
[^r18]: 04_service_definitions/accounts_payable/pay_file.xml, ll:errors
[^r20]: 04_service_definitions/accounts_payable/pay_get.xml, ll:errors
[^r22]: 04_service_definitions/accounts_payable/pay_release.xml, ll:errors
[^r2]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PAY-0007, SHEET Error codes
[^r8]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 20, Messages
[^r23]: 04_service_definitions/accounts_payable/pay_release.xml, ll:errors
[^r15]: 04_service_definitions/accounts_payable/pay_approve.xml, ll:errors
[^r3]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PAY-0105, SHEET Error codes
[^r9]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 20, Messages
[^r21]: 04_service_definitions/accounts_payable/pay_propose.xml, ll:errors
[^r24]: 04_service_definitions/accounts_payable/pay_search.xml, ll:errors
[^r4]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PAY-0430, SHEET Error codes
[^r10]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 20, Messages
[^r16]: 04_service_definitions/accounts_payable/pay_approve.xml, ll:errors
[^r5]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PAY-0440, SHEET Error codes
[^r11]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 21, Messages
[^r19]: 04_service_definitions/accounts_payable/pay_file.xml, ll:errors
[^r6]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PAY-0801, SHEET Error codes
[^r12]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 21, Messages
[^r25]: 04_service_definitions/accounts_payable/pay_cancel.xml, ll:errors
