---
title: "AP cur services"
type: "service-group"
slug: "services-ap-cur"
summary: "Ledgerline AP currency rate services cur_get, cur_save, and cur_list managing exchange rates to GBP on screen AP-CUR-13."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/accounts_payable/cur_get.yaml", "04_service_definitions/accounts_payable/cur_list.yaml", "04_service_definitions/accounts_payable/cur_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | Accounts Payable (AP) |
| Object | Currency Rate (cur) |
| Services | cur_get, cur_save, cur_list |
| Screen | AP-CUR-13 |
| Introduced | Ledgerline 7.0 |
| Status | Current |

The `cur` service group provides Ledgerline Accounts Payable services for managing currency exchange rates against GBP on screen [[screen-ap-cur-13|AP-CUR-13]][^r6]. It includes read and write services to retrieve existing rates, store validated conversion factors in the ledger database, and review historical rate entries[^r1][^r2][^r4][^r6]. All services in this group operate under module AP and require role authorisation alongside a valid session token[^r10][^r11][^r15][^r16][^r20][^r21].

## Services

### cur_get

Service `cur_get` (CURRENCY RATE GET) is an Accounts Payable read service introduced in Ledgerline 7.0 that queries the central rate table by currency code and rate date to populate RATE TO GBP on screen [[screen-ap-cur-13|AP-CUR-13]][^r1][^r3][^r7][^r10]. It is exposed at endpoint `POST /ll72/svc/cur_get` and requires a session token in header `X-LL-Session` with a permitted user role[^r10][^r11].

* **Required fields:** `cur_cd` (string, CUR CD)[^r7][^r12].
* **Optional fields:** none[^r12].
* **Errors:** [[err-cur-0001|ERR-CUR-0001]] (CURRENCY RATE NOT FOUND), ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503[^r7][^r14].
* **Response envelope:** `rc` (S | W | E), `err_cd`, `msg`, `data`[^r13].
* **Source file:** `04_service_definitions/accounts_payable/cur_get.yaml`[^r10].

### cur_save

Service `cur_save` (CURRENCY RATE SAVE) is an Accounts Payable write service introduced in Ledgerline 7.0 that validates entries against master control tables and stores conversion factors into the ledger database on screen [[screen-ap-cur-13|AP-CUR-13]][^r4][^r8][^r20]. It is exposed at endpoint `POST /ll72/svc/cur_save`, requires a session token in header `X-LL-Session` with an authorised user role, and executes stored procedure `sp_cur_save`[^r8][^r21][^r24].

* **Required fields:** `cur_cd` (string, CURRENCY), `rate_dt` (date, RATE DT), and `rate` (float, RATE TO GBP)[^r8][^r22].
* **Optional fields:** none[^r22].
* **Errors:** ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), ERR-SYS-0503 (SERVER BUSY, TRY LATER)[^r25].
* **Response envelope:** `rc` (S | W | E), `err_cd`, `msg`, `data`[^r23].
* **Source file:** `04_service_definitions/accounts_payable/cur_save.yaml`[^r20].

### cur_list

Service `cur_list` (CURRENCY RATE LIST) is an Accounts Payable read service available since Ledgerline 7.0 that provides a reverse-chronological list of past exchange entries across time on screen [[screen-ap-cur-13|AP-CUR-13]][^r2][^r5][^r9][^r15]. It is exposed at endpoint `POST /ll72/svc/cur_list` and requires a session token in header `X-LL-Session` with role permission[^r16].

* **Required fields:** none[^r17].
* **Optional fields:** `cur_cd` (string, CURRENCY)[^r9][^r17].
* **Errors:** ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), ERR-SYS-0503 (SERVER BUSY, TRY LATER)[^r19].
* **Response envelope:** `rc` (S | W | E), `err_cd`, `msg`, `data`[^r18].
* **Source file:** `04_service_definitions/accounts_payable/cur_list.yaml`[^r15].

## See also

* [[screen-ap-cur-13|AP-CUR-13 Currency Rate]]
* [[err-cur-0001|ERR-CUR-0001 Currency Rate Action Failed]]
* [[services-ap-inv|AP inv services]]
* [[services-ap-pay|AP pay services]]

## References

[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 5, AP-CUR-13 CURRENCY RATE
[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 48, Step by step
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 48, Step by step
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 49, Messages
[^r10]: 04_service_definitions/accounts_payable/cur_get.yaml, service: cur_get
[^r11]: 04_service_definitions/accounts_payable/cur_get.yaml, auth
[^r15]: 04_service_definitions/accounts_payable/cur_list.yaml, service: cur_list
[^r16]: 04_service_definitions/accounts_payable/cur_list.yaml, service: cur_list
[^r20]: 04_service_definitions/accounts_payable/cur_save.yaml, service: cur_save
[^r21]: 04_service_definitions/accounts_payable/cur_save.yaml, endpoint
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 49, Messages
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 35, cur_get CURRENCY RATE GET
[^r12]: 04_service_definitions/accounts_payable/cur_get.yaml, request.fields
[^r14]: 04_service_definitions/accounts_payable/cur_get.yaml, errors
[^r13]: 04_service_definitions/accounts_payable/cur_get.yaml, response.envelope
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 35, cur_save CURRENCY RATE SAVE
[^r24]: 04_service_definitions/accounts_payable/cur_save.yaml, procedures
[^r22]: 04_service_definitions/accounts_payable/cur_save.yaml, request.fields
[^r25]: 04_service_definitions/accounts_payable/cur_save.yaml, common_errors
[^r23]: 04_service_definitions/accounts_payable/cur_save.yaml, response.envelope
[^r5]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 50, Worked example
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 36, cur_list CURRENCY RATE LIST
[^r17]: 04_service_definitions/accounts_payable/cur_list.yaml, request
[^r19]: 04_service_definitions/accounts_payable/cur_list.yaml, common_errors
[^r18]: 04_service_definitions/accounts_payable/cur_list.yaml, response
