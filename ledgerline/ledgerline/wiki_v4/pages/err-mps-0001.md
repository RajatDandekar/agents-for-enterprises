---
title: "ERR-MPS-0001 Missing Mandatory Field or Invalid Format in MPS"
type: "error"
slug: "err-mps-0001"
summary: "Validation error raised by mps_save on PRD-MPS-05 when mandatory schedule fields are blank, invalid, out of calendar, or record-locked."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error Code | ERR-MPS-0001 |
| Message | Missing Mandatory Field or Invalid Format in MPS |
| Module | PRD |
| Raised By | mps_save |
| Screen | PRD-MPS-05 Master Schedule Entry |
| Status | current |

ERR-MPS-0001 is a Ledgerline production validation error raised during master production schedule entry on [[screen-prd-mps-05|PRD-MPS-05 Master Schedule Entry]]. It halts processing when required schedule header or line fields are missing, formatted incorrectly, or reference weeks outside the configured operating calendar.[^r1] As of 26 October 2026, the error also indicates concurrent terminal locks on the target schedule timeframe.[^r2]

| Property | Value |
|---|---|
| Error code | ERR-MPS-0001 |
| Message text | Missing Mandatory Field or Invalid Format in MPS |
| Module | PRD |
| Service | `mps_save` ([[services-prd-mps|PRD mps services]]) |
| Screen | [[screen-prd-mps-05|PRD-MPS-05 Master Schedule Entry]] |
| Reference manual | [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]] |

## Meaning
ERR-MPS-0001 indicates that the master production schedule record failed basic validation checks or could not be updated by the service layer.[^r1][^r2]

## Cause
The error is triggered under any of the following conditions:
* The `ITEM CD`, `WEEK`, or `QTY` field is left blank.[^r1]
* The specified week falls outside the active operating calendar.[^r1]
* An invalid, non-numeric value is entered into the build volume quantity field.[^r1]
* The schedule record for the selected timeframe is currently locked by another active user terminal.[^r2]

## How to fix
To resolve ERR-MPS-0001:
* Verify that `ITEM CD`, `WEEK`, and `QTY` contain valid entries before saving.[^r1]
* Ensure the build volume consists solely of numeric characters.[^r1]
* Confirm that the target week exists within the current operating calendar.[^r1]
* If all fields are valid and populated, check whether another terminal has opened the timeframe record and wait for the lock to clear.[^r2]

## Raised by
The error is raised by the `mps_save` service in [[services-prd-mps|PRD mps services]] when submitting records from [[screen-prd-mps-05|PRD-MPS-05 Master Schedule Entry]].[^r1]

## See also
* [[screen-prd-mps-05|PRD-MPS-05 Master Schedule Entry]]
* [[services-prd-mps|PRD mps services]]
* [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]]
* [[screen-prd-mrp-09|PRD-MRP-09 Mrp Run]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 27, Messages
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 29, Questions users ask
