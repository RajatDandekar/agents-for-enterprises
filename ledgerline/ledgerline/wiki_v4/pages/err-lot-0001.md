---
title: "ERR-LOT-0001 Duplicate lot or serial identifier"
type: "error"
slug: "err-lot-0001"
summary: "Ledgerline error raised when a lot or serial identifier is already recorded in the database for the given item code."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-LOT-0001 |
| type | Error |
| module | INV |
| screen | [[screen-inv-lot-10|INV-LOT-10 Lot / Serial Entry]] |
| manual | [[man-inv-72|MAN-INV-72]] |
| status | current |

`ERR-LOT-0001` is an inventory module error in Ledgerline ERP indicating a duplicate tracking number. It is triggered when an operator attempts to record an existing lot or serial identifier for an item code that already has that identifier assigned in the database.[^r1]

## Meaning

The error signifies that the identifier entered in the LOT/SERIAL field already exists in the system for the specified item code.[^r1]

## Cause

A user or transaction attempted to register or reuse a lot or serial number that is already assigned to the item code in the inventory database.[^r1]

## How to fix

Verify the physical label or documentation of the material and enter a unique, unused lot or serial identifier for the item code, or check whether the item was already registered in the system.[^r1]

## Raised by

This error is raised by Ledgerline inventory services during lot or serial number creation or assignment when validating entries against existing database records.[^r1]

## See also

* [[screen-inv-lot-10|INV-LOT-10 Lot / Serial Entry]]
* [[services-inv-lot|INV lot services]]
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]
* [[errors-inv|Errors INV (ERR-INV-*)]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 27, Messages
