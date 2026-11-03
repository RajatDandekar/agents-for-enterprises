---
title: "AP pcs services"
type: "service-group"
slug: "services-ap-pcs"
summary: "Ledgerline AP petty cash services (pcs_save, pcs_get, pcs_search, pcs_post) for recording, querying, and posting petty cash vouchers on screen AP-PCS-15."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/accounts_payable/pcs_get.yaml", "04_service_definitions/accounts_payable/pcs_post.yaml", "04_service_definitions/accounts_payable/pcs_save.yaml", "04_service_definitions/accounts_payable/pcs_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | AP (Accounts Payable) |
| Screen | AP-PCS-15 |
| Services | pcs_save, pcs_get, pcs_search, pcs_post |
| Protocol | POST /ll72/svc/* |
| Auth header | X-LL-Session |
| Status | Current |

The AP petty cash service group provides write and read operations for managing petty cash vouchers on [[screen-ap-pcs-15|AP-PCS-15 Petty Cash Entry]][^r5][^r9]. It encompasses `pcs_save` for drafting new vouchers, `pcs_get` and `pcs_search` for voucher queries, and `pcs_post` for final general ledger validation and posting[^r1][^r2][^r3][^r4]. All services authenticate requests using a session token passed in the `X-LL-Session` header and require an authorised user role[^r10][^r15][^r20][^r23].

## Services

### pcs_save

The `pcs_save` service handles the initial entry of petty cash vouchers on [[screen-ap-pcs-15|AP-PCS-15]][^r5][^r19]. Available since version 7.0 at endpoint `POST /ll72/svc/pcs_save`, it checks input formatting, executes database procedure `sp_pcs_save`, generates a serial voucher number into `PCS NO`, and sets `STATUS` to draft[^r1][^r5][^r19][^r27].

* **Required fields:** `ou_cd` (string), `amount` (float), `purpose` (string), `cc_cd` (string)[^r5][^r21].
* **Optional fields:** none[^r21].
* **Errors:** [[err-cc-0009|ERR-CC-0009]] if the cost centre is invalid[^r5][^r27].
* **Source file:** `04_service_definitions/accounts_payable/pcs_save.yaml`[^r19].

### pcs_get

The `pcs_get` service performs a `PETTY CASH GET` read operation to retrieve existing petty cash records on [[screen-ap-pcs-15|AP-PCS-15]][^r2][^r6][^r9]. Introduced in version 7.0 at endpoint `POST /ll72/svc/pcs_get`, it retrieves values for `OU CD`, `AMOUNT`, `PURPOSE`, `CC CD`, `STATUS`, and `COMMENT` for a specified voucher[^r2][^r9]. It returns a standard envelope with fields `rc` (`S | W | E`), `err_cd`, `msg`, and `data`[^r12].

* **Required fields:** `pcs_no` (string, representing `PCS NO`)[^r11].
* **Optional fields:** none[^r11].
* **Errors:** [[err-pcs-0001|ERR-PCS-0001]] (`PETTY CASH NOT FOUND`), along with common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503`[^r13].
* **Source file:** `04_service_definitions/accounts_payable/pcs_get.yaml`[^r9].

### pcs_search

The `pcs_search` service executes the `PETTY CASH LIST` read operation on [[screen-ap-pcs-15|AP-PCS-15]] to query past vouchers filtered by active site selection without using stored procedures[^r3][^r7][^r22]. It was introduced in version 7.0 at endpoint `POST /ll72/svc/pcs_search` and returns an envelope containing `rc` (`S | W | E`), `err_cd`, `msg`, and `data`[^r22][^r25].

* **Required fields:** none[^r24].
* **Optional fields:** `ou_cd` (string, `OU CD`), `amount` (float, `AMOUNT`), `purpose` (string, `PURPOSE`), `status` (string, `STATUS`)[^r7][^r24].
* **Errors:** `ERR-SEC-0001` (`ACCESS DENIED`), `ERR-SYS-0421` (`<FIELD> MANDATORY`), `ERR-SYS-0422` (`UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>`), and `ERR-SYS-0503` (`SERVER BUSY, TRY LATER`)[^r26].
* **Source file:** `04_service_definitions/accounts_payable/pcs_search.yaml`[^r22].

### pcs_post

The `pcs_post` service performs the `PETTY CASH POST` write operation on [[screen-ap-pcs-15|AP-PCS-15]], available since version 7.0 at endpoint `POST /ll72/svc/pcs_post`[^r8][^r14]. It executes final ledger validations via database stored procedure `sp_pcs_post`, updates the general ledger, locks the voucher against subsequent changes, and updates `STATUS` to posted[^r4][^r8][^r17].

* **Required fields:** `pcs_no` (string, `PCS NO`)[^r8][^r16].
* **Optional fields:** `comment` (string, `COMMENT`)[^r16].
* **Errors:** [[err-pcs-0001|ERR-PCS-0001]] (`PETTY CASH NOT FOUND`) and [[err-pcs-0007|ERR-PCS-0007]] (`PETTY CASH NOT IN DRAFT (<status>)`)[^r8][^r18].
* **Source file:** `04_service_definitions/accounts_payable/pcs_post.yaml`[^r14].

## See also

* [[screen-ap-pcs-15|AP-PCS-15 Petty Cash Entry]]
* [[err-cc-0009|ERR-CC-0009]]
* [[err-pcs-0001|ERR-PCS-0001]]
* [[err-pcs-0007|ERR-PCS-0007]]
* [[services-ap-exp|AP exp services]]
* [[services-ap-gl|AP gl services]]

## References

[^r5]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 36, pcs_save PETTY CASH SAVE
[^r9]: 04_service_definitions/accounts_payable/pcs_get.yaml, service: pcs_get
[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 56, Entering a new voucher:
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 56, Retrieving existing records:
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 56, Retrieving existing records:
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 57, Final posting:
[^r10]: 04_service_definitions/accounts_payable/pcs_get.yaml, auth
[^r15]: 04_service_definitions/accounts_payable/pcs_post.yaml, auth
[^r20]: 04_service_definitions/accounts_payable/pcs_save.yaml, auth
[^r23]: 04_service_definitions/accounts_payable/pcs_search.yaml, whole file
[^r19]: 04_service_definitions/accounts_payable/pcs_save.yaml, whole file
[^r27]: 04_service_definitions/accounts_payable/pcs_save.yaml, errors
[^r21]: 04_service_definitions/accounts_payable/pcs_save.yaml, request.fields
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 36, pcs_get PETTY CASH GET
[^r12]: 04_service_definitions/accounts_payable/pcs_get.yaml, response.envelope
[^r11]: 04_service_definitions/accounts_payable/pcs_get.yaml, request.fields
[^r13]: 04_service_definitions/accounts_payable/pcs_get.yaml, errors
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 37, pcs_search PETTY CASH LIST
[^r22]: 04_service_definitions/accounts_payable/pcs_search.yaml, whole file
[^r25]: 04_service_definitions/accounts_payable/pcs_search.yaml, response.envelope
[^r24]: 04_service_definitions/accounts_payable/pcs_search.yaml, request.fields
[^r26]: 04_service_definitions/accounts_payable/pcs_search.yaml, common_errors
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 37, pcs_post PETTY CASH POST
[^r14]: 04_service_definitions/accounts_payable/pcs_post.yaml, whole file
[^r17]: 04_service_definitions/accounts_payable/pcs_post.yaml, procedures
[^r16]: 04_service_definitions/accounts_payable/pcs_post.yaml, request.fields
[^r18]: 04_service_definitions/accounts_payable/pcs_post.yaml, errors
