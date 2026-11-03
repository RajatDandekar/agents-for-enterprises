---
title: "Errors QIN"
type: "error-list"
slug: "errors-qin"
summary: "System error and warning codes with prefix QIN raised by Ledgerline incoming inspection services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/production/qin_get.yaml", "04_service_definitions/production/qin_post.yaml", "04_service_definitions/production/qin_reject.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | QIN |
| Domain | Quality / Incoming Inspection |
| Module | Production |
| Services | qin_get, qin_post, qin_reject |

The QIN error list defines the standard error codes and warnings returned by Ledgerline's incoming inspection services in the production module [^r1][^r2]. These codes are raised during inspection retrieval, posting, and rejection workflows, enforcing record existence, status validation, and quality sampling compliance [^r1][^r2][^r3][^r4][^r6]. As of 26 October 2026, the list covers inspection lookups, draft verification, AQL plan thresholds, and concession warnings [^r1][^r3][^r4][^r5].

### ERR-QIN-0001
* **Message:** INCOMING INSPECTION NOT FOUND [^r1][^r2][^r6]
* **Cause:** The requested incoming inspection record does not exist in Ledgerline [^r1][^r2][^r6].
* **Remedy:** Verify the inspection identifier before attempting retrieval, posting, or rejection [^r1][^r2][^r6].
* **Raised by:** `qin_get`, `qin_post`, and `qin_reject` services in [[services-prd-qin|PRD qin services]] [^r1][^r2][^r6].

### ERR-QIN-0007
* **Message:** INCOMING INSPECTION NOT IN DRAFT (<status>) [^r3]
* **Cause:** The transaction attempted to post an incoming inspection record that is currently in a state other than DRAFT [^r3].
* **Remedy:** Check the current record status in [[screen-qa-ins-01|QA-INS-01 Incoming Inspection Entry]] and ensure it is in DRAFT before posting [^r3].
* **Raised by:** `qin_post` service [^r3].

### ERR-QIN-0230
* **Message:** SAMPLE SIZE BELOW AQL PLAN [^r4]
* **Cause:** The recorded inspection sample count does not meet the minimum sample size required by the active AQL plan [^r4].
* **Remedy:** Inspect the full required sample quantity specified by the plan before posting the result [^r4].
* **Raised by:** `qin_post` service [^r4].

### W-QIN-231
* **Message:** PASSED WITH CONCESSION [^r5]
* **Cause:** An inspection record was posted where acceptance was granted under an approved concession [^r5].
* **Remedy:** Confirm the concession approval details on file; this is a warning and does not block posting [^r5].
* **Raised by:** `qin_post` service [^r5].

## See also
* [[screen-qa-ins-01|QA-INS-01 Incoming Inspection Entry]]
* [[services-prd-qin|PRD qin services]]
* [[user-jfletcher|Joanna Fletcher (JFLETCHER)]]

## References

[^r1]: 04_service_definitions/production/qin_get.yaml, errors
[^r2]: 04_service_definitions/production/qin_post.yaml, errors
[^r3]: 04_service_definitions/production/qin_post.yaml, errors
[^r4]: 04_service_definitions/production/qin_post.yaml, errors
[^r6]: 04_service_definitions/production/qin_reject.yaml, errors
[^r5]: 04_service_definitions/production/qin_post.yaml, errors
