---
title: "ERR-WHS Error Codes Reference"
type: "error-list"
slug: "errors-whs"
summary: "Reference list of ERR-WHS warehouse error codes raised by Ledgerline inventory services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/inventory/whs_get.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-WHS |
| Domain | Inventory / Warehouse |
| Module | INV |
| Status | Current |

This catalogue lists the system error codes with prefix ERR-WHS returned by Ledgerline warehouse services. It identifies the standard message text and the invoking service for warehouse operational failures. Personnel troubleshooting warehouse lookups should verify the code against the registered service definitions.

### ERR-WHS-0001
* **Message:** WAREHOUSE MASTER NOT FOUND [^r1]
* **Cause:** The requested warehouse master record cannot be found [^r1].
* **Remedy:** Refer to [[err-whs-0001|ERR-WHS-0001 Warehouse validation failure]] for resolution steps and check record existence in [[screen-inv-whs-01|INV-WHS-01 Warehouse Master]].
* **Raised by:** [[services-inv-whs|whs_get]] [^r1]

## See also
* [[err-whs-0001|ERR-WHS-0001 Warehouse validation failure]]
* [[screen-inv-whs-01|INV-WHS-01 Warehouse Master]]
* [[services-inv-whs|INV whs services]]

## References

[^r1]: 04_service_definitions/inventory/whs_get.yaml, errors
