---
title: "ERR-SUP-0030"
type: "error"
slug: "err-sup-0030"
summary: "Ledgerline error indicating a supplier account code does not exist, is inactive, suspended, closed, or lacks consignment setup."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-SUP-0030 |
| display | SUPPLIER NOT FOUND |
| module | AP / INV |
| field | SUP CD |
| status | current |

`ERR-SUP-0030` is a Ledgerline validation error that displays the message text 'SUPPLIER NOT FOUND' [^r5]. It prevents processing across accounts payable and inventory transactions when the specified supplier code cannot be validated [^r1][^r2].

## Meaning

In the Section 20 message table, `ERR-SUP-0030` displays 'SUPPLIER NOT FOUND' [^r5].

## Cause

The error indicates that the supplier account entered in the `SUP CD` field does not exist in the master records [^r1][^r2]. It also triggers when the supplier account has been flagged as inactive, closed, suspended, prohibited from inventory transactions, or placed on administrative stop [^r1][^r2]. Additionally, in inventory contexts it represents a supplier account validation failure where `SUP CD` belongs to a vendor lacking a valid consignment contract setup in accounts [^r4].

## How to fix

To resolve `ERR-SUP-0030`, verify the supplier code against the purchase order, delivery docket, or supplier enquiry tool [^r3]. Confirm the account status with finance to ensure the supplier is active and not restricted [^r3].

## Raised by

This error is documented in the user manual [[man-ap-72|MAN-AP-72]] for accounts payable and in inventory manual MAN-INV-72 [^r1][^r2]. It is raised during supplier account validation against the `SUP CD` field across both modules [^r1][^r2][^r4].

## See also

* [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]]
* [[services-ap-sup|AP sup services]]
* [[services-ap-inv|AP inv services]]
* [[screen-ap-inv-01|AP-INV-01 Supplier Invoice Entry]]
* [[screen-ap-spy-16|AP-SPY-16 Supplier Payment Hold Hold]]
* [[sop-inv-002|SOP-INV-002 Returns to Vendor (RTV)]]
* [[screen-inv-rtv-07|INV-RTV-07 Return To Vendor Entry]]

## References

[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 69, §20. Messages
[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 13, Messages
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 59, Messages
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 66, Messages
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 59, Messages
