---
title: "ERR-LOT Error Codes"
type: "error-list"
slug: "errors-lot"
summary: "Reference list of ERR-LOT error codes raised across Ledgerline inventory lot services including lot_get, lot_hold, lot_release, and lot_trace."
audience: "staff"
status: "current"
sources: ["04_service_definitions/inventory/lot_get.yaml", "04_service_definitions/inventory/lot_hold.yaml", "04_service_definitions/inventory/lot_release.yaml", "04_service_definitions/inventory/lot_trace.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-LOT |
| Module | Inventory |
| Owner | Inventory Control |
| Status | current |

Catalogue of ERR-LOT error codes generated across Ledgerline lot management operations as of 26 October 2026. These errors are returned by core inventory services handling lot retrieval, tracking, holds, and releases. Each entry defines the specific message text and the inventory services that raise the code.

### ERR-LOT-0001: LOT / SERIAL NOT FOUND
* **Message:** `LOT / SERIAL NOT FOUND` [^r1][^r2][^r4][^r6]
* **Cause:** The requested lot or serial identifier does not exist in the system [^r1].
* **Remedy:** Verify the lot or serial identifier entered and ensure it exists before re-invoking the transaction [^r1].
* **Raised by:** Service `lot_get` [^r1], service `lot_hold` [^r2], service `lot_release` [^r4], and service `lot_trace` [^r6].
* **Error page:** [[err-lot-0001|ERR-LOT-0001 Duplicate lot or serial identifier]]

### ERR-LOT-0007: LOT / SERIAL NOT IN DRAFT (<status>)
* **Message:** `LOT / SERIAL NOT IN DRAFT (<status>)` [^r5]
* **Cause:** The `lot_release` service was executed against a lot or serial record that is not currently in draft status [^r5].
* **Remedy:** Check the current lifecycle status of the lot or serial before attempting release [^r5].
* **Raised by:** Service `lot_release` [^r5].
* **Error page:** [[err-lot-0007|ERR-LOT-0007 Lot or serial number not found]]

### ERR-LOT-0301: LOT ALREADY ON HOLD
* **Message:** `LOT ALREADY ON HOLD` [^r3]
* **Cause:** An attempt was made via `lot_hold` to place a hold on a lot that is already under an active hold [^r3].
* **Remedy:** Check the existing hold status before applying a new hold on the lot [^r3].
* **Raised by:** Service `lot_hold` [^r3].
* **Error page:** [[err-lot-0301|ERR-LOT-0301 Lot locked or invalid status transition]]

## See also
* [[services-inv-lot|INV lot services]]
* [[screen-inv-lot-10|INV-LOT-10 Lot / Serial Entry]]
* [[err-lot-0001|ERR-LOT-0001 Duplicate lot or serial identifier]]
* [[err-lot-0007|ERR-LOT-0007 Lot or serial number not found]]
* [[err-lot-0301|ERR-LOT-0301 Lot locked or invalid status transition]]

## References

[^r1]: 04_service_definitions/inventory/lot_get.yaml, errors
[^r2]: 04_service_definitions/inventory/lot_hold.yaml, errors
[^r4]: 04_service_definitions/inventory/lot_release.yaml, errors
[^r6]: 04_service_definitions/inventory/lot_trace.yaml, errors
[^r5]: 04_service_definitions/inventory/lot_release.yaml, errors
[^r3]: 04_service_definitions/inventory/lot_hold.yaml, errors
