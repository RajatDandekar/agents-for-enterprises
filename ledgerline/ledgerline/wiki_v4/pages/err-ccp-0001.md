---
title: "ERR-CCP-0001 Cycle count plan parameter error"
type: "error"
slug: "err-ccp-0001"
summary: "Ledgerline error raised when cycle count plan parameters fail validation due to invalid warehouse, category, scheduling data, or active duplicate plans."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-CCP-0001 |
| module | Inventory (INV) |
| raised_by | services-inv-ccp |
| screen | screen-inv-ccp-14 |
| source_manual | man-inv-72 |
| status | current |

ERR-CCP-0001 is a Ledgerline validation error encountered during cycle count plan maintenance on [[screen-inv-ccp-14|INV-CCP-14 Cycle Count Plan Entry]]. It indicates that the entered plan parameters contain invalid warehouse, category, or scheduling values, or that a conflicting active plan already covers the selected scope [^r1]. Users must correct the parameter entries or close existing open plans before saving [^r2].

## Meaning

The error flags an invalid cycle count configuration where parameter values violate master data constraints or conflict with active plan schedules [^r1].

## Cause

ERR-CCP-0001 occurs when:
* The specified warehouse code does not exist or is locked [^r1].
* The ABC CLASS value is unrecognised [^r1].
* Mandatory scheduling data is missing [^r1].
* An active cycle count plan already exists for the designated warehouse and category combination [^r1].

## How to fix

To clear ERR-CCP-0001:
1. Verify that WHS CD is open and valid in the warehouse master [^r2].
2. Confirm that the ABC CLASS and FREQUENCY parameters are correctly specified [^r2].
3. Check the CYCLE COUNT PLAN LIST to determine whether an active plan is currently open for that warehouse and category combination [^r2].

## Raised by

This message is documented in [[man-inv-72|MAN-INV-72]] and handled by [[services-inv-ccp|INV ccp services]] during plan definition on [[screen-inv-ccp-14|INV-CCP-14 Cycle Count Plan Entry]] [^r1].

## See also

* [[errors-inv|Errors INV (ERR-INV-*)]]
* [[errors-cnt|Stock Count Error Codes (ERR-CNT-*)]]
* [[screen-inv-cnt-06|INV-CNT-06 Stock Count Entry]]
* [[screen-inv-whs-01|INV-WHS-01 Warehouse Master]]
* [[services-inv-cnt|INV cnt services]]
* [[services-inv-whs|INV whs services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 55, Messages
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 55, Messages
