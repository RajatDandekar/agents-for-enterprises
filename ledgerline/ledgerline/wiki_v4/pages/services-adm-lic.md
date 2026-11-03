---
title: "ADM lic services"
type: "service-group"
slug: "services-adm-lic"
summary: "Ledgerline ADM licence services including lic_status for querying system licence status."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/admin/lic_status.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | ADM |
| Object | lic |
| Status | current |
| Screens | SYS-LIC-10 |
| Available since | 7.0 |

The ADM lic service group provides backend operations for querying Ledgerline licence records [^r3]. As of 26 October 2026, the group contains the `lic_status` read service, which powers licence verification on the [[screen-sys-lic-10|SYS-LIC-10 Licence Status]] screen [^r1][^r2][^r3]. Callers authenticate using session tokens and must have permissions granted to their role [^r4].

## Services

### lic_status

The `lic_status` service retrieves the status of a specified licence from the system [^r1][^r2]. It is an ADM read service available since version 7.0, associated with screen [[screen-sys-lic-10|SYS-LIC-10 Licence Status]], and is invoked via HTTP POST to `/ll72/svc/lic_status` [^r3]. Callers must provide an active session token in the `X-LL-Session` HTTP header, and the calling user's role must be authorised to run the service [^r4].

The response envelope returns four fields: `rc` (return code: 'S | W | E'), `err_cd` (the error code when `rc` is E), `msg` (short message in capitals), and `data` (the result payload) [^r6].

* **Required fields**: `lic_id` (str, LIC ID) [^r2][^r5].
* **Optional fields**: none [^r5].
* **Errors**: ERR-LIC-0001 (raised when the licence ID is missing or the licence is not found) [^r1][^r2][^r7], ERR-SEC-0001 [^r7], ERR-SYS-0421 [^r7], ERR-SYS-0422 [^r7], and ERR-SYS-0503 [^r7].
* **Source file**: `04_service_definitions/admin/lic_status.yaml` [^r3][^r4][^r5][^r6][^r7].

## See also

* [[screen-sys-lic-10|SYS-LIC-10 Licence Status]]
* [[services-adm-dlg|ADM dlg services]]
* [[services-adm-imp|ADM imp services]]
* [[services-adm-par|ADM par services]]

## References

[^r3]: 04_service_definitions/admin/lic_status.yaml, service: lic_status
[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 42, SYS-LIC-10 LICENCE STATUS
[^r2]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 72, lic_status LICENCE STATUS
[^r4]: 04_service_definitions/admin/lic_status.yaml, auth
[^r6]: 04_service_definitions/admin/lic_status.yaml, response
[^r5]: 04_service_definitions/admin/lic_status.yaml, request
[^r7]: 04_service_definitions/admin/lic_status.yaml, errors
