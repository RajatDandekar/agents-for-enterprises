---
title: "Routing error codes (ERR-RTG)"
type: "error-list"
slug: "errors-rtg"
summary: "Catalogue of routing error codes (ERR-RTG) raised by production routing services in Ledgerline."
audience: "staff"
status: "current"
sources: ["04_service_definitions/production/rtg_get.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| prefix | ERR-RTG |
| module | Production (PRD) |
| type | error-list |
| status | current |

Catalogue of routing-related error codes under the `ERR-RTG` prefix raised by Ledgerline production operations as of 26 October 2026. These error messages indicate failures encountered when retrieving or handling routing definitions within the manufacturing module.

### ERR-RTG-0001
* **Message**: ROUTING NOT FOUND [^r1].
* **Cause**: The requested routing record cannot be located [^r1].
* **Remedy**: Verify the routing identifier or create the necessary definition via [[screen-prd-rtg-03|PRD-RTG-03 Routing]].
* **Raised by**: Raised by service `rtg_get` within [[services-prd-rtg|PRD rtg services]] [^r1].
* **Detailed page**: See [[err-rtg-0001|ERR-RTG-0001 Routing Save Failed]].

## See also
* [[screen-prd-rtg-03|PRD-RTG-03 Routing]]
* [[services-prd-rtg|PRD rtg services]]
* [[err-rtg-0001|ERR-RTG-0001 Routing Save Failed]]
* [[errors-itm|ERR-ITM error codes]]
* [[user-jfletcher|Joanna Fletcher]]

## References

[^r1]: 04_service_definitions/production/rtg_get.yaml, errors
