---
title: "ADM usr services"
type: "service-group"
slug: "services-adm-usr"
summary: "Ledgerline ERP ADM module user administration services operating on screen SYS-USR-01 for creating, updating, locking, unlocking, searching, and managing user credentials."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/admin/usr_create.yaml", "04_service_definitions/admin/usr_disable.yaml", "04_service_definitions/admin/usr_lock.yaml", "04_service_definitions/admin/usr_pwd_reset.yaml", "04_service_definitions/admin/usr_search.yaml", "04_service_definitions/admin/usr_unlock.yaml", "04_service_definitions/admin/usr_update.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | ADM |
| Object | usr |
| Screen | SYS-USR-01 |
| Service count | 7 |
| Version introduced | 7.0 |
| Status | current |

The `usr` service group comprises the Ledgerline ERP 7.2 administration services responsible for user account lifecycle management in module ADM[^r10]. All services in this group link directly to screen [[screen-sys-usr-01|SYS-USR-01]] and execute stored procedures against the system database[^r1][^r3]. Available since Ledgerline version 7.0, these services handle user profile creation, search queries, record updates, credential resets, locking, unlocking, and account deactivation[^r1][^r10].

| Attribute | Details |
|---|---|
| Module | ADM[^r10] |
| Object | usr[^r10] |
| Screen | [[screen-sys-usr-01|SYS-USR-01]][^r1][^r10] |
| Service count | 7[^r1] |
| Version introduced | 7.0[^r10] |
| Status | current[^r10] |

## Services

### usr_create
The `usr_create` service ("USER CREATE") is a write service in module ADM operating on screen [[screen-sys-usr-01|SYS-USR-01]], available since version 7.0, and invoked via endpoint `POST /ll72/svc/usr_create`[^r10]. It executes backend database procedure `sp_usr_create`[^r3][^r10]. Authentication requires a session token in header `X-LL-Session` and a role authorised for the service[^r11]. The response envelope contains `rc` (`S | W | E`), `err_cd`, `msg`, and `data`[^r13].
* **Required fields**: `user_id` (string), `name` (string), `role_cd` (string), `ou_cd` (string)[^r3][^r12].
* **Optional fields**: `appr_limit` (float), `manager_id` (string), `default_cc` (string)[^r12].
* **Errors**: `ERR-USR-0118` ("USER ID ALREADY EXISTS")[^r14][^r46], `ERR-USR-0130` ("LIMIT ABOVE APPROVAL MATRIX FOR ROLE")[^r14][^r46], `ERR-SEC-0001` ("ACCESS DENIED")[^r15], `ERR-SYS-0421` ("<FIELD> MANDATORY")[^r15], `ERR-SYS-0422` ("UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>")[^r15], and `ERR-SYS-0503` ("SERVER BUSY, TRY LATER")[^r15].
* **Source file**: `04_service_definitions/admin/usr_create.yaml`[^r10].

### usr_update
The `usr_update` service ("USER UPDATE") is a write service in module ADM operating on screen [[screen-sys-usr-01|SYS-USR-01]], available since version 7.0, and invoked via endpoint `POST /ll72/svc/usr_update`[^r4][^r40]. It executes stored procedure `sp_usr_update`[^r4][^r43]. Authentication requires a session token in header `X-LL-Session` and an authorised role[^r41]. The response envelope provides `rc` (`S | W | E`), `err_cd`, `msg`, and `data`[^r43].
* **Required fields**: `user_id` (string)[^r4][^r42].
* **Optional fields**: `name` (string), `role_cd` (string), `ou_cd` (string), `appr_limit` (float)[^r42].
* **Errors**: `ERR-USR-0001` ("USER NOT FOUND")[^r44][^r45], `ERR-USR-0801` ("USER CLOSED (<status>)")[^r44][^r47], `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503`[^r44].
* **Source file**: `04_service_definitions/admin/usr_update.yaml`[^r40].

