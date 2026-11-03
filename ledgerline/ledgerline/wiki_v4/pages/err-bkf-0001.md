---
title: "ERR-BKF-0001: Works order invalid or not in valid state for backflush"
type: "error"
slug: "err-bkf-0001"
summary: "Ledgerline ERP error indicating an invalid, unreleased, closed, or held works order, or missing mandatory serial numbers during backflush."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-BKF-0001 |
| Module | PRD (Production) |
| Screen | PRD-BKF-08 Backflush |
| Associated service | services-prd-bkf |
| Status | Current |

ERR-BKF-0001 is a Ledgerline ERP 7.2 production execution error encountered on [[screen-prd-bkf-08|PRD-BKF-08 Backflush]] when an entered works order cannot be processed for material consumption and completion[^r1]. It signals that the target works order is nonexistent, not in an active released state, or missing prerequisite component registrations[^r1][^r2]. Resolving the error requires checking the order's status on [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]] and verifying that mandatory serial numbers are recorded[^r1][^r2].

## Meaning

ERR-BKF-0001 indicates that Ledgerline ERP 7.2 cannot locate the works order specified in WO NO, or that the works order is unreleased, closed, or on hold[^r1].

## Cause

The error occurs when a user enters a works order number that does not exist in the database, or references a works order that currently has an invalid lifecycle status such as unreleased, closed, or on hold[^r1]. Additionally, the error is displayed if mandatory battery or motor serial numbers have not yet been registered against the works order prior to backflushing[^r2].

## How to fix

* Verify the works order number entered in the WO NO field on [[screen-prd-bkf-08|PRD-BKF-08 Backflush]][^r1].
* Open [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]] to check that the works order exists and is in a released status, ensuring it is neither on hold nor already closed[^r1].
* If processing assemblies requiring traceability, confirm that all mandatory battery and motor serial numbers have been fully registered against the works order before reattempting backflush execution[^r2].

## Raised by

* Screen: [[screen-prd-bkf-08|PRD-BKF-08 Backflush]][^r1]
* Production backflush services under [[services-prd-bkf|PRD bkf services]][^r1]
* Documented in [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]][^r1][^r2]

## See also

* [[screen-prd-bkf-08|PRD-BKF-08 Backflush]]
* [[services-prd-bkf|PRD bkf services]]
* [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]
* [[services-prd-wo|PRD wo services]]
* [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]]
* [[errors-wo|ERR-WO error codes]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 17, Messages
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 18, Questions users ask
