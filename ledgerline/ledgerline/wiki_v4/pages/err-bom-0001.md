---
title: "ERR-BOM-0001 Parent assembly not found on bill of materials master"
type: "error"
slug: "err-bom-0001"
summary: "Production error raised when a parent assembly or work order item lacks an active bill of materials master record."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-BOM-0001 |
| Module | PRD |
| Type | Error |
| Owner | Production |
| Source manual | MAN-PRD-72 |
| Status | current |

Error ERR-BOM-0001 indicates that a requested parent assembly does not exist in the bill of materials master records during retrieval or order processing [^r1]. It occurs primarily when calling BOM query routines or saving a work order against an item without an active structure [^r1][^r2]. Resolving the condition requires confirming the item code against the master file or finding valid engineering structures [^r3].

| Field | Value |
|---|---|
| Error code | ERR-BOM-0001 |
| Module | PRD |
| Severity | Error |
| Documentation | [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]] |

## Meaning
The error indicates that the parent assembly entered in `PARENT` cannot be found on the bill of materials master file [^r1]. During work order entry on screen [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]], it reports that the entered `ITEM CD` lacks an active, signed-off bill of materials in the engineering register [^r2].

## Cause
The condition is triggered when running `bom_get` against an unlisted parent identifier, or when attempting to save an order without an active BOM [^r1]. It also occurs during execution of `wo_save` if the specified item code has no approved, active bill of materials registered in the system [^r2].

## How to fix
Verify the parent item code against the item master file to ensure it is entered correctly [^r3]. Use `bom_search` to locate existing valid structures in the master [^r3].

## Raised by
* `bom_get` service in [[services-prd-bom|PRD bom services]] [^r1]
* `wo_save` service in [[services-prd-wo|PRD wo services]] [^r2]
* Saving an order without an active BOM on [[screen-prd-bom-02|PRD-BOM-02 Bill Of Materials]] or work order processing [^r1]

## See also
* [[screen-prd-bom-02|PRD-BOM-02 Bill Of Materials]]
* [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]
* [[services-prd-bom|PRD bom services]]
* [[services-prd-wo|PRD wo services]]
* [[err-bom-0120|ERR-BOM-0120 Circular or recursive bill of materials structure detected]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 9, Messages
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 7, Questions users ask
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 9, Messages
