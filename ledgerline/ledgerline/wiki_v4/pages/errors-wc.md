---
title: "ERR-WC Work Centre Error Codes"
type: "error-list"
slug: "errors-wc"
summary: "Reference catalogue of work centre error codes raised by production services in Ledgerline."
audience: "staff"
status: "current"
sources: ["04_service_definitions/production/wc_get.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-WC |
| Domain | Production |
| Module | PRD |
| Services | [[services-prd-wc|PRD wc services]] |
| Status | Current |

The `ERR-WC` error series covers work centre validation and retrieval failures raised by Ledgerline production services as of 26 October 2026 [^r1]. These codes prevent operations from referencing invalid, missing, or inactive work centre records during shop-floor routing and capacity lookups [^r1].

### ERR-WC-0001

* **Message**: `WORK CENTRE NOT FOUND` [^r1]
* **Cause**: The requested work centre identifier does not exist in the database or could not be retrieved by the service [^r1].
* **Remedy**: Verify the work centre code in [[screen-prd-wc-10|PRD-WC-10 Work Centre]] and confirm the identifier supplied to the service call matches an existing record. Narrative handling and context are detailed in [[err-wc-0001|ERR-WC-0001 Work Centre Processing Failure]].
* **Raised by**: Service `wc_get` within [[services-prd-wc|PRD wc services]] [^r1].

## See also

* [[err-wc-0001|ERR-WC-0001 Work Centre Processing Failure]]
* [[screen-prd-wc-10|PRD-WC-10 Work Centre]]
* [[services-prd-wc|PRD wc services]]

## References

[^r1]: 04_service_definitions/production/wc_get.yaml, errors
