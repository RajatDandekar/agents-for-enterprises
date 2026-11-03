---
title: "ERR-BOM Error Code Reference"
type: "error-list"
slug: "errors-bom"
summary: "Reference catalogue of ERR-BOM error codes raised by Ledgerline production bill of materials and work order release services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/production/bom_copy.yaml", "04_service_definitions/production/bom_explode.yaml", "04_service_definitions/production/bom_get.yaml", "04_service_definitions/production/bom_save.yaml", "04_service_definitions/production/bom_search.yaml", "04_service_definitions/production/bom_where_used.yaml", "04_service_definitions/production/wo_release.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code prefix | ERR-BOM |
| module | Production (PRD) |
| type | error-list |
| status | current |

This page catalogues the `ERR-BOM` error codes raised by Ledgerline production service definitions as of 26 October 2026. These validation errors occur during bill of materials maintenance, structure lookups, and work order processing across [[services-prd-bom]] and [[services-prd-wo]]. Each entry lists the message text, triggering conditions, and calling services defined in the system interfaces.

### ERR-BOM-0001

* **Message:** BILL OF MATERIALS NOT FOUND [^r1][^r3][^r4][^r8] / NO ACTIVE BOM [^r9]
* **Cause:** The requested bill of materials record does not exist or has no active version for the specified assembly item [^r1][^r3][^r4][^r8][^r9].
* **Remedy:** Verify that the parent assembly has a valid, active bill of materials configured in [[screen-prd-bom-02|PRD-BOM-02]] before querying or releasing the work order [^r1][^r9].
* **Raised by:** `bom_copy` [^r1], `bom_explode` [^r3], `bom_get` [^r4], `bom_where_used` [^r8], and `wo_release` [^r9].
* **Detailed page:** [[err-bom-0001]]

### ERR-BOM-0120

* **Message:** CIRCULAR BOM REFERENCE [^r6]
* **Cause:** A component line establishes a circular or recursive loop within the bill of materials hierarchy [^r6].
* **Remedy:** Restructure the parent-component hierarchy to remove recursive assembly references prior to saving [^r6].
* **Raised by:** `bom_save` [^r6].
* **Detailed page:** [[err-bom-0120]]

### ERR-BOM-0201

* **Message:** QTY MUST BE > 0 [^r2][^r5][^r7]
* **Cause:** A bill of materials operation or line save attempted to record a component quantity less than or equal to zero [^r5].
* **Remedy:** Ensure all component line quantities are strictly greater than zero before submitting changes [^r2][^r5][^r7].
* **Raised by:** `bom_copy` [^r2], `bom_save` [^r5], and `bom_search` [^r7].
* **Detailed page:** [[err-bom-0201]]

## Versions and conflicts

* **ERR-BOM-0001 message wording (`contradiction`):** In BOM query and copy definitions (`bom_copy`, `bom_explode`, `bom_get`, and `bom_where_used`), code `ERR-BOM-0001` returns the message `BILL OF MATERIALS NOT FOUND` [^r1][^r3][^r4][^r8]. In `wo_release`, the same code `ERR-BOM-0001` returns the message `NO ACTIVE BOM` when no active bill of materials exists for the item on the work order [^r9].

## See also

* [[err-bom-0001|ERR-BOM-0001 Parent assembly not found on bill of materials master]]
* [[err-bom-0120|ERR-BOM-0120 Circular or recursive bill of materials structure detected]]
* [[err-bom-0201|ERR-BOM-0201 Component line missing or invalid data]]
* [[screen-prd-bom-02|PRD-BOM-02 Bill Of Materials]]
* [[services-prd-bom|PRD bom services]]
* [[services-prd-wo|PRD wo services]]
* [[errors-wo|ERR-WO error codes]]
* [[errors-itm|ERR-ITM error codes]]
* [[sop-prd-001|SOP-PRD-001 Work Order Release and Backflush]]

## References

[^r1]: 04_service_definitions/production/bom_copy.yaml, errors
[^r3]: 04_service_definitions/production/bom_explode.yaml, errors
[^r4]: 04_service_definitions/production/bom_get.yaml, errors
[^r8]: 04_service_definitions/production/bom_where_used.yaml, errors
[^r9]: 04_service_definitions/production/wo_release.yaml, errors
[^r6]: 04_service_definitions/production/bom_save.yaml, errors
[^r2]: 04_service_definitions/production/bom_copy.yaml, errors
[^r5]: 04_service_definitions/production/bom_save.yaml, errors
[^r7]: 04_service_definitions/production/bom_search.yaml, errors
