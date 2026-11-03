---
title: "AP crn services"
type: "service-group"
slug: "services-ap-crn"
summary: "Accounts Payable service group for entering, retrieving, searching, and posting supplier credit notes on screen AP-CRN-05."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/accounts_payable/crn_get.yaml", "04_service_definitions/accounts_payable/crn_post.yaml", "04_service_definitions/accounts_payable/crn_save.yaml", "04_service_definitions/accounts_payable/crn_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | services-ap-crn |
| module | Accounts Payable (AP) |
| screen | [[screen-ap-crn-05|AP-CRN-05]] |
| services | crn_save, crn_get, crn_search, crn_post |
| version_introduced | 7.0 |
| status | current |

The `services-ap-crn` service group provides read and write operations for managing supplier credit notes within Ledgerline's Accounts Payable module [^r5][^r10]. Bound to screen [[screen-ap-crn-05|AP-CRN-05 Supplier Credit Note Entry]], it comprises `crn_save`, `crn_get`, `crn_search`, and `crn_post` [^r5]. All endpoints require HTTP POST requests with a valid session token supplied in the `X-LL-Session` header and appropriate role authorisation [^r11][^r16][^r21][^r26]. Each service returns a standard response envelope containing return code `rc` (`S`, `W`, or `E`), `err_cd`, short uppercase message `msg`, and `data` [^r13][^r18][^r23][^r28].

## Services

### crn_save

Write service titled SUPPLIER CREDIT NOTE SAVE used on screen [[screen-ap-crn-05|AP-CRN-05]] to generate a system reference, assign `CRN NO`, and store an unposted draft credit note [^r1][^r6][^r20]. Available since Ledgerline 7.0, it is accessed at endpoint `POST /ll72/svc/crn_save` and executes stored procedure `sp_crn_save` [^r6][^r20][^r21][^r24]. Authentication requires a session token in the `X-LL-Session` header and an authorised role [^r21].

* **Required fields**: `sup_cd` (str), `sup_crn_no` (str), `amount` (float) [^r6][^r22].
* **Optional fields**: `ap_doc` (str) [^r6][^r22].
* **Errors**: [[err-sup-0030|ERR-SUP-0030]] (SUPPLIER NOT FOUND) if the supplier code does not exist [^r6][^r24]. Common errors include `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503`.
* **Source file**: `04_service_definitions/accounts_payable/crn_save.yaml` [^r20].

### crn_get

Read service titled SUPPLIER CREDIT NOTE GET used to retrieve draft or posted supplier credit note details on screen [[screen-ap-crn-05|AP-CRN-05]] [^r3][^r7][^r10]. Available since version 7.0, it operates at endpoint `POST /ll72/svc/crn_get` using session header `X-LL-Session` with role validation [^r10][^r11].

* **Required fields**: `crn_no` (str) [^r7][^r12].
* **Optional fields**: none [^r12].
* **Errors**: `ERR-CRN-0001` (SUPPLIER CREDIT NOTE NOT FOUND), alongside common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r5][^r7][^r14].
* **Source file**: `04_service_definitions/accounts_payable/crn_get.yaml` [^r10].

### crn_search

Read service titled SUPPLIER CREDIT NOTE LIST used on screen [[screen-ap-crn-05|AP-CRN-05]] to query matching credit note records [^r4][^r8][^r25]. Introduced in version 7.0, it is exposed at endpoint `POST /ll72/svc/crn_search` and requires session authentication via `X-LL-Session` [^r25][^r26].

* **Required fields**: none [^r27].
* **Optional fields**: `sup_cd` (str), `sup_crn_no` (str), `amount` (float), `status` (str) [^r8][^r27].
* **Errors**: common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r29].
* **Source file**: `04_service_definitions/accounts_payable/crn_search.yaml` [^r25].

### crn_post

Write service titled SUPPLIER CREDIT NOTE POST used on screen [[screen-ap-crn-05|AP-CRN-05]] to validate ledger balances, post amounts to the supplier ledger account, set credit note status to posted, and lock the document from further edits [^r2][^r9][^r15]. Available since version 7.0, it connects to endpoint `POST /ll72/svc/crn_post` and runs database stored procedure `sp_crn_post` under session authentication in `X-LL-Session` [^r9][^r15][^r16].

* **Required fields**: `crn_no` (str) [^r9][^r17].
* **Optional fields**: `comment` (str) [^r9][^r17].
* **Errors**: `ERR-CRN-0001`, `ERR-CRN-0007` (raised if the credit note is not in draft status), and common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r5][^r9][^r18][^r19].
* **Source file**: `04_service_definitions/accounts_payable/crn_post.yaml` [^r15].

## See also

* [[screen-ap-crn-05|AP-CRN-05 Supplier Credit Note Entry]]
* [[services-ap-inv|AP inv services]]
* [[services-ap-dbn|AP dbn services]]
* [[err-sup-0030|ERR-SUP-0030]]

## References

[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 5, AP-CRN-05 SUPPLIER CREDIT NOTE ENTRY
[^r10]: 04_service_definitions/accounts_payable/crn_get.yaml, service: crn_get
[^r11]: 04_service_definitions/accounts_payable/crn_get.yaml, service: crn_get
[^r16]: 04_service_definitions/accounts_payable/crn_post.yaml, auth
[^r21]: 04_service_definitions/accounts_payable/crn_save.yaml, endpoint
[^r26]: 04_service_definitions/accounts_payable/crn_search.yaml, service: crn_search
[^r13]: 04_service_definitions/accounts_payable/crn_get.yaml, response.envelope
[^r18]: 04_service_definitions/accounts_payable/crn_post.yaml, errors
[^r23]: 04_service_definitions/accounts_payable/crn_save.yaml, response.envelope
[^r28]: 04_service_definitions/accounts_payable/crn_search.yaml, response.envelope
[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 16, Entering a new credit note:
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 28, crn_save SUPPLIER CREDIT NOTE SAVE
[^r20]: 04_service_definitions/accounts_payable/crn_save.yaml, service: crn_save
[^r24]: 04_service_definitions/accounts_payable/crn_save.yaml, errors
[^r22]: 04_service_definitions/accounts_payable/crn_save.yaml, request.fields
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 16, Retrieving an existing credit note:
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 28, crn_get SUPPLIER CREDIT NOTE GET
[^r12]: 04_service_definitions/accounts_payable/crn_get.yaml, request.fields
[^r14]: 04_service_definitions/accounts_payable/crn_get.yaml, errors
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 16, Searching for credit notes:
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 28, crn_search SUPPLIER CREDIT NOTE LIST
[^r25]: 04_service_definitions/accounts_payable/crn_search.yaml, service: crn_search
[^r27]: 04_service_definitions/accounts_payable/crn_search.yaml, request.fields
[^r29]: 04_service_definitions/accounts_payable/crn_search.yaml, common_errors
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 16, Entering a new credit note:
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 29, crn_post SUPPLIER CREDIT NOTE POST
[^r15]: 04_service_definitions/accounts_payable/crn_post.yaml, service: crn_post
[^r17]: 04_service_definitions/accounts_payable/crn_post.yaml, request.fields
[^r19]: 04_service_definitions/accounts_payable/crn_post.yaml, common_errors
