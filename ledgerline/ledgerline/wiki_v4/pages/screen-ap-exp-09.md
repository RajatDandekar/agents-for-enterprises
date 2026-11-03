---
title: "AP-EXP-09 Expense Claim Entry"
type: "screen"
slug: "screen-ap-exp-09"
summary: "Ledgerline screen for entering, searching, approving, rejecting, and paying staff out-of-pocket expense claims."
audience: "staff"
status: "mixed"
sources: ["01_policies/POL-TEX-007 Travel and Expenses Policy v2.4.pdf", "01_policies/POL-TEX-007 Travel and Expenses Policy v3.0 (effective 2027-01-01).pdf", "03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/accounts_payable/exp_approve.yaml", "04_service_definitions/accounts_payable/exp_get.yaml", "04_service_definitions/accounts_payable/exp_pay.yaml", "04_service_definitions/accounts_payable/exp_reject.yaml", "04_service_definitions/accounts_payable/exp_save.yaml", "04_service_definitions/accounts_payable/exp_search.yaml", "04_service_definitions/accounts_payable/exp_submit.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | AP-EXP-09 |
| Module | Accounts payable |
| Menu path | Accounts payable > Expense claim |
| Roles | AP-CLERK, AP-MGR, FIN-CTRL, SYS-ADMIN |
| Status | current |

Screen AP-EXP-09 is the Ledgerline screen used to enter, retrieve, review, and process staff out-of-pocket expense claims [^r1][^r3]. Staff enter claims into the screen within 60 days of incurring an expense, creating a header and line items with business purpose, cost centre, and ledger allocation [^r1]. Physical receipts for items exceeding £10 are referenced to the system line items on the screen and approved by the line manager before submission to purchase ledger [^r2]. Access is assigned to the roles AP-CLERK, AP-MGR, FIN-CTRL, and SYS-ADMIN [^r9].

## Fields

During initial drafting, the operator enters the user identifier, claim date, amount, cost centre, expense type, and an optional comment before saving [^r6]. Once submitted, core entry fields on the docket are locked against amendment unless rejected back to draft [^r8].

| Field label | Technical name | Mandatory | Purpose / Behaviour |
|---|---|---|---|
| USER ID | `user_id` | Yes [^r4][^r10] | Identifier of the claimant [^r4][^r6]. |
| CLAIM DT | `claim_dt` | Yes [^r4][^r10] | Date on which the claim is submitted or incurred [^r4][^r6]. |
| AMOUNT | `amount` | Yes [^r4][^r10] | Claim monetary total [^r4][^r6]. |
| CC CD | `cc_cd` | Yes [^r4][^r10] | Cost centre code charged; validated against master records [^r4][^r18]. |
| EXP TYPE | `exp_type` | Yes [^r4][^r10] | Category or code for the expense [^r4][^r6]. |
| EXP NO | `exp_no` | Yes [^r4][^r10] | System reference number identifying the expense docket [^r4][^r7]. |
| REASON | `reason` | Conditional [^r5] / Yes [^r10] | Rejection explanation; mandatory when rejecting a claim [^r5][^r10][^r16]. |
| STATUS | `status` | No [^r4][^r10] | Current processing status of the expense docket [^r4][^r10]. |
| COMMENT | `comment` | No [^r5][^r10] | Optional narrative notes entered at draft [^r5][^r6][^r10]. |

## Keys and services

Screen AP-EXP-09 is located under `Accounts payable > Expense claim` [^r3][^r9]. It triggers backend operations mapped to dedicated function keys and endpoints from [[services-ap-exp]]:

| Action | Function key | Service | Description |
|---|---|---|---|
| Save | F8 [^r11] | `exp_save` [^r3][^r11] | Write service that saves draft expense claim entries [^r13][^r17]. Validates `cc_cd` [^r18]. |
| Get | F3 [^r11] | `exp_get` [^r3][^r11] | Read service that retrieves an existing docket using `exp_no` via endpoint `POST /ll72/svc/exp_get` [^r7][^r14]. |
| Search | F2 / Enter [^r11] | `exp_search` [^r3][^r11] | Read service via `POST /ll72/svc/exp_search` querying claims across departments and dates using `user_id`, `claim_dt`, `amount`, and `status` [^r7][^r19][^r20]. |
| Submit | F9 [^r11] | `exp_submit` [^r3][^r11] | Write service that submits draft claims for management review [^r8][^r21]. |
| Approve | F9 [^r11] | `exp_approve` [^r3][^r11] | Write service that approves claims via stored procedure `sp_exp_approve` [^r11][^r13]. |
| Reject | Shift+F9 [^r11] | `exp_reject` [^r3][^r11] | Write service that returns claims to draft, requiring `exp_no` and `reason` [^r5][^r8][^r16]. |
| Pay | — [^r11] | `exp_pay` [^r3][^r11] | Backend write service that executes approved claim disbursements [^r11][^r15]. |

## Messages

Validation rules on AP-EXP-09 surface standard Ledgerline error codes [^r12]:

* [[err-cc-0009]]: Raised during `exp_save` if the specified cost centre code is not found [^r12][^r18].
* `ERR-EXP-0001`: Expense validation failure [^r12].
* `ERR-EXP-0007`: Expense header or line entry error [^r12].
* `ERR-EXP-0230`: Receipt Missing For Line Above Limit [^r12].
* [[err-apr-0003]]: Self-approval not permitted [^r12].
* [[err-apr-0004]]: Advance amount exceeds PO unbilled commitment [^r12].
* `ERR-EXP-0240`: Claim Older Than 90 Days [^r12].

## Versions and conflicts

* **Claim submission window**: Today, staff must enter claims on AP-EXP-09 within 60 days of incurring the expense ([[pol-tex-007]] v2.4, 1 July 2024) [^r1]. From 1 January 2027, claims must be recorded directly into screen AP-EXP-09 within 45 days of the spend (POL-TEX-007 v3.0) [^r22].
* **Review routing**: Today, grouped receipts for lines over £10 are approved by the line manager before passing to the purchase ledger clerk ([[pol-tex-007]] v2.4, 1 July 2024) [^r2]. From 1 January 2027, saved electronic entries route to the departmental manager for review prior to purchase ledger payment processing (POL-TEX-007 v3.0) [^r23].

## See also

* [[pol-tex-007]]: Travel and Expenses Policy governing expense claim submission rules
* [[services-ap-exp]]: Service definitions powering AP-EXP-09 (`exp_save`, `exp_get`, `exp_search`, `exp_submit`, `exp_approve`, `exp_reject`, `exp_pay`)
* [[errors-exp]]: Complete listing of `ERR-EXP-*` validation error codes
* [[err-cc-0009]]: Validation error raised when cost centre code is invalid
* [[err-apr-0003]]: Error code blocking self-approval on expense submissions
* [[err-apr-0004]]: Error code for commitment advance validation
* [[screen-fin-cc-01]]: Cost Centre Entry master screen

## References

[^r1]: 01_policies/POL-TEX-007 Travel and Expenses Policy v2.4.pdf, p. 4, §5. Claims
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 43, §14. Expense Claim (AP-EXP-09)
[^r2]: 01_policies/POL-TEX-007 Travel and Expenses Policy v2.4.pdf, p. 4, §5. Claims
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 6, AP-EXP-09 EXPENSE CLAIM ENTRY
[^r6]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 44, Step by step
[^r8]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 46, Tips
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 43, §14. Expense Claim (AP-EXP-09)
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 6, AP-EXP-09 EXPENSE CLAIM ENTRY
[^r18]: 04_service_definitions/accounts_payable/exp_save.yaml, errors
[^r7]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 45, Step by step
[^r5]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 44, Expense Claim (AP-EXP-09)
[^r16]: 04_service_definitions/accounts_payable/exp_reject.yaml, whole file
[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 6, AP-EXP-09 EXPENSE CLAIM ENTRY
[^r13]: 04_service_definitions/accounts_payable/exp_approve.yaml, screen
[^r17]: 04_service_definitions/accounts_payable/exp_save.yaml, service: exp_save
[^r14]: 04_service_definitions/accounts_payable/exp_get.yaml, service: exp_get
[^r19]: 04_service_definitions/accounts_payable/exp_search.yaml, service: exp_search
[^r20]: 04_service_definitions/accounts_payable/exp_search.yaml, request.fields
[^r21]: 04_service_definitions/accounts_payable/exp_submit.yaml, whole file
[^r15]: 04_service_definitions/accounts_payable/exp_pay.yaml, service: exp_pay
[^r12]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 6, AP-EXP-09 EXPENSE CLAIM ENTRY
[^r22]: 01_policies/POL-TEX-007 Travel and Expenses Policy v3.0 (effective 2027-01-01).pdf, p. 2, Purpose and Process
[^r23]: 01_policies/POL-TEX-007 Travel and Expenses Policy v3.0 (effective 2027-01-01).pdf, p. 3, Purpose and Process
