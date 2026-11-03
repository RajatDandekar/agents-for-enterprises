---
title: "SYS-SES-09 Session"
type: "screen"
slug: "screen-sys-ses-09"
summary: "Ledgerline screen for listing active user sessions and terminating sessions by ID, restricted to IT-ADMIN and SYS-ADMIN roles."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/admin/ses_kill.yaml", "04_service_definitions/admin/ses_list.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | SYS-SES-09 |
| Module | System |
| Path | System > Session |
| Allowed roles | IT-ADMIN, SYS-ADMIN |
| Read service | ses_list |
| Write service | ses_kill |

SYS-SES-09 (Session) is the administrative screen in Ledgerline used to monitor and terminate active user sessions [^r1]. It is accessed under System > Session and is restricted to users with the IT-ADMIN or SYS-ADMIN roles [^r1]. The screen supports listing sessions and killing specific sessions by session identifier [^r3][^r5].

## Fields

| Field | Required / Optional | Notes |
|---|---|---|
| `ses_id` | Mandatory | Session identifier [^r2]. |
| `user_id` | Optional | User identifier filter or context [^r2]. |
| `reason` | Optional | Reason for terminating the session [^r2][^r3]. |

## Keys and services

SYS-SES-09 provides the buttons List and Kill to manage sessions [^r5].

* **List**: Calls the read service `ses_list` at endpoint `POST /ll72/svc/ses_list` to retrieve active sessions [^r4][^r5].
* **Kill**: Invokes the write service `ses_kill` using the required field `ses_id` and optional field `reason` to terminate a session [^r3][^r5].

These underlying services belong to the [[services-adm-ses|ADM ses services]] group.

## Messages

* `ERR-SES-0001`: Raised when a specified session is not found [^r5].

## See also

* [[services-adm-ses|ADM ses services]]
* [[screen-sys-usr-01|SYS-USR-01 User]]
* [[screen-sys-par-04|SYS-PAR-04 System Parameter]]
* [[screen-sys-job-06|SYS-JOB-06 Batch Job Submit]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 44, SYS-SES-09 SESSION
[^r3]: 04_service_definitions/admin/ses_kill.yaml, whole file
[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 44, SYS-SES-09 SESSION
[^r2]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 44, SYS-SES-09 SESSION
[^r4]: 04_service_definitions/admin/ses_list.yaml, screen: SYS-SES-09
