---
title: "ERR-SHF-0001 Invalid period definition / shift parameters"
type: "error"
slug: "err-shf-0001"
summary: "Ledgerline error raised when shift parameters, timing logic, or shift codes are invalid on PRD-SHF-11."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-SHF-0001 |
| module | PRD |
| service | shf_save |
| screen | PRD-SHF-11 |
| severity | Error |
| status | current |

Error ERR-SHF-0001 indicates that shift parameters submitted in Ledgerline failed validation rules due to an invalid shift code or inconsistent start and end times [^r1]. It is triggered during shift record creation or updates, preventing malformed schedules from being committed to the database [^r1][^r2]. Users must provide valid shift parameters before schedule changes can take effect [^r2].

## Meaning

The error signifies an invalid period definition or shift parameter set on the shift configuration record [^r1].

## Cause

The error occurs when validation rules detect a malformed shift code (`SHF CD`), missing time values, or an `END` time that precedes the `START` time [^r1].

## How to fix

When ERR-SHF-0001 occurs, the database rejects the submission and no schedule changes are committed [^r2]. The user must correct the `SHF CD`, `START`, or `END` values on screen [[screen-prd-shf-11|PRD-SHF-11]] before re-saving the record [^r1][^r2].

## Raised by

The error is returned by service `shf_save` (see [[services-prd-shf]]) on screen [[screen-prd-shf-11|PRD-SHF-11]] [^r1]. The screen and its associated validation rules are documented in [[man-prd-72|MAN-PRD-72]] [^r1].

## See also

* [[screen-prd-shf-11|PRD-SHF-11 Shift]]
* [[services-prd-shf|PRD shf services]]
* [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 53, Messages
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 54, Messages
