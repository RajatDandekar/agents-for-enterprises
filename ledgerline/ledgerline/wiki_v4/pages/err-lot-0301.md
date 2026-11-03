---
title: "ERR-LOT-0301 Lot locked or invalid status transition"
type: "error"
slug: "err-lot-0301"
summary: "Ledgerline error raised when a lot action fails due to an active lock or an invalid lot status transition."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-LOT-0301 |
| Type | Error |
| Module | Inventory |
| Owner | Inventory Control |
| Status | Current |

`ERR-LOT-0301` is an inventory error in Ledgerline ERP that blocks an attempted lot operation [^r1]. It indicates that the target lot is either currently locked by a concurrent inventory process or that the requested status change is invalid for the lot's current state [^r1]. Users encountering this message must verify active transactions on the batch or review its current status before re-attempting the action [^r1].

## Meaning
The error signals that the requested lot action cannot be completed because the record is locked by another transaction or violates permitted status lifecycle rules [^r1].

## Cause
This error occurs under two primary circumstances:
* The lot is locked by another active inventory transaction [^r1].
* An invalid status transition was attempted, such as executing `lot_release` on a lot that is not currently on hold, or attempting to place a hold on an exhausted batch [^r1].

## How to fix
* Wait for any concurrent inventory transactions locking the lot to complete before retrying [^r1].
* Confirm the current state of the lot to ensure the attempted transition is valid; do not invoke `lot_release` unless the lot is actively on hold, and do not attempt to place holds on exhausted batches [^r1].

## Raised by
Raised during lot lifecycle actions such as `lot_release` or hold attempts within [[services-inv-lot|INV lot services]] and [[man-inv-72|MAN-INV-72]] inventory workflows [^r1].

## See also
* [[screen-inv-lot-10|INV-LOT-10 Lot / Serial Entry]]
* [[screen-inv-qch-11|INV-QCH-11 Quality Hold Entry]]
* [[services-inv-lot|INV lot services]]
* [[services-inv-qch|INV qch services]]
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]
* [[errors-inv|Errors INV (ERR-INV-*)]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 27, Messages
