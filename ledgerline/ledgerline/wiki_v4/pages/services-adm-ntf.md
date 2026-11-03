---
title: "ADM ntf services"
type: "service-group"
slug: "services-adm-ntf"
summary: "Services in the ADM module for managing the notification queue and notification templates, associated with screen SYS-NTF-11."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/admin/ntf_queue_list.yaml", "04_service_definitions/admin/ntf_retry.yaml", "04_service_definitions/admin/ntf_tpl_get.yaml", "04_service_definitions/admin/ntf_tpl_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | ADM |
| Object | ntf |
| Screen | [[screen-sys-ntf-11|SYS-NTF-11]] |
| Endpoint prefix | /ll72/svc/ |
| Version added | 7.0 |
| Status | current |

The `ntf` service group handles notification queue processing and template configuration within the ADM module of Ledgerline ERP 7.2 [^r5][^r10]. All services authenticate via a session token in the `X-LL-Session` HTTP header and verify authorization against the user's role [^r6][^r11][^r17][^r22]. The services operate primarily against screen [[screen-sys-ntf-11|SYS-NTF-11]] to monitor delivery status, retry failed dispatches, and maintain templates [^r1][^r2][^r10][^r21].

## Services

### ntf_queue_list

The read service `ntf_queue_list` queries notification queue records on screen [[screen-sys-ntf-11|SYS-NTF-11]] via endpoint `POST /ll72/svc/ntf_queue_list` [^r2][^r5]. It has been available since version 7.0 and returns standard envelope fields `rc`, `err_cd`, `msg`, and `data` [^r5][^r8].

* **Required fields:** none [^r7].
* **Optional fields:** `id` (str, QUEUE ID) [^r2][^r7].
* **Errors:** ERR-NTF-0001 (NOTIFICATION NOT FOUND), ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r2][^r9].
* **Source file:** `04_service_definitions/admin/ntf_queue_list.yaml` [^r5].

### ntf_retry

The write service `ntf_retry` triggers a re-dispatch of an existing queued notification via endpoint `POST /ll72/svc/ntf_retry` and executes stored procedure `sp_ntf_retry` [^r3][^r11][^r13]. It belongs to screen [[screen-sys-ntf-11|SYS-NTF-11]] and has been available since version 7.0 [^r10].

* **Required fields:** `id` (str, ID) [^r3][^r12].
* **Optional fields:** `comment` (str, COMMENT) [^r3][^r12].
* **Errors:** ERR-NTF-0001 (NOTIFICATION NOT FOUND), ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r3][^r14][^r15].
* **Source file:** `04_service_definitions/admin/ntf_retry.yaml` [^r10].

### ntf_tpl_get

The read service `ntf_tpl_get` fetches notification template details via endpoint `POST /ll72/svc/ntf_tpl_get` [^r4][^r16]. It has been available since version 7.0 and uses the standard response envelope [^r16][^r19].

* **Required fields:** `id` (str, template ID) [^r4][^r18].
* **Optional fields:** none [^r18].
* **Errors:** ERR-NTF-0001 (NOTIFICATION NOT FOUND), ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r20].
* **Source file:** `04_service_definitions/admin/ntf_tpl_get.yaml` [^r16].

### ntf_tpl_save

The write service `ntf_tpl_save` updates notification templates via endpoint `POST /ll72/svc/ntf_tpl_save` by executing database stored procedure `sp_ntf_tpl_save` [^r4][^r21][^r25]. It is associated with screen [[screen-sys-ntf-11|SYS-NTF-11]] and has been present since version 7.0 [^r21].

* **Required fields:** `id` (str) [^r4][^r23].
* **Optional fields:** `comment` (str) [^r4][^r23].
* **Errors:** ERR-NTF-0001 (NOTIFICATION NOT FOUND), ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r26].
* **Source file:** `04_service_definitions/admin/ntf_tpl_save.yaml` [^r21].

## See also

* [[screen-sys-ntf-11|SYS-NTF-11 Notification Queue]]
* [[services-adm-dlg|ADM dlg services]]
* [[services-adm-par|ADM par services]]

## References

[^r5]: 04_service_definitions/admin/ntf_queue_list.yaml, service: ntf_queue_list
[^r10]: 04_service_definitions/admin/ntf_retry.yaml, whole file
[^r6]: 04_service_definitions/admin/ntf_queue_list.yaml, auth
[^r11]: 04_service_definitions/admin/ntf_retry.yaml, auth
[^r17]: 04_service_definitions/admin/ntf_tpl_get.yaml, auth
[^r22]: 04_service_definitions/admin/ntf_tpl_save.yaml, auth
[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 43, SYS-NTF-11 NOTIFICATION QUEUE
[^r2]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 72, ntf_queue_list NOTIFICATION QUEUE LIST
[^r21]: 04_service_definitions/admin/ntf_tpl_save.yaml, service: ntf_tpl_save
[^r8]: 04_service_definitions/admin/ntf_queue_list.yaml, response.envelope
[^r7]: 04_service_definitions/admin/ntf_queue_list.yaml, request.fields
[^r9]: 04_service_definitions/admin/ntf_queue_list.yaml, errors
[^r3]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 72, ntf_retry NOTIFICATION RETRY
[^r13]: 04_service_definitions/admin/ntf_retry.yaml, procedures
[^r12]: 04_service_definitions/admin/ntf_retry.yaml, request.fields
[^r14]: 04_service_definitions/admin/ntf_retry.yaml, errors
[^r15]: 04_service_definitions/admin/ntf_retry.yaml, common_errors
[^r4]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 72, ntf_tpl_save NOTIFICATION TPL SAVE
[^r16]: 04_service_definitions/admin/ntf_tpl_get.yaml, service: ntf_tpl_get
[^r19]: 04_service_definitions/admin/ntf_tpl_get.yaml, response.envelope
[^r18]: 04_service_definitions/admin/ntf_tpl_get.yaml, request.fields
[^r20]: 04_service_definitions/admin/ntf_tpl_get.yaml, errors
[^r25]: 04_service_definitions/admin/ntf_tpl_save.yaml, procedures
[^r23]: 04_service_definitions/admin/ntf_tpl_save.yaml, request.fields
[^r26]: 04_service_definitions/admin/ntf_tpl_save.yaml, errors
