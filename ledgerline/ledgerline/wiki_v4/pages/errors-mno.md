---
title: "ERR-MNO-* Message and Error Codes"
type: "error-list"
slug: "errors-mno"
summary: "Catalogue of Ledgerline ERR-MNO maintenance order error codes, including not found and invalid closure status messages."
audience: "staff"
status: "current"
sources: ["04_service_definitions/production/mnt_close.yaml", "04_service_definitions/production/mnt_get.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-MNO |
| Module | PRD (Production / Maintenance) |
| Object | Maintenance Order |
| Status | Current |

Error codes prefixed with `ERR-MNO` are raised by Ledgerline maintenance order services in the production module. They signal invalid record retrieval or improper status transitions when processing maintenance orders. As of 26 October 2026, these definitions govern failure responses for maintenance service execution across screens such as [[screen-prd-mnt-07|PRD-MNT-07 Maintenance Order Entry]].

### ERR-MNO-0001

* **Message:** MAINTENANCE ORDER NOT FOUND [^r1][^r3]
* **Cause:** The requested maintenance order cannot be located during operation processing or retrieval [^r1][^r3].
* **Remedy:** Verify the maintenance order number and confirm that the record exists prior to executing operations.
* **Raised by:** [[services-prd-mnt|mnt_close]] [^r1], [[services-prd-mnt|mnt_get]] [^r3]

### ERR-MNO-0801

* **Message:** MAINTENANCE ORDER CLOSED (<status>) [^r2]
* **Cause:** Service `mnt_close` was called against a maintenance order that holds an invalid status [^r2].
* **Remedy:** Confirm the current lifecycle status of the maintenance order before attempting closure.
* **Raised by:** [[services-prd-mnt|mnt_close]] [^r2]

## See also

* [[screen-prd-mnt-07|PRD-MNT-07 Maintenance Order Entry]]
* [[services-prd-mnt|PRD mnt services]]

## References

[^r1]: 04_service_definitions/production/mnt_close.yaml, errors
[^r3]: 04_service_definitions/production/mnt_get.yaml, errors
[^r2]: 04_service_definitions/production/mnt_close.yaml, errors
