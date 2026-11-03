---
title: "SYS-CFG-16 Menu Config"
type: "screen"
slug: "screen-sys-cfg-16"
summary: "Ledgerline screen for configuring menu structures and role-based menu access via cfg_get and cfg_save."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/admin/cfg_get.yaml", "04_service_definitions/admin/cfg_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | SYS-CFG-16 |
| Title | Menu Config |
| Module | System |
| Navigation | System > Menu config |
| Authorised roles | IT-ADMIN, SYS-ADMIN |
| Services | cfg_get, cfg_save |
| Status | current |

Screen SYS-CFG-16 (Menu Config) provides system administrators with tools to retrieve and maintain role-specific menu configurations within Ledgerline [^r1][^r2]. Accessed under System > Menu config, access is restricted to administrative user roles [^r1]. It executes underlying administration services to read existing layouts and save menu structure updates [^r2][^r4].

| Field | Detail |
|---|---|
| Screen code | SYS-CFG-16 [^r1] |
| Navigation path | System > Menu config [^r1] |
| Permitted roles | IT-ADMIN, SYS-ADMIN [^r1] |
| Primary services | `cfg_get`, `cfg_save` [^r2] |

## Fields

* `menu_cd`: Mandatory menu code identifier required for retrieval and saving [^r1][^r3][^r5].
* `role_cd`: Role code identifier, accepted as an optional filter on screen entry but mandatory when executing a configuration save [^r1][^r5].

## Keys and services

Screen SYS-CFG-16 interacts with configuration services detailed under [[services-adm-cfg]]:

* **cfg_get**: Read service (`MENU CONFIG GET`) that retrieves menu configuration records matching the specified `menu_cd` [^r2][^r3].
* **cfg_save**: Write service invoked over endpoint `POST /ll72/svc/cfg_save` to persist menu configuration changes [^r2][^r4]. It validates that mandatory fields `role_cd` and `menu_cd` are supplied and executes stored procedure `sp_cfg_save` [^r5].

## Messages

* `ERR-CFG-0001`: Raised when a requested menu configuration record cannot be found [^r2].

## See also

* [[services-adm-cfg]]
* [[screen-sys-api-14]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 40, SYS-CFG-16 MENU CONFIG
[^r2]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 74, cfg_get MENU CONFIG GET
[^r4]: 04_service_definitions/admin/cfg_save.yaml, whole file
[^r3]: 04_service_definitions/admin/cfg_get.yaml, service
[^r5]: 04_service_definitions/admin/cfg_save.yaml, request.fields
