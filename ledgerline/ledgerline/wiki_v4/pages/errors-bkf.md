---
title: "ERR-BKF error codes"
type: "error-list"
slug: "errors-bkf"
summary: "Error code catalogue for Ledgerline ERR-BKF backflush messages raised by production backflush services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/production/bkf_get.yaml", "04_service_definitions/production/bkf_post.yaml", "04_service_definitions/production/bkf_reverse.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-BKF |
| Domain | Production (backflush) |
| Source services | bkf_get, bkf_post, bkf_reverse |
| Status | current |

Catalogue of ERR-BKF error codes returned by Ledgerline production backflushing services. These codes handle record lookups, validation states, and execution controls when querying, posting, or reversing backflush transactions. Backflush operational screens and batch jobs return these messages during component consumption and inventory recording.

### [[err-bkf-0001|ERR-BKF-0001]]
* **Message:** BACKFLUSH NOT FOUND [^r1]
* **Cause:** The requested backflush record cannot be located in the system [^r1].
* **Remedy:** Verify the backflush transaction identifier before retrying the operation [^r1].
* **Raised by:** `bkf_get` [^r1], `bkf_post` [^r2], `bkf_reverse` [^r4]

### [[err-bkf-0007|ERR-BKF-0007]]
* **Message:** BACKFLUSH NOT IN DRAFT (<status>) [^r3]
* **Cause:** The backflush transaction is not in draft status at the time of posting [^r3].
* **Remedy:** Check the current status of the backflush record and ensure it is in draft state before submitting [^r3].
* **Raised by:** `bkf_post` [^r3]

## See also
* [[services-prd-bkf|PRD bkf services]]
* [[screen-prd-bkf-08|PRD-BKF-08 Backflush]]
* [[err-bkf-0001|ERR-BKF-0001: Works order invalid or not in valid state for backflush]]
* [[err-bkf-0007|ERR-BKF-0007: Component inventory shortage during backflush]]

## References

[^r1]: 04_service_definitions/production/bkf_get.yaml, errors
[^r2]: 04_service_definitions/production/bkf_post.yaml, errors
[^r4]: 04_service_definitions/production/bkf_reverse.yaml, errors
[^r3]: 04_service_definitions/production/bkf_post.yaml, errors
