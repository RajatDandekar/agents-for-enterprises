---
title: "AP mat services"
type: "service-group"
slug: "services-ap-mat"
summary: "Ledgerline accounts payable three-way matching services attaching to screen AP-MAT-02 for invoice verification, retrieval, search, and manager override."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/accounts_payable/mat_get.yaml", "04_service_definitions/accounts_payable/mat_override.yaml", "04_service_definitions/accounts_payable/mat_run.yaml", "04_service_definitions/accounts_payable/mat_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| service_group | services-ap-mat |
| module | AP |
| screen | screen-ap-mat-02 |
| services | mat_get, mat_override, mat_run, mat_search |
| available_since | 7.0 |
| status | current |

The `mat` service group provides three-way matching services in the Ledgerline Accounts Payable module, operating against screen [[screen-ap-mat-02|AP-MAT-02]] [^r8][^r13][^r23]. It enables AP operators to search matching records, retrieve invoice lines alongside linked purchase order and goods receipt lines, execute matching checks against tolerance rules, and apply authorized management overrides [^r1][^r2][^r3][^r4]. All services in this group have been available since Ledgerline version 7.0 and communicate through standard POST endpoints requiring an active session token [^r13][^r14][^r18][^r23][^r28].

## Services

### mat_get

The `mat_get` service (THREE-WAY MATCH GET) is an Accounts Payable read service operating since version 7.0 at endpoint `POST /ll72/svc/mat_get` for screen [[screen-ap-mat-02|AP-MAT-02]] [^r10][^r13]. It retrieves invoice lines, linked purchase order lines, and warehouse receipt lines for the document referenced in the AP document field [^r2]. Authentication requires a session token in header `X-LL-Session` and a user role permitted to execute the service [^r14]. The service returns a standard envelope containing return code `rc` (`S | W | E`), `err_cd`, a short uppercase `msg`, and the result `data` [^r16].

* **Required fields**: `ap_doc` (str) [^r15].
* **Optional fields**: none [^r15].
* **Errors**: Specific error ERR-MAT-0001 (THREE-WAY MATCH NOT FOUND), as well as common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r5][^r17].
* **Source file**: `04_service_definitions/accounts_payable/mat_get.yaml` [^r13].

### mat_override

The `mat_override` service (THREE-WAY MATCH OVERRIDE) is an Accounts Payable write service operating since version 7.0 at endpoint `POST /ll72/svc/mat_override` on screen [[screen-ap-mat-02|AP-MAT-02]], executing database stored procedure `sp_mat_override` [^r11][^r18][^r21]. It forces an invoice record into an approved state, clears error conditions, and updates status to cleared by management, requiring commentary [^r4]. Calling the service requires an authenticated session token in header `X-LL-Session` and the AP-MGR role [^r7][^r19]. The service returns a standard envelope containing `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r21].

* **Required fields**: `ap_doc` (str) [^r11][^r20].
* **Optional fields**: `tol_pct` (float) [^r11][^r20].
* **Errors**: ERR-MAT-0001 and [[err-mat-0420|ERR-MAT-0420]] (OVERRIDE NEEDS AP-MGR ROLE), as well as common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r5][^r7][^r11][^r22].
* **Source file**: `04_service_definitions/accounts_payable/mat_override.yaml` [^r18].

### mat_run

The `mat_run` service (THREE-WAY MATCH RUN) is an Accounts Payable write service available since version 7.0 at endpoint `POST /ll72/svc/mat_run` for screen [[screen-ap-mat-02|AP-MAT-02]], executing backend procedure `sp_mat_run` [^r9][^r23][^r24][^r27]. It compares invoiced quantities against warehouse receipts and invoiced unit prices against purchase orders, advancing cleared vouchers to the payment register [^r3]. Requests require an authenticated session token in header `X-LL-Session` with an authorized role, and responses use the envelope format with fields `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r24][^r26].

* **Required fields**: `ap_doc` (str) [^r9][^r25].
* **Optional fields**: `comment` (str) [^r9][^r25].
* **Errors**: [[errors-mat|ERR-MAT-0410]] for price tolerance failures, ERR-MAT-0411 for quantity invoice excesses, and ERR-MAT-0412 when no GRN exists for a PO line [^r6][^r9].
* **Source file**: `04_service_definitions/accounts_payable/mat_run.yaml` [^r23].

