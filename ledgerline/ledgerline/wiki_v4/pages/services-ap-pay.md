---
title: "AP pay services"
type: "service-group"
slug: "services-ap-pay"
summary: "Ledgerline AP payment run services supporting screen AP-PAY-03 for proposing, approving, releasing, generating, and cancelling supplier payment batches."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/accounts_payable/pay_approve.xml", "04_service_definitions/accounts_payable/pay_cancel.xml", "04_service_definitions/accounts_payable/pay_file.xml", "04_service_definitions/accounts_payable/pay_get.xml", "04_service_definitions/accounts_payable/pay_propose.xml", "04_service_definitions/accounts_payable/pay_release.xml", "04_service_definitions/accounts_payable/pay_search.xml", "12_integrations/wsdl/LedgerlineGateway.wsdl"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | AP |
| Screen | [[screen-ap-pay-03|AP-PAY-03]] |
| Object | pay |
| Gateway Port | GatewayPort |
| Endpoint Host | ll72-app01:8091 |
| IT Owner | [[user-jfletcher|Joanna Fletcher (JFLETCHER)]] |
| Status | current |

The `pay` service group in the Accounts Payable (AP) module manages the full lifecycle of automated supplier payment proposals and disbursements in Ledgerline [^r11][^r19]. Invoked primarily from screen [[screen-ap-pay-03|AP-PAY-03]], these operations handle proposal generation, record retrieval, segregation-of-duties approval, treasury release, clearing file creation, historical searches, and batch cancellations [^r1][^r2][^r3][^r4][^r5][^r6][^r7][^r11]. Originally created under Ledgerline 7.0, all seven operations remain exposed via the Ledgerline 7.2 compatibility listener on port 8091 under the `GatewayPort` port type and are maintained by IT owner [[user-jfletcher|Joanna Fletcher (JFLETCHER)]] [^r19][^r20][^r35][^r39][^r49].

| Field | Value |
|---|---|
| Module | AP [^r19] |
| Screen | [[screen-ap-pay-03|AP-PAY-03]] [^r11] |
| Service Object | pay [^r11] |
| Target Namespace | `urn:ledgerline:svc:ap` [^r31][^r36][^r40] |
| Compatibility Endpoint | `http://ll72-app01:8091/ws/ap/<service>` [^r19][^r24][^r28][^r31][^r36][^r42][^r46] |
| Gateway PortType | GatewayPort [^r49] |
| IT Owner | [[user-jfletcher|Joanna Fletcher (JFLETCHER)]] [^r20][^r39][^r44] |

## Services

### pay_propose

The `pay_propose` write service executes stored procedure `sp_pay_propose` to evaluate open items, enforce settlement discount rules, verify supplier bank mandates, generate draft proposals, and allocate a run number [^r1][^r12].

* **Type**: write [^r12][^r36]
* **Endpoint**: `http://ll72-app01:8091/ws/ap/pay_propose` [^r36]
* **Stored procedure**: `sp_pay_propose` [^r12]
* **Required fields**: `run_dt` (xs:date), `bank_cd` (xs:string), `due_upto` (xs:date) [^r12][^r37]
* **Optional fields**: `sup_cd` (xs:string) [^r12][^r37]
* **Errors**: [[err-sup-0030|ERR-SUP-0030]], ERR-PAY-0105 [^r10][^r12][^r38]
* **Source file**: `04_service_definitions/accounts_payable/pay_propose.xml` [^r36]

### pay_get

The `pay_get` read service retrieves proposed invoice transactions into the working grid for user review [^r2][^r13][^r31].

* **Type**: read [^r13][^r31]
* **Endpoint**: `http://ll72-app01:8091/ws/ap/pay_get` [^r31]
* **Required fields**: `run_no` (xs:string) [^r13][^r32]
* **Optional fields**: none [^r32]
* **Errors**: ERR-PAY-0001 [^r8][^r13][^r34]
* **Source file**: `04_service_definitions/accounts_payable/pay_get.xml` [^r31]

### pay_approve

The `pay_approve` write service invokes `sp_pay_approve` to validate user delegation limits, prevent duplicate settlement runs, enforce segregation of duties, and advance the run status [^r3][^r14].

