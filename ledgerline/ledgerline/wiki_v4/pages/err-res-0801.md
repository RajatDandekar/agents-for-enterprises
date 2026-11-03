---
title: "ERR-RES-0801 Cancellation rejected"
type: "error"
slug: "err-res-0801"
summary: "Ledgerline ERP error indicating stock reservation cancellation failure because it is already cancelled or parts are already issued."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-RES-0801 |
| Message | Cancellation rejected |
| Module | Inventory (INV) |
| Service | res_cancel |
| Status | Current |

`ERR-RES-0801` is an inventory reservation error in Ledgerline ERP indicating that a cancellation request has been rejected [^r1]. It prevents the cancellation service from running on a stock reservation that is no longer in an open or unfulfilled state [^r1].

## Meaning
The system rejects the cancellation operation because the specified reservation record cannot be cancelled in its current state [^r1].

## Cause
This error is triggered when the `res_cancel` service cannot process the request because the reservation has already been cancelled, or parts have already been issued against the works order [^r1].

## How to fix
Check the current status of the stock reservation record in [[screen-inv-res-12|INV-RES-12 Stock Reservation Entry]] and verify whether the line items have already been cancelled or issued [^r1]. If materials have already been issued against the works order, standard cancellation cannot proceed [^r1].

## Raised by
The error is raised by the `res_cancel` service in [[services-inv-res|INV res services]], documented in [[man-inv-72|MAN-INV-72]] [^r1].

## See also
* [[screen-inv-res-12|INV-RES-12 Stock Reservation Entry]]
* [[services-inv-res|INV res services]]
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]
* [[errors-inv|Errors INV (ERR-INV-*)]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 35, Messages
