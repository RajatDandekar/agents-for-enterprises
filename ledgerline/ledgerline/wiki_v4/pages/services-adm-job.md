---
title: "ADM job services"
type: "service-group"
slug: "services-adm-job"
summary: "Ledgerline ADM services for submitting, querying, scheduling, and cancelling batch jobs on screen SYS-JOB-06."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/admin/job_cancel.yaml", "04_service_definitions/admin/job_list.yaml", "04_service_definitions/admin/job_log.yaml", "04_service_definitions/admin/job_schedule.yaml", "04_service_definitions/admin/job_status.yaml", "04_service_definitions/admin/job_submit.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | ADM |
| Object | job |
| Screen | SYS-JOB-06 |
| Endpoint base | /ll72/svc/ |
| Since version | 7.0 |
| Protocol | POST |
| Session header | X-LL-Session |

The ADM job service group provides endpoints for submitting, monitoring, scheduling, and cancelling batch background jobs in Ledgerline [^r1][^r6]. All services operate under module ADM, are associated with screen [[screen-sys-job-06|SYS-JOB-06]], and require session authentication via the `X-LL-Session` header with appropriate role permissions [^r6][^r7][^r13][^r14][^r17][^r18][^r22][^r23][^r27][^r28][^r31][^r32]. Responses return a standard envelope containing return code `rc` (`S | W | E`), error code `err_cd`, message `msg`, and payload `data` [^r9][^r16][^r20][^r25][^r30][^r34].

## Services

### job_submit
The `job_submit` service is a write service available since version 7.0 at endpoint `POST /ll72/svc/job_submit`, triggered on screen [[screen-sys-job-06|SYS-JOB-06]] by pressing F9 [^r1][^r2][^r31]. It executes database procedure `sp_job_submit` [^r2][^r35].

* **Required fields:** `job_cd` (str) [^r2][^r33].
* **Optional fields:** `comment` (str) [^r2][^r33].
* **Errors:** Specific errors include ERR-JOB-0001, ERR-JOB-0007, and ERR-JOB-0101 [^r1][^r2]. Common errors include ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r12].
* **Source files:** `04_service_definitions/admin/job_submit.yaml`, `MAN-SCR-72 v7.2.3`, `MAN-SVC-72 v7.2.3` [^r1][^r2][^r31].

### job_status
The `job_status` service is a read service available since version 7.0 at endpoint `POST /ll72/svc/job_status` [^r27].

* **Required fields:** `job_cd` (str) [^r3][^r29].
* **Optional fields:** None [^r3][^r29].
* **Errors:** Specific error ERR-JOB-0001 (BATCH JOB NOT FOUND), alongside common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r3][^r36].
* **Source files:** `04_service_definitions/admin/job_status.yaml`, `MAN-SCR-72 v7.2.3`, `MAN-SVC-72 v7.2.3` [^r1][^r3][^r27].

### job_list
The `job_list` service is a read service available since version 7.0 at endpoint `POST /ll72/svc/job_list` [^r13].

* **Required fields:** None [^r3][^r15].
* **Optional fields:** `job_cd` (str) [^r3][^r15].
* **Errors:** ERR-JOB-0001, alongside common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r3][^r16].
* **Source files:** `04_service_definitions/admin/job_list.yaml`, `MAN-SCR-72 v7.2.3`, `MAN-SVC-72 v7.2.3` [^r1][^r3][^r13].

### job_cancel
The `job_cancel` service is a write service available since version 7.0 at endpoint `POST /ll72/svc/job_cancel`, mapped to Shift+F8 on screen [[screen-sys-job-06|SYS-JOB-06]] and calling stored procedure `sp_job_cancel` [^r1][^r4][^r6][^r10].

* **Required fields:** `job_cd` (str) and `reason` (str) [^r4][^r8].
* **Optional fields:** None [^r4][^r8].
* **Errors:** Specific errors ERR-JOB-0001 (BATCH JOB NOT FOUND) and ERR-JOB-0801 (BATCH JOB CLOSED (<status>)), alongside common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r4][^r11][^r12].
* **Source files:** `04_service_definitions/admin/job_cancel.yaml`, `MAN-SCR-72 v7.2.3`, `MAN-SVC-72 v7.2.3` [^r1][^r4][^r6].