* **Type**: write [^r14][^r19]
* **Endpoint**: `http://ll72-app01:8091/ws/ap/pay_approve` [^r19]
* **Stored procedure**: `sp_pay_approve` [^r14]
* **Required fields**: `run_no` (xs:string) [^r14][^r21]
* **Optional fields**: `comment` (xs:string) [^r14][^r21]
* **Errors**: ERR-PAY-0001, ERR-PAY-0007, [[err-apr-0003|ERR-APR-0003]], [[err-apr-0004|ERR-APR-0004]], [[err-pay-0430|ERR-PAY-0430]], [[err-bnk-0101|ERR-BNK-0101]] [^r8][^r9][^r14][^r23]
* **Source file**: `04_service_definitions/accounts_payable/pay_approve.xml` [^r19]

### pay_release

The `pay_release` write service executes `sp_pay_release` to advance proposals to released status for file creation, lock records against manual edits, and queue batches into the treasury release buffer [^r4][^r15].

* **Type**: write [^r15][^r40]
* **Endpoint**: `http://ll72-app01:8091/ws/ap/pay_release` [^r42]
* **Stored procedure**: `sp_pay_release` [^r15]
* **Required fields**: `run_no` (xs:string) [^r15][^r41]
* **Optional fields**: `comment` (xs:string) [^r15][^r41]
* **Errors**: ERR-PAY-0001, ERR-PAY-0007 [^r8][^r9][^r15][^r43]
* **Source file**: `04_service_definitions/accounts_payable/pay_release.xml` [^r40]

### pay_file

The `pay_file` write service invokes `sp_pay_file` to compile payment batches into bank clearing media, deposit transmission files into the network interface directory, mark the run complete, and post General Ledger balance reductions [^r5][^r16].

* **Type**: write [^r16][^r27]
* **Endpoint**: `http://ll72-app01:8091/ws/ap/pay_file` [^r28]
* **Stored procedure**: `sp_pay_file` [^r16]
* **Required fields**: `run_no` (xs:string) [^r16][^r29]
* **Optional fields**: none [^r29]
* **Errors**: ERR-PAY-0001, ERR-PAY-0440, [[err-bnk-0101|ERR-BNK-0101]] [^r8][^r16][^r51]
* **Source file**: `04_service_definitions/accounts_payable/pay_file.xml` [^r27]

### pay_cancel

The `pay_cancel` write service runs `sp_pay_cancel` with a mandatory cancellation explanation, clearing temporary staging tables, unlocking open invoices, and marking the run cancelled [^r7][^r17].

* **Type**: write [^r17][^r25]
* **Endpoint**: `http://ll72-app01:8091/ws/ap/pay_cancel` [^r24]
* **Stored procedure**: `sp_pay_cancel` [^r17]
* **Required fields**: `run_no` (xs:string), `reason` (xs:string) [^r17][^r26]
* **Optional fields**: none [^r26]
* **Errors**: ERR-PAY-0001, ERR-PAY-0801 [^r8][^r17][^r50]
* **Source file**: `04_service_definitions/accounts_payable/pay_cancel.xml` [^r24]

### pay_search

The `pay_search` read service queries historical payment runs across settlements, filtering by date, bank code, due date, and status [^r6][^r18][^r45].

* **Type**: read [^r18][^r45]
* **Endpoint**: `http://ll72-app01:8091/ws/ap/pay_search` [^r46]
* **Required fields**: none [^r47]
* **Optional fields**: `run_dt` (xs:date), `bank_cd` (xs:string), `due_upto` (xs:date), `status` (xs:string) [^r18][^r47]
* **Errors**: ERR-PAY-0105 [^r10][^r18][^r48]
* **Source file**: `04_service_definitions/accounts_payable/pay_search.xml` [^r45]

## See also

* [[screen-ap-pay-03|AP-PAY-03 Payment Run]]
* [[errors-pay|Errors PAY]]
* [[errors-bnk|Errors BNK]]
* [[services-ap-bnk|AP bnk services]]
* [[services-ap-inv|AP inv services]]
* [[services-ap-spy-16|AP-SPY-16 Supplier Payment Hold Hold]]
* [[user-jfletcher|Joanna Fletcher (JFLETCHER)]]
* [[user-dramsden|Derek Ramsden (DRAMSDEN)]]

