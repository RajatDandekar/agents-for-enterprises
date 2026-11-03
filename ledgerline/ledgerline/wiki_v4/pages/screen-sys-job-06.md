---
title: "SYS-JOB-06 Batch Job Submit"
type: "screen"
slug: "screen-sys-job-06"
summary: "Ledgerline screen to submit, schedule, monitor, and cancel background batch routines under module ADM."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/admin/job_cancel.yaml", "04_service_definitions/admin/job_list.yaml", "04_service_definitions/admin/job_log.yaml", "04_service_definitions/admin/job_schedule.yaml", "04_service_definitions/admin/job_status.yaml", "04_service_definitions/admin/job_submit.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | SYS-JOB-06 |
| Screen title | Batch Job Submit |
| Module | ADM |
| Menu path | System > Batch job |
| Access roles | IT-ADMIN, SYS-ADMIN |
| Primary write service | job_submit |
| Status | current |

SYS-JOB-06 is the Ledgerline administration screen used to submit, schedule, monitor, and cancel background batch routines [^r1][^r5]. It displays task execution states including active, completed, held, and aborted [^r1]. In operational practice, running batch jobs must be cancelled formally within SYS-JOB-06 rather than via host OS commands to ensure clean rollbacks of partial postings [^r2].

The screen is accessed via the navigation path System > Batch job by users assigned the IT-ADMIN or SYS-ADMIN roles [^r3]. Further administrative guidance is documented in [[man-adm-72|MAN-ADM-72]] [^r1][^r2].

## Fields

SYS-JOB-06 contains the following parameter and control fields:

| Field | Mandatory | Description |
|---|---|---|
| `job_cd` | Yes | Identifier code of the batch job routine [^r4]. |
| `reason` | Yes | Mandatory justification or explanation text for the action [^r4]. |
| `comment` | No | Optional supplemental comment [^r4]. |
| `params` | No | Optional execution parameters passed to the routine [^r4]. |
| `run_at` | No | Optional scheduled start time for deferred execution [^r4]. |

## Keys and services

SYS-JOB-06 integrates with the [[services-adm-job|ADM job services]] suite via the following functional keys, actions, and API endpoints:

* **F9 (Submit)**: Calls write service `job_submit` via `POST /ll72/svc/job_submit` to execute a batch job [^r5][^r12].
* **Shift+F8 (Cancel)**: Invokes write service `job_cancel` via `POST /ll72/svc/job_cancel` using parameters `job_cd` and `reason` to trigger a clean rollback [^r5][^r7].
* **Schedule**: Calls write service `job_schedule` to schedule background batch runs [^r5][^r10].
* **Status**: Invokes read service `job_status` to inspect current execution status [^r5][^r11].
* **List**: Invokes read service `job_list` via `POST /ll72/svc/job_list` with optional criterion `job_cd` to query job listings [^r5][^r8].
* **Log**: Invokes read service `job_log` via `POST /ll72/svc/job_log` to display batch execution logs [^r5][^r9].

## Messages

The screen can raise errors catalogued under [[errors-job|ERR-JOB Error Codes]], including [^r6]:

* `ERR-JOB-0001` [^r6]
* `ERR-JOB-0007` [^r6]
* `ERR-JOB-0101` (Job Already Running) [^r6]
* `ERR-JOB-0801` (Batch Job Closed) [^r6]

## See also

* [[man-adm-72|MAN-ADM-72 Ledgerline ERP 7.2 System Administration]]
* [[man-bat-72|MAN-BAT-72 Ledgerline ERP 7.2 Batch Jobs: Northbridge]]
* [[services-adm-job|ADM job services]]
* [[errors-job|ERR-JOB Error Codes]]
* [[sop-it-002|SOP-IT-002 Service Account Management]]
* [[screen-sys-usr-01|SYS-USR-01 User]]
* [[screen-sys-par-04|SYS-PAR-04 System Parameter]]

## References

[^r1]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 7, Operational practice
[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 42, SYS-JOB-06 BATCH JOB SUBMIT
[^r2]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 8, Practical guidance
[^r3]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 41, SYS-JOB-06 BATCH JOB SUBMIT
[^r4]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 42, SYS-JOB-06 BATCH JOB SUBMIT
[^r12]: 04_service_definitions/admin/job_submit.yaml, screen: SYS-JOB-06
[^r7]: 04_service_definitions/admin/job_cancel.yaml, service: job_cancel
[^r10]: 04_service_definitions/admin/job_schedule.yaml, job_schedule
[^r11]: 04_service_definitions/admin/job_status.yaml, whole file
[^r8]: 04_service_definitions/admin/job_list.yaml, service: job_list
[^r9]: 04_service_definitions/admin/job_log.yaml, screen
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 42, SYS-JOB-06 BATCH JOB SUBMIT
