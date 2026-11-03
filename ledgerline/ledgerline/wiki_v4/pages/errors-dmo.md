---
title: "Errors DMO (ERR-DMO-*)"
type: "error-list"
slug: "errors-dmo"
summary: "Reference list of ERR-DMO error codes raised by demo bike services in Ledgerline."
audience: "staff"
status: "current"
sources: ["04_service_definitions/sales/dmo_close.yaml", "04_service_definitions/sales/dmo_get.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

This page catalogues the `ERR-DMO-*` error codes returned by demo bike services in Ledgerline sales processing. These errors identify invalid retrieval attempts or prohibited state transitions during demo bike lifecycle operations. They are raised by backend services associated with [[services-sal-dmo|SAL dmo services]].

### ERR-DMO-0001

* **Message:** DEMO BIKE NOT FOUND [^r1][^r3]
* **Cause:** Raised when a demo bike record does not exist [^r3].
* **Remedy:** Verify the demo bike identifier and re-attempt the lookup.
* **Raised by:** Service `dmo_close` [^r1] and service `dmo_get` [^r3].
* **Detailed page:** [[err-dmo-0001|ERR-DMO-0001 DEMO BIKE NOT FOUND]]

### ERR-DMO-0801

* **Message:** DEMO BIKE CLOSED (<status>) [^r2]
* **Cause:** Raised when an action is attempted on a demo bike record that is already closed [^r2].
* **Remedy:** Check the current status of the demo bike before attempting closure.
* **Raised by:** Service `dmo_close` [^r2].
* **Detailed page:** [[err-dmo-0801|ERR-DMO-0801 DEMO BIKE CLOSED (<status>)]]

## See also

* [[err-dmo-0001|ERR-DMO-0001 DEMO BIKE NOT FOUND]]
* [[err-dmo-0801|ERR-DMO-0801 DEMO BIKE CLOSED (<status>)]]
* [[services-sal-dmo|SAL dmo services]]

## References

[^r1]: 04_service_definitions/sales/dmo_close.yaml, errors
[^r3]: 04_service_definitions/sales/dmo_get.yaml, errors
[^r2]: 04_service_definitions/sales/dmo_close.yaml, errors
