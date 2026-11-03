---
title: "ADM role services"
type: "service-group"
slug: "services-adm-role"
summary: "Ledgerline ADM role services role_get, role_list, role_save, role_svc_add, and role_svc_remove managing user roles and service access on screen SYS-ROL-02."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/admin/role_get.yaml", "04_service_definitions/admin/role_list.yaml", "04_service_definitions/admin/role_save.yaml", "04_service_definitions/admin/role_svc_add.yaml", "04_service_definitions/admin/role_svc_remove.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | ADM |
| Object | role |
| Screen | SYS-ROL-02 |
| Available since | Ledgerline 7.0 |
| Endpoints | /ll72/svc/role_* |
| Auth header | X-LL-Session |
| Stored procedures | sp_role_save, sp_role_svc_add, sp_role_svc_remove |

The ADM role service group provides read and write operations to manage system roles and their assigned service permissions in Ledgerline ERP [^r1]. These services power screen [[screen-sys-rol-02|SYS-ROL-02]] and execute against the underlying stored procedures `sp_role_save`, `sp_role_svc_add`, and `sp_role_svc_remove` [^r1][^r3][^r4][^r20][^r25][^r30]. All services require an authenticated session token in the `X-LL-Session` header and appropriate role authorisation [^r6][^r11][^r16][^r22][^r28].

## Services

### role_get

The `role_get` service is a read service introduced in Ledgerline 7.0 that fetches role records by role code for screen [[screen-sys-rol-02|SYS-ROL-02]] via endpoint `POST /ll72/svc/role_get` [^r2][^r5]. On the screen interface, it is invoked via F3 [^r1].

* **Required fields**: `role_cd` (string) [^r7].
* **Optional fields**: None [^r7].
* **Response**: Envelope containing `rc` (`S | W | E`), `err_cd`, uppercase `msg`, and `data` [^r8].
* **Errors**: Domain error `ERR-ROL-0001` (ROLE NOT FOUND) if unrecognised, alongside common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r1][^r2][^r9].
* **Source file**: `04_service_definitions/admin/role_get.yaml` [^r5].

### role_list

The `role_list` service is a read service introduced in Ledgerline 7.0 that lists defined roles for screen [[screen-sys-rol-02|SYS-ROL-02]] via endpoint `POST /ll72/svc/role_list` [^r1][^r10].

* **Required fields**: None [^r12].
* **Optional fields**: `role_cd` (string) [^r12].
* **Response**: Envelope returning return code `rc` (`S | W | E`), `err_cd`, `msg`, and result `data` [^r13].
* **Errors**: Common errors `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (`<FIELD>` MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD `<FIELD>` / BAD VALUE FOR `<FIELD>`), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r14].
* **Source file**: `04_service_definitions/admin/role_list.yaml` [^r10].

### role_save

The `role_save` service is a write service introduced in Ledgerline 7.0 that writes role definitions on screen [[screen-sys-rol-02|SYS-ROL-02]] via endpoint `POST /ll72/svc/role_save`, invoking stored procedure `sp_role_save` [^r3][^r15][^r20]. It maps to function key F8 on the screen [^r1].

* **Required fields**: `role_cd` (string) [^r3][^r17].
* **Optional fields**: `descr` (string) and `svc` (string) [^r3][^r17].
* **Response**: Envelope returning `rc` (`S | W | E`), `err_cd`, uppercase `msg`, and `data` [^r18].
* **Errors**: Common errors `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (`<FIELD>` MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD `<FIELD>` / BAD VALUE FOR `<FIELD>`), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r19].
* **Source file**: `04_service_definitions/admin/role_save.yaml` [^r15].

### role_svc_add

The `role_svc_add` service is a write service available since Ledgerline 7.0 that adds service access permissions to a role via endpoint `POST /ll72/svc/role_svc_add` and stored procedure `sp_role_svc_add` on screen [[screen-sys-rol-02|SYS-ROL-02]] [^r4][^r21][^r22][^r25].