## References

[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 8, AP-PAY-03 PAYMENT RUN
[^r19]: 04_service_definitions/accounts_payable/pay_approve.xml, wsdl:definitions
[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 19, Step by step
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 19, Step by step
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 19, Step by step
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 20, Step by step
[^r5]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 20, Step by step
[^r6]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 20, Step by step
[^r7]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 20, Step by step
[^r20]: 04_service_definitions/accounts_payable/pay_approve.xml, wsdl:definitions
[^r35]: 04_service_definitions/accounts_payable/pay_get.xml, header comment
[^r39]: 04_service_definitions/accounts_payable/pay_propose.xml, header comment
[^r49]: 12_integrations/wsdl/LedgerlineGateway.wsdl, GatewayPort
[^r31]: 04_service_definitions/accounts_payable/pay_get.xml, wsdl:documentation
[^r36]: 04_service_definitions/accounts_payable/pay_propose.xml, wsdl:documentation
[^r40]: 04_service_definitions/accounts_payable/pay_release.xml, wsdl:documentation
[^r24]: 04_service_definitions/accounts_payable/pay_cancel.xml, Header comment
[^r28]: 04_service_definitions/accounts_payable/pay_file.xml, wsdl:definitions
[^r42]: 04_service_definitions/accounts_payable/pay_release.xml, wsdl:service
[^r46]: 04_service_definitions/accounts_payable/pay_search.xml, header
[^r44]: 04_service_definitions/accounts_payable/pay_release.xml, Comments
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 29, pay_propose PAYMENT RUN PROPOSE
[^r37]: 04_service_definitions/accounts_payable/pay_propose.xml, pay_proposeRequest
[^r10]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 15, ERR-PAY-0105 DATE IN PAST
[^r38]: 04_service_definitions/accounts_payable/pay_propose.xml, ll:errors
[^r13]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 29, pay_get PAYMENT RUN GET
[^r32]: 04_service_definitions/accounts_payable/pay_get.xml, wsdl:types/xs:schema
[^r8]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 15, ERR-PAY-0001 PAYMENT RUN NOT FOUND
[^r34]: 04_service_definitions/accounts_payable/pay_get.xml, ll:errors
[^r14]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 29, pay_approve PAYMENT RUN APPROVE
[^r21]: 04_service_definitions/accounts_payable/pay_approve.xml, pay_approveRequest
[^r9]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 15, ERR-PAY-0007 PAYMENT RUN NOT IN DRAFT (<status>)
[^r23]: 04_service_definitions/accounts_payable/pay_approve.xml, ll:errors
[^r15]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 29, pay_release PAYMENT RUN RELEASE
[^r41]: 04_service_definitions/accounts_payable/pay_release.xml, wsdl:types
[^r43]: 04_service_definitions/accounts_payable/pay_release.xml, ll:errors
[^r16]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 30, pay_file PAYMENT RUN FILE
[^r27]: 04_service_definitions/accounts_payable/pay_file.xml, wsdl:documentation
[^r29]: 04_service_definitions/accounts_payable/pay_file.xml, xs:element name="pay_fileRequest"
[^r51]: 04_service_definitions/accounts_payable/pay_file.xml, ll:errors
[^r17]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 30, pay_cancel PAYMENT RUN CANCEL
[^r25]: 04_service_definitions/accounts_payable/pay_cancel.xml, wsdl:documentation
[^r26]: 04_service_definitions/accounts_payable/pay_cancel.xml, pay_cancelRequest
[^r50]: 04_service_definitions/accounts_payable/pay_cancel.xml, ll:errors
[^r18]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 30, pay_search PAYMENT RUN LIST
[^r45]: 04_service_definitions/accounts_payable/pay_search.xml, wsdl:documentation
[^r47]: 04_service_definitions/accounts_payable/pay_search.xml, wsdl:types
[^r48]: 04_service_definitions/accounts_payable/pay_search.xml, ll:errors
