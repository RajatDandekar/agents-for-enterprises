---
title: "AP exp services"
type: "service-group"
slug: "services-ap-exp"
summary: "Ledgerline Accounts Payable backend services for entering, searching, approving, rejecting, and paying employee expense claims via screen AP-EXP-09."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/accounts_payable/exp_approve.yaml", "04_service_definitions/accounts_payable/exp_get.yaml", "04_service_definitions/accounts_payable/exp_pay.yaml", "04_service_definitions/accounts_payable/exp_reject.yaml", "04_service_definitions/accounts_payable/exp_save.yaml", "04_service_definitions/accounts_payable/exp_search.yaml", "04_service_definitions/accounts_payable/exp_submit.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | Accounts Payable (AP) |
| Object | Expense claims (exp) |
| Screen | AP-EXP-09 |
| Available since | Ledgerline 7.0 |
| Endpoints | POST /ll72/svc/exp_* |
| Transport | HTTP POST with X-LL-Session token |
| Services | exp_save, exp_get, exp_search, exp_submit, exp_approve, exp_reject, exp_pay |

The AP expense service group provides the backend procedures for processing employee expense claims in Ledgerline ERP 7.2 [^r1][^r14]. Operating primarily behind screen [[screen-ap-exp-09|AP-EXP-09]], the suite manages the full claim lifecycle across draft creation, submission, approval, rejection, and final payment disbursement [^r1][^r6]. All seven services require HTTP POST requests authenticated by a valid session token in header `X-LL-Session` with an authorized user role [^r15][^r19][^r24][^r29][^r33][^r37][^r42].

## Services

### exp_save

Service `exp_save` (EXPENSE CLAIM SAVE) is a write service introduced in version 7.0 that creates or updates draft expense claims via stored procedure `sp_exp_save` [^r2][^r7][^r32][^r35]. It assigns the expense claim number on screen [[screen-ap-exp-09|AP-EXP-09]] upon saving [^r2][^r7].

* **Endpoint**: `POST /ll72/svc/exp_save` [^r33]
* **Required fields**: `user_id` (str), `claim_dt` (date), `amount` (float), `cc_cd` (str), and `exp_type` (str) [^r7][^r34]
* **Optional fields**: None [^r34]
* **Errors**: [[err-cc-0009|ERR-CC-0009]], as well as standard system and security errors [^r7]
* **Source file**: `04_service_definitions/accounts_payable/exp_save.yaml` [^r32]

### exp_get

Service `exp_get` (EXPENSE CLAIM GET) is a read service used to retrieve an existing expense claim record for display on screen [[screen-ap-exp-09|AP-EXP-09]] [^r3][^r8][^r18]. It returns a standard envelope with `rc`, `err_cd`, `msg`, and `data` [^r21].

* **Endpoint**: `POST /ll72/svc/exp_get` [^r18]
* **Required fields**: `exp_no` (str) [^r8][^r20]
* **Optional fields**: None [^r20]
* **Errors**: ERR-EXP-0001 (EXPENSE CLAIM NOT FOUND), ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r8][^r22]
* **Source file**: `04_service_definitions/accounts_payable/exp_get.yaml` [^r18]

### exp_search

Service `exp_search` (EXPENSE CLAIM LIST) executes a query to browse and list matching expense claims for screen [[screen-ap-exp-09|AP-EXP-09]] [^r3][^r9][^r36].

* **Endpoint**: `POST /ll72/svc/exp_search` [^r36]
* **Required fields**: None [^r38]
* **Optional fields**: `user_id` (str), `claim_dt` (date), `amount` (float), and `status` (str) [^r9][^r38]
* **Errors**: ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r40]
* **Source file**: `04_service_definitions/accounts_payable/exp_search.yaml` [^r36]

### exp_submit

Service `exp_submit` (EXPENSE CLAIM SUBMIT) submits a draft expense claim for approval, executing stored procedure `sp_exp_submit` [^r4][^r10][^r41][^r44]. It returns the standard response envelope [^r45].

* **Endpoint**: `POST /ll72/svc/exp_submit` [^r42]
* **Required fields**: `exp_no` (str) [^r43]
* **Optional fields**: `comment` (str) [^r43]
* **Errors**: ERR-EXP-0001, ERR-EXP-0007, and ERR-EXP-0230 (RECEIPT MISSING FOR LINE ABOVE LIMIT) [^r5][^r6][^r10]
* **Source file**: `04_service_definitions/accounts_payable/exp_submit.yaml` [^r41]

### exp_approve

Service `exp_approve` (EXPENSE CLAIM APPROVE) approves a submitted claim via stored procedure `sp_exp_approve` while validating approval thresholds and claim age [^r4][^r11][^r14][^r15].

* **Endpoint**: `POST /ll72/svc/exp_approve` [^r14]
* **Required fields**: `exp_no` (str) [^r16]
* **Optional fields**: `comment` (str) [^r16]
* **Errors**: ERR-EXP-0001 (EXPENSE CLAIM NOT FOUND), ERR-EXP-0007 (EXPENSE CLAIM NOT IN DRAFT (<status>)), [[err-apr-0003|ERR-APR-0003]] (SELF APPROVAL NOT ALLOWED), [[err-apr-0004|ERR-APR-0004]] (VALUE ABOVE YOUR LIMIT), and ERR-EXP-0240 (CLAIM OLDER THAN 90 DAYS) [^r5][^r6][^r11][^r17]
* **Source file**: `04_service_definitions/accounts_payable/exp_approve.yaml` [^r14]

