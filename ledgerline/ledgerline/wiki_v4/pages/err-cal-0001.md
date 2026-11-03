---
title: "ERR-CAL-0001 Calibration Tool Not Found"
type: "error"
slug: "err-cal-0001"
summary: "Validation error raised when a keyed gauge number does not match an active tool record in the database."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error Code | ERR-CAL-0001 |
| Message | Calibration Tool Not Found |
| Module | Calibration / Production |
| Field | GAUGE NO |
| Severity | Error |
| Source Document | MAN-PRD-72 |

`ERR-CAL-0001` is a Ledgerline calibration validation error indicating that an entered gauge reference cannot be identified. It prevents the progression of calibration transactions against missing or unregistered equipment. To proceed, users must verify the entry format or register the asset shell in the system.

## Meaning
The system cannot locate an active tool record corresponding to the value supplied in the gauge reference field [^r1].

## Cause
This error is raised when the reference keyed into `GAUGE NO` does not match any active tool record in the database [^r1]. This commonly occurs due to typographical mistakes, misplaced spaces, character transpositions, or attempts to reference newly acquired gauges that have not yet been set up [^r2].

## How to fix
Users must check the tool reference for spaces or transposition errors [^r2]. If the gauge is newly acquired, have the quality supervisor create the asset shell before re-entering the reference [^r2].

## Raised by
The error is raised by the gauge number validation routines documented in [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]], associated with calibration processing such as [[screen-qa-cal-04|QA-CAL-04 Calibration Entry]] and [[services-prd-cal|PRD cal services]] [^r1].

## See also
* [[screen-qa-cal-04|QA-CAL-04 Calibration Entry]]
* [[services-prd-cal|PRD cal services]]
* [[screen-prd-tol-14|PRD-TOL-14 Tool Master]]
* [[services-prd-tool|PRD tool services]]
* [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 48, Questions users ask
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 48, Questions users ask
