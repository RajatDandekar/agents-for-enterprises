---
title: "ERR-ACR-0001: Accrual execution or reversal failed"
type: "error"
slug: "err-acr-0001"
summary: "Error code raised when Ledgerline GRNI accrual run or reversal execution fails due to locks, closed periods, invalid references, or missing data."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-ACR-0001 |
| module | Accounts Payable |
| raised_by | GRNI ACCRUAL RUN, GRNI ACCRUAL REVERSE |
| screen | AP-ACR-10 |
| manual | MAN-AP-72 |
| status | current |

ERR-ACR-0001 is an Accounts Payable error raised during goods received not invoiced (GRNI) accrual processing in [[man-ap-72|MAN-AP-72]]. It indicates that the system failed to execute a GRNI accrual batch or reverse an existing accrual record. Resolving the error requires checking for record locks, ensuring accounting periods remain open, verifying user posting authority, and confirming all required text inputs are provided.

## Meaning
The error indicates that an accrual generation or reversal action could not be completed by Ledgerline ERP [^r1].

## Cause
The error is triggered when the service GRNI ACCRUAL RUN or GRNI ACCRUAL REVERSE fails because the target record is locked, the accounting period is closed, required fields such as REASON or COMMENT are missing, or the specified ACR NO does not exist [^r1].

## How to fix
To resolve the error, ensure that all required text fields are populated prior to submission [^r2]. Check for concurrent user locks or orphaned database sessions affecting the target records [^r2]. Additionally, verify general ledger posting authority and ensure that previous accrual batches have been reversed [^r2].

## Raised by
* Service `GRNI ACCRUAL RUN` [^r1]
* Service `GRNI ACCRUAL REVERSE` [^r1]

## See also
* [[screen-ap-acr-10|AP-ACR-10 Grni Accrual]]
* [[services-ap-acr|AP acr services]]
* [[screen-ap-per-11|AP-PER-11 Ap Period]]
* [[services-ap-gl|AP gl services]]
* [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 35, Messages
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 35, Messages
