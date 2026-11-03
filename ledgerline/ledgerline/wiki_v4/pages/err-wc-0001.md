---
title: "ERR-WC-0001 Work Centre Processing Failure"
type: "error"
slug: "err-wc-0001"
summary: "Ledgerline error code indicating a failure to store or retrieve a work centre record during work centre maintenance operations."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-WC-0001 |
| Module | Production (PRD) |
| Service | wc_save |
| Status | Current |

ERR-WC-0001 is a Ledgerline production module error indicating that the system cannot store or retrieve a work centre record [^r1]. It arises when maintaining work centres via [[screen-prd-wc-10|PRD-WC-10 Work Centre]] and executing work centre persistence operations [^r1][^r2]. Resolving the error requires validating mandatory fields and field limits before attempting to save the record again [^r2].

## Meaning
Message ERR-WC-0001 indicates that the system is unable to store or retrieve the work centre record [^r1].

## Cause
This error is commonly caused by missing mandatory fields, code integrity violations, or duplicate records [^r1].

## How to fix
To resolve the error, ensure that `WC CD` is not empty and valid, `NAME` is populated, and `HRS/DAY` is within acceptable limits before retrying the action [^r2].

## Raised by
The error is raised by the `wc_save` service within [[services-prd-wc|PRD wc services]], documented in [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]] [^r1][^r2].

## See also
* [[screen-prd-wc-10|PRD-WC-10 Work Centre]]
* [[services-prd-wc|PRD wc services]]
* [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 50, Messages
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 50, Messages
