---
title: "ERR-GL-0007 Ledger Integrity Failure"
type: "error"
slug: "err-gl-0007"
summary: "Ledgerline error code indicating a general ledger posting or reversal integrity check failure."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-GL-0007 |
| module | GL |
| severity | Error |
| system | Ledgerline ERP 7.2 |
| status | current |

ERR-GL-0007 is a Ledgerline error code indicating an integrity failure encountered during General Ledger posting or journal reversal [^r1][^r2]. It halts processing when posting conditions violate ledger consistency or user authority requirements [^r1][^r2]. Today, resolving this error requires verifying nominal account statuses, distribution balancing, posting dates, reversal reason values, and operator permissions [^r1][^r2].

| Field | Value |
|---|---|
| Error Code | ERR-GL-0007 |
| Module | GL |
| System | Ledgerline ERP 7.2 [^r1] |
| Status | Current [^r1] |

## Meaning

The message signals that Ledgerline has rejected a transaction due to a general ledger integrity failure [^r1].

## Cause

The error is triggered during GL posting or reversal when:
* An unbalanced ledger distribution exists across lines [^r1].
* A line references an inactive nominal account code [^r1].
* A user attempts to execute `gl_reverse` without entering an explanation in the `REASON` field, or the entered `REASON` field was not accepted by the terminal during reversal [^r1][^r2].
* The journal voucher date (`JV DT`) falls within a closed ledger period [^r2].
* The user lacks designated posting rights [^r2].

## How to fix

* Balance the debit and credit totals across the transaction lines before posting [^r1].
* Confirm all referenced nominal account codes are active in the chart of accounts [^r1].
* Ensure a valid explanation is entered into and accepted by the terminal in the `REASON` field when performing a `gl_reverse` transaction [^r1][^r2].
* Verify that the `JV DT` falls within an open period on [[screen-ap-per-11|AP-PER-11 Ap Period]] or update the transaction date accordingly [^r2].
* Verify that the operating user profile has the required GL posting rights assigned [^r2].

## Raised by

* Execution of `gl_reverse` or general ledger posting services via [[services-ap-gl|AP gl services]] and [[screen-ap-gl-14|AP-GL-14 Gl Posting]] [^r1][^r2].
* Accounting workflows described in [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]] [^r1][^r2].

## See also

* [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]]
* [[screen-ap-gl-14|AP-GL-14 Gl Posting]]
* [[services-ap-gl|AP gl services]]
* [[screen-ap-per-11|AP-PER-11 Ap Period]]
* [[services-ap-per|AP per services]]
* [[errors-per|ERR-PER Error Codes]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 53, Messages
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 54, Questions users ask
