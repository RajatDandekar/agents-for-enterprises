---
title: "ERR-PER Error Codes"
type: "error-list"
slug: "errors-per"
summary: "Ledgerline ERP 7.2 AP period error codes (ERR-PER-*) raised during period maintenance and posting."
audience: "staff"
status: "current"
sources: ["07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx", "02_procedures/SOP-AP-002 Period Close v3.0.pdf", "03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "04_service_definitions/accounts_payable/inv_post.yaml", "04_service_definitions/accounts_payable/per_close.yaml", "04_service_definitions/accounts_payable/per_open.yaml", "04_service_definitions/accounts_payable/per_status.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-PER |
| Module | Accounts Payable (PER) |
| System | Ledgerline ERP 7.2 |
| Scope | AP period maintenance and posting validation |
| Owner | Accounts Payable |

This page catalogues the `ERR-PER-*` error codes raised in [[man-ap-72|Ledgerline ERP 7.2]] during Accounts Payable period control and transaction posting [^r10]. These errors validate calendar periods across period maintenance actions and prevent postings or period close when preconditions are unmet [^r2][^r3][^r4][^r11].

### ERR-PER-0001
* **Message**: `AP PERIOD NOT FOUND` [^r1][^r10]
* **Cause**: The identifier entered in the PERIOD field does not exist in the calendar tables or has been left blank [^r7].
* **Remedy**: Check the typing or run `per_list` to see valid codes [^r7].
* **Raised by**: [[services-ap-per|per_close]] [^r12], `per_open` [^r16], and `per_status` [^r17].

### ERR-PER-0003
* **Message**: `AP PERIOD CLOSED (<period>)` [^r2][^r10][^r11]
* **Cause**: An attempt was made to post a transaction into a closed AP accounting period [^r2][^r11].
* **Remedy**: Verify the posting date or open the relevant period if authorized [^r2][^r11].
* **Raised by**: [[services-ap-inv|inv_post]] [^r11].

### ERR-PER-0010
* **Message**: `UNPOSTED DOCUMENTS IN PERIOD` [^r3][^r10][^r14]
* **Cause**: A user attempts to close the AP period on [[screen-ap-per-11|AP-PER-11]] while batches or documents remain unposted in the period [^r3][^r6][^r14].
* **Remedy**: Complete or cancel all pending batches and unposted documents before running the period close routine [^r3][^r6].
* **Raised by**: [[services-ap-per|per_close]] [^r14]. Link: [[err-per-0010|ERR-PER-0010 Documents unposted at period close]].

### ERR-PER-0011
* **Message**: `GRNI ACCRUAL NOT RUN` [^r4][^r10][^r15]
* **Cause**: AP period close is attempted before the GRNI accrual has been processed [^r4][^r15].
* **Remedy**: Run the GRNI accrual routine prior to closing the AP period [^r4][^r15].
* **Raised by**: [[services-ap-per|per_close]] [^r15].

### ERR-PER-0801
* **Message**: `AP PERIOD CLOSED (<status>)` [^r5][^r10][^r13]
* **Cause**: An update is attempted against a period whose status is closed [^r5][^r13].
* **Remedy**: Verify the period status before attempting status updates [^r5][^r13].
* **Raised by**: [[services-ap-per|per_close]] [^r13].

## Versions and conflicts

* **ERR-PER-0010 definition**: The [[data-data-dictionary|data dictionary]], the [[services-ap-per|per_close]] service definition, [[sop-ap-002|SOP-AP-002 v3.0]], and §20 of [[man-ap-72|MAN-AP-72 v7.2.3]] define ERR-PER-0010 as `UNPOSTED DOCUMENTS IN PERIOD`, triggered when batches or unposted documents block period close [^r3][^r6][^r10][^r14]. In contrast, p. 38 of MAN-AP-72 states ERR-PER-0010 occurs when running `per_open` on an already open or permanently sealed period (`contradiction`) [^r8].
* **ERR-PER-0011 definition**: The [[data-data-dictionary|data dictionary]], the [[services-ap-per|per_close]] service definition, and §20 of [[man-ap-72|MAN-AP-72 v7.2.3]] define ERR-PER-0011 as `GRNI ACCRUAL NOT RUN`, which blocks AP period close [^r4][^r10][^r15]. In contrast, p. 38 of MAN-AP-72 states ERR-PER-0011 occurs when executing `per_close` on an interval that is already closed, was never opened, or is closed out of sequence (`contradiction`) [^r9].

## See also

* [[err-per-0010|ERR-PER-0010 Documents unposted at period close]]
* [[screen-ap-per-11|AP-PER-11 Ap Period]]
* [[services-ap-per|AP per services]]
* [[services-ap-inv|AP inv services]]
* [[sop-ap-002|SOP-AP-002 Accounts Payable Period Close]]
* [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]]
* [[data-data-dictionary|Ledgerline_7.2_tables_and_fields]]

## References

[^r10]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 66, §20. Messages
[^r2]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PER-0003, SHEET Error codes
[^r3]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PER-0010, SHEET Error codes
[^r4]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PER-0011, SHEET Error codes
[^r11]: 04_service_definitions/accounts_payable/inv_post.yaml, errors
[^r1]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PER-0001, SHEET Error codes
[^r7]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 38, Messages
[^r12]: 04_service_definitions/accounts_payable/per_close.yaml, errors
[^r16]: 04_service_definitions/accounts_payable/per_open.yaml, errors
[^r17]: 04_service_definitions/accounts_payable/per_status.yaml, errors
[^r14]: 04_service_definitions/accounts_payable/per_close.yaml, errors
[^r6]: 02_procedures/SOP-AP-002 Period Close v3.0.pdf, p. 4, What to check on screen
[^r15]: 04_service_definitions/accounts_payable/per_close.yaml, errors
[^r5]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PER-0801, SHEET Error codes
[^r13]: 04_service_definitions/accounts_payable/per_close.yaml, errors
[^r8]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 38, Messages
[^r9]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 38, Messages
