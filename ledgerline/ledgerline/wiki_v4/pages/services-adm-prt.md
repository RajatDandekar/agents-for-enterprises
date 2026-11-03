---
title: "ADM prt services"
type: "service-group"
slug: "services-adm-prt"
summary: "Administration printing services prt_form_get and prt_list handling print form definitions on screen SYS-PRT-12."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/admin/prt_form_get.yaml", "04_service_definitions/admin/prt_list.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | ADM |
| Object | prt |
| Screen | SYS-PRT-12 |
| Services | prt_form_get, prt_list |
| Status | current |

The ADM `prt` service group comprises the Ledgerline administration services that manage print form definitions.[^r1] These services support screen [[screen-sys-prt-12|SYS-PRT-12]] (PRINT FORMS) and handle querying form metadata as well as retrieving specific form definitions.[^r1][^r4][^r9] Both services execute as read operations over HTTP POST endpoints requiring session token authentication and role authorisation.[^r5][^r10]

## Services

### prt_form_get

The `prt_form_get` service (PRINT FORMS FORM GET) is a read operation in module ADM associated with screen [[screen-sys-prt-12|SYS-PRT-12]], available since version 7.0.[^r3][^r4] It is accessed at endpoint `POST /ll72/svc/prt_form_get` using a session token in header `X-LL-Session`, and requires the user's role to permit the service.[^r5]

* **Required fields:** `form_cd` (string, FORM CD).[^r3][^r6]
* **Optional fields:** None.[^r6]
* **Response:** Envelope containing `rc` (`S | W | E`), `err_cd` (error code when `rc` is `E`), `msg` (short message in capitals), and `data` (result).[^r7]
* **Errors:** Specific error `ERR-PRT-0001` (PRINT FORMS NOT FOUND), and common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503`.[^r1][^r3][^r8]
* **Source file:** `04_service_definitions/admin/prt_form_get.yaml`.[^r4]

### prt_list

The `prt_list` service (PRINT FORMS LIST) is a read operation in module ADM supporting screen [[screen-sys-prt-12|SYS-PRT-12]], available since Ledgerline version 7.0 at endpoint `POST /ll72/svc/prt_list`.[^r9] Authentication requires a session token in header `X-LL-Session` and a role authorised for the service.[^r10]

* **Required fields:** None.[^r11]
* **Optional fields:** `form_cd` (string, for filtering by form).[^r11]
* **Errors:** Raises `ERR-PRT-0001` if form definitions are not found, alongside common errors `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (`<FIELD> MANDATORY`), `ERR-SYS-0422` (`UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>`), and `ERR-SYS-0503` (`SERVER BUSY, TRY LATER`).[^r1][^r12]
* **Source file:** `04_service_definitions/admin/prt_list.yaml`.[^r9]

## Versions and conflicts

* **Version introduction for `prt_list`:** The service definition file records `prt_list` as available since Ledgerline version 7.0.[^r9] However, vendor manual MAN-SVC-72 (v7.2.3, 2025-01-15) states that `prt_list` was introduced in Ledgerline 7.2.[^r2] (kind: `contradiction`).

## See also

* [[screen-sys-prt-12|SYS-PRT-12 Print Forms]]
* [[services-adm-dlg|ADM dlg services]]
* [[services-adm-imp|ADM imp services]]
* [[services-adm-par|ADM par services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 44, SYS-PRT-12 PRINT FORMS
[^r4]: 04_service_definitions/admin/prt_form_get.yaml, service: prt_form_get
[^r9]: 04_service_definitions/admin/prt_list.yaml, whole file
[^r5]: 04_service_definitions/admin/prt_form_get.yaml, auth
[^r10]: 04_service_definitions/admin/prt_list.yaml, whole file
[^r3]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 73, prt_form_get PRINT FORMS FORM GET
[^r6]: 04_service_definitions/admin/prt_form_get.yaml, request
[^r7]: 04_service_definitions/admin/prt_form_get.yaml, response
[^r8]: 04_service_definitions/admin/prt_form_get.yaml, errors
[^r11]: 04_service_definitions/admin/prt_list.yaml, request.fields
[^r12]: 04_service_definitions/admin/prt_list.yaml, common_errors
[^r2]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 72, prt_list PRINT FORMS LIST
