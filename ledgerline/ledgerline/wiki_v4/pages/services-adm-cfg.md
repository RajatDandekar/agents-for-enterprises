---
title: "ADM cfg services"
type: "service-group"
slug: "services-adm-cfg"
summary: "Ledgerline ADM services for reading and saving menu configuration records on screen SYS-CFG-16."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/admin/cfg_get.yaml", "04_service_definitions/admin/cfg_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| service_group | services-adm-cfg |
| module | ADM |
| object | cfg |
| version_introduced | 7.0 |
| associated_screen | SYS-CFG-16 |
| services | cfg_get, cfg_save |

The ADM cfg service group manages menu configuration read and write operations in Ledgerline [^r4][^r10]. Introduced in version 7.0, these services operate on screen [[screen-sys-cfg-16|SYS-CFG-16]] to retrieve and assign menu definitions by role [^r2][^r3][^r4][^r10]. Both endpoints authenticate calls via a session token in header `X-LL-Session` and verify role-based execution permissions [^r5][^r11].

## Services

### cfg_get

The `cfg_get` service ('MENU CONFIG GET') is a read service in module ADM associated with screen [[screen-sys-cfg-16|SYS-CFG-16]] and introduced in Ledgerline 7.0 [^r2][^r4]. It is bound to key F3 Get on screen SYS-DLG-03 and is hosted at endpoint `POST /ll72/svc/cfg_get` [^r1][^r5]. The endpoint requires an authentication session token in header `X-LL-Session` and permission from the user's role [^r5]. The response envelope returns return code `rc` ('S | W | E'), error code `err_cd`, message `msg` in capitals, and the `data` result [^r7].

* Required fields: string field `menu_cd` (MENU CD) [^r2][^r6].
* Optional fields: none [^r6].
* Errors: specific error `ERR-CFG-0001` ('MENU CONFIG NOT FOUND') when a configuration is missing, and common errors `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r1][^r2][^r8][^r9].
* Source file: `04_service_definitions/admin/cfg_get.yaml` [^r4].

### cfg_save

The `cfg_save` service ('MENU CONFIG SAVE') is a write service in module ADM introduced in Ledgerline 7.0, hosted at endpoint `POST /ll72/svc/cfg_save` [^r10]. It is bound to key F8 Save on screen SYS-DLG-03 and writes menu configuration for screen [[screen-sys-cfg-16|SYS-CFG-16]] by running stored procedure `sp_cfg_save` [^r1][^r3][^r13]. The service requires authentication using a session token in header `X-LL-Session` under an authorised role [^r11]. Its response envelope provides `rc` ('S | W | E'), `err_cd`, `msg`, and `data` [^r13].

* Required fields: string fields `role_cd` (ROLE) and `menu_cd` (MENU) [^r3][^r12].
* Optional fields: none [^r12].
* Errors: common errors `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r14].
* Source file: `04_service_definitions/admin/cfg_save.yaml` [^r10].

## See also

* [[screen-sys-cfg-16|SYS-CFG-16 Menu Config]]
* [[services-adm-dlg|ADM dlg services]]
* [[services-adm-imp|ADM imp services]]
* [[services-adm-par|ADM par services]]

## References

[^r4]: 04_service_definitions/admin/cfg_get.yaml, service
[^r10]: 04_service_definitions/admin/cfg_save.yaml, whole file
[^r2]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 74, cfg_get MENU CONFIG GET
[^r3]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 74, cfg_save MENU CONFIG SAVE
[^r5]: 04_service_definitions/admin/cfg_get.yaml, endpoint
[^r11]: 04_service_definitions/admin/cfg_save.yaml, auth
[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 41, SYS-DLG-03 APPROVAL DELEGATION ENTRY
[^r7]: 04_service_definitions/admin/cfg_get.yaml, response.envelope
[^r6]: 04_service_definitions/admin/cfg_get.yaml, request.fields
[^r8]: 04_service_definitions/admin/cfg_get.yaml, errors
[^r9]: 04_service_definitions/admin/cfg_get.yaml, common_errors
[^r13]: 04_service_definitions/admin/cfg_save.yaml, response
[^r12]: 04_service_definitions/admin/cfg_save.yaml, request.fields
[^r14]: 04_service_definitions/admin/cfg_save.yaml, common_errors
