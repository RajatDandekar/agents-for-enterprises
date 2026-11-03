---
title: "SYS-USR-01 User"
type: "screen"
slug: "screen-sys-usr-01"
summary: "Ledgerline screen SYS-USR-01 manages user master records, roles, operating units, approval limits, password resets, and account status."
audience: "staff"
status: "current"
sources: ["05_master_data/Users_and_approval_limits.xlsx", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/admin/usr_create.yaml", "04_service_definitions/admin/usr_disable.yaml", "04_service_definitions/admin/usr_lock.yaml", "04_service_definitions/admin/usr_pwd_reset.yaml", "04_service_definitions/admin/usr_search.yaml", "04_service_definitions/admin/usr_unlock.yaml", "04_service_definitions/admin/usr_update.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | SYS-USR-01 |
| name | User |
| module | System |
| navigation | System > User |
| roles | IT-ADMIN, SYS-ADMIN |
| status | current |

Screen SYS-USR-01 manages Ledgerline user master records including user ID, name, job title, role code, operating unit, approval limit, manager ID, default cost centre, email address, and account status [^r1]. The screen is accessed via System > User by users assigned roles IT-ADMIN and SYS-ADMIN [^r2]. It serves as the primary administrative interface for provisioning, updating, locking, and resetting credentials for Northbridge Cycles personnel [^r1][^r4].

| Attribute | Value |
|---|---|
| Screen Code | SYS-USR-01 |
| Title | User |
| Navigation | System > User |
| Authorised Roles | IT-ADMIN, SYS-ADMIN |
| Primary Services | [[services-adm-usr|usr_create]], usr_update, usr_search |

## Fields

SYS-USR-01 captures both core identity attributes and operational routing parameters across the master record [^r1][^r3].

* **Mandatory fields**: `user_id`, `name`, `role_cd`, and `ou_cd` [^r3][^r7].
* **Optional fields**: `appr_limit`, `manager_id`, `default_cc`, `reason`, `comment`, and `status` [^r3][^r7].
* **Managed attributes**: In addition to core inputs, the screen manages job title, email address, and account status entries [^r1].

## Keys and services

The screen provides dedicated action buttons mapped to underlying ADM service definitions and database stored procedures [^r4][^r8]:

* **Create**: Invokes write service `usr_create` via endpoint `POST /ll72/svc/usr_create` and procedure `sp_usr_create` using mandatory fields `user_id`, `name`, `role_cd`, and `ou_cd`, alongside optional fields `appr_limit`, `manager_id`, and `default_cc` [^r4][^r6][^r7].
* **Update**: Invokes write service `usr_update` to handle modifications to `user_id`, `name`, `role_cd`, `ou_cd`, and `appr_limit` via stored procedure `sp_usr_update` [^r4][^r13].
* **Search (F2 / Enter)**: Invokes read service `usr_search` via endpoint `POST /ll72/svc/usr_search` to query records by optional parameters `user_id`, `name`, `role_cd`, and `status` [^r4][^r11].
* **Lock**: Executes write service `usr_lock` via endpoint `POST /ll72/svc/usr_lock` and stored procedure `sp_usr_lock` [^r4][^r9].
* **Unlock**: Invokes write service `usr_unlock` to restore locked accounts [^r4][^r12].
* **Disable**: Executes user disablement through the ADM write service `usr_disable` [^r4][^r8].
* **Pwd Reset**: Invokes write service `usr_pwd_reset` to initiate password resets via procedure `sp_usr_pwd_reset` [^r4][^r10].

## Messages

The screen raises validation errors defined under the [[errors-usr|ERR-USR]] and ERR-SEC series when processing user operations [^r5]:

* `ERR-USR-0001`: User Not Found [^r5].
* `ERR-USR-0118`: User Id Already Exists [^r5].
* `ERR-USR-0130`: Limit Above Approval Matrix For Role [^r5].
* `ERR-USR-0801`: User Closed [^r5].
* `ERR-SEC-0012`: Password Does Not Meet Policy [^r5].

## See also

* [[data-users-and-approval-limits|Users_and_approval_limits]]: Master register containing user IDs, approval thresholds, and assigned cost centres.
* [[services-adm-usr|ADM usr services]]: Backing service definitions for user management transactions.
* [[errors-usr|ERR-USR Error Codes]]: Reference list for user-related system error messages.
* [[screen-sys-api-14|SYS-API-14 Service Account Key Key Issue]]: Interface for service account credentials.

## References

[^r1]: 05_master_data/Users_and_approval_limits.xlsx, sheet Users, SHEET Users
[^r2]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 45, SYS-USR-01 USER
[^r4]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 45, SYS-USR-01 USER
[^r3]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 45, SYS-USR-01 USER
[^r7]: 04_service_definitions/admin/usr_create.yaml, request.fields
[^r8]: 04_service_definitions/admin/usr_disable.yaml, screen
[^r6]: 04_service_definitions/admin/usr_create.yaml, service: usr_create
[^r13]: 04_service_definitions/admin/usr_update.yaml, screen
[^r11]: 04_service_definitions/admin/usr_search.yaml, whole file
[^r9]: 04_service_definitions/admin/usr_lock.yaml, screen
[^r12]: 04_service_definitions/admin/usr_unlock.yaml, service: usr_unlock
[^r10]: 04_service_definitions/admin/usr_pwd_reset.yaml, whole file
[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 45, SYS-USR-01 USER
