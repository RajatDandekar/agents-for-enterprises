---
title: "ERR-MRN Error Code Reference"
type: "error-list"
slug: "errors-mrn"
summary: "Reference list of ERR-MRN material issue error codes raised by Ledgerline inventory services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/inventory/mrn_cancel.yaml", "04_service_definitions/inventory/mrn_post.yaml", "04_service_definitions/inventory/mrn_save.yaml", "04_service_definitions/inventory/mrn_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-MRN |
| Domain | Inventory (Material Issue) |
| Related services | [[services-inv-mrn|INV mrn services]] |
| Related screen | [[screen-inv-mrn-08|INV-MRN-08 Material Issue Entry]] |
| Status | current |

This catalogue documents the ERR-MRN error codes raised by Ledgerline inventory material issue operations as of 26 October 2026. These validation errors occur during the creation, modification, posting, searching, and cancellation of material issues handled by the [[services-inv-mrn|INV mrn services]] and the [[screen-inv-mrn-08|INV-MRN-08 Material Issue Entry]] screen.

### ERR-MRN-0001

* **Message:** MATERIAL ISSUE NOT FOUND [^r1][^r3]
* **Cause:** The requested material issue record cannot be identified in the database [^r1][^r3].
* **Remedy:** Verify the material issue document reference and retry the operation [^r1][^r3].
* **Raised by:** `mrn_cancel` [^r1], `mrn_post` [^r3]

### ERR-MRN-0007

* **Message:** MATERIAL ISSUE NOT IN DRAFT (<status>) [^r4]
* **Cause:** An attempt is made to post an MRN that is not currently in draft status [^r4].
* **Remedy:** Ensure the material issue document is in draft state before attempting to post it [^r4].
* **Raised by:** `mrn_post` [^r4]

### ERR-MRN-0201

* **Message:** QTY MUST BE > 0 [^r5][^r6]
* **Cause:** An invalid quantity less than or equal to zero was supplied in material issue operations [^r5][^r6].
* **Remedy:** Enter a positive quantity value greater than zero [^r5][^r6].
* **Raised by:** `mrn_save` [^r5], `mrn_search` [^r6]

### ERR-MRN-0801

* **Message:** MATERIAL ISSUE CLOSED (<status>) [^r2]
* **Cause:** A cancellation attempt was made on a material issue that is already closed [^r2].
* **Remedy:** Check the current lifecycle status of the material issue before requesting cancellation [^r2].
* **Raised by:** `mrn_cancel` [^r2]

## See also

* [[screen-inv-mrn-08|INV-MRN-08 Material Issue Entry]]
* [[services-inv-mrn|INV mrn services]]
* [[errors-itm|ERR-ITM error codes]]
* [[user-jfletcher|Joanna Fletcher (JFLETCHER)]]

## References

[^r1]: 04_service_definitions/inventory/mrn_cancel.yaml, errors
[^r3]: 04_service_definitions/inventory/mrn_post.yaml, errors
[^r4]: 04_service_definitions/inventory/mrn_post.yaml, errors
[^r5]: 04_service_definitions/inventory/mrn_save.yaml, errors
[^r6]: 04_service_definitions/inventory/mrn_search.yaml, errors
[^r2]: 04_service_definitions/inventory/mrn_cancel.yaml, errors
