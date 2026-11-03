---
title: "MPS Error Codes"
type: "error-list"
slug: "errors-mps"
summary: "Master reference catalogue listing system error codes generated across Ledgerline master production schedule services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/production/mps_get.yaml", "04_service_definitions/production/mps_save.yaml", "04_service_definitions/production/mps_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-MPS |
| Domain | Master Production Schedule |
| Module | Production |
| Governing services | [[services-prd-mps|PRD mps services]] |
| Primary screen | [[screen-prd-mps-05|PRD-MPS-05 Master Schedule Entry]] |
| Status | Current |

The ERR-MPS error catalogue defines system messages returned by Ledgerline master production scheduling operations [^r1][^r2][^r3]. These validation codes enforce data integrity when retrieving, searching, or updating schedule records across production modules [^r1][^r2][^r3]. They appear on interface forms including [[screen-prd-mps-05|PRD-MPS-05 Master Schedule Entry]] during transaction processing [^r1][^r2].

### ERR-MPS-0001

* **Message**: `MASTER SCHEDULE NOT FOUND` [^r1].
* **Cause**: The requested master schedule record does not exist or cannot be retrieved with the supplied key [^r1].
* **Remedy**: Verify the schedule identifier and ensure the target schedule has been created and indexed [^r1].
* **Raised by**: Raised by the master schedule retrieval service `mps_get` [^r1]. For related narrative context, see [[err-mps-0001|ERR-MPS-0001 Missing Mandatory Field or Invalid Format in MPS]].

### ERR-MPS-0201

* **Message**: `QTY MUST BE > 0` [^r2][^r3].
* **Cause**: An entry contains a zero or negative quantity value when processing master schedule records [^r2][^r3].
* **Remedy**: Specify a positive production quantity greater than zero before submitting or searching entries [^r2][^r3].
* **Raised by**: Raised by the schedule persistence service `mps_save` and search service `mps_search` [^r2][^r3]. For related narrative context, see [[err-mps-0201|ERR-MPS-0201 Master Schedule Line Locked Against Modification]].

## See also

* [[err-mps-0001|ERR-MPS-0001 Missing Mandatory Field or Invalid Format in MPS]]
* [[err-mps-0201|ERR-MPS-0201 Master Schedule Line Locked Against Modification]]
* [[screen-prd-mps-05|PRD-MPS-05 Master Schedule Entry]]
* [[services-prd-mps|PRD mps services]]
* [[errors-itm|ERR-ITM error codes]]
* [[user-jfletcher|Joanna Fletcher (JFLETCHER)]]

## References

[^r1]: 04_service_definitions/production/mps_get.yaml, errors
[^r2]: 04_service_definitions/production/mps_save.yaml, errors
[^r3]: 04_service_definitions/production/mps_search.yaml, errors