### exp_reject

Service `exp_reject` (EXPENSE CLAIM REJECT) rejects a claim via stored procedure `sp_exp_reject` [^r4][^r12][^r31].

* **Endpoint**: `POST /ll72/svc/exp_reject` [^r28]
* **Required fields**: `exp_no` (str) and `reason` (str) [^r12][^r30]
* **Optional fields**: None [^r30]
* **Errors**: ERR-EXP-0001 (EXPENSE CLAIM NOT FOUND) [^r31]
* **Source file**: `04_service_definitions/accounts_payable/exp_reject.yaml` [^r28]

### exp_pay

Service `exp_pay` (EXPENSE CLAIM PAY) marks an approved expense claim as paid using stored procedure `sp_exp_pay` [^r4][^r13][^r23][^r26].

* **Endpoint**: `POST /ll72/svc/exp_pay` [^r24]
* **Required fields**: `exp_no` (str) [^r13][^r25]
* **Optional fields**: `comment` (str) [^r13][^r25]
* **Errors**: ERR-EXP-0001 (EXPENSE CLAIM NOT FOUND), ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r27]
* **Source file**: `04_service_definitions/accounts_payable/exp_pay.yaml` [^r23]

## See also

* [[screen-ap-exp-09|AP-EXP-09 Expense Claim Entry]]
* [[errors-exp|ERR-EXP error codes]]
* [[err-apr-0003|ERR-APR-0003 Self-approval not permitted]]
* [[err-apr-0004|ERR-APR-0004 Advance amount exceeds PO unbilled commitment]]
* [[err-cc-0009|ERR-CC-0009]]
* [[services-ap-pay|AP pay services]]
* [[services-ap-inv|AP inv services]]
* [[services-ap-adv|AP adv services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 43, §14. Expense Claim (AP-EXP-09)
[^r14]: 04_service_definitions/accounts_payable/exp_approve.yaml, service
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 6, AP-EXP-09 EXPENSE CLAIM ENTRY
[^r15]: 04_service_definitions/accounts_payable/exp_approve.yaml, auth
[^r19]: 04_service_definitions/accounts_payable/exp_get.yaml, auth
[^r24]: 04_service_definitions/accounts_payable/exp_pay.yaml, auth
[^r29]: 04_service_definitions/accounts_payable/exp_reject.yaml, whole file
[^r33]: 04_service_definitions/accounts_payable/exp_save.yaml, endpoint
[^r37]: 04_service_definitions/accounts_payable/exp_search.yaml, auth
[^r42]: 04_service_definitions/accounts_payable/exp_submit.yaml, whole file
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 45, Step by step
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 34, exp_save EXPENSE CLAIM SAVE
[^r32]: 04_service_definitions/accounts_payable/exp_save.yaml, service: exp_save
[^r35]: 04_service_definitions/accounts_payable/exp_save.yaml, response
[^r34]: 04_service_definitions/accounts_payable/exp_save.yaml, request.fields
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 45, Step by step
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 34, exp_get EXPENSE CLAIM GET
[^r18]: 04_service_definitions/accounts_payable/exp_get.yaml, service: exp_get
[^r21]: 04_service_definitions/accounts_payable/exp_get.yaml, response
[^r20]: 04_service_definitions/accounts_payable/exp_get.yaml, request
[^r22]: 04_service_definitions/accounts_payable/exp_get.yaml, errors
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 34, exp_search EXPENSE CLAIM LIST
[^r36]: 04_service_definitions/accounts_payable/exp_search.yaml, service: exp_search
[^r38]: 04_service_definitions/accounts_payable/exp_search.yaml, request.fields
[^r40]: 04_service_definitions/accounts_payable/exp_search.yaml, common_errors
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 45, Step by step
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 35, exp_submit EXPENSE CLAIM SUBMIT
[^r41]: 04_service_definitions/accounts_payable/exp_submit.yaml, whole file
[^r44]: 04_service_definitions/accounts_payable/exp_submit.yaml, procedures
[^r45]: 04_service_definitions/accounts_payable/exp_submit.yaml, response.envelope
[^r43]: 04_service_definitions/accounts_payable/exp_submit.yaml, request.fields
[^r5]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 9
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 35, exp_approve EXPENSE CLAIM APPROVE
[^r16]: 04_service_definitions/accounts_payable/exp_approve.yaml, request.fields
[^r17]: 04_service_definitions/accounts_payable/exp_approve.yaml, errors
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 35, exp_reject EXPENSE CLAIM REJECT
[^r31]: 04_service_definitions/accounts_payable/exp_reject.yaml, errors
[^r28]: 04_service_definitions/accounts_payable/exp_reject.yaml, whole file
[^r30]: 04_service_definitions/accounts_payable/exp_reject.yaml, request.fields
[^r13]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 35, exp_pay EXPENSE CLAIM PAY
[^r23]: 04_service_definitions/accounts_payable/exp_pay.yaml, service: exp_pay
[^r26]: 04_service_definitions/accounts_payable/exp_pay.yaml, response
[^r25]: 04_service_definitions/accounts_payable/exp_pay.yaml, request
[^r27]: 04_service_definitions/accounts_payable/exp_pay.yaml, errors
