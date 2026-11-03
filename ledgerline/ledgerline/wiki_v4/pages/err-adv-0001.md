---
title: "ERR-ADV-0001 Missing or invalid advance payment fields"
type: "error"
slug: "err-adv-0001"
summary: "Error code ERR-ADV-0001 raised during advance payment save when supplier code, purchase order number, or amount is missing or invalid."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-ADV-0001 |
| module | AP |
| raised_by | adv_save |
| screen | AP-ADV-07 |
| severity | Error |
| status | current |

Error `ERR-ADV-0001` is an Accounts Payable validation error in Ledgerline ERP.[^r1] It blocks the submission of an advance payment record whenever mandatory header fields are omitted or improperly formatted.[^r1] Resolving the error requires supplying valid values for the supplier, purchase order reference, or advance amount before retrying the save operation.[^r1]

| Field | Value |
|---|---|
| Code | `ERR-ADV-0001` |
| Module | Accounts Payable (AP) |
| Screen | [[screen-ap-adv-07|AP-ADV-07]] |
| Service | `adv_save` (under [[services-ap-adv|AP adv services]]) |
| Status | Current |

## Meaning

`ERR-ADV-0001` indicates that required header data on an advance payment transaction is either missing or fails standard format validation checks.[^r1]

## Cause

The error is triggered when `SUP CD`, `PO NO`, or `AMOUNT` is left blank or entered in an invalid format.[^r1]

## How to fix

To resolve this error, inspect the advance payment entry form and ensure that valid, correctly formatted values are entered for the supplier code (`SUP CD`), purchase order number (`PO NO`), and payment amount (`AMOUNT`).[^r1] Re-execute the save action once the fields are corrected.[^r1]

## Raised by

This error is raised by the `adv_save` service on screen [[screen-ap-adv-07|AP-ADV-07 Advance Payment Entry]].[^r1]

## See also

* [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]]
* [[screen-ap-adv-07|AP-ADV-07 Advance Payment Entry]]
* [[services-ap-adv|AP adv services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 28, Messages
