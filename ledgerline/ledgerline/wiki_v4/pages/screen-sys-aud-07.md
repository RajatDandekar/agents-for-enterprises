---
title: "SYS-AUD-07 Audit Trail"
type: "screen"
slug: "screen-sys-aud-07"
summary: "Ledgerline audit trail query and export screen for system administrators and IT staff."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/admin/aud_export.yaml", "04_service_definitions/admin/aud_query.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen | SYS-AUD-07 |
| Name | Audit Trail |
| Menu path | System > Audit trail |
| Roles | IT-ADMIN, SYS-ADMIN |
| Read services | aud_query, aud_export |
| Status | current |

SYS-AUD-07 is the Ledgerline screen located under System > Audit trail used to query and export system audit trail records [^r1]. It is accessible only to users assigned the IT-ADMIN or SYS-ADMIN roles [^r1]. The screen allows administrators to filter historical system actions and export logs for investigation [^r1][^r3].

| Attribute | Value |
|---|---|
| Screen code | SYS-AUD-07 |
| Module path | System > Audit trail |
| Allowed roles | IT-ADMIN, SYS-ADMIN |
| Primary services | aud_query, aud_export |

## Fields

Screen SYS-AUD-07 requires a mandatory `id` field [^r1]. It also accepts optional fields `user_id`, `svc`, `from_dt`, and `comment` [^r1]. For search operations, query filters supported by the screen include the optional fields `user_id`, `svc`, and `from_dt` [^r5].

## Keys and services

SYS-AUD-07 connects to the [[services-adm-aud|ADM aud services]] service group for retrieving and outputting audit data.
* **Query**: Executes the read service `aud_query` via endpoint `POST /ll72/svc/aud_query` to query audit trail entries based on the provided filter parameters [^r2][^r4].
* **Export**: Executes the read service `aud_export` via endpoint `POST /ll72/svc/aud_export` to export audit trail records by ID [^r2][^r3].

## Messages

The screen handles error code `ERR-AUD-0001` during operation [^r2].

## See also

* [[services-adm-aud|ADM aud services]]
* [[screen-sys-usr-01|SYS-USR-01 User]]
* [[screen-sys-api-14|SYS-API-14 Service Account Key Key Issue]]
* [[screen-sys-job-06|SYS-JOB-06 Batch Job Submit]]
* [[screen-sys-par-04|SYS-PAR-04 System Parameter]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 40, SYS-AUD-07 AUDIT TRAIL
[^r3]: 04_service_definitions/admin/aud_export.yaml, screen
[^r5]: 04_service_definitions/admin/aud_query.yaml, request.fields
[^r2]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 40, SYS-AUD-07 AUDIT TRAIL
[^r4]: 04_service_definitions/admin/aud_query.yaml, service: aud_query
