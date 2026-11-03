---
title: "ERR-MRP Error Codes"
type: "error-list"
slug: "errors-mrp"
summary: "Reference list of ERR-MRP error codes returned by Ledgerline production MRP services, detailing messages and raising services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/production/mrp_exceptions.yaml", "04_service_definitions/production/mrp_firm.yaml", "04_service_definitions/production/mrp_get.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-MRP |
| Module | PRD (Production) |
| Object | MRP |
| Status | current |

This page catalogues the `ERR-MRP` error codes emitted by Ledgerline production planning services. These errors occur when requesting, querying exceptions for, or firming material requirements planning runs.

### ERR-MRP-0001

* **Message:** MRP RUN NOT FOUND [^r1][^r2][^r3]
* **Cause:** The requested MRP run identifier does not exist in the system [^r1][^r2][^r3].
* **Remedy:** Verify the MRP run ID before querying exceptions, viewing the run, or firming planned orders [^r1][^r2][^r3].
* **Raised by:** Service `mrp_exceptions` when querying MRP exceptions [^r1], service `mrp_firm` [^r2], and service `mrp_get` [^r3].
* **Detailed page:** [[err-mrp-0001|ERR-MRP-0001]]

## See also

* [[err-mrp-0001|ERR-MRP-0001]]
* [[services-prd-mrp|PRD mrp services]]
* [[screen-prd-mrp-09|PRD-MRP-09 Mrp Run]]
* [[user-jfletcher|Joanna Fletcher (JFLETCHER)]]

## References

[^r1]: 04_service_definitions/production/mrp_exceptions.yaml, errors
[^r2]: 04_service_definitions/production/mrp_firm.yaml, errors
[^r3]: 04_service_definitions/production/mrp_get.yaml, errors
