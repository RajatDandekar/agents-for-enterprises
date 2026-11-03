---
title: "SYS-ROL-02 Role"
type: "screen"
slug: "screen-sys-rol-02"
summary: "Ledgerline screen for role management, service assignment, and maintenance under System menu, restricted to IT-ADMIN and SYS-ADMIN."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/admin/role_get.yaml", "04_service_definitions/admin/role_list.yaml", "04_service_definitions/admin/role_save.yaml", "04_service_definitions/admin/role_svc_add.yaml", "04_service_definitions/admin/role_svc_remove.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen Code | SYS-ROL-02 |
| Name | Role |
| Menu Path | System > Role |
| Module | System Administration |
| Authorized Roles | IT-ADMIN, SYS-ADMIN |
| Read Services | role_get, role_list |
| Write Services | role_save, role_svc_add, role_svc_remove |

SYS-ROL-02 is the Ledgerline system screen used to configure and maintain user roles and their associated service authorizations [^r1]. It is accessed via the navigation path System > Role by operators assigned the IT-ADMIN or SYS-ADMIN roles [^r1]. The screen allows administrators to query role definitions, save updates, and manage authorized services linked to each role [^r1][^r2][^r3].

## Fields

| Field Name | Description | Status |
|---|---|---|
| `role_cd` | Unique role identifier code used to retrieve and define records [^r2][^r5]. | Mandatory [^r2] |
| `descr` | Textual description of the role [^r2][^r7]. | Optional [^r2] |
| `svc` | Backend service associated with the role [^r2][^r7]. | Optional [^r2] |
| `comment` | Additional notes or comments regarding the role [^r2]. | Optional [^r2] |

## Keys and services

* **F3 (Get)**: Invokes the read service `role_get` to retrieve role details using the specified `role_cd` parameter [^r3][^r5].
* **F8 (Save)**: Calls the backend write service `role_save` (POST `/ll72/svc/role_save`) to persist role attributes including `role_cd`, `descr`, and `svc` [^r3][^r7].
* **List**: Calls the read service `role_list` (POST `/ll72/svc/role_list`) to query roles using the optional `role_cd` filter parameter [^r3][^r6].
* **Svc Add**: Executes the ADM write service `role_svc_add` (POST `/ll72/svc/role_svc_add`) to attach services to roles [^r3][^r8].
* **Svc Remove**: Executes the backend write service `role_svc_remove` (POST `/ll72/svc/role_svc_remove`) to remove services from roles [^r3][^r9].

The backend service operations powering this screen are documented under [[services-adm-role|ADM role services]] [^r5][^r6][^r7][^r8][^r9].

## Messages

* `ERR-ROL-0001`: Returned when a queried role is not found in the system [^r4].

## See also

* [[services-adm-role|ADM role services]]
* [[screen-sys-usr-01|SYS-USR-01 User]]
* [[screen-sys-api-14|SYS-API-14 Service Account Key Key Issue]]
* [[screen-sys-dlg-03|SYS-DLG-03 Approval Delegation Entry]]
* [[screen-sys-par-04|SYS-PAR-04 System Parameter]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 44, SYS-ROL-02 ROLE
[^r2]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 44, SYS-ROL-02 ROLE
[^r3]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 44, SYS-ROL-02 ROLE
[^r5]: 04_service_definitions/admin/role_get.yaml, screen: SYS-ROL-02
[^r7]: 04_service_definitions/admin/role_save.yaml, service: role_save
[^r6]: 04_service_definitions/admin/role_list.yaml, service: role_list
[^r8]: 04_service_definitions/admin/role_svc_add.yaml, service: role_svc_add
[^r9]: 04_service_definitions/admin/role_svc_remove.yaml, screen
[^r4]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 44, SYS-ROL-02 ROLE
