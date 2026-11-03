---
title: "ERR-OPR-* Operation Confirmation Error Codes"
type: "error-list"
slug: "errors-opr"
summary: "Reference list of ERR-OPR-* error codes raised during production operation confirmation processing in Ledgerline."
audience: "staff"
status: "current"
sources: ["04_service_definitions/production/opr_get.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

This page documents the ERR-OPR-* error codes encountered during Ledgerline production operation confirmation processing as of 26 October 2026. These error codes are raised when reading, validating, or updating operation records. Narrative handling and deeper analysis for specific errors are maintained on individual error pages where applicable.

### ERR-OPR-0001: OPERATION CONFIRMATION NOT FOUND

* **Message:** `OPERATION CONFIRMATION NOT FOUND` [^r1]
* **Cause:** The requested operation confirmation record cannot be located in the system using the provided lookup criteria [^r1].
* **Remedy:** Verify the operation confirmation identifier and ensure the target record exists before repeating the lookup [^r1].
* **Raised by:** Service `opr_get` in [[services-prd-opr|PRD opr services]] [^r1].
* **Detailed guide:** See [[err-opr-0001|ERR-OPR-0001: Operation confirmation conflict or invalid data]].

## See also

* [[err-opr-0001|ERR-OPR-0001: Operation confirmation conflict or invalid data]]
* [[screen-prd-opr-04|PRD-OPR-04 Operation Confirmation Entry]]
* [[services-prd-opr|PRD opr services]]
* [[user-jfletcher|Joanna Fletcher (JFLETCHER)]]

## References

[^r1]: 04_service_definitions/production/opr_get.yaml, errors
