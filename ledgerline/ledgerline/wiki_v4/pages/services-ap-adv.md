---
title: "AP adv services"
type: "service-group"
slug: "services-ap-adv"
summary: "Accounts Payable advance payment services handling creation, enquiry, retrieval, amendment, and approval on screen AP-ADV-07."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/accounts_payable/adv_adjust.yaml", "04_service_definitions/accounts_payable/adv_approve.yaml", "04_service_definitions/accounts_payable/adv_get.yaml", "04_service_definitions/accounts_payable/adv_save.yaml", "04_service_definitions/accounts_payable/adv_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Group | services-ap-adv |
| Module | Accounts Payable (AP) |
| Primary Screen | AP-ADV-07 |
| Services | adv_save, adv_get, adv_search, adv_approve, adv_adjust |
| Version Introduced | Ledgerline 7.0 |
| Status | Current |

The `services-ap-adv` service group provides backend processing for advance payments to suppliers within the Accounts Payable module [^r18][^r34]. Linked directly to screen [[screen-ap-adv-07|AP-ADV-07 Advance Payment Entry]], these services manage the creation, retrieval, listing, adjustment, and authorisation of advance payment records [^r11][^r18]. As of 26 October 2026, all five services run against Ledgerline ERP 7.2 using stored procedures to enforce PO commitment validation and approval authority rules [^r1][^r2][^r18][^r23].

## Services

### adv_save
* **Title / Description:** ADVANCE PAYMENT SAVE validates supplier and purchase order existence, verifies that the advance value does not exceed the authorised threshold or purchase order balance, creates an advance payment record with status pending, and assigns an advance reference number [^r1][^r6][^r12].
* **Screen:** [[screen-ap-adv-07|AP-ADV-07]] [^r12]
* **Endpoint:** `POST /ll72/svc/adv_save` [^r35]
* **Stored Procedure:** `sp_adv_save` [^r12][^r37]
* **Authentication:** Requires session token in header `X-LL-Session` and role permissions authorizing execution [^r35].
* **Required fields:** `sup_cd` (string), `po_no` (string), `amount` (float) [^r12][^r36].
* **Optional fields:** None [^r36].
* **Errors:** [[err-sup-0030|ERR-SUP-0030]] (SUPPLIER NOT FOUND) [^r12][^r37].
* **Source file:** `04_service_definitions/accounts_payable/adv_save.yaml` [^r34].

### adv_get
* **Title / Description:** ADVANCE PAYMENT GET retrieves an existing advance payment record by advance number to populate supplier, PO, amount, status, and comments [^r4][^r7][^r13][^r29].
* **Screen:** [[screen-ap-adv-07|AP-ADV-07]] [^r13][^r29]
* **Endpoint:** `POST /ll72/svc/adv_get` [^r30]
* **Stored Procedure:** None specified; read service [^r13][^r29].
* **Authentication:** Requires session token in header `X-LL-Session` and authorized user role [^r30].
* **Required fields:** `adv_no` (string, ADV NO) [^r13][^r31].
* **Optional fields:** None [^r31].
* **Errors:** [[err-adv-0001|ERR-ADV-0001]] (ADVANCE PAYMENT NOT FOUND), ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r13][^r33].
* **Response envelope:** `rc` ('S | W | E'), `err_cd`, `msg` (short message in capitals), `data` ('result') [^r32].
* **Source file:** `04_service_definitions/accounts_payable/adv_get.yaml` [^r29].

### adv_search
* **Title / Description:** ADVANCE PAYMENT LIST queries and lists advance payment records matching search criteria prior to authorisation [^r5][^r8][^r14][^r38].
* **Screen:** [[screen-ap-adv-07|AP-ADV-07]] [^r14][^r38]
* **Endpoint:** `POST /ll72/svc/adv_search` [^r38]
* **Stored Procedure:** None specified; read service [^r14][^r38].
* **Authentication:** Requires session token in header `X-LL-Session` and authorized caller role [^r39].
* **Required fields:** None [^r40].
* **Optional fields:** `sup_cd` (string, SUP CD), `po_no` (string, PO NO), `amount` (float, AMOUNT), `status` (string, STATUS) [^r14][^r40].
* **Errors:** ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r42].
* **Response envelope:** `rc` ('S | W | E'), `err_cd`, `msg` (short message in capitals), `data` ('result') [^r41].
* **Source file:** `04_service_definitions/accounts_payable/adv_search.yaml` [^r38].

### adv_approve
* **Title / Description:** ADVANCE PAYMENT APPROVE authorises an advance payment by validating individual user approval limits against AMOUNT and checking unbilled PO commitment before setting status to approved [^r2][^r9][^r23].
* **Screen:** [[screen-ap-adv-07|AP-ADV-07]] [^r15]
* **Endpoint:** `POST /ll72/svc/adv_approve` [^r23]
* **Stored Procedure:** `sp_adv_approve` [^r15][^r23]
* **Authentication:** Requires session token in header `X-LL-Session` and authorized role permissions [^r24].
* **Required fields:** `adv_no` (string) [^r25].
* **Optional fields:** `comment` (string) [^r25].
* **Errors:** [[err-adv-0001|ERR-ADV-0001]] (ADVANCE PAYMENT NOT FOUND), [[err-adv-0007|ERR-ADV-0007]] (ADVANCE PAYMENT NOT IN DRAFT (<status>)), [[err-apr-0003|ERR-APR-0003]] (SELF APPROVAL NOT ALLOWED), [[err-apr-0004|ERR-APR-0004]] (VALUE ABOVE YOUR LIMIT), ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r9][^r11][^r27][^r28].
* **Response envelope:** `rc` ('S | W | E'), `err_cd`, `msg` (capitalised string), `data` [^r26].
* **Source file:** `04_service_definitions/accounts_payable/adv_approve.yaml` [^r23].

