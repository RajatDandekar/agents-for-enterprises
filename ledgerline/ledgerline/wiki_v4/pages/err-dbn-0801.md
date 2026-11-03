---
title: "ERR-DBN-0801"
type: "error"
slug: "err-dbn-0801"
summary: "Error ERR-DBN-0801 is raised during debit note save or post when amount validation fails or the referenced document is invalid."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-DBN-0801 |
| Module | Accounts Payable (AP) |
| Severity | Error |
| Services | dbn_save, dbn_post |
| Manual | MAN-AP-72 |

ERR-DBN-0801 is an Accounts Payable validation error raised in Ledgerline ERP during debit note processing [^r1]. As documented in [[man-ap-72|MAN-AP-72]], it prevents invalid debit note records from being saved or posted via screen [[screen-ap-dbn-04|AP-DBN-04]] [^r1][^r2]. Users encountering this message must verify both the monetary values entered and the status of the referenced document before reattempting the transaction [^r1][^r2].

## Meaning
ERR-DBN-0801 indicates a validation failure when creating or posting a debit note [^r1]. It signals either an issue with the entered monetary value or a problem resolving the underlying invoice or reference document [^r1][^r2].

## Cause
The error is triggered by the system under the following conditions:
* The `AMOUNT` field contains a zero, negative, or improperly formatted monetary value, or has been left blank [^r1].
* The document specified in the `REF DOC` field does not exist in the system [^r2].
* The document specified in the `REF DOC` field has already been settled [^r2].

## How to fix
To resolve ERR-DBN-0801 on screen [[screen-ap-dbn-04|AP-DBN-04]]:
1. Inspect the `AMOUNT` field to ensure a valid, positive monetary value is entered in the correct currency format [^r1].
2. Confirm that the reference document entered in `REF DOC` exists and is open for adjustment rather than already fully settled [^r2].

## Raised by
The error is raised by the [[services-ap-dbn|AP dbn services]] `dbn_save` and `dbn_post` during transaction processing on screen [[screen-ap-dbn-04|AP-DBN-04]] [^r1][^r2].

## Versions and conflicts
* **Today's rule:** [[man-ap-72|MAN-AP-72]] defines ERR-DBN-0801 in the Messages catalogue as an `AMOUNT` field validation error (missing, zero, negative, or invalid monetary formatting) [^r1].
* **Other rule:** In the worked example for [[screen-ap-dbn-04|AP-DBN-04]], [[man-ap-72|MAN-AP-72]] also describes ERR-DBN-0801 as being returned if the `REF DOC` reference does not exist or has already been settled [^r2].
* **Sources and dates:** [[man-ap-72|MAN-AP-72]] (v7.2.3, 2025-01-15), p. 13 vs p. 14 [^r1][^r2].
* **Kind:** `contradiction`.

## See also
* [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]]
* [[screen-ap-dbn-04|AP-DBN-04 Debit Note Entry]]
* [[services-ap-dbn|AP dbn services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 13, Messages
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 14, Worked example
