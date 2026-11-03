---
title: "PUR pr services"
type: "service-group"
slug: "services-pur-pr"
summary: "Ledgerline PUR purchase request services covering PR defaults, creation, submission, approval, retrieval, and search."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/purchase/pr_approve.yaml", "04_service_definitions/purchase/pr_fetch.yaml", "04_service_definitions/purchase/pr_get.yaml", "04_service_definitions/purchase/pr_save.yaml", "04_service_definitions/purchase/pr_search.yaml", "04_service_definitions/purchase/pr_submit.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | PUR |
| Object | PR (Purchase Request) |
| Services | pr_fetch, pr_save, pr_submit, pr_approve, pr_get, pr_search |
| Primary screens | PUR-PR-01, PUR-PR-04 |
| Authentication | X-LL-Session header with authorised role |

The PUR purchase request service group manages the lifecycle of purchase requests in Ledgerline, including fetching defaults, draft creation, workflow submission, approval routing, and querying [^r4][^r6][^r7][^r8][^r9]. These services interact primarily with screens [[screen-pur-pr-01|PUR-PR-01]] for request entry and [[screen-pur-pr-04|PUR-PR-04]] for approvals [^r4][^r8][^r10]. All services authenticate callers via the `X-LL-Session` session token header and require an authorised user role [^r11][^r17][^r24][^r29][^r34][^r39].

| Field | Value |
|---|---|
| Module | PUR [^r6][^r10] |
| Target object | Purchase Request (PR) [^r4][^r6] |
| Services | pr_fetch, pr_save, pr_submit, pr_approve, pr_get, pr_search [^r4][^r8][^r9] |
| Associated screens | [[screen-pur-pr-01|PUR-PR-01]], [[screen-pur-pr-04|PUR-PR-04]] [^r4][^r8] |
| Auth header | `X-LL-Session` [^r11][^r17][^r24][^r29][^r34][^r39] |

## Services

### pr_fetch

The read service `pr_fetch` (PR DEFAULTS) populates item defaults on screen [[screen-pur-pr-01|PUR-PR-01]] and has been available since version 7.2.3 [^r5][^r16]. Its endpoint is `POST /ll72/svc/pr_fetch` [^r16]. In this service, the estimated rate `est_rate` is derived from the rate on the last released order for the item rather than the contract rate [^r22].

* **Required fields:** `itm_cd` (string, ITEM CD) [^r5][^r18].
* **Optional fields:** none [^r18].
* **Errors:** ERR-ITM-0010 ('ITEM NOT FOUND') [^r5][^r20], along with common errors ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r21].
* **Envelope:** returns `rc` ('S | W | E'), `err_cd` (when rc is E), `msg` (short message in capitals), and `data` [^r19].
* **Source file:** `04_service_definitions/purchase/pr_fetch.yaml` [^r16].

### pr_save

The write service `pr_save` creates or updates purchase requests on screen [[screen-pur-pr-01|PUR-PR-01]] at endpoint `POST /ll72/svc/pr_save`, available since Ledgerline version 7.0 [^r4][^r6][^r28]. It executes stored procedures `sp_pr_save` and `sp_doc_no_next`, and calculates the estimated value as quantity multiplied by estimated rate multiplied by 1.20 because Ledgerline assumes 20% VAT on every request [^r6][^r31].

* **Required fields:** `cc_cd`, `need_dt`, `itm_cd`, and `qty` [^r6][^r30].
* **Optional fields:** `pr_type`, `whs_cd`, `est_rate`, and `remarks` [^r30].
* **Errors:** ERR-ITM-0010, [[err-itm-0011|ERR-ITM-0011]], [[err-cc-0009|ERR-CC-0009]], and ERR-PR-0105 (raised when the need-by date is in the past), as well as ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r3][^r32].
* **Source file:** `04_service_definitions/purchase/pr_save.yaml` [^r28].

### pr_submit

The write service `pr_submit` submits a purchase request into workflow routing from screen [[screen-pur-pr-01|PUR-PR-01]] via endpoint `POST /ll72/svc/pr_submit`, available since version 7.0 [^r4][^r7][^r38][^r39]. It triggers stored procedures `sp_appr_route` and `sp_ntf_enqueue` [^r7][^r42].

* **Required fields:** `pr_no` (string, PR NO) [^r7][^r40].
* **Optional fields:** none [^r40].
* **Errors:** ERR-PR-0001 (PR NOT FOUND), ERR-PR-0007 (PR NOT IN DRAFT (<status>), raised when the PR is not in Draft status), and [[err-apr-0009|ERR-APR-0009]] (NO APPROVER FOUND), as well as ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r1][^r7][^r43][^r44].
* **Envelope:** returns `rc` ('S | W | E'), `err_cd` (when rc is E), `msg` (short message in capitals), and `data` [^r41].
* **Source file:** `04_service_definitions/purchase/pr_submit.yaml` [^r38].

### pr_approve

The write service `pr_approve` (PR APPROVE/REJECT) executes an approval or rejection decision on screen [[screen-pur-pr-04|PUR-PR-04]] via endpoint `POST /ll72/svc/pr_approve`, available since version 7.0 [^r8][^r10].

* **Required fields:** `pr_no` (string, PR NO) and `decision` (string, 'A' or 'R') [^r8][^r12].
* **Optional fields:** `comment` (string, COMMENT) [^r12].
* **Errors:** ERR-PR-0001 (PR NOT FOUND), ERR-PR-0008 (PR NOT PENDING (<status>), raised when approval is attempted on a PR not in pending status), [[err-apr-0003|ERR-APR-0003]] (SELF APPROVAL NOT ALLOWED), and [[err-apr-0004|ERR-APR-0004]] (VALUE ABOVE YOUR LIMIT, raised when value exceeds approval limits), plus ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r2][^r8][^r14][^r15].
* **Envelope:** returns `rc` ('S | W | E'), `err_cd` (when rc is E), `msg` (short message in capitals), and `data` [^r13].
* **Source file:** `04_service_definitions/purchase/pr_approve.yaml` [^r10].