### usr_lock
The `usr_lock` service ("USER LOCK") is a write service in module ADM linked to screen [[screen-sys-usr-01|SYS-USR-01]], available since version 7.0, and invoked via HTTP POST at endpoint `/ll72/svc/usr_lock`[^r21][^r22]. It executes database procedure `sp_usr_lock`[^r5][^r25]. Authentication requires a session token in header `X-LL-Session` and a role permitted to execute the service[^r22]. The response envelope returns `rc` (`S | W | E`), `err_cd`, `msg`, and `data`[^r24].
* **Required fields**: `user_id` (string)[^r5][^r23].
* **Optional fields**: `reason` (string)[^r23].
* **Errors**: `ERR-USR-0001` ("USER NOT FOUND")[^r25][^r45].
* **Source file**: `04_service_definitions/admin/usr_lock.yaml`[^r21].

### usr_unlock
The `usr_unlock` service ("USER UNLOCK") is a write service in module ADM linked to screen [[screen-sys-usr-01|SYS-USR-01]], available since Ledgerline 7.0, and invoked via endpoint `POST /ll72/svc/usr_unlock`[^r36]. It executes stored procedure `sp_usr_unlock`[^r6][^r37]. Authentication requires a session token in header `X-LL-Session` and an authorised role[^r37].
* **Required fields**: `user_id` (string)[^r6][^r38].
* **Optional fields**: `comment` (string)[^r6][^r38].
* **Errors**: `ERR-USR-0001` ("USER NOT FOUND")[^r39][^r45], `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503`[^r39].
* **Source file**: `04_service_definitions/admin/usr_unlock.yaml`[^r36].

### usr_search
The `usr_search` service ("USER LIST") is a read service in module ADM backed by screen [[screen-sys-usr-01|SYS-USR-01]], available since version 7.0, and accessed via F2/Enter or endpoint `POST /ll72/svc/usr_search`[^r1][^r31][^r32]. Authentication requires a session token in header `X-LL-Session` and a role permitted to run the service[^r32]. The service responds with envelope fields `rc` (`S | W | E`), `err_cd`, `msg`, and `data`[^r34].
* **Required fields**: None[^r33].
* **Optional fields**: `user_id` (string), `name` (string), `role_cd` (string), `status` (string)[^r7][^r33].
* **Errors**: `ERR-SEC-0001` ("ACCESS DENIED")[^r35], `ERR-SYS-0421` ("<FIELD> MANDATORY")[^r35], `ERR-SYS-0422` ("UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>")[^r35], and `ERR-SYS-0503` ("SERVER BUSY, TRY LATER")[^r35].
* **Source file**: `04_service_definitions/admin/usr_search.yaml`[^r31].

### usr_pwd_reset
The `usr_pwd_reset` service ("USER PWD RESET") is a write service in module ADM tied to screen [[screen-sys-usr-01|SYS-USR-01]], available since version 7.0, and invoked via endpoint `POST /ll72/svc/usr_pwd_reset`[^r26]. It executes backend stored procedure `sp_usr_pwd_reset`[^r8][^r29]. Authentication requires a session token in header `X-LL-Session` and an authorised role[^r27]. The response envelope returns `rc` (`S | W | E`), `err_cd`, `msg`, and `data`[^r30].
* **Required fields**: `user_id` (string)[^r28].
* **Optional fields**: `comment` (string)[^r28].
* **Errors**: `ERR-USR-0001` ("USER NOT FOUND")[^r45] and `ERR-SEC-0012` (raised if the password fails policy requirements)[^r2][^r8].
* **Source file**: `04_service_definitions/admin/usr_pwd_reset.yaml`[^r26].

### usr_disable
The `usr_disable` service ("USER DISABLE") is a write service in module ADM on screen [[screen-sys-usr-01|SYS-USR-01]], available since version 7.0, and invoked via endpoint `POST /ll72/svc/usr_disable`[^r9][^r16]. It executes backend database procedure `sp_usr_disable`[^r9][^r20]. Authentication requires an `X-LL-Session` token and role permission[^r17]. The response envelope provides `rc` (`S | W | E`), `err_cd`, `msg`, and `data`[^r19].
* **Required fields**: `user_id` (string)[^r9][^r18].
* **Optional fields**: `reason` (string)[^r18].
* **Errors**: `ERR-USR-0001` ("USER NOT FOUND")[^r9][^r45].
* **Source file**: `04_service_definitions/admin/usr_disable.yaml`[^r16].

