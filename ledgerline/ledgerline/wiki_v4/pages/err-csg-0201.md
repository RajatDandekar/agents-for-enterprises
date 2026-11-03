---
title: "ERR-CSG-0201 QTY MUST BE > 0 / Invalid Consignment Status"
type: "error"
slug: "err-csg-0201"
summary: "Ledgerline error ERR-CSG-0201 raised during consignment settlement when the record status is invalid, frozen, or the settlement quantity is invalid."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-CSG-0201 |
| Message | QTY MUST BE > 0 |
| Module | Inventory (CSG) |
| Raised by service | csg_settle |
| Manual | MAN-INV-72 |
| Status | current |

ERR-CSG-0201 is a Ledgerline inventory error generated when attempting to settle consignment inventory records [^r1]. It blocks settlement actions if the consignment status is invalid, frozen, or if the entered quantity is invalid or exceeds the remaining balance [^r1][^r2].

## Meaning
The message text defined for ERR-CSG-0201 in the error table is `QTY MUST BE > 0` [^r2]. Functionally, the message signals that the consignment line cannot be settled because of an ineligible status or an improper settlement quantity [^r1][^r2].

## Cause
The error is triggered when executing settlement against a consignment stock record that is already marked fully settled, cancelled, or frozen by central finance [^r1]. It also occurs if the entered settlement quantity is not greater than zero or exceeds the remaining balance of the consignment record [^r1][^r2].

## How to fix
Check the consignment record status on the screen and confirm it is not cancelled, fully settled, or placed on freeze by central finance [^r1]. If the record is open and valid, verify that the entered settlement quantity is greater than zero and does not exceed the remaining unsettled balance [^r1][^r2].

## Raised by
Raised by the consignment settlement action `csg_settle` within [[services-inv-csg]] [^r1].

## Versions and conflicts
- Contradiction: In [[man-inv-72|MAN-INV-72]] §20 Messages table (p. 68), ERR-CSG-0201 specifies the message text "QTY MUST BE > 0" [^r2]. However, the narrative description on p. 66 indicates the error covers records already marked fully settled, cancelled, frozen by central finance, or where the settlement quantity exceeds the remaining balance [^r1].

## See also
* [[screen-inv-csg-17|INV-CSG-17 Consignment Stock Entry]]
* [[services-inv-csg|INV csg services]]
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]
* [[errors-inv|Errors INV (ERR-INV-*)]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 66, Messages
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 68, §20. Messages
