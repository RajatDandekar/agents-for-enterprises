---
title: "ERR-CAP Capacity Error Codes"
type: "error-list"
slug: "errors-cap"
summary: "Reference list of ERR-CAP capacity error codes raised by Ledgerline production capacity planning services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/production/cap_load.yaml", "04_service_definitions/production/cap_query.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-CAP |
| Domain | Production Capacity |
| Module | PRD |
| Related services | cap_load, cap_query |
| Status | current |

This catalogue documents error codes under the `ERR-CAP` prefix returned by production capacity services in Ledgerline. As of 26 October 2026, these messages indicate missing or unresolvable capacity records during planning and query operations. They surface primarily when executing transactions linked to [[services-prd-cap|PRD cap services]] or inspecting workloads via [[screen-prd-cap-13|PRD-CAP-13 Capacity]].

### ERR-CAP-0001

* **Message:** `CAPACITY NOT FOUND` [^r1][^r2]
* **Cause:** The system cannot locate a matching capacity record for the requested entity or time bucket [^r1][^r2].
* **Remedy:** Verify that capacity profiles are defined and available for the required work centre and scheduling window before resubmitting the request [^r1][^r2].
* **Raised by:** Service `cap_load` [^r1] and service `cap_query` [^r2].

## See also

* [[screen-prd-cap-13|PRD-CAP-13 Capacity]]
* [[services-prd-cap|PRD cap services]]

## References

[^r1]: 04_service_definitions/production/cap_load.yaml, errors
[^r2]: 04_service_definitions/production/cap_query.yaml, errors
