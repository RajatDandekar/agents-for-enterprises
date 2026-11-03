---
title: "ERR-DBN-0001"
type: "error"
slug: "err-dbn-0001"
summary: "Ledgerline error raised when a debit note cannot be found during retrieval or when entering a zero balance in AP-DBN-04."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | ERR-DBN-0001 |
| Module | Accounts Payable (AP) |
| Screen | [[screen-ap-dbn-04|AP-DBN-04]] |
| Service | dbn_get |
| Severity | Error |
| Status | current |

ERR-DBN-0001 is an Accounts Payable error in Ledgerline ERP 7.2 indicating that a debit note record could not be found or retrieved [^r1]. In standard operation, it is encountered on [[screen-ap-dbn-04|AP-DBN-04]] when querying an unrecognised reference number or encountering record corruption [^r1]. Additionally, documentation for [[screen-ap-dbn-04|AP-DBN-04]] identifies this code when attempting to input a zero balance in the amount field [^r2].

## Meaning
The error indicates that the requested debit note record does not exist in the database or could not be resolved by the system [^r1]. It also represents an invalid zero-amount input during debit note entry [^r2].

## Cause
The error is triggered by:
* Entering an unrecognised reference in the `DBN NO` field during record retrieval [^r1].
* Underlying record corruption preventing the debit note from being located [^r1].
* Entering a zero balance in the `AMOUNT` field within the entry interface [^r2].

## How to fix
* Verify that the reference entered in `DBN NO` corresponds to a valid, existing debit note [^r1].
* If the reference is correct but still fails to load, inspect the database record for potential underlying corruption [^r1].
* Ensure that the value entered in `AMOUNT` is greater than zero when creating or updating a debit note on [[screen-ap-dbn-04|AP-DBN-04]] [^r2].

## Raised by
* Service `dbn_get` in [[services-ap-dbn|AP dbn services]] when executing a fetch request against an unknown reference or corrupt record [^r1].
* Screen [[screen-ap-dbn-04|AP-DBN-04 Debit Note Entry]] when validating the `AMOUNT` field [^r2].

## Versions and conflicts
* **Contradiction**: In [[man-ap-72|MAN-AP-72]] (p. 13, Messages), ERR-DBN-0001 is formally defined as a record lookup failure raised by `dbn_get` when an unrecognised reference is entered in `DBN NO` or due to record corruption [^r1]. However, in the worked example for [[screen-ap-dbn-04|AP-DBN-04]] (p. 14), entering a zero balance in the `AMOUNT` field is also stated to produce ERR-DBN-0001 [^r2]. Both descriptions appear in [[man-ap-72|MAN-AP-72]] v7.2.3 (dated 2025-01-15).

## See also
* [[screen-ap-dbn-04|AP-DBN-04 Debit Note Entry]]
* [[services-ap-dbn|AP dbn services]]
* [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 13, Messages
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 14, Worked example
