---
title: "ERR-RTG-0001 Routing Save Failed"
type: "error"
slug: "err-rtg-0001"
summary: "Ledgerline error raised when ROUTING SAVE cannot commit a routing record due to duplicate operation numbers, missing work centres, or invalid standard minutes."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | ERR-RTG-0001 |
| Module | PRD |
| Raised by | ROUTING SAVE |
| Severity | Error |
| Source | MAN-PRD-72 |
| Status | current |

ERR-RTG-0001 is a Ledgerline production error encountered during routing maintenance on screen [[screen-prd-rtg-03|PRD-RTG-03 Routing]]. It prevents the system from committing a routing definition when basic operation constraints or timing allowances are violated [^r1]. Resolving it requires correcting operation sequencing, assigning an existing work centre, or specifying a valid standard minute allowance before retrying the save [^r1].

| Field | Value |
|---|---|
| Error code | ERR-RTG-0001 |
| Message | Routing Save Failed |
| Module | PRD |
| Service / Action | ROUTING SAVE |
| Screen | [[screen-prd-rtg-03|PRD-RTG-03]] |

## Meaning
The system cannot commit the routing record to the database because the entry fails validation rules governing operation identifiers, work centre assignments, or standard minute allowances [^r1].

## Cause
The error occurs when saving a routing with one or more of the following data integrity issues [^r1]:
* A duplicate `OP NO` exists under active status [^r1].
* A required `WORK CENTRE` is missing from an operation line [^r1].
* The `STD MIN` allowance contains an invalid value [^r1].

## How to fix
1. Verify the operation sequence numbers on the routing and ensure that each active operation possesses a unique `OP NO` [^r1].
2. Ensure every operation line specifies a valid, active [[screen-prd-wc-10|work centre]] [^r1].
3. Check the `STD MIN` field and supply a valid positive numeric value for the standard minute allowance [^r1].
4. Re-execute the routing save action [^r1].

## Raised by
Raised by the `ROUTING SAVE` operation within [[services-prd-rtg|PRD rtg services]] documented in [[man-prd-72|MAN-PRD-72]] [^r1].

## See also
* [[screen-prd-rtg-03|PRD-RTG-03 Routing]]
* [[services-prd-rtg|PRD rtg services]]
* [[screen-prd-wc-10|PRD-WC-10 Work Centre]]
* [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]]
* [[err-bom-0001|ERR-BOM-0001 Parent assembly not found on bill of materials master]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 14, Messages
