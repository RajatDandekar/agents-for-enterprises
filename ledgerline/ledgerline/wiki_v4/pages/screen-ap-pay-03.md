---
title: "AP-PAY-03 Payment Run"
type: "screen"
slug: "screen-ap-pay-03"
summary: "Accounts Payable screen managing proposal, authorisation, file generation, and clearing of supplier payment runs to Northbridge Cycles bank accounts."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-AP-003 Supplier Payment Run v1.4.pdf", "03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/accounts_payable/pay_approve.xml", "04_service_definitions/accounts_payable/pay_cancel.xml", "04_service_definitions/accounts_payable/pay_file.xml", "04_service_definitions/accounts_payable/pay_get.xml", "04_service_definitions/accounts_payable/pay_propose.xml", "04_service_definitions/accounts_payable/pay_release.xml", "04_service_definitions/accounts_payable/pay_search.xml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen Code | AP-PAY-03 |
| Title | Payment Run |
| Module | Accounts Payable |
| Navigation | Accounts payable > Payment run |
| Roles | AP-CLERK, AP-MGR, FIN-CTRL, SYS-ADMIN |
| Key Services | pay_propose, pay_get, pay_approve, pay_release, pay_file, pay_cancel, pay_search |
| Status | current |

Screen AP-PAY-03 manages disbursement preparation, authorisation, and electronic transmission from Northbridge Cycles bank accounts to suppliers [^r4]. It provides Accounts Payable staff with tools to review proposed remittances, reconcile cash allocations, inspect individual lines for stops or disputes, and verify electronic transfer configurations [^r1][^r2]. The screen also tracks omitted supplier entries via an exclusion pane and enforces segregation of duties across payment approvals and bank file exports [^r3][^r16].

## Fields

The screen layout is located under Accounts payable > Payment run and is accessible to users holding roles AP-CLERK, AP-MGR, FIN-CTRL, or SYS-ADMIN [^r11].

| Field label | Technical name | Mandatory / Optional | Notes |
|---|---|---|---|
| RUN DT | `run_dt` | Mandatory | Processing date evaluated during proposals and searches [^r5][^r12][^r24]. |
| BANK CD | `bank_cd` | Mandatory | Source bank account code [^r5][^r12][^r24]. |
| DUE UPTO | `due_upto` | Mandatory | Cut-off date for open item selection [^r5][^r12][^r24]. |
| RUN NO | `run_no` | Mandatory | Payment run identifier generated or searched [^r5][^r12][^r18][^r20]. |
| REASON | `reason` | Mandatory | Explanatory note, required when cancelling a proposal [^r5][^r10][^r12][^r18]. |
| SUP CD | `sup_cd` | Optional | Supplier code filter [^r5][^r12][^r21]. |
| COMMENT | `comment` | Optional | Additional narrative on approval or header records [^r5][^r12][^r15]. |
| STATUS | `status` | Optional | Payment run lifecycle status [^r5][^r12][^r24]. |

Staff review proposal header details on screen AP-PAY-03 to confirm the processing date, ensure automated job JOB-AP-030 has completed, and reconcile proposed remittances against cash allocations [^r1]. Users also check lines for unresolved debit notes, disputed invoices, or stop notices, confirming electronic transfer lines reflect format STD18 [^r2]. An exclusion summary pane displays supplier lines excluded under [[err-bnk-0101|ERR-BNK-0101]] [^r3].

## Keys and services

Screen actions link interface controls to service group [[services-ap-pay|services-ap-pay]] [^r13]:

* **Propose (`pay_propose`)**: Evaluates open items using `run_dt`, `bank_cd`, `due_upto`, and optional `sup_cd` to build a working register, assigns an audit reference in `run_no`, and sets `status` to draft [^r6][^r13][^r21].
* **Get (`pay_get` / F3)**: Invokes the read service passing `run_no` to retrieve existing payment run details [^r13][^r20].
* **Search (`pay_search` / F2 or Enter)**: Queries payment run lists based on `run_dt`, `bank_cd`, `due_upto`, and `status` [^r13][^r23][^r24].
* **Approve (`pay_approve` / F9)**: Invokes the write service using `run_no` and optional `comment`, validates sign-off authority, locks underlying invoices, and advances `status` to indicate management approval [^r7][^r13][^r15].
* **Release (`pay_release` / F9)**: Locks records against manual intervention and places transactions into the treasury release buffer [^r8][^r13][^r22].
* **File (`pay_file`)**: Passes `run_no` to format clearing media, writes the file to the local bank interface directory, marks `status` as completed, and posts general ledger entries reducing supplier balances and updating bank clearing controls [^r9][^r13][^r25].
* **Cancel (`pay_cancel` / Shift+F8)**: Requires an explanatory remark in `reason` along with `run_no`, releasing invoice holds, wiping temporary proposal tables, and changing `status` to cancelled [^r10][^r13][^r17][^r18].

