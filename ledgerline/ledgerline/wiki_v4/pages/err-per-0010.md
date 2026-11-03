---
title: "ERR-PER-0010 Documents unposted at period close"
type: "error"
slug: "err-per-0010"
summary: "Ledgerline error blocking AP period close on screen AP-PER-11 when unposted documents, batches, journals, or matchings remain."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-AP-002 Period Close v3.0.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-PER-0010 |
| module | AP |
| screen | AP-PER-11 |
| severity | Error |
| raised_by | AP Period Close routine |

`ERR-PER-0010` is a Ledgerline error encountered during the accounts payable period close routine [^r1]. It triggers when an operator attempts to close the AP period while pending documents, batches, journals, or matchings remain unposted [^r1]. Resolving it requires clearing or posting all pending transactions before retrying the period close [^r2].

## Meaning
`ERR-PER-0010` signifies that the AP period cannot be closed because unposted documents, batches, journals, or matchings are still present [^r1].

## Cause
The error occurs when a user attempts to execute the period close on screen [[screen-ap-per-11|AP-PER-11]] while batches, documents, journals, or matchings remain in an unposted state [^r1].

## How to fix
To clear the error, open the batch control screen and identify any batches holding an unposted status [^r2]. Complete the posting routine for all valid entries, or delete temporary draft batches if they are not required [^r2]. Once all pending items are resolved, re-attempt the period close on screen [[screen-ap-per-11|AP-PER-11]] [^r2].

## Raised by
This error is raised on screen [[screen-ap-per-11|AP-PER-11]] during the AP period close procedure governed by [[sop-ap-002|SOP-AP-002]] [^r1].

## See also
* [[screen-ap-per-11|AP-PER-11 Ap Period]]
* [[sop-ap-002|SOP-AP-002 Accounts Payable Period Close]]
* [[errors-per|ERR-PER Error Codes]]

## References

[^r1]: 02_procedures/SOP-AP-002 Period Close v3.0.pdf, p. 3, §5. Procedure
[^r2]: 02_procedures/SOP-AP-002 Period Close v3.0.pdf, p. 4, What to do when something does not look right
