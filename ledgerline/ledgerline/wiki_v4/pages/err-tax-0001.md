---
title: "ERR-TAX-0001 TAX CODE MASTER NOT FOUND"
type: "error"
slug: "err-tax-0001"
summary: "Error raised when tax details fail validation or the tax code cannot be processed by the server service."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-TAX-0001 |
| module | AP |
| severity | Error |
| source | MAN-AP-72 |
| status | current |

ERR-TAX-0001 is an Accounts Payable error indicating that a database operation could not be completed during tax code processing [^r1]. It occurs when entered tax details fail basic validation checks or when the tax code cannot be processed by the underlying server service [^r1]. Correcting field formatting and values in the tax record resolves the condition [^r2].

## Meaning
The system was unable to complete the database operation because entered tax details failed basic validation or the tax code could not be processed by the server service [^r1].

## Cause
This error is triggered when tax record fields contain invalid formatting or missing data, preventing successful processing by the server service during database operations [^r1][^r2].

## How to fix
Users must check that TAX CD lacks extra spaces or illegal punctuation [^r2]. In addition, verify that DESCR has text, ensure RATE holds a valid calculation entry, and verify that INTRA/INTER conforms to standard usage [^r2].

## Raised by
The error is raised by the server service during tax processing operations, documented in [[man-ap-72|MAN-AP-72]] [^r1].

## See also
* [[screen-ap-tax-17|AP-TAX-17 Tax Code Master]]
* [[services-ap-tax|AP tax services]]
* [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 64, ERR-TAX-0001
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 64, ERR-TAX-0001
