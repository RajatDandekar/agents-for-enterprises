---
title: "ERR-WHS-0001 Warehouse validation failure"
type: "error"
slug: "err-whs-0001"
summary: "Ledgerline ERP inventory error indicating a warehouse validation failure on save or retrieval operations."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-WHS-0001 |
| Message | Warehouse validation failure |
| Module | Inventory (INV) |
| Services | whs_save, whs_get |
| Primary screen | INV-WHS-01 |
| Status | current |

ERR-WHS-0001 is a Ledgerline ERP inventory message indicating a warehouse record validation failure during record creation, update, or retrieval [^r1]. It is raised by the warehouse services when parameter checks fail, duplicate identifiers are supplied, or organizational unit linkages are invalid [^r1][^r2]. Users encountering the error must ensure unique warehouse coding and correct linkage to the designated operating unit before saving [^r2][^r3].

## Meaning

ERR-WHS-0001 signifies that an operation involving warehouse master records could not be validated or completed by Ledgerline [^r1]. It indicates either omitted or malformed input parameters, an invalid organizational unit mapping, an attempt to use an identifier that already exists, or a retrieval timeout on the warehouse entity [^r1][^r2].

## Cause

The error is triggered under any of the following circumstances:
* Mandatory parameters are omitted when attempting to save warehouse data [^r1][^r2].
* Formatting on entry fields is invalid [^r1].
* The operating unit code (`OU CD`) fails validation or has an invalid link to the selected warehouse [^r1][^r2].
* The identifier entered in `WHS CD` already exists in the system database [^r2].
* The requested `WHS CD` does not exist during a retrieval request [^r1].
* A database network communication timeout occurs while querying the warehouse record [^r1].

## How to fix

To resolve ERR-WHS-0001, follow these steps:
* Verify warehouse details against the master stores register [^r3].
* Ensure an unallocated identifier is chosen for `WHS CD` rather than an existing code [^r2][^r3].
* Confirm that all mandatory parameters are completed with valid formatting [^r1].
* Validate that the `OU CD` is active and correctly linked to the warehouse [^r1][^r2].
* Confirm that another user is not maintaining the same warehouse code simultaneously [^r3].
* Confirm that another user is not running an inventory valuation report on [[screen-inv-stk-03|INV-STK-03 Stock Val]] that could interfere with the database session [^r3].

## Raised by

* Services: `whs_save` and `whs_get` under [[services-inv-whs|INV whs services]] [^r1].
* Primary screen: [[screen-inv-whs-01|INV-WHS-01 Warehouse Master]] [^r1][^r2].

## See also

* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]
* [[services-inv-whs|INV whs services]]
* [[screen-inv-whs-01|INV-WHS-01 Warehouse Master]]
* [[screen-inv-stk-03|INV-STK-03 Stock Val]]
* [[errors-inv|Errors INV (ERR-INV-*)]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 38, Messages
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 40, Questions users ask
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 39, Tips
