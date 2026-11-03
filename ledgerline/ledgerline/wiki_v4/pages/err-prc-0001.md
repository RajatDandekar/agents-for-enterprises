---
title: "ERR-PRC-0001 Mandatory parameters absent or pricing conflict"
type: "error"
slug: "err-prc-0001"
summary: "Ledgerline error raised when pricing parameters are missing, unit values fail validation syntax, or price lines contain date conflicts."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-PRC-0001 |
| Module | Sales (SAL) |
| Primary screen | SAL-PRC-08 |
| Related screen | SAL-DSC-10 |
| Services | prc_get, prc_save |
| Status | Current |

ERR-PRC-0001 is a Ledgerline Sales error indicating missing mandatory parameters, invalid value syntax, or date conflicts in pricing records [^r1][^r3]. It is primarily encountered on screen [[screen-sal-prc-08|SAL-PRC-08]] during pricing operations and also occurs under discount processing on [[screen-sal-dsc-10|SAL-DSC-10]] [^r1][^r3]. Resolving the error requires correcting syntax, supplying missing entries, and ensuring date ranges do not conflict [^r2].

## Meaning
The error indicates that mandatory pricing data is missing or that a pricing entry fails ledger validation rules [^r1][^r3]. It signals either an unpopulated required header, syntactically malformed unit numbers, or a duplicate record spanning an identical validity period [^r1][^r3].

## Cause
ERR-PRC-0001 occurs on [[screen-sal-prc-08|SAL-PRC-08]] if PRICE LIST is blank when calling prc_get [^r1]. It also triggers if the unit value in PRICE contains invalid syntax, or if an identical line already exists for the same VALID FROM point [^r1]. Additionally, on [[screen-sal-dsc-10|SAL-DSC-10]], the error is raised when the value entered in the PRICE field fails ledger validation, such as containing invalid figures, prohibited punctuation, or negative values [^r3].

## How to fix
To resolve the error, ensure that all required fields contain valid text [^r2]. Check that effective date periods do not overlap incorrectly [^r2]. Once corrected, re-attempt prc_save [^r2].

## Raised by
The message is raised by the [[services-sal-prc|prc]] service routines, specifically during prc_get calls or when committing updates with prc_save [^r1][^r2]. It is encountered by users operating screens [[screen-sal-prc-08|SAL-PRC-08]] and [[screen-sal-dsc-10|SAL-DSC-10]] [^r1][^r3].

## See also
* [[screen-sal-prc-08|SAL-PRC-08 Price List]]
* [[screen-sal-dsc-10|SAL-DSC-10 Discount]]
* [[services-sal-prc|SAL prc services]]
* [[services-sal-dsc|SAL dsc services]]
* [[man-sal-72|MAN-SAL-72 Ledgerline ERP 7.2 User Manual: Sales]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 35, Messages
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 37, §12. Discount (SAL-DSC-10)
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 35, Messages
