---
title: "AP per services"
type: "service-group"
slug: "services-ap-per"
summary: "Accounts Payable accounting period services controlling listing, status querying, opening, and closing of financial posting intervals on screen AP-PER-11."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/accounts_payable/per_close.yaml", "04_service_definitions/accounts_payable/per_list.yaml", "04_service_definitions/accounts_payable/per_open.yaml", "04_service_definitions/accounts_payable/per_status.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | Accounts Payable (AP) |
| Screen | AP-PER-11 |
| Services | per_list, per_status, per_open, per_close |
| Available Since | Ledgerline 7.0 |
| Protocol | POST /ll72/svc/<service> |

The Accounts Payable period services manage the operational state of financial posting intervals within Ledgerline ERP 7.2 [^r14][^r21]. These services execute against [[screen-ap-per-11|screen AP-PER-11]] to inspect, open, and close accounting intervals for transactional postings [^r1][^r3][^r4][^r10][^r11][^r12][^r13]. Validating posting periods and running accrual verifications through these services prevents unallocated documents from remaining unposted across accounting cutoffs [^r4][^r36].

## Services

### per_list

The read service `per_list` (AP PERIOD LIST) queries system control tables to list configured accounting intervals and their operational statuses (open, closed, or future) on [[screen-ap-per-11|AP-PER-11]] [^r1][^r10][^r21]. It has been available since Ledgerline version 7.0 and is invoked at endpoint `POST /ll72/svc/per_list` [^r21][^r22]. Authentication requires a session token in header `X-LL-Session` with a role authorised for the service [^r22].

* **Required fields:** none [^r23].
* **Optional fields:** `period` (string) [^r10][^r23].
* **Errors:** Returns envelope rc (`S | W | E`), `err_cd`, uppercase `msg`, and `result` data with no service-specific errors defined [^r24]. Common errors are ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r25].
* **Source file:** `04_service_definitions/accounts_payable/per_list.yaml` [^r21].

### per_status

The read service `per_status` (AP PERIOD STATUS) queries database records on screen [[screen-ap-per-11|AP-PER-11]] to determine the operational posting state of a designated period [^r2][^r13][^r31]. Available since version 7.0, it is accessed at endpoint `POST /ll72/svc/per_status` using a session token in header `X-LL-Session` under an authorised role [^r31][^r32].

* **Required fields:** `period` (string) [^r13][^r33].
* **Optional fields:** none [^r33].
* **Errors:** Returns rc, `err_cd`, uppercase `msg`, and data [^r34]. Raises [[errors-per|ERR-PER-0001]] (AP PERIOD NOT FOUND) if the period record cannot be found [^r9][^r13][^r35]. Common errors are ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r35].
* **Source file:** `04_service_definitions/accounts_payable/per_status.yaml` [^r31].

### per_open

The write service `per_open` (AP PERIOD OPEN) activates an accounting interval for live transactional postings and updates master control tables via screen [[screen-ap-per-11|AP-PER-11]] and stored procedure `sp_per_open` [^r3][^r12][^r26][^r29]. It has been available since version 7.0 at endpoint `POST /ll72/svc/per_open` with authentication header `X-LL-Session` [^r26][^r27].

* **Required fields:** `period` (string) [^r12][^r28].
* **Optional fields:** `comment` (string) [^r3][^r12][^r28].
* **Errors:** Specific error [[errors-per|ERR-PER-0001]] (AP PERIOD NOT FOUND) [^r9][^r30]. Common errors include ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r30].
* **Source file:** `04_service_definitions/accounts_payable/per_open.yaml` [^r26].

### per_close

The write service `per_close` (AP PERIOD CLOSE) verifies accounting conditions before sealing an interval on screen [[screen-ap-per-11|AP-PER-11]], writing remarks to the audit log, and executing stored procedure `sp_per_close` [^r4][^r11][^r14][^r20]. Invoked at endpoint `POST /ll72/svc/per_close`, it requires a session token in header `X-LL-Session` and role authorisation [^r14][^r15].

