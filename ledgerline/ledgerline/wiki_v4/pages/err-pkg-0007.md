---
title: "ERR-PKG-0007 Invalid or duplicate packaging number"
type: "error"
slug: "err-pkg-0007"
summary: "Ledgerline error when a packaging identifier already exists as an active container for the vendor or violates packaging-type format patterns."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | ERR-PKG-0007 |
| Module | Inventory (INV) |
| Type | Error |
| Screen | [[screen-inv-pkg-15|INV-PKG-15 Returnable Packaging Entry]] |
| Manual | [[man-inv-72|MAN-INV-72]] |
| Status | Current |

`ERR-PKG-0007` is a Ledgerline inventory error encountered during packaging data entry on screens such as [[screen-inv-pkg-15|INV-PKG-15 Returnable Packaging Entry]][^r1]. It indicates that the entered container identifier cannot be accepted because it conflicts with an active record or fails syntax validation[^r1]. Resolving the condition requires verifying physical container markings before re-entering the data[^r2].

| Field | Value |
|---|---|
| Error code | `ERR-PKG-0007` |
| Module | Inventory (INV) |
| System | Ledgerline ERP 7.2 |
| Reference manual | [[man-inv-72|MAN-INV-72]] |

## Meaning
`ERR-PKG-0007` indicates that the packaging number (`PKG NO`) entered either already exists as an active on-site container recorded under the designated vendor, or its format does not comply with the pattern defined for that packaging type (`PKG TYPE`)[^r1].

## Cause
The error is triggered under two conditions[^r1]:
* An on-site container with the same `PKG NO` is currently marked active under the specified vendor[^r1].
* The text entered into `PKG NO` does not match the expected structural pattern configured for the chosen `PKG TYPE`[^r1].

## How to fix
To clear the error, verify the physical label or marking on the container to confirm the accurate identifier and re-enter the correct packaging number into the field[^r2].

## Raised by
The error is raised by the packaging validation services in [[services-inv-pkg|INV pkg services]] and documented in [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]][^r1].

## See also
* [[screen-inv-pkg-15|INV-PKG-15 Returnable Packaging Entry]]
* [[services-inv-pkg|INV pkg services]]
* [[errors-inv|Errors INV (ERR-INV-*)]]
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 59, Messages
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 59, Messages