### pr_get

The read service `pr_get` retrieves an individual PR record and has been available since version 7.0 [^r9][^r23]. It is called via endpoint `POST /ll72/svc/pr_get` and is not assigned to a screen [^r23][^r24].

* **Required fields:** `pr_no` (string, PR NO) [^r9][^r25].
* **Optional fields:** none [^r25].
* **Errors:** ERR-PR-0001 (PR NOT FOUND), ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r27].
* **Envelope:** returns `rc` ('S | W | E'), `err_cd` (when rc is E), `msg` (short message in capitals), and `data` [^r26].
* **Source file:** `04_service_definitions/purchase/pr_get.yaml` [^r23].

### pr_search

The read service `pr_search` (PR LIST) queries purchase requests and has been available since version 7.0 [^r9][^r33]. It operates via endpoint `POST /ll72/svc/pr_search` and is not bound to a specific screen [^r33][^r34].

* **Required fields:** none [^r35].
* **Optional fields:** `status` (string, STATUS) and `raised_by` (string, USER ID) [^r9][^r35].
* **Errors:** ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r37].
* **Envelope:** returns `rc` ('S | W | E'), `err_cd` (when rc is E), `msg` (short message in capitals), and `data` [^r36].
* **Source file:** `04_service_definitions/purchase/pr_search.yaml` [^r33].

## See also

* [[screen-pur-pr-01|PUR-PR-01 Purchase Request Entry]]
* [[screen-pur-pr-04|PUR-PR-04 Purchase Request Approval]]
* [[services-pur-po|PUR po services]]
* [[services-pur-sup|PUR sup services]]
* [[services-pur-bud|PUR bud services]]
* [[err-apr-0003|ERR-APR-0003 Self-approval not permitted]]
* [[err-apr-0004|ERR-APR-0004 Advance amount exceeds PO unbilled commitment]]
* [[err-apr-0009|ERR-APR-0009 No approver found]]
* [[err-cc-0009|ERR-CC-0009]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]

## References

[^r4]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 29, PUR-PR-01 PURCHASE REQUEST ENTRY
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 4, §2. Purchase services
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 5, §2. Purchase services
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 5, §2. Purchase services
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 5, §2. Purchase services
[^r10]: 04_service_definitions/purchase/pr_approve.yaml, whole file
[^r11]: 04_service_definitions/purchase/pr_approve.yaml, auth
[^r17]: 04_service_definitions/purchase/pr_fetch.yaml, auth
[^r24]: 04_service_definitions/purchase/pr_get.yaml, endpoint
[^r29]: 04_service_definitions/purchase/pr_save.yaml, auth
[^r34]: 04_service_definitions/purchase/pr_search.yaml, auth
[^r39]: 04_service_definitions/purchase/pr_submit.yaml, service: pr_submit
[^r5]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 4, §2. Purchase services
[^r16]: 04_service_definitions/purchase/pr_fetch.yaml, service
[^r22]: 04_service_definitions/purchase/pr_fetch.yaml, notes
[^r18]: 04_service_definitions/purchase/pr_fetch.yaml, request.fields
[^r20]: 04_service_definitions/purchase/pr_fetch.yaml, errors
[^r21]: 04_service_definitions/purchase/pr_fetch.yaml, common_errors
[^r19]: 04_service_definitions/purchase/pr_fetch.yaml, response.envelope
[^r28]: 04_service_definitions/purchase/pr_save.yaml, service: pr_save
[^r31]: 04_service_definitions/purchase/pr_save.yaml, procedures
[^r30]: 04_service_definitions/purchase/pr_save.yaml, request.fields
[^r3]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 19, ERR-PR-0105
[^r32]: 04_service_definitions/purchase/pr_save.yaml, errors
[^r38]: 04_service_definitions/purchase/pr_submit.yaml, service: pr_submit
[^r42]: 04_service_definitions/purchase/pr_submit.yaml, procedures
[^r40]: 04_service_definitions/purchase/pr_submit.yaml, request
[^r1]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 19, ERR-PR-0007
[^r43]: 04_service_definitions/purchase/pr_submit.yaml, errors
[^r44]: 04_service_definitions/purchase/pr_submit.yaml, common_errors
[^r41]: 04_service_definitions/purchase/pr_submit.yaml, response
[^r12]: 04_service_definitions/purchase/pr_approve.yaml, request.fields
[^r2]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 19, ERR-PR-0008
[^r14]: 04_service_definitions/purchase/pr_approve.yaml, errors
[^r15]: 04_service_definitions/purchase/pr_approve.yaml, common_errors
[^r13]: 04_service_definitions/purchase/pr_approve.yaml, response.envelope
[^r23]: 04_service_definitions/purchase/pr_get.yaml, service: pr_get
[^r25]: 04_service_definitions/purchase/pr_get.yaml, request
[^r27]: 04_service_definitions/purchase/pr_get.yaml, errors
[^r26]: 04_service_definitions/purchase/pr_get.yaml, response
[^r33]: 04_service_definitions/purchase/pr_search.yaml, service: pr_search
[^r35]: 04_service_definitions/purchase/pr_search.yaml, request
[^r37]: 04_service_definitions/purchase/pr_search.yaml, common_errors
[^r36]: 04_service_definitions/purchase/pr_search.yaml, response
