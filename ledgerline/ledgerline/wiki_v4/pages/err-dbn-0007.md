---
title: "ERR-DBN-0007"
type: "error"
slug: "err-dbn-0007"
summary: "Ledgerline error raised during debit note posting or cancellation when records are already processed, periods are closed, or posting runs are locked."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | ERR-DBN-0007 |
| Type | Error |
| Module | AP (Accounts Payable) |
| Source | MAN-AP-72 |

ERR-DBN-0007 is an Accounts Payable error in Ledgerline ERP encountered during debit note processing [^r1]. It blocks posting or cancellation actions when the target debit note has already reached a finalized status or when financial posting controls prevent updates [^r1][^r2]. As of 26 October 2026, users encountering this error on [[screen-ap-dbn-04|AP-DBN-04 Debit Note Entry]] must verify the debit note's processing state and the status of the purchase ledger period [^r1][^r2].

## Meaning

ERR-DBN-0007 signals that an attempted debit note transaction cannot proceed because the document is already processed or the ledger posting environment is restricted [^r1][^r2].

## Cause

The error occurs when a user attempts to execute the services `dbn_post` or `dbn_cancel` on a debit note record that has already been posted or processed [^r1]. It is also triggered when attempting to post while the purchase ledger financial period is closed, or when the posting run is locked for maintenance [^r2].

## How to fix

Confirm whether the debit note record has already been processed or cancelled in [[screen-ap-dbn-04|AP-DBN-04]] [^r1]. If the debit note is pending but posting fails, inspect the financial period status using [[screen-ap-per-11|AP-PER-11 Ap Period]] and verify that no active posting run locks or maintenance windows are in effect [^r2].

## Raised by

This error is raised by the [[services-ap-dbn|AP dbn services]] `dbn_post` and `dbn_cancel` [^r1]. Reference documentation for the error is provided in the manual [[man-ap-72|MAN-AP-72]] [^r1][^r2].

## Versions and conflicts

- **Contradiction**: In the Messages section of [[man-ap-72|MAN-AP-72]], ERR-DBN-0007 is defined specifically as occurring when executing `dbn_post` or `dbn_cancel` on an already processed or posted record [^r1]. Conversely, the "Questions users ask" section of the same manual states that the code indicates the purchase ledger financial period is closed or the posting run is locked for maintenance [^r2]. Both conditions are documented concurrently without reconciliation in version 7.2.3 [^r1][^r2].

## See also

- [[screen-ap-dbn-04|AP-DBN-04 Debit Note Entry]]
- [[services-ap-dbn|AP dbn services]]
- [[screen-ap-per-11|AP-PER-11 Ap Period]]
- [[services-ap-per|AP per services]]
- [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 13, Messages
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 14, Questions users ask
