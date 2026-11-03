---
title: "ERR-COM-0001 Period Not Open or Already Posted"
type: "error"
slug: "err-com-0001"
summary: "Ledgerline error raised during com_run when PERIOD is not open for commission processing or is already posted and locked."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-COM-0001 |
| Message | Period Not Open or Already Posted |
| Module | Sales (SAL) |
| Raised by | com_run |
| Screen | SAL-COM-15 |
| Manual | MAN-SAL-72 |
| Status | current |

Error ERR-COM-0001 prevents sales commission calculation when running the commission calculation service in [[screen-sal-com-15|SAL-COM-15 Sales Commission]]. It indicates that the period entered either does not correspond to an active open cycle or has already been posted and locked by finance. Users must ensure the period is open or correct the entered identifier before re-attempting the run.

| Field | Value |
|---|---|
| Error code | ERR-COM-0001 |
| Message | Period Not Open or Already Posted |
| Module | Sales (SAL) |
| Service | com_run |
| Screen | [[screen-sal-com-15|SAL-COM-15 Sales Commission]] |
| Reference manual | [[man-sal-72|MAN-SAL-72]] |

## Meaning

The error signals that the value specified in the `PERIOD` field cannot be processed for commissions because it does not represent an open cycle or refers to a closed accounting period.[^r1]

## Cause

The error is raised when clicking `com_run` if the value entered in `PERIOD` does not match an open commission cycle, or represents an accounting period that has already been posted and locked.[^r1]

## How to fix

To resolve the error, verify with the accounts department that the target period has been opened for commission processing.[^r2] Alternatively, clear the `PERIOD` field, re-enter the correct identifier, and re-run `com_run`.[^r2]

## Raised by

This error is triggered by the `com_run` service within [[services-sal-com|SAL com services]] from [[screen-sal-com-15|SAL-COM-15 Sales Commission]]. [^r1]

## See also

* [[man-sal-72|MAN-SAL-72 Ledgerline ERP 7.2 User Manual: Sales]]
* [[screen-sal-com-15|SAL-COM-15 Sales Commission]]
* [[services-sal-com|SAL com services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 62, Questions users ask
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 62, Questions users ask
