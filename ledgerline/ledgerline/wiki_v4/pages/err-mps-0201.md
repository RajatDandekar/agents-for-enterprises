---
title: "ERR-MPS-0201 Master Schedule Line Locked Against Modification"
type: "error"
slug: "err-mps-0201"
summary: "Ledgerline error raised when attempting to modify a locked master schedule line due to shop floor tracking, committed components, or a closed week."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-MPS-0201 |
| message | Master Schedule Line Locked Against Modification |
| module | PRD |
| severity | Error |
| manual | MAN-PRD-72 |
| status | current |

ERR-MPS-0201 is a Ledgerline production scheduling validation error encountered in [[man-prd-72|MAN-PRD-72]]. It prevents users from modifying an existing master schedule line for a given item and week once execution or accounting commitments have occurred. As of 26 October 2026, planners must handle changes for locked weeks through downstream works order adjustments rather than altering the schedule line directly.

## Meaning

ERR-MPS-0201 indicates that a schedule line for an item and week cannot be modified because shop floor tracking has raised tickets, components are committed from stores, or the week is closed [^r1].

## Cause

The error occurs when an update or overwrite is attempted on an existing line in [[screen-prd-mps-05|PRD-MPS-05 Master Schedule Entry]] after the planning horizon has reached execution status [^r1][^r2]. Specifically, Ledgerline locks the schedule line when shop floor tracking tickets exist, material allocations from stores are active, or the production calendar week has already been closed [^r1].

## How to fix

To resolve or handle required volume and schedule adjustments on weeks locked with ERR-MPS-0201, contact the planning office supervisor to execute works order amendments rather than overwriting entries on [[screen-prd-mps-05|PRD-MPS-05]] [^r2].

## Raised by

This error is raised by the master production scheduling services in [[services-prd-mps|services-prd-mps]] and the [[screen-prd-mps-05|PRD-MPS-05 Master Schedule Entry]] screen [^r1][^r2].

## See also

* [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]]
* [[screen-prd-mps-05|PRD-MPS-05 Master Schedule Entry]]
* [[services-prd-mps|PRD mps services]]
* [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]
* [[services-prd-wo|PRD wo services]]
* [[errors-wo|ERR-WO error codes]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 28, Messages
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 28, Messages
