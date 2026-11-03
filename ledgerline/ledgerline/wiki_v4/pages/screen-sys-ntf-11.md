---
title: "SYS-NTF-11 Notification Queue"
type: "screen"
slug: "screen-sys-ntf-11"
summary: "Ledgerline screen for inspecting system notification queues, retrying failed notifications, and maintaining notification templates."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/admin/ntf_queue_list.yaml", "04_service_definitions/admin/ntf_retry.yaml", "04_service_definitions/admin/ntf_tpl_get.yaml", "04_service_definitions/admin/ntf_tpl_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen Code | SYS-NTF-11 |
| Screen Title | Notification Queue |
| Module | System |
| Access Roles | IT-ADMIN, SYS-ADMIN |
| Navigation | System > Notification queue |
| Read Service | ntf_queue_list |
| Write Services | ntf_retry, ntf_tpl_save |

SYS-NTF-11 Notification Queue is the Ledgerline administrative interface used to inspect outgoing notification queues and maintain system templates [^r1][^r3][^r7]. It allows administrative users to trigger retries for failed dispatches or update template records directly in the queue subsystem [^r3][^r6][^r8]. As of 26 October 2026, access is restricted to system administrative personnel under System > Notification queue [^r1].

## Fields

| Field Name | Type | Requirement | Description |
|---|---|---|---|
| id | String | Optional on screen; required for retries | Identifier of the notification record [^r2][^r6]. |
| comment | String | Optional | Free-text operational note or retry comment [^r2][^r6]. |

Screen SYS-NTF-11 presents optional string inputs for `id` and `comment` [^r2]. When invoking a retry operation from the screen, the notification `id` serves as a required parameter while `comment` remains optional [^r6].

## Keys and services

SYS-NTF-11 invokes services grouped under [[services-adm-ntf|ADM ntf services]] via dedicated action buttons:

* **Queue List**: Invokes the read service `ntf_queue_list` (`POST /ll72/svc/ntf_queue_list`) to load and view entries in the notification queue [^r3][^r5].
* **Retry**: Executes the write service `ntf_retry` to reprocess a notification dispatch using parameters `id` and `comment` [^r3][^r6].
* **Tpl Get**: Calls the read service `ntf_tpl_get` to retrieve notification template definitions [^r3][^r7].
* **Tpl Save**: Executes the write service `ntf_tpl_save` (`POST /ll72/svc/ntf_tpl_save`) to commit template updates back to the system [^r3][^r8].

Access to the screen and its actions is granted to roles IT-ADMIN and SYS-ADMIN [^r1].

## Messages

* `ERR-NTF-0001`: Notification Not Found, raised when an operation targets an invalid or missing notification record [^r4]. Message details and remedies are indexed under [[errors-ntf|ERR-NTF Notification Error Codes]].

## See also

* [[services-adm-ntf|ADM ntf services]]
* [[errors-ntf|ERR-NTF Notification Error Codes]]
* [[screen-sys-usr-01|SYS-USR-01 User]]
* [[screen-sys-job-06|SYS-JOB-06 Batch Job Submit]]
* [[screen-sys-par-04|SYS-PAR-04 System Parameter]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 42, SYS-NTF-11 NOTIFICATION QUEUE
[^r3]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 43, SYS-NTF-11 NOTIFICATION QUEUE
[^r7]: 04_service_definitions/admin/ntf_tpl_get.yaml, screen
[^r6]: 04_service_definitions/admin/ntf_retry.yaml, whole file
[^r8]: 04_service_definitions/admin/ntf_tpl_save.yaml, service: ntf_tpl_save
[^r2]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 43, SYS-NTF-11 NOTIFICATION QUEUE
[^r5]: 04_service_definitions/admin/ntf_queue_list.yaml, screen
[^r4]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 43, SYS-NTF-11 NOTIFICATION QUEUE
