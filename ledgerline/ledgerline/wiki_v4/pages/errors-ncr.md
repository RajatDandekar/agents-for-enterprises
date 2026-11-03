---
title: "NCR Error Codes (ERR-NCR-*)"
type: "error-list"
slug: "errors-ncr"
summary: "Ledgerline error codes with prefix ERR-NCR raised by production non-conformance report services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/production/ncr_close.yaml", "04_service_definitions/production/ncr_get.yaml", "04_service_definitions/production/ncr_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-NCR |
| Module | Production (PRD) |
| Domain | Non-conformance reporting |
| Status | current |

Error codes prefixed with `ERR-NCR-` are raised by Ledgerline non-conformance reporting services under [[services-prd-ncr|PRD ncr services]]. They validate report numbers, transaction quantities, and workflow states during entry and maintenance on screens such as [[screen-qa-ncr-02|QA-NCR-02 Non-Conformance Report Entry]]. When an operation fails, the calling service returns one of these codes to block invalid database updates.

### ERR-NCR-0001
* **Message:** NON-CONFORMANCE REPORT NOT FOUND [^r1][^r3]
* **Cause:** The transaction references an invalid or non-existent `ncr_no` [^r3].
* **Remedy:** Verify the report number before querying or updating the record.
* **Raised by:** Service `ncr_get` [^r3], service `ncr_close` [^r1].

### ERR-NCR-0201
* **Message:** QTY MUST BE > 0 [^r4]
* **Cause:** The specified non-conformance quantity is zero or negative [^r4].
* **Remedy:** Enter a positive quantity greater than zero [^r4].
* **Raised by:** Service `ncr_save` [^r4].

### ERR-NCR-0801
* **Message:** NON-CONFORMANCE REPORT CLOSED (<status>) [^r2]
* **Cause:** An operation was attempted on an NCR that is already closed [^r2].
* **Remedy:** Confirm the NCR workflow status and select an active report.
* **Raised by:** Service `ncr_close` [^r2].

## See also
* [[screen-qa-ncr-02|QA-NCR-02 Non-Conformance Report Entry]]
* [[services-prd-ncr|PRD ncr services]]

## References

[^r1]: 04_service_definitions/production/ncr_close.yaml, errors
[^r3]: 04_service_definitions/production/ncr_get.yaml, errors
[^r4]: 04_service_definitions/production/ncr_save.yaml, errors
[^r2]: 04_service_definitions/production/ncr_close.yaml, errors
