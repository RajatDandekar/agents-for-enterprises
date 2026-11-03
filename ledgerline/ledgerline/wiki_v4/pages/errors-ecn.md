---
title: "ERR-ECN Error Codes Reference"
type: "error-list"
slug: "errors-ecn"
summary: "Reference catalogue of ERR-ECN error codes raised by engineering change services and release procedures in Ledgerline."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-PRD-002 Engineering Change v1.0.pdf", "04_service_definitions/production/ecn_approve.yaml", "04_service_definitions/production/ecn_release.yaml", "04_service_definitions/production/ecn_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-ECN |
| Module | Production |
| Domain | Engineering Change Notes |
| System | Ledgerline |
| Source files | ecn_approve.yaml, ecn_release.yaml, ecn_search.yaml, SOP-PRD-002 |

The `ERR-ECN-*` error codes are raised by Ledgerline engineering change services during change search, approval, and release workflows. They enforce lifecycle validation states on engineering change notices and prevent production revisions while active shop-floor commitments persist. Resolving these conditions is required under [[sop-prd-002|SOP-PRD-002]] before an engineering change note can be moved from draft status or released into active production.

## Error codes

### ERR-ECN-0001
* **Message:** ENGINEERING CHANGE NOT FOUND [^r2][^r4]
* **Cause:** The requested engineering change record does not exist in Ledgerline under the provided key [^r2][^r4].
* **Remedy:** Verify the engineering change identifier and ensure the record has been created and saved [^r2][^r4].
* **Raised by:** Service `ecn_approve` [^r2]; service `ecn_release` [^r4]. Part of [[services-prd-ecn|PRD ecn services]].

### ERR-ECN-0007
* **Message:** ENGINEERING CHANGE NOT IN DRAFT (<status>) [^r3][^r5]
* **Cause:** The operation requires the change notice to be in draft status, but the target record is currently in a different status [^r3][^r5].
* **Remedy:** Check the current workflow status of the change record before initiating approval or release [^r3][^r5].
* **Raised by:** Service `ecn_approve` [^r3]; service `ecn_release` [^r5].

### ERR-ECN-0105
* **Message:** DATE IN PAST [^r7]
* **Cause:** A date parameter supplied in the search criteria precedes the allowable date range [^r7].
* **Remedy:** Correct the search filter parameters to use valid non-past dates [^r7].
* **Raised by:** Service `ecn_search` [^r7].

### ERR-ECN-0220
* **Message:** OPEN WORK ORDERS ON OLD REVISION [^r6]
* **Cause:** Active work orders remain committed to the superseded revision when attempting to release the engineering change [^r1][^r6].
* **Remedy:** Close, complete, or reassign all committed active work orders on the superseded revision before re-attempting release [^r1]. Full handling is detailed on [[err-ecn-0220|ERR-ECN-0220 Open Work Orders on Revision]].
* **Raised by:** Service `ecn_release` [^r6]; [[sop-prd-002|SOP-PRD-002]] §5 [^r1].

## See also
* [[err-ecn-0220|ERR-ECN-0220 Open Work Orders on Revision]]
* [[services-prd-ecn|PRD ecn services]]
* [[sop-prd-002|SOP-PRD-002 Engineering Change (ECN)]]
* [[screen-prd-ecn-06|PRD-ECN-06 Engineering Change Entry]]

## References

[^r2]: 04_service_definitions/production/ecn_approve.yaml, errors
[^r4]: 04_service_definitions/production/ecn_release.yaml, errors
[^r3]: 04_service_definitions/production/ecn_approve.yaml, errors
[^r5]: 04_service_definitions/production/ecn_release.yaml, errors
[^r7]: 04_service_definitions/production/ecn_search.yaml, errors
[^r6]: 04_service_definitions/production/ecn_release.yaml, errors
[^r1]: 02_procedures/SOP-PRD-002 Engineering Change v1.0.pdf, p. 3, §5. Procedure
