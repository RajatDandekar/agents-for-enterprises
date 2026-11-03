---
title: "ERR-CSG-0001 CONSIGNMENT STOCK NOT FOUND"
type: "error"
slug: "err-csg-0001"
summary: "Ledgerline error ERR-CSG-0001 CONSIGNMENT STOCK NOT FOUND raised when consignment records are missing or parameters are inconsistent during save or settlement."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | ERR-CSG-0001 |
| Message | CONSIGNMENT STOCK NOT FOUND |
| Module | Inventory (INV) |
| Severity | Error |
| Services | csg_save, csg_settle |

ERR-CSG-0001 is a Ledgerline inventory validation error with the catalogue message "CONSIGNMENT STOCK NOT FOUND" [^r2]. It halts processing when an operation cannot locate an expected consignment stock record or encounters invalid input data [^r1][^r2]. As of 26 October 2026, operations involving consignment saves or settlements must ensure all required consignment parameters are valid to avoid this failure [^r1].

## Meaning
The message catalogue defines ERR-CSG-0001 as "CONSIGNMENT STOCK NOT FOUND" [^r2]. It represents a general consignment stock validation failure or a missing record condition in the inventory module [^r1][^r2].

## Cause
The error is triggered when mandatory consignment entries are missing or when inconsistent parameters are passed during execution [^r1].

## How to fix
Users must verify that all mandatory consignment fields and parameters are populated accurately and match existing consignment stock records before resubmitting the transaction [^r1].

## Raised by
This error is raised by the consignment services `csg_save` and `csg_settle` in [[services-inv-csg|INV csg services]] [^r1]. These services support transactions initiated from [[screen-inv-csg-17|INV-CSG-17 Consignment Stock Entry]] according to [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]] [^r1].

## See also
* [[screen-inv-csg-17|INV-CSG-17 Consignment Stock Entry]]
* [[services-inv-csg|INV csg services]]
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]
* [[errors-inv|Errors INV (ERR-INV-*)]]

## References

[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 68, §20. Messages
[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 66, Messages