### adv_adjust
* **Title / Description:** ADVANCE PAYMENT ADJUST updates an advance payment amount, comment, or associated fields against remaining PO commitments and supplier status before approval [^r3][^r10][^r16][^r18].
* **Screen:** [[screen-ap-adv-07|AP-ADV-07]] [^r16][^r18]
* **Endpoint:** `POST /ll72/svc/adv_adjust` [^r18]
* **Stored Procedure:** `sp_adv_adjust` [^r16][^r22]
* **Authentication:** Requires session token in header `X-LL-Session` and user role execution permissions [^r19].
* **Required fields:** `adv_no` (string, ADV NO) [^r17][^r20].
* **Optional fields:** `sup_cd` (string, SUP CD), `po_no` (string, PO NO), `amount` (float, AMOUNT) [^r17][^r20].
* **Errors:** [[err-adv-0001|ERR-ADV-0001]], [[err-sup-0030|ERR-SUP-0030]] [^r17][^r22].
* **Response envelope:** `rc` ('S | W | E'), `err_cd`, `msg` (short message in capitals), `data` ('result') [^r21].
* **Source file:** `04_service_definitions/accounts_payable/adv_adjust.yaml` [^r18].

## See also
* [[screen-ap-adv-07|AP-ADV-07 Advance Payment Entry]]
* [[services-ap-inv|AP inv services]]
* [[services-ap-pay|AP pay services]]
* [[services-pur-po|PUR po services]]
* [[err-adv-0001|ERR-ADV-0001 Missing or invalid advance payment fields]]
* [[err-adv-0007|ERR-ADV-0007 Purchase order supplier mismatch or closed]]
* [[err-apr-0003|ERR-APR-0003 Self-approval not permitted]]
* [[err-apr-0004|ERR-APR-0004 Advance amount exceeds PO unbilled commitment]]
* [[err-sup-0030|ERR-SUP-0030]]

## References

[^r18]: 04_service_definitions/accounts_payable/adv_adjust.yaml, service: adv_adjust
[^r34]: 04_service_definitions/accounts_payable/adv_save.yaml, service
[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 4, AP-ADV-07 ADVANCE PAYMENT ENTRY
[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 27, Screen layout
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 27, Screen layout
[^r23]: 04_service_definitions/accounts_payable/adv_approve.yaml, service: adv_approve
[^r6]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 29, Advance Payment (AP-ADV-07)
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 31, adv_save ADVANCE PAYMENT SAVE
[^r35]: 04_service_definitions/accounts_payable/adv_save.yaml, endpoint
[^r37]: 04_service_definitions/accounts_payable/adv_save.yaml, errors
[^r36]: 04_service_definitions/accounts_payable/adv_save.yaml, request.fields
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 27, Screen layout
[^r7]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 29, Advance Payment (AP-ADV-07)
[^r13]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 31, adv_get ADVANCE PAYMENT GET
[^r29]: 04_service_definitions/accounts_payable/adv_get.yaml, whole file
[^r30]: 04_service_definitions/accounts_payable/adv_get.yaml, whole file
[^r31]: 04_service_definitions/accounts_payable/adv_get.yaml, request.fields
[^r33]: 04_service_definitions/accounts_payable/adv_get.yaml, errors
[^r32]: 04_service_definitions/accounts_payable/adv_get.yaml, response.envelope
[^r5]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 27, Screen layout
[^r8]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 29, Advance Payment (AP-ADV-07)
[^r14]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 31, adv_search ADVANCE PAYMENT LIST
[^r38]: 04_service_definitions/accounts_payable/adv_search.yaml, service: adv_search
[^r39]: 04_service_definitions/accounts_payable/adv_search.yaml, auth
[^r40]: 04_service_definitions/accounts_payable/adv_search.yaml, request.fields
[^r42]: 04_service_definitions/accounts_payable/adv_search.yaml, common_errors
[^r41]: 04_service_definitions/accounts_payable/adv_search.yaml, response.envelope
[^r9]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 29, Advance Payment (AP-ADV-07)
[^r15]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 31, adv_approve ADVANCE PAYMENT APPROVE
[^r24]: 04_service_definitions/accounts_payable/adv_approve.yaml, auth
[^r25]: 04_service_definitions/accounts_payable/adv_approve.yaml, request.fields
[^r27]: 04_service_definitions/accounts_payable/adv_approve.yaml, errors
[^r28]: 04_service_definitions/accounts_payable/adv_approve.yaml, common_errors
[^r26]: 04_service_definitions/accounts_payable/adv_approve.yaml, response.envelope
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 27, Screen layout
[^r10]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 29, Advance Payment (AP-ADV-07)
[^r16]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 32, adv_adjust ADVANCE PAYMENT ADJUST
[^r22]: 04_service_definitions/accounts_payable/adv_adjust.yaml, errors
[^r19]: 04_service_definitions/accounts_payable/adv_adjust.yaml, auth
[^r17]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 32, adv_adjust ADVANCE PAYMENT ADJUST
[^r20]: 04_service_definitions/accounts_payable/adv_adjust.yaml, request.fields
[^r21]: 04_service_definitions/accounts_payable/adv_adjust.yaml, response.envelope
