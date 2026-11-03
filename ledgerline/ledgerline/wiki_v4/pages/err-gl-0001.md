---
title: "ERR-GL-0001 Missing or Invalid Header Information"
type: "error"
slug: "err-gl-0001"
summary: "General ledger posting rejection raised when header data is missing or invalid, accounts are invalid or suspended, or debits and credits do not balance."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-GL-0001 |
| Message | Missing or Invalid Header Information |
| Module | Accounts Payable / General Ledger |
| Screen | AP-GL-14 |
| Service | gl_post |

`ERR-GL-0001` is a Ledgerline general ledger posting error indicating missing or invalid header information or unpostable journal lines [^r1]. It is triggered during journal processing when header fields are invalid, a posting date is outside the open calendar, nominal accounts are missing or suspended, or debits and credits fail to balance [^r1][^r2]. Resolving the error requires correcting the journal header values or adjusting the line accounts and amounts before retrying the posting [^r1][^r2].

## Meaning
`ERR-GL-0001` indicates missing or invalid header information, a blank mandatory field, an account missing from the chart of accounts, or a date falling outside permissible posting calendars during posting [^r1]. It also represents an unbalanced journal entry or a reference to an inactive account [^r2].

## Cause
The error occurs under the following conditions:
* A mandatory header field is left blank or contains invalid data [^r1].
* The entered posting date falls outside the permissible posting calendars [^r1].
* An entered account code does not exist in the chart of accounts [^r1].
* An entered nominal account code is suspended [^r2].
* Total debits and total credits on the entry do not balance [^r2].

## How to fix
To resolve the error:
1. Verify that all mandatory header fields on [[screen-ap-gl-14|AP-GL-14 Gl Posting]] are populated with valid entries [^r1][^r2].
2. Confirm that the posting date falls within an open accounting period defined in the permissible posting calendars [^r1].
3. Check all line entries to ensure every nominal account code exists in the active chart of accounts and is not suspended [^r1][^r2].
4. Verify that total debits equal total credits across the entry lines [^r2].

## Raised by
* Service: `gl_post` in [[services-ap-gl|AP gl services]] [^r1][^r2]
* Screen: [[screen-ap-gl-14|AP-GL-14 Gl Posting]] [^r2]
* Document reference: [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]] [^r1]

## See also
* [[screen-ap-gl-14|AP-GL-14 Gl Posting]]
* [[services-ap-gl|AP gl services]]
* [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]]
* [[screen-ap-per-11|AP-PER-11 Ap Period]]
* [[errors-per|ERR-PER Error Codes]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 53, Messages
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 54, Worked example: Gl Posting