### mat_search

The `mat_search` service (THREE-WAY MATCH LIST) is an Accounts Payable read service available since version 7.0 at endpoint `POST /ll72/svc/mat_search` on screen [[screen-ap-mat-02|AP-MAT-02]] [^r12][^r28][^r29]. It retrieves a selection list of unposted invoices awaiting clearance when AP DOC is left blank, filtering matches across optional criteria [^r1][^r12][^r30]. Requests require authentication via a session token in header `X-LL-Session` with a permitted user role, returning envelope fields `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r29][^r31].

* **Required fields**: none [^r30].
* **Optional fields**: `ap_doc` (str), `tol_pct` (float), and `status` (str) [^r12][^r30].
* **Errors**: Common errors ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r32].
* **Source file**: `04_service_definitions/accounts_payable/mat_search.yaml` [^r28].

## See also

* [[screen-ap-mat-02|screen-ap-mat-02]]: AP-MAT-02 Three-Way Match screen
* [[err-mat-0420|err-mat-0420]]: ERR-MAT-0420 Match override permission denied
* [[errors-mat|errors-mat]]: ERR-MAT message and error codes
* [[screen-ap-inv-01|screen-ap-inv-01]]: AP-INV-01 Supplier Invoice Entry
* [[services-ap-inv|services-ap-inv]]: AP inv services
* [[services-ap-pay|services-ap-pay]]: AP pay services
* [[services-pur-po|services-pur-po]]: PUR po services
* [[services-inv-grn|services-inv-grn]]: INV grn services

## References

[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 8, AP-MAT-02 THREE-WAY MATCH
[^r13]: 04_service_definitions/accounts_payable/mat_get.yaml, service: mat_get
[^r23]: 04_service_definitions/accounts_payable/mat_run.yaml, service: mat_run
[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 8, Step by step
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 8, Step by step
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 8, Step by step
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 8, Step by step
[^r14]: 04_service_definitions/accounts_payable/mat_get.yaml, service: mat_get
[^r18]: 04_service_definitions/accounts_payable/mat_override.yaml, whole file
[^r28]: 04_service_definitions/accounts_payable/mat_search.yaml, whole file
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 26, mat_get THREE-WAY MATCH GET
[^r16]: 04_service_definitions/accounts_payable/mat_get.yaml, response.envelope
[^r15]: 04_service_definitions/accounts_payable/mat_get.yaml, request.fields
[^r5]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 13, ERR-MAT-0001 THREE-WAY MATCH NOT FOUND
[^r17]: 04_service_definitions/accounts_payable/mat_get.yaml, errors
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 27, mat_override THREE-WAY MATCH OVERRIDE
[^r21]: 04_service_definitions/accounts_payable/mat_override.yaml, response
[^r7]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 13, ERR-MAT-0420 OVERRIDE NEEDS AP-MGR ROLE
[^r19]: 04_service_definitions/accounts_payable/mat_override.yaml, auth
[^r20]: 04_service_definitions/accounts_payable/mat_override.yaml, request.fields
[^r22]: 04_service_definitions/accounts_payable/mat_override.yaml, errors
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 26, mat_run THREE-WAY MATCH RUN
[^r24]: 04_service_definitions/accounts_payable/mat_run.yaml, endpoint
[^r27]: 04_service_definitions/accounts_payable/mat_run.yaml, procedures
[^r26]: 04_service_definitions/accounts_payable/mat_run.yaml, response.envelope
[^r25]: 04_service_definitions/accounts_payable/mat_run.yaml, request.fields
[^r6]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 13, ERR-MAT-0412 NO GRN FOR PO LINE
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 27, mat_search THREE-WAY MATCH LIST
[^r29]: 04_service_definitions/accounts_payable/mat_search.yaml, whole file
[^r30]: 04_service_definitions/accounts_payable/mat_search.yaml, request.fields
[^r31]: 04_service_definitions/accounts_payable/mat_search.yaml, response.envelope
[^r32]: 04_service_definitions/accounts_payable/mat_search.yaml, common_errors
