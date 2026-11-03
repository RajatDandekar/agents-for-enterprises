---
title: "ERR-CC-0009"
type: "error"
slug: "err-cc-0009"
summary: "Ledgerline Accounts Payable error indicating an invalid, missing, or inactive cost centre code entered in the CC CD field."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-CC-0009 |
| type | error |
| module | Accounts Payable |
| raised_by | Ledgerline Accounts Payable validation |
| severity | Error |
| status | current |

Error ERR-CC-0009 is a Ledgerline Accounts Payable message generated when cost distribution validation fails on an entered cost centre code [^r1]. It signals that the identifier supplied in the CC CD field cannot be found within the chart of accounts or has been designated as closed or inactive [^r1]. Transactions triggering this message cannot proceed until an active and valid cost centre is provided [^r1].

## Meaning
Message ERR-CC-0009 indicates that the cost centre code entered in field CC CD does not exist in the chart of accounts or is marked closed/inactive [^r1].

## Cause
The error is caused by submitting a cost centre code in CC CD that is either missing from the chart of accounts master setup or has been flagged with an inactive or closed status [^r1].

## How to fix
Verify the intended cost centre code against the current chart of accounts and replace the invalid or inactive code in field CC CD with an open, active cost centre [^r1].

## Raised by
This message is raised by Ledgerline Accounts Payable system validations as documented in [[man-ap-72|MAN-AP-72]] [^r1].

## See also
* [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 57, Messages