* **Required fields**: `role_cd` (string) [^r23].
* **Optional fields**: `comment` (string) [^r23].
* **Response**: Envelope containing `rc` (`S | W | E`), `err_cd`, uppercase `msg`, and `data` [^r24].
* **Errors**: Domain error `ERR-ROL-0001` (ROLE NOT FOUND) if the role does not exist, plus common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r1][^r4][^r26].
* **Source file**: `04_service_definitions/admin/role_svc_add.yaml` [^r21].

### role_svc_remove

The `role_svc_remove` service is a write service available since Ledgerline 7.0 that removes service access permissions from a role on screen [[screen-sys-rol-02|SYS-ROL-02]] using endpoint `POST /ll72/svc/role_svc_remove` and stored procedure `sp_role_svc_remove` [^r4][^r27][^r28][^r30].

* **Required fields**: `role_cd` (string) [^r29].
* **Optional fields**: `comment` (string) [^r29].
* **Response**: Standard response envelope containing `rc`, `err_cd`, `msg`, and `data` [^r8][^r18][^r24].
* **Errors**: Domain error `ERR-ROL-0001` (ROLE NOT FOUND) if the role does not exist, alongside common system errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r1][^r4][^r30].
* **Source file**: `04_service_definitions/admin/role_svc_remove.yaml` [^r27].

## See also

* [[screen-sys-rol-02|SYS-ROL-02 Role]]
* [[services-adm-par|ADM par services]]
* [[services-adm-dlg|ADM dlg services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 44, SYS-ROL-02 ROLE
[^r3]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 66, role_save ROLE SAVE
[^r4]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 66, role_svc_add ROLE SVC ADD
[^r20]: 04_service_definitions/admin/role_save.yaml, procedures
[^r25]: 04_service_definitions/admin/role_svc_add.yaml, procedures
[^r30]: 04_service_definitions/admin/role_svc_remove.yaml, errors
[^r6]: 04_service_definitions/admin/role_get.yaml, auth
[^r11]: 04_service_definitions/admin/role_list.yaml, auth
[^r16]: 04_service_definitions/admin/role_save.yaml, auth
[^r22]: 04_service_definitions/admin/role_svc_add.yaml, service: role_svc_add
[^r28]: 04_service_definitions/admin/role_svc_remove.yaml, auth
[^r2]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 66, role_get ROLE GET
[^r5]: 04_service_definitions/admin/role_get.yaml, service: role_get
[^r7]: 04_service_definitions/admin/role_get.yaml, request
[^r8]: 04_service_definitions/admin/role_get.yaml, response
[^r9]: 04_service_definitions/admin/role_get.yaml, errors
[^r10]: 04_service_definitions/admin/role_list.yaml, service: role_list
[^r12]: 04_service_definitions/admin/role_list.yaml, request.fields
[^r13]: 04_service_definitions/admin/role_list.yaml, response.envelope
[^r14]: 04_service_definitions/admin/role_list.yaml, common_errors
[^r15]: 04_service_definitions/admin/role_save.yaml, service: role_save
[^r17]: 04_service_definitions/admin/role_save.yaml, request
[^r18]: 04_service_definitions/admin/role_save.yaml, response
[^r19]: 04_service_definitions/admin/role_save.yaml, common_errors
[^r21]: 04_service_definitions/admin/role_svc_add.yaml, service: role_svc_add
[^r23]: 04_service_definitions/admin/role_svc_add.yaml, request.fields
[^r24]: 04_service_definitions/admin/role_svc_add.yaml, response.envelope
[^r26]: 04_service_definitions/admin/role_svc_add.yaml, errors
[^r27]: 04_service_definitions/admin/role_svc_remove.yaml, service: role_svc_remove
[^r29]: 04_service_definitions/admin/role_svc_remove.yaml, request.fields
