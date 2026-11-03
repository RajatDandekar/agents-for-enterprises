---
title: "ERR-JOB Error Codes"
type: "error-list"
slug: "errors-job"
summary: "Reference list of ERR-JOB batch job error codes raised by administrative batch processing services in Ledgerline."
audience: "staff"
status: "current"
sources: ["04_service_definitions/admin/job_cancel.yaml", "04_service_definitions/admin/job_log.yaml", "04_service_definitions/admin/job_schedule.yaml", "04_service_definitions/admin/job_status.yaml", "04_service_definitions/admin/job_submit.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-JOB |
| Domain | Admin / Batch Jobs |
| Related module | ADM |
| Source | Service definitions |

The `ERR-JOB` error code series covers exceptions raised during administrative batch job management in Ledgerline. These codes are triggered by core background processing services when attempting to submit, cancel, schedule, or query batch jobs. Operations involving these services may also return common system and security errors.

### ERR-JOB-0001

* **Message:** BATCH JOB NOT FOUND [^r1]
* **Cause:** The requested batch job identifier cannot be located in the system [^r1].
* **Remedy:** Verify the batch job identifier and confirm the job record exists before re-issuing the request.
* **Raised by:** `job_cancel` [^r1], `job_log` [^r3], `job_schedule` [^r4], `job_status` [^r5], and `job_submit` [^r6].

### ERR-JOB-0007

* **Message:** BATCH JOB NOT IN DRAFT (<status>) [^r6]
* **Cause:** Attempted to submit a batch job that is not currently in draft state [^r6].
* **Remedy:** Check the current job status and ensure submissions are performed only on draft jobs.
* **Raised by:** `job_submit` [^r6].

### ERR-JOB-0101

* **Message:** JOB ALREADY RUNNING [^r6]
* **Cause:** The target batch job is already executing [^r6].
* **Remedy:** Await job completion or check the job execution log before re-attempting submission.
* **Raised by:** `job_submit` [^r6].

### ERR-JOB-0801

* **Message:** BATCH JOB CLOSED (<status>) [^r2]
* **Cause:** Attempted to cancel a batch job that is already closed [^r2].
* **Remedy:** Inspect the batch job status to determine whether it has already finished, aborted, or closed.
* **Raised by:** `job_cancel` [^r2].

## Common related errors

The batch job service `job_submit` also commonly returns system and security errors, including access denial (`ERR-SEC-0001`), missing required fields (`ERR-SYS-0421`), invalid field values (`ERR-SYS-0422`), and server capacity limits (`ERR-SYS-0503`) [^r7].

## See also

* [[screen-sys-job-06|SYS-JOB-06 Batch Job Submit]]
* [[services-adm-job|ADM job services]]

## References

[^r1]: 04_service_definitions/admin/job_cancel.yaml, errors
[^r3]: 04_service_definitions/admin/job_log.yaml, errors
[^r4]: 04_service_definitions/admin/job_schedule.yaml, errors
[^r5]: 04_service_definitions/admin/job_status.yaml, errors
[^r6]: 04_service_definitions/admin/job_submit.yaml, errors
[^r2]: 04_service_definitions/admin/job_cancel.yaml, errors
[^r7]: 04_service_definitions/admin/job_submit.yaml, common_errors
