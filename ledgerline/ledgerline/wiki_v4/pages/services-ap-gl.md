---
title: "AP gl services"
type: "service-group"
slug: "services-ap-gl"
summary: "Ledgerline AP general ledger journal voucher services gl_post, gl_query, and gl_reverse for screen AP-GL-14."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/accounts_payable/gl_post.yaml", "04_service_definitions/accounts_payable/gl_query.yaml", "04_service_definitions/accounts_payable/gl_reverse.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| service_group | services-ap-gl |
| module | accounts_payable |
| screen | AP-GL-14 |
| services | gl_post, gl_query, gl_reverse |
| introduced | Ledgerline 7.0 |
| status | current |

The `services-ap-gl` service group provides journal voucher processing for the Accounts Payable module on screen [[screen-ap-gl-14|AP-GL-14]] [^r8][^r12]. Available since Ledgerline 7.0, it contains the three services `gl_post`, `gl_query`, and `gl_reverse` to post, inspect, and reverse general ledger journal vouchers [^r8][^r12][^r18][^r23]. All requests authenticate via session tokens passed in the `X-LL-Session` header and require corresponding user role authorizations [^r13][^r19][^r24].

## Services

### gl_post

The `gl_post` service is an AP write service that provides GL POSTING POST functionality on screen [[screen-ap-gl-14|AP-GL-14]] [^r9][^r12]. It validates nominal accounts, period controls, and fields, closes the entry against editing, assigns references, and commits balances to the nominal ledger [^r2][^r4]. It executes backend procedure `sp_gl_post` at endpoint `POST /ll72/svc/gl_post` [^r13][^r15].

* **Required fields:** `jv_no` (string, JV NO) [^r9][^r14].
* **Optional fields:** `comment` (string, COMMENT) [^r14].
* **Errors:** [[err-gl-0001|ERR-GL-0001]] (GL POSTING NOT FOUND), [[err-gl-0007|ERR-GL-0007]] (GL POSTING NOT IN DRAFT (<status>)), ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r4][^r7][^r16][^r17].
* **Source file:** `04_service_definitions/accounts_payable/gl_post.yaml` [^r12].

### gl_query

The `gl_query` service is an AP read service that retrieves committed general ledger journal voucher details into screen [[screen-ap-gl-14|AP-GL-14]] at endpoint `POST /ll72/svc/gl_query` [^r1][^r6][^r10][^r18]. It returns a standard response envelope containing `rc`, `err_cd`, `msg`, and `data` [^r21].

* **Required fields:** none [^r10][^r20].
* **Optional fields:** `jv_dt` (date, JV DT), `acct_cd` (string, ACCOUNT), and `amount` (float, AMOUNT) [^r10][^r20].
* **Errors:** [[err-gl-0001|ERR-GL-0001]] (GL POSTING NOT FOUND), ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r22].
* **Source file:** `04_service_definitions/accounts_payable/gl_query.yaml` [^r18].

### gl_reverse

The `gl_reverse` service is an AP write service providing GL POSTING REVERSE operations on screen [[screen-ap-gl-14|AP-GL-14]] at endpoint `POST /ll72/svc/gl_reverse` [^r11][^r23]. After prompting for a posting date and corrective explanation, it executes database procedure `sp_gl_reverse` to create an offsetting journal entry in the nominal ledger and link the original posting to the generated reversal voucher [^r3][^r5][^r11][^r27]. Its response envelope contains `rc`, `err_cd`, `msg`, and `data` [^r26].

* **Required fields:** `jv_no` (string, JV NO) [^r11][^r25].
* **Optional fields:** `reason` (string, REASON) [^r11][^r25].
* **Errors:** [[err-gl-0001|ERR-GL-0001]] (GL POSTING NOT FOUND) [^r27].
* **Source file:** `04_service_definitions/accounts_payable/gl_reverse.yaml` [^r23].

## See also

* [[screen-ap-gl-14|AP-GL-14 Gl Posting]]
* [[err-gl-0001|ERR-GL-0001 Missing or Invalid Header Information]]
* [[err-gl-0007|ERR-GL-0007 Ledger Integrity Failure]]
* [[services-ap-inv|AP inv services]]
* [[services-ap-per|AP per services]]

## References

[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 7, AP-GL-14 GL POSTING
[^r12]: 04_service_definitions/accounts_payable/gl_post.yaml, whole file
[^r18]: 04_service_definitions/accounts_payable/gl_query.yaml, whole file
[^r23]: 04_service_definitions/accounts_payable/gl_reverse.yaml, whole file
[^r13]: 04_service_definitions/accounts_payable/gl_post.yaml, auth
[^r19]: 04_service_definitions/accounts_payable/gl_query.yaml, auth
[^r24]: 04_service_definitions/accounts_payable/gl_reverse.yaml, whole file
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 36, gl_post GL POSTING POST
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 52, Buttons and services
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 54, Worked example: Gl Posting
[^r15]: 04_service_definitions/accounts_payable/gl_post.yaml, procedures
[^r14]: 04_service_definitions/accounts_payable/gl_post.yaml, request.fields
[^r7]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 10
[^r16]: 04_service_definitions/accounts_payable/gl_post.yaml, errors
[^r17]: 04_service_definitions/accounts_payable/gl_post.yaml, common_errors
[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 52, Buttons and services
[^r6]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 55, Questions users ask
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 36, gl_query GL POSTING QUERY
[^r21]: 04_service_definitions/accounts_payable/gl_query.yaml, response.envelope
[^r20]: 04_service_definitions/accounts_payable/gl_query.yaml, request.fields
[^r22]: 04_service_definitions/accounts_payable/gl_query.yaml, errors
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 36, gl_reverse GL POSTING REVERSE
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 53, Reversing a posted journal
[^r5]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 55, Questions users ask
[^r27]: 04_service_definitions/accounts_payable/gl_reverse.yaml, errors
[^r26]: 04_service_definitions/accounts_payable/gl_reverse.yaml, response
[^r25]: 04_service_definitions/accounts_payable/gl_reverse.yaml, request.fields