### job_log
The `job_log` service is a read service available since version 7.0 at endpoint `POST /ll72/svc/job_log` [^r17].

* **Required fields:** `job_cd` (str) [^r3][^r19].
* **Optional fields:** None [^r3][^r19].
* **Errors:** Specific error ERR-JOB-0001 (BATCH JOB NOT FOUND), alongside common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r3][^r21].
* **Source files:** `04_service_definitions/admin/job_log.yaml`, `MAN-SCR-72 v7.2.3`, `MAN-SVC-72 v7.2.3` [^r1][^r3][^r17].

### job_schedule
The `job_schedule` service is a write service available since version 7.0 at endpoint `POST /ll72/svc/job_schedule`, executing procedure `sp_job_schedule` [^r5][^r22].

* **Required fields:** `job_cd` (str) [^r5][^r24].
* **Optional fields:** `params` (str) and `run_at` (str) [^r5][^r24].
* **Errors:** Specific error ERR-JOB-0001 (BATCH JOB NOT FOUND), alongside common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r5][^r25][^r26].
* **Source files:** `04_service_definitions/admin/job_schedule.yaml`, `MAN-SCR-72 v7.2.3`, `MAN-SVC-72 v7.2.3` [^r1][^r5][^r22].

## See also
* [[screen-sys-job-06|SYS-JOB-06 Batch Job Submit]]
* [[errors-job|ERR-JOB Error Codes]]
* [[services-adm-dlg|ADM dlg services]]
* [[services-adm-par|ADM par services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 42, SYS-JOB-06 BATCH JOB SUBMIT
[^r6]: 04_service_definitions/admin/job_cancel.yaml, service: job_cancel
[^r7]: 04_service_definitions/admin/job_cancel.yaml, auth
[^r13]: 04_service_definitions/admin/job_list.yaml, service: job_list
[^r14]: 04_service_definitions/admin/job_list.yaml, service: job_list
[^r17]: 04_service_definitions/admin/job_log.yaml, service: job_log
[^r18]: 04_service_definitions/admin/job_log.yaml, auth
[^r22]: 04_service_definitions/admin/job_schedule.yaml, job_schedule
[^r23]: 04_service_definitions/admin/job_schedule.yaml, auth
[^r27]: 04_service_definitions/admin/job_status.yaml, whole file
[^r28]: 04_service_definitions/admin/job_status.yaml, whole file
[^r31]: 04_service_definitions/admin/job_submit.yaml, service: job_submit
[^r32]: 04_service_definitions/admin/job_submit.yaml, auth
[^r9]: 04_service_definitions/admin/job_cancel.yaml, response.envelope
[^r16]: 04_service_definitions/admin/job_list.yaml, response
[^r20]: 04_service_definitions/admin/job_log.yaml, response.envelope
[^r25]: 04_service_definitions/admin/job_schedule.yaml, response
[^r30]: 04_service_definitions/admin/job_status.yaml, response.envelope
[^r34]: 04_service_definitions/admin/job_submit.yaml, response.envelope
[^r2]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 68, job_submit BATCH JOB SUBMIT
[^r35]: 04_service_definitions/admin/job_submit.yaml, procedures
[^r33]: 04_service_definitions/admin/job_submit.yaml, request.fields
[^r12]: 04_service_definitions/admin/job_cancel.yaml, common_errors
[^r3]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 69, job_status BATCH JOB STATUS
[^r29]: 04_service_definitions/admin/job_status.yaml, request.fields
[^r36]: 04_service_definitions/admin/job_status.yaml, errors
[^r15]: 04_service_definitions/admin/job_list.yaml, request
[^r4]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 69, job_cancel BATCH JOB CANCEL
[^r10]: 04_service_definitions/admin/job_cancel.yaml, procedures
[^r8]: 04_service_definitions/admin/job_cancel.yaml, request.fields
[^r11]: 04_service_definitions/admin/job_cancel.yaml, errors
[^r19]: 04_service_definitions/admin/job_log.yaml, request.fields
[^r21]: 04_service_definitions/admin/job_log.yaml, errors
[^r5]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 69, job_schedule BATCH JOB SCHEDULE
[^r24]: 04_service_definitions/admin/job_schedule.yaml, request.fields
[^r26]: 04_service_definitions/admin/job_schedule.yaml, common_errors
