---
title: "SYS-SYS-15 System Ping"
type: "screen"
slug: "screen-sys-sys-15"
summary: "Ledgerline diagnostic screen accessed under System > System by IT-ADMIN and SYS-ADMIN to run ping, version, and health queries."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/admin/sys_health.yaml", "04_service_definitions/admin/sys_ping.yaml", "04_service_definitions/admin/sys_version.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen | SYS-SYS-15 |
| Title | System Ping |
| Module | System (ADM) |
| Navigation | System > System |
| Access roles | IT-ADMIN, SYS-ADMIN |
| Backed services | sys_ping, sys_version, sys_health |

Screen SYS-SYS-15 (System Ping) is a diagnostic screen in Ledgerline accessed under System > System by IT-ADMIN and SYS-ADMIN roles [^r1]. It allows administrators to run basic system connectivity, build version, and health checks [^r1][^r2][^r3]. The screen is backed by read-only administrative services in the ADM module [^r4][^r5][^r6].

| Field | Detail |
|---|---|
| Screen code | SYS-SYS-15 |
| Screen title | System Ping |
| Navigation | System > System |
| Roles | IT-ADMIN, SYS-ADMIN |
| Module | ADM |

## Fields

SYS-SYS-15 services diagnostic queries regarding system health, connectivity status, and software version [^r3]. The screen executes read-only query operations rather than transactional data-entry fields [^r4][^r5][^r6].

## Keys and services

SYS-SYS-15 provides buttons to execute three diagnostic services [^r2]:
* **Ping**: Triggers `sys_ping`, an ADM read service (endpoint `POST /ll72/svc/sys_ping`) available since version 7.0 [^r2][^r5].
* **Version**: Triggers `sys_version`, a read-only ADM service that retrieves the system version via endpoint `POST /ll72/svc/sys_version` [^r2][^r6].
* **Health**: Triggers `sys_health`, a read service under the ADM module providing system health data [^r2][^r4].

All three underlying services are grouped under [[services-adm-sys|ADM sys services]] [^r4][^r5][^r6].

## Messages

The screen reports diagnostic responses returned by `sys_ping`, `sys_version`, and `sys_health` [^r2][^r3].

## See also

* [[services-adm-sys|ADM sys services]]
* [[screen-sys-api-14|SYS-API-14 Service Account Key Key Issue]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 45, SYS-SYS-15 SYSTEM PING
[^r2]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 45, SYS-SYS-15 SYSTEM PING
[^r3]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 74, sys_ping SYSTEM PING
[^r4]: 04_service_definitions/admin/sys_health.yaml, whole file
[^r5]: 04_service_definitions/admin/sys_ping.yaml, service: sys_ping
[^r6]: 04_service_definitions/admin/sys_version.yaml, whole file
