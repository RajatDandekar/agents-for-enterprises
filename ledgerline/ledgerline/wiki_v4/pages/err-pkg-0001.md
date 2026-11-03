---
title: "ERR-PKG-0001 Packaging information missing or unrecognised"
type: "error"
slug: "err-pkg-0001"
summary: "Ledgerline error when packaging type is blank or invalid, or quantity is zero or outside entry rules."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-PKG-0001 |
| module | Inventory (INV) |
| severity | Error |
| manual | MAN-INV-72 |
| status | current |

ERR-PKG-0001 is a Ledgerline inventory error generated when packaging details on a record fail validation [^r1]. It indicates that the packaging type is blank or unrecognised, or that the specified quantity violates acceptable entry parameters [^r1]. Resolving it requires aligning the packaging classification with system master data and ensuring the entered quantity is valid before saving [^r2].

## Meaning
ERR-PKG-0001 indicates that PKG TYPE is blank or invalid, or QTY is zero or outside acceptable entry rules [^r1].

## Cause
The error is triggered when the transaction specifies a packaging type that does not exist in master data, leaves the packaging type field blank, or enters a quantity of zero or an amount exceeding allowed boundaries [^r1].

## How to fix
To resolve ERR-PKG-0001, review the packaging classification against master data and verify the entered quantity before saving [^r2].

## Raised by
The message is defined in [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]] under packaging message handling [^r1]. It is associated with packaging tracking in Ledgerline, including [[screen-inv-pkg-15|INV-PKG-15 Returnable Packaging Entry]] and [[services-inv-pkg|INV pkg services]].

## See also
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]
* [[screen-inv-pkg-15|INV-PKG-15 Returnable Packaging Entry]]
* [[services-inv-pkg|INV pkg services]]
* [[errors-inv|Errors INV (ERR-INV-*)]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 58, Messages
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 58, Messages
