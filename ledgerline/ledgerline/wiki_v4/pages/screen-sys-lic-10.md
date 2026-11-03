---
title: "SYS-LIC-10 Licence Status"
type: "screen"
slug: "screen-sys-lic-10"
summary: "Ledgerline screen SYS-LIC-10 displays licence status details for a given licence identifier via the lic_status service."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/admin/lic_status.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | SYS-LIC-10 |
| Screen name | Licence Status |
| Module | System (SYS) |
| Menu path | System > Licence |
| Roles | IT-ADMIN, SYS-ADMIN |
| Primary service | lic_status |
| Status | Current |

Screen SYS-LIC-10 provides licence status enquiry functions within Ledgerline under the System navigation menu [^r1]. It interfaces directly with backend licensing services to retrieve and present current licence validation records [^r3]. Access to this enquiry screen is restricted to system administration personnel [^r1].

| Field | Value |
|---|---|
| Screen code | SYS-LIC-10 |
| Name | Licence Status |
| Menu path | System > Licence |
| Permitted roles | IT-ADMIN, SYS-ADMIN |
| Primary service | lic_status |

## Fields

SYS-LIC-10 requires a single mandatory input field:

* `lic_id`: Mandatory string representing the licence identifier to inspect [^r2].

The screen displays returned licence attributes fetched from the backend [^r3].

## Keys and services

* **Status**: Triggers the execution of the `lic_status` service using the provided `lic_id` to query and refresh licence state on screen [^r2][^r3].

Service interaction is handled through [[services-adm-lic|ADM lic services]] [^r3].

## Messages

* `ERR-LIC-0001`: Licence Not Found. Raised when the submitted `lic_id` does not match an existing licence record [^r2].

## See also

* [[services-adm-lic|ADM lic services]]
* [[screen-sys-usr-01|SYS-USR-01 User]]
* [[screen-sys-api-14|SYS-API-14 Service Account Key Key Issue]]
* [[screen-sys-par-04|SYS-PAR-04 System Parameter]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 42, SYS-LIC-10 LICENCE STATUS
[^r3]: 04_service_definitions/admin/lic_status.yaml, screen
[^r2]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 42, SYS-LIC-10 LICENCE STATUS
