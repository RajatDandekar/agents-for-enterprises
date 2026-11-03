---
title: "ADM ses services"
type: "service-group"
slug: "services-adm-ses"
summary: "Administrative session services for listing active user sessions and terminating sessions on screen SYS-SES-09."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/admin/ses_kill.yaml", "04_service_definitions/admin/ses_list.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | ADM |
| Object | ses |
| Screen | SYS-SES-09 |
| Services | ses_list, ses_kill |
| Available since | Ledgerline 7.0 |
| Status | current |

The ADM ses service group provides session management operations for Ledgerline ERP on screen [[screen-sys-ses-09|SYS-SES-09]][^r1][^r2][^r14]. These services allow system administrators to inspect active user sessions and terminate specific sessions[^r14]. Both services require authentication using a session token passed in the `X-LL-Session` header and appropriate role authorisation[^r4][^r10].

## Services

### ses_list

Read service used to retrieve active user sessions associated with screen [[screen-sys-ses-09|SYS-SES-09]][^r1][^r9]. It has been available since Ledgerline version 7.0 and is invoked at endpoint `POST /ll72/svc/ses_list`[^r8][^r9].

* **Required fields:** None[^r11].
* **Optional fields:** `user_id` (str)[^r1][^r11].
* **Response envelope:** Standard envelope returning return code `rc` (`S | W | E`), error code `err_cd`, message `msg`, and `data`[^r12].
* **Errors:** `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER)[^r13].
* **Source file:** `04_service_definitions/admin/ses_list.yaml`[^r8].

### ses_kill

Write service that executes database procedure `sp_ses_kill` on screen [[screen-sys-ses-09|SYS-SES-09]] to terminate a user session[^r2][^r3][^r6]. It has been available since Ledgerline version 7.0 and is called via `POST /ll72/svc/ses_kill`[^r3][^r4].

* **Required fields:** `ses_id` (str)[^r2][^r5].
* **Optional fields:** `reason` (str)[^r2][^r5].
* **Response envelope:** Standard envelope returning return code `rc` (`S | W | E`), error code `err_cd`, message `msg`, and `data`[^r7].
* **Errors:** Returns `ERR-SES-0001` if the target session does not exist or is not found[^r2][^r14].
* **Source file:** `04_service_definitions/admin/ses_kill.yaml`[^r3].

## See also

* [[screen-sys-ses-09|SYS-SES-09 Session]]
* [[services-adm-par|ADM par services]]
* [[services-adm-dlg|ADM dlg services]]
* [[services-adm-imp|ADM imp services]]
* [[screen-sys-api-14|SYS-API-14 Service Account Key Key Issue]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 71, ses_list SESSION LIST
[^r2]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 72, ses_kill SESSION KILL
[^r14]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 44, SYS-SES-09 SESSION
[^r4]: 04_service_definitions/admin/ses_kill.yaml, whole file
[^r10]: 04_service_definitions/admin/ses_list.yaml, auth
[^r9]: 04_service_definitions/admin/ses_list.yaml, screen: SYS-SES-09
[^r8]: 04_service_definitions/admin/ses_list.yaml, service: ses_list
[^r11]: 04_service_definitions/admin/ses_list.yaml, request
[^r12]: 04_service_definitions/admin/ses_list.yaml, response
[^r13]: 04_service_definitions/admin/ses_list.yaml, common_errors
[^r3]: 04_service_definitions/admin/ses_kill.yaml, whole file
[^r6]: 04_service_definitions/admin/ses_kill.yaml, procedures
[^r5]: 04_service_definitions/admin/ses_kill.yaml, request.fields
[^r7]: 04_service_definitions/admin/ses_kill.yaml, response.envelope