* **Required fields:** `period` (string) [^r11][^r16].
* **Optional fields:** `comment` (string) [^r16].
* **Errors:** Envelope returns rc (`S | W | E`), `err_cd`, uppercase `msg`, and data [^r17]. Service-specific errors are [[errors-per|ERR-PER-0001]] (AP PERIOD NOT FOUND), ERR-PER-0801 (AP PERIOD CLOSED (<status>)), [[err-per-0010|ERR-PER-0010]] (UNPOSTED DOCUMENTS IN PERIOD), and ERR-PER-0011 (GRNI ACCRUAL NOT RUN) [^r9][^r11][^r18][^r36]. Common errors are ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r19].
* **Source file:** `04_service_definitions/accounts_payable/per_close.yaml` [^r14].

## Versions and conflicts

* **Error code assignments across manual narrative and service specifications:** Under the service definitions and error manual, `per_close` checks for unposted documents with [[err-per-0010|ERR-PER-0010]], unrun GRNI accruals with ERR-PER-0011, and closed status with ERR-PER-0801, while `per_open` and `per_status` raise [[errors-per|ERR-PER-0001]] if the record is missing [^r9][^r18][^r30][^r35][^r36]. In contrast, the worked examples and message summary in user manual MAN-AP-72 state that `per_status` raises ERR-PER-0001 when pending transactions exist, `per_close` raises ERR-PER-0801 for unbalanced transactions and ERR-PER-0010 for already closed intervals, and `per_open` raises ERR-PER-0011 for invalid intervals or ERR-PER-0801 for lack of authorisation [^r5][^r6][^r7][^r8] (`contradiction`).

## See also

* [[screen-ap-per-11|AP-PER-11 Ap Period]]
* [[err-per-0010|ERR-PER-0010 Documents unposted at period close]]
* [[errors-per|ERR-PER Error Codes]]
* [[services-ap-acr|AP acr services]]
* [[services-ap-inv|AP inv services]]
* [[services-ap-gl|AP gl services]]

## References

[^r14]: 04_service_definitions/accounts_payable/per_close.yaml, service: per_close
[^r21]: 04_service_definitions/accounts_payable/per_list.yaml, whole file
[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 37, Viewing existing period records
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 38, Opening an accounting period
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 38, Closing an accounting period
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 33, per_list AP PERIOD LIST
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 33, per_close AP PERIOD CLOSE
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 33, per_open AP PERIOD OPEN
[^r13]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 33, per_status AP PERIOD STATUS
[^r36]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 17, ERR-PER-0011
[^r22]: 04_service_definitions/accounts_payable/per_list.yaml, whole file
[^r23]: 04_service_definitions/accounts_payable/per_list.yaml, request.fields
[^r24]: 04_service_definitions/accounts_payable/per_list.yaml, response
[^r25]: 04_service_definitions/accounts_payable/per_list.yaml, common_errors
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 37, Checking a specific period status
[^r31]: 04_service_definitions/accounts_payable/per_status.yaml, service: per_status
[^r32]: 04_service_definitions/accounts_payable/per_status.yaml, auth
[^r33]: 04_service_definitions/accounts_payable/per_status.yaml, request
[^r34]: 04_service_definitions/accounts_payable/per_status.yaml, response
[^r9]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 16, ERR-PER-0001
[^r35]: 04_service_definitions/accounts_payable/per_status.yaml, errors
[^r26]: 04_service_definitions/accounts_payable/per_open.yaml, whole file
[^r29]: 04_service_definitions/accounts_payable/per_open.yaml, procedures
[^r27]: 04_service_definitions/accounts_payable/per_open.yaml, whole file
[^r28]: 04_service_definitions/accounts_payable/per_open.yaml, request.fields
[^r30]: 04_service_definitions/accounts_payable/per_open.yaml, errors
[^r20]: 04_service_definitions/accounts_payable/per_close.yaml, procedures
[^r15]: 04_service_definitions/accounts_payable/per_close.yaml, auth
[^r16]: 04_service_definitions/accounts_payable/per_close.yaml, request
[^r17]: 04_service_definitions/accounts_payable/per_close.yaml, response
[^r18]: 04_service_definitions/accounts_payable/per_close.yaml, errors
[^r19]: 04_service_definitions/accounts_payable/per_close.yaml, common_errors
[^r5]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 38, Messages
[^r6]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 39, Worked example
[^r7]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 39, Worked example
[^r8]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 40, Worked example
