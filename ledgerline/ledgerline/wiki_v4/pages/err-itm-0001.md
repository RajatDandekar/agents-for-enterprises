---
title: "ERR-ITM-0001: Item code already exists in Item Master"
type: "error"
slug: "err-itm-0001"
summary: "Error raised when attempting to save a new item record using an item code that already exists in the Item Master."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | ERR-ITM-0001 |
| Type | Error |
| Module | INV (Inventory) |
| Raised by service | itm_save |
| Remedy | Retrieve part and run itm_update, or allocate an unused reference |

ERR-ITM-0001 is a Ledgerline Inventory error indicating that an item code entered during creation already exists in the database [^r1]. It occurs when executing the item save service on a record whose primary key is already taken [^r1]. Resolving it requires updating the existing item or re-attempting creation with an unallocated item code reference [^r2].

## Meaning
ERR-ITM-0001 reports that the item code specified for a new record is already present in the Item Master database [^r1].

## Cause
The error is triggered when calling the `itm_save` service with an item code that duplicates an existing item entry [^r1].

## How to fix
To resolve the error, retrieve the existing part and use `itm_update` if the intention is to amend an existing item, or allocate an unused reference before re-attempting `itm_save` [^r2].

## Raised by
* `itm_save` in [[services-inv-itm|INV itm services]] [^r1]
* Documented in [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]] [^r1]

## See also
* [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]]
* [[services-inv-itm|INV itm services]]
* [[errors-itm|ERR-ITM error codes]]
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 43, Messages
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 43, Messages