## Messages

The interface validates entry and service execution against the following error messages:

* [[err-sup-0030|ERR-SUP-0030]]: Supplier Not Found, raised during supplier validation [^r14].
* ERR-PAY-0105: Date In Past, raised on invalid date entries [^r14].
* ERR-PAY-0001: Payment Run Not Found, raised when querying or processing an invalid run number [^r14][^r25].
* ERR-PAY-0007: Payment Run Not In Draft (<Status>), raised when actions require draft state [^r14].
* [[err-apr-0003|ERR-APR-0003]]: Self-approval not permitted, verified during approval execution [^r16].
* [[err-apr-0004|ERR-APR-0004]]: Advance amount exceeds PO unbilled commitment, verified during approval [^r16].
* [[err-pay-0430|ERR-PAY-0430]]: Payment proposal approver cannot be proposer, checked on approval submission [^r16].
* ERR-PAY-0440: Returned during payment file generation errors [^r25].
* [[err-bnk-0101|ERR-BNK-0101]]: Supplier bank details unverified, checked during approval and file creation, and highlighted in the exclusion pane [^r3][^r16][^r25].

## See also

* [[sop-ap-003|SOP-AP-003 Supplier Payment Run]]
* [[sop-ap-004|SOP-AP-004 Supplier Bank Detail Changes]]
* [[services-ap-pay|AP pay services]]
* [[errors-pay|Errors PAY]]
* [[errors-bnk|Errors BNK]]
* [[screen-ap-bnk-06|AP-BNK-06 Supplier Bank Details Entry]]
* [[screen-ap-inv-01|AP-INV-01 Supplier Invoice Entry]]
* [[screen-ap-dbn-04|AP-DBN-04 Debit Note Entry]]
* [[screen-ap-spy-16|AP-SPY-16 Supplier Payment Hold Hold]]

## References

[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 18, Purpose
[^r1]: 02_procedures/SOP-AP-003 Supplier Payment Run v1.4.pdf, p. 4, Screen checks on AP-PAY-03
[^r2]: 02_procedures/SOP-AP-003 Supplier Payment Run v1.4.pdf, p. 4, Screen checks on AP-PAY-03
[^r3]: 02_procedures/SOP-AP-003 Supplier Payment Run v1.4.pdf, p. 4, Screen checks on AP-PAY-03
[^r16]: 04_service_definitions/accounts_payable/pay_approve.xml, ll:errors
[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 8, AP-PAY-03 PAYMENT RUN
[^r5]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 18, §7. Payment Run (AP-PAY-03)
[^r12]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 8, AP-PAY-03 PAYMENT RUN
[^r24]: 04_service_definitions/accounts_payable/pay_search.xml, wsdl:types
[^r18]: 04_service_definitions/accounts_payable/pay_cancel.xml, pay_cancelRequest
[^r20]: 04_service_definitions/accounts_payable/pay_get.xml, wsdl:documentation
[^r10]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 20, Step by step
[^r21]: 04_service_definitions/accounts_payable/pay_propose.xml, wsdl:documentation
[^r15]: 04_service_definitions/accounts_payable/pay_approve.xml, wsdl:documentation
[^r13]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 8, AP-PAY-03 PAYMENT RUN
[^r6]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 19, Step by step
[^r23]: 04_service_definitions/accounts_payable/pay_search.xml, wsdl:documentation
[^r7]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 19, Step by step
[^r8]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 20, Step by step
[^r22]: 04_service_definitions/accounts_payable/pay_release.xml, wsdl:documentation
[^r9]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 20, Step by step
[^r25]: 04_service_definitions/accounts_payable/pay_file.xml, ll:errors
[^r17]: 04_service_definitions/accounts_payable/pay_cancel.xml, wsdl:documentation
[^r14]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 8, AP-PAY-03 PAYMENT RUN
