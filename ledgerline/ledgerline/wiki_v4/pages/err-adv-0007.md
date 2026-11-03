---
title: "ERR-ADV-0007 Purchase order supplier mismatch or closed"
type: "error"
slug: "err-adv-0007"
summary: "Ledgerline error when an advance payment references a closed purchase order or a purchase order assigned to a different supplier."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | ERR-ADV-0007 |
| Module | Accounts Payable (AP) |
| Screen | AP-ADV-07 |
| Type | Error |
| Owner | Finance / AP |

ERR-ADV-0007 is an Accounts Payable validation error raised in [[screen-ap-adv-07|AP-ADV-07]] (Advance Payment Entry) of Ledgerline ERP [[man-ap-72|MAN-AP-72]][^r1]. It blocks processing when the entered purchase order is closed or does not match the supplier specified on the advance payment entry[^r1].

## Meaning
The error indicates that the purchase order referenced in the advance payment transaction cannot be associated with the selected supplier account or is no longer open for financial transactions[^r1].

## Cause
The error occurs on screen [[screen-ap-adv-07|AP-ADV-07]] when the purchase order entered in the `PO NO` field does not belong to the supplier entered in `SUP CD`, or when the referenced purchase order is already closed[^r1].

## How to fix
Verify that the correct supplier code is entered in `SUP CD` and matches the vendor on the purchase order[^r1]. If the supplier code is correct, confirm the status of the purchase order in `PO NO` to ensure it is not closed[^r1].

## Raised by
The validation is raised by screen [[screen-ap-adv-07|AP-ADV-07]] during advance payment entry in the Accounts Payable module[^r1].

## See also
* [[screen-ap-adv-07|AP-ADV-07 Advance Payment Entry]]
* [[services-ap-adv|AP adv services]]
* [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]]
* [[errors-po|ERR-PO Error Codes]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 28, Messages
