---
title: "ERR-BOM-0120 Circular or recursive bill of materials structure detected"
type: "error"
slug: "err-bom-0120"
summary: "Ledgerline error ERR-BOM-0120 halts processing when a circular or recursive bill of materials structure is detected."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | ERR-BOM-0120 |
| Type | Error |
| Module | PRD |
| Severity | Fatal / Transaction Halt |
| Raised by | bom_save, explosion processing |
| Manual | MAN-PRD-72 |

Error ERR-BOM-0120 is a validation error raised by [[man-prd-72|MAN-PRD-72]] when Ledgerline detects a circular or recursive structure in a bill of materials [^r1]. It halts the transaction immediately to prevent infinite loops during structure explosion or save operations [^r1][^r2]. As of 26 October 2026, engineering and production teams must resolve recursive parent-child references before saving or exploding affected assemblies [^r1][^r2].

## Meaning
The message indicates that a recursive or circular structure has been detected during `bom_save` or explosion processing [^r1].

## Cause
Ledgerline halts transactions with ERR-BOM-0120 when a parent item is entered as a component of itself, or where an intermediate sub-assembly contains a higher-level assembly in its hierarchy [^r2].

## How to fix
Remove the self-referencing component from the bill of materials, or reconfigure the intermediate sub-assembly hierarchy so that no child component references an ancestor assembly [^r2]. Once the circular reference is removed, retry the operation in [[screen-prd-bom-02|PRD-BOM-02 Bill Of Materials]] or through [[services-prd-bom|PRD bom services]] [^r1][^r2].

## Raised by
Raised by `bom_save` or bill of materials explosion processing routines [^r1].

## See also
* [[screen-prd-bom-02|PRD-BOM-02 Bill Of Materials]]
* [[services-prd-bom|PRD bom services]]
* [[err-bom-0001|ERR-BOM-0001 Parent assembly not found on bill of materials master]]
* [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 10, Messages
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 10, Messages
