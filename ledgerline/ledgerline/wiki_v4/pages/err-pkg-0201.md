---
title: "ERR-PKG-0201 Packaging posting failure"
type: "error"
slug: "err-pkg-0201"
summary: "Ledgerline error ERR-PKG-0201 indicates a posting failure during pkg_post execution when a packaging record is not saved, is locked, or has invalid status."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-PKG-0201 |
| module | INV |
| severity | Error |
| raised_by | pkg_post |
| manual | MAN-INV-72 |
| status | Current |

ERR-PKG-0201 is an error code in Ledgerline ERP 7.2 raised when attempting to post returnable packaging transactions [^r1]. It indicates that the execution of the posting service has failed because the transaction record was either not saved beforehand, is locked by another terminal, or possesses an invalid internal status [^r1]. Operators encountering this error must ensure that the record is cleanly saved before attempting to post again [^r2].

## Meaning
ERR-PKG-0201 signals a packaging posting failure encountered during the execution of `pkg_post` [^r1].

## Cause
The error occurs when `pkg_post` executes against a record that was not saved first, is currently locked by another terminal session, or maintains an invalid internal status [^r1].

## How to fix
To resolve ERR-PKG-0201, ensure the record is saved via `pkg_save` without any errors before clicking `pkg_post` [^r2].

## Raised by
This error is raised by the `pkg_post` service, documented in [[man-inv-72|MAN-INV-72]] [^r1].

## See also
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]
* [[screen-inv-pkg-15|INV-PKG-15 Returnable Packaging Entry]]
* [[services-inv-pkg|INV pkg services]]
* [[errors-inv|Errors INV (ERR-INV-*)]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 59, Messages
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 59, Messages
