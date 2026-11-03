---
title: "ERR-LOT-0007 Lot or serial number not found"
type: "error"
slug: "err-lot-0007"
summary: "Error ERR-LOT-0007 is raised by lot_get and lot_trace when a requested lot or serial number cannot be located for an item."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | ERR-LOT-0007 |
| Message | Lot or serial number not found |
| Module | Inventory |
| Raised by | lot_get, lot_trace |
| Status | Current |

ERR-LOT-0007 is an inventory module error code in Ledgerline ERP [^r1]. It indicates that a requested lot or serial number cannot be located for the specified item code during query execution [^r1]. The message is encountered primarily when running [[services-inv-lot|lot_get]] or [[services-inv-lot|lot_trace]] operations [^r1].

## Meaning
ERR-LOT-0007 signifies that the requested lot or serial number cannot be found for the specified item code [^r1].

## Cause
The error occurs when executing a query using [[services-inv-lot|lot_get]] or [[services-inv-lot|lot_trace]] where the requested lot or serial identifier does not match any record registered under the specified item code [^r1].

## How to fix
Verify that the correct item code and lot or serial number have been entered before re-executing [[services-inv-lot|lot_get]] or [[services-inv-lot|lot_trace]] [^r1]. Ensure that the lot or serial entry exists for the specified item code [^r1].

## Raised by
* `lot_get` service [^r1]
* `lot_trace` service [^r1]

## See also
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]
* [[screen-inv-lot-10|INV-LOT-10 Lot / Serial Entry]]
* [[services-inv-lot|INV lot services]]
* [[errors-inv|Errors INV (ERR-INV-*)]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 27, Messages
