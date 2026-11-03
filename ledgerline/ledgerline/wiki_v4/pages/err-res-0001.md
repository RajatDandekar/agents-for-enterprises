---
title: "ERR-RES-0001 General reservation validation failure"
type: "error"
slug: "err-res-0001"
summary: "Ledgerline error code raised when a stock reservation fails validation due to missing header data, zero quantity, or omitted work order number."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | ERR-RES-0001 |
| Module | Inventory (INV) |
| Type | Error |
| Owner | Ledgerline ERP |
| Status | Current |

`ERR-RES-0001` is a general reservation validation error code in Ledgerline ERP's inventory module [^r1]. It blocks processing when a stock reservation record is submitted with incomplete header fields or invalid quantities [^r1]. Operators encountering this error must verify mandatory fields before retrying the reservation entry [^r1].

## Meaning
The error indicates a general reservation validation failure during record submission [^r1].

## Cause
This error is triggered by omitting mandatory header data such as `WHS CD`, omitting the `WO NO` (work order number), or leaving the `QTY` field blank or set to zero [^r1].

## How to fix
To resolve the error, supply the required warehouse code (`WHS CD`), enter a valid work order number (`WO NO`), and ensure that `QTY` contains a non-zero, positive value [^r1].

## Raised by
The message is raised by reservation validation routines, primarily documented in [[man-inv-72|MAN-INV-72]] [^r1]. It relates to transaction processing on reservation interfaces such as [[screen-inv-res-12|INV-RES-12 Stock Reservation Entry]] handled by [[services-inv-res|INV res services]].

## See also
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]
* [[screen-inv-res-12|INV-RES-12 Stock Reservation Entry]]
* [[services-inv-res|INV res services]]
* [[errors-inv|Errors INV (ERR-INV-*)]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 35, Messages
