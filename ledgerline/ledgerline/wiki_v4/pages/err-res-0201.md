---
title: "ERR-RES-0201 Insufficient unreserved stock available"
type: "error"
slug: "err-res-0201"
summary: "Ledgerline ERP inventory error indicating insufficient unreserved stock in the specified warehouse to fulfill a reservation request."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-RES-0201 |
| message | Insufficient unreserved stock available |
| module | INV |
| severity | Error |
| owner | Inventory Control |

`ERR-RES-0201` is a Ledgerline ERP inventory error raised when an operation attempts to allocate or reserve inventory beyond current uncommitted quantities [^r1]. It indicates that the available, unreserved stock level for the specified item code in the selected warehouse is less than the requested reservation quantity [^r1]. Inventory operators encountering this message must verify existing stock balances, check active reservations, or adjust the requested transfer or allocation quantity [^r1].

## Meaning
The system displays `ERR-RES-0201` when the requested reservation quantity (`QTY`) exceeds the unreserved on-hand balance for the specified `ITEM CD` within the target warehouse code (`WHS CD`) [^r1].

## Cause
The error is triggered when:
* The requested reservation quantity is larger than the total quantity physically available in the specified warehouse [^r1].
* Physical stock exists, but existing allocations or active reservations have reduced the unreserved stock balance below the requested `QTY` [^r1].

## How to fix
To resolve `ERR-RES-0201`:
* Query stock levels and existing reservations in [[screen-inv-res-12|INV-RES-12 Stock Reservation Entry]] to confirm the current unreserved balance for the item in the warehouse [^r1].
* Reduce the requested quantity to match the available unreserved balance [^r1].
* Cancel or release unnecessary existing reservations to free up stock for the item code [^r1].
* Transfer additional stock into the specified warehouse before retrying the reservation transaction [^r1].

## Raised by
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]] [^r1].
* [[services-inv-res|INV res services]] during reservation creation or update requests [^r1].
* [[screen-inv-res-12|INV-RES-12 Stock Reservation Entry]] [^r1].

## See also
* [[screen-inv-res-12|INV-RES-12 Stock Reservation Entry]]
* [[services-inv-res|INV res services]]
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]
* [[errors-inv|Errors INV (ERR-INV-*)]]
* [[errors-stk|ERR-STK Error Codes]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 35, Messages
