---
title: "ADM sys services"
type: "service-group"
slug: "services-adm-sys"
summary: "ADM module system diagnostic read services (sys_ping, sys_version, sys_health) operating on screen SYS-SYS-15."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/admin/sys_health.yaml", "04_service_definitions/admin/sys_ping.yaml", "04_service_definitions/admin/sys_version.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | ADM |
| Object | sys |
| Available since | Ledgerline 7.0 |
| Endpoint prefix | POST /ll72/svc/ |
| Screen | SYS-SYS-15 |
| Authentication | X-LL-Session token |

The ADM sys service group provides system diagnostic read services for Ledgerline, comprising sys_ping, sys_version, and sys_health [^r1]. These services operate on screen [[screen-sys-sys-15|SYS-SYS-15]] without stored procedures and have been available since Ledgerline 7.0 [^r2]. Each endpoint is invoked via HTTP POST with a session token passed in the `X-LL-Session` header and requires an authorised user role [^r4][^r8][^r12].

| Key | Value |
|---|---|
| Module | ADM [^r3][^r7][^r11] |
| Object | sys [^r1] |
| Available since | Ledgerline 7.0 [^r2][^r3][^r7][^r11] |
| Associated screen | [[screen-sys-sys-15|SYS-SYS-15]] [^r1][^r2][^r3][^r7] |
| Authentication | Header `X-LL-Session` [^r4][^r8][^r12] |

## Services

### sys_health

* **Title**: SYSTEM HEALTH [^r3]
* **Kind**: Read [^r3]
* **Source file**: `04_service_definitions/admin/sys_health.yaml` [^r3]
* **Endpoint**: `POST /ll72/svc/sys_health` [^r4]
* **Screen**: [[screen-sys-sys-15|SYS-SYS-15]] [^r2][^r3]
* **Available since**: Ledgerline 7.0 [^r2][^r3]
* **Required fields**: None [^r5]
* **Optional fields**: None [^r5]
* **Return envelope**: Returns code `rc` ('S | W | E'), `err_cd` ('error code when rc is E'), `msg` ('short message in capitals'), and `data` ('result') [^r5].
* **Errors**: ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r6].

### sys_ping

* **Title**: SYSTEM PING [^r1][^r2][^r7]
* **Kind**: Read [^r2][^r7]
* **Source file**: `04_service_definitions/admin/sys_ping.yaml` [^r7]
* **Endpoint**: `POST /ll72/svc/sys_ping` [^r8]
* **Screen**: [[screen-sys-sys-15|SYS-SYS-15]] [^r1][^r2][^r7]
* **Available since**: Ledgerline 7.0 [^r2][^r7]
* **Required fields**: None [^r9]
* **Optional fields**: None [^r9]
* **Return envelope**: Returns envelope containing `rc` (S | W | E), `err_cd` (error code when rc is E), `msg` (short message in capitals), and `data` (result) [^r9].
* **Errors**: ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r10].

### sys_version

* **Title**: SYSTEM VERSION [^r11]
* **Kind**: Read [^r2][^r11]
* **Source file**: `04_service_definitions/admin/sys_version.yaml` [^r11]
* **Endpoint**: `POST /ll72/svc/sys_version` [^r12]
* **Screen**: [[screen-sys-sys-15|SYS-SYS-15]] [^r1][^r2]
* **Available since**: Ledgerline 7.0 [^r2][^r11]
* **Required fields**: None [^r13]
* **Optional fields**: None [^r13]
* **Return envelope**: Returns envelope containing `rc` ('S | W | E'), `err_cd`, `msg`, and `data` result [^r13].
* **Errors**: ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r14].

## See also

* [[screen-sys-sys-15|SYS-SYS-15 System Ping]]
* [[screen-sys-api-14|SYS-API-14 Service Account Key Key Issue]]
* [[services-adm-dlg|ADM dlg services]]
* [[services-adm-par|ADM par services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 45, SYS-SYS-15 SYSTEM PING
[^r2]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 74, sys_ping SYSTEM PING
[^r4]: 04_service_definitions/admin/sys_health.yaml, whole file
[^r8]: 04_service_definitions/admin/sys_ping.yaml, service: sys_ping
[^r12]: 04_service_definitions/admin/sys_version.yaml, whole file
[^r3]: 04_service_definitions/admin/sys_health.yaml, whole file
[^r7]: 04_service_definitions/admin/sys_ping.yaml, service: sys_ping
[^r11]: 04_service_definitions/admin/sys_version.yaml, whole file
[^r5]: 04_service_definitions/admin/sys_health.yaml, whole file
[^r6]: 04_service_definitions/admin/sys_health.yaml, whole file
[^r9]: 04_service_definitions/admin/sys_ping.yaml, request / response
[^r10]: 04_service_definitions/admin/sys_ping.yaml, common_errors
[^r13]: 04_service_definitions/admin/sys_version.yaml, whole file
[^r14]: 04_service_definitions/admin/sys_version.yaml, whole file
