---
title: "ERR-PCK error codes"
type: "error-list"
slug: "errors-pck"
summary: "Catalogue of ERR-PCK error codes raised by sales pick list services in Ledgerline."
audience: "staff"
status: "current"
sources: ["04_service_definitions/sales/pck_confirm.yaml", "04_service_definitions/sales/pck_get.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-PCK |
| Module | Sales (SAL) |
| Object | Pick List |
| Service group | [[services-sal-pck|SAL pck services]] |
| Status | current |

Catalogue of ERR-PCK error codes raised by sales pick list services in Ledgerline. These codes indicate record lookup failures or invalid status transitions when processing sales pick lists. They are encountered when fetching or confirming pick lists through [[services-sal-pck|SAL pck services]] and the associated screens.

### ERR-PCK-0001

* **Message:** PICK LIST NOT FOUND [^r1][^r3]
* **Cause:** The specified pick list record `pck_no` cannot be found in the system [^r3].
* **Remedy:** Verify that the pick list number exists and was entered correctly before re-running the operation.
* **Raised by:** `pck_confirm` [^r1], `pck_get` [^r3]

### ERR-PCK-0007

* **Message:** PICK LIST NOT IN DRAFT (<status>) [^r2]
* **Cause:** The pick list cannot be confirmed because it is in a state other than draft [^r2].
* **Remedy:** Inspect the current status of the pick list on [[screen-sal-pck-04|SAL-PCK-04 Pick List Entry]] to determine if it has already been processed or cancelled.
* **Raised by:** `pck_confirm` [^r2]

## See also

* [[screen-sal-pck-04|SAL-PCK-04 Pick List Entry]]
* [[services-sal-pck|SAL pck services]]

## References

[^r1]: 04_service_definitions/sales/pck_confirm.yaml, errors
[^r3]: 04_service_definitions/sales/pck_get.yaml, errors
[^r2]: 04_service_definitions/sales/pck_confirm.yaml, errors
