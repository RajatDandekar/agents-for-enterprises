---
title: "ERR-SCR Scrap Error Codes"
type: "error-list"
slug: "errors-scr"
summary: "Reference catalogue of ERR-SCR scrap note error codes raised by Ledgerline inventory scrap services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/inventory/scr_approve.yaml", "04_service_definitions/inventory/scr_get.yaml", "04_service_definitions/inventory/scr_post.yaml", "04_service_definitions/inventory/scr_save.yaml", "04_service_definitions/inventory/scr_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-SCR |
| Module | Inventory |
| Owner | Inventory Control |
| Type | System error codes |
| Status | current |

Error codes prefixed with `ERR-SCR` are returned by Ledgerline inventory scrap transaction services during scrap note entry, retrieval, approval, posting, and searching. These codes enforce data integrity rules across scrap handling, ensuring scrap records exist, remain in valid workflow statuses, and specify non-zero item quantities. Understanding these errors helps operators resolve transaction rejections when recording physical inventory write-offs.

### ERR-SCR-0001
* **Message**: `SCRAP NOTE NOT FOUND` [^r1][^r3][^r4]
* **Cause**: A referenced scrap note number does not exist in the system [^r1].
* **Remedy**: Verify the scrap note identifier entered and confirm the record has been created before requesting or updating it.
* **Raised by**: `scr_approve` [^r1], `scr_get` [^r3], and `scr_post` [^r4].

### ERR-SCR-0007
* **Message**: `SCRAP NOTE NOT IN DRAFT (<status>)` [^r2][^r5]
* **Cause**: An operation requiring a draft record, such as approval or posting, was attempted on a scrap note that is currently in a non-draft status [^r2][^r5].
* **Remedy**: Review the current workflow status of the scrap note and ensure it is in draft before resubmitting.
* **Raised by**: `scr_approve` [^r2] and `scr_post` [^r5].

### ERR-SCR-0201
* **Message**: `QTY MUST BE > 0` [^r6][^r7]
* **Cause**: A scrap note operation specifies a scrap quantity that is zero or negative [^r6][^r7].
* **Remedy**: Enter a positive scrap quantity greater than zero on the line item.
* **Raised by**: `scr_save` [^r6] and `scr_search` [^r7].

## See also
* [[screen-inv-scr-16|INV-SCR-16 Scrap Note Entry]]
* [[services-inv-scr|INV scr services]]
* [[errors-itm|ERR-ITM error codes]]
* [[errors-apr|Errors APR]]

## References

[^r1]: 04_service_definitions/inventory/scr_approve.yaml, errors
[^r3]: 04_service_definitions/inventory/scr_get.yaml, errors
[^r4]: 04_service_definitions/inventory/scr_post.yaml, errors
[^r2]: 04_service_definitions/inventory/scr_approve.yaml, errors
[^r5]: 04_service_definitions/inventory/scr_post.yaml, errors
[^r6]: 04_service_definitions/inventory/scr_save.yaml, errors
[^r7]: 04_service_definitions/inventory/scr_search.yaml, errors