## See also
* [[screen-sys-usr-01|SYS-USR-01 User]]
* [[errors-usr|ERR-USR Error Codes]]
* [[services-adm-dlg|ADM dlg services]]
* [[services-adm-imp|ADM imp services]]
* [[screen-sys-api-14|SYS-API-14 Service Account Key Key Issue]]

## References

[^r10]: 04_service_definitions/admin/usr_create.yaml, service: usr_create
[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 45, SYS-USR-01 USER
[^r3]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 65, §7. Administration services
[^r11]: 04_service_definitions/admin/usr_create.yaml, auth
[^r13]: 04_service_definitions/admin/usr_create.yaml, response.envelope
[^r12]: 04_service_definitions/admin/usr_create.yaml, request.fields
[^r14]: 04_service_definitions/admin/usr_create.yaml, errors
[^r46]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 27
[^r15]: 04_service_definitions/admin/usr_create.yaml, common_errors
[^r4]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 65, usr_update USER UPDATE
[^r40]: 04_service_definitions/admin/usr_update.yaml, service: usr_update
[^r43]: 04_service_definitions/admin/usr_update.yaml, response.envelope
[^r41]: 04_service_definitions/admin/usr_update.yaml, auth
[^r42]: 04_service_definitions/admin/usr_update.yaml, request.fields
[^r44]: 04_service_definitions/admin/usr_update.yaml, errors
[^r45]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 26
[^r47]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 27
[^r21]: 04_service_definitions/admin/usr_lock.yaml, service: usr_lock
[^r22]: 04_service_definitions/admin/usr_lock.yaml, auth
[^r5]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 65, usr_lock USER LOCK
[^r25]: 04_service_definitions/admin/usr_lock.yaml, errors
[^r24]: 04_service_definitions/admin/usr_lock.yaml, response.envelope
[^r23]: 04_service_definitions/admin/usr_lock.yaml, request.fields
[^r36]: 04_service_definitions/admin/usr_unlock.yaml, service: usr_unlock
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 65, usr_unlock USER UNLOCK
[^r37]: 04_service_definitions/admin/usr_unlock.yaml, auth
[^r38]: 04_service_definitions/admin/usr_unlock.yaml, request
[^r39]: 04_service_definitions/admin/usr_unlock.yaml, errors
[^r31]: 04_service_definitions/admin/usr_search.yaml, whole file
[^r32]: 04_service_definitions/admin/usr_search.yaml, whole file
[^r34]: 04_service_definitions/admin/usr_search.yaml, response.envelope
[^r33]: 04_service_definitions/admin/usr_search.yaml, request.fields
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 65, usr_search USER LIST
[^r35]: 04_service_definitions/admin/usr_search.yaml, common_errors
[^r26]: 04_service_definitions/admin/usr_pwd_reset.yaml, whole file
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 66, usr_pwd_reset USER PWD RESET
[^r29]: 04_service_definitions/admin/usr_pwd_reset.yaml, procedures
[^r27]: 04_service_definitions/admin/usr_pwd_reset.yaml, auth
[^r30]: 04_service_definitions/admin/usr_pwd_reset.yaml, response.envelope
[^r28]: 04_service_definitions/admin/usr_pwd_reset.yaml, request.fields
[^r2]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 45, SYS-USR-01 USER
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 66, usr_disable USER DISABLE
[^r16]: 04_service_definitions/admin/usr_disable.yaml, service
[^r20]: 04_service_definitions/admin/usr_disable.yaml, procedures
[^r17]: 04_service_definitions/admin/usr_disable.yaml, auth
[^r19]: 04_service_definitions/admin/usr_disable.yaml, response.envelope
[^r18]: 04_service_definitions/admin/usr_disable.yaml, request.fields
