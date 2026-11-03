---
title: "ERR-BKF-0007: Component inventory shortage during backflush"
type: "error"
slug: "err-bkf-0007"
summary: "Ledgerline error code indicating a bill of materials component inventory shortage at the line warehouse during backflush posting."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-BKF-0007 |
| Module | Production (PRD) |
| Service | bkf_post (BACKFLUSH POST) |
| Severity | Error |
| Screen | PRD-BKF-08 Backflush |

ERR-BKF-0007 is a Ledgerline production error raised when processing a backflush transaction without sufficient component stock. It signals that one or more bill of materials items required for the assembly are depleted at the assigned line warehouse location. Resolving the error requires replenishing lineside inventory balances through internal store transfers prior to re-posting the backflush.

| Field | Value |
|---|---|
| Error code | ERR-BKF-0007 |
| Module | Production (PRD) |
| Raised by | BACKFLUSH POST (`bkf_post`) |
| Relevant screen | [[screen-prd-bkf-08|PRD-BKF-08 Backflush]] |

## Meaning
ERR-BKF-0007 indicates that Ledgerline encountered an inventory shortage for one or more bill of materials components at the designated line warehouse during execution of the backflush transaction.[^r1]

## Cause
The error occurs when the BACKFLUSH POST service attempts to deduct component quantities required by the assembly's bill of materials, but the recorded stock balance at the line warehouse is less than the required quantity.[^r1]

## How to fix
To resolve ERR-BKF-0007, lineside inventory balances must be reviewed and internal store transfers processed to reconcile physical stock with system balances.[^r2] Once inventory is adjusted and available at the line warehouse, re-attempt the `bkf_post` transaction.[^r2]

## Raised by
The message is raised by the BACKFLUSH POST service within Ledgerline ERP.[^r1]

## See also
* [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]]
* [[screen-prd-bkf-08|PRD-BKF-08 Backflush]]
* [[services-prd-bkf|PRD bkf services]]
* [[screen-prd-bom-02|PRD-BOM-02 Bill Of Materials]]
* [[services-prd-bom|PRD bom services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 17, Messages
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 17, Messages
