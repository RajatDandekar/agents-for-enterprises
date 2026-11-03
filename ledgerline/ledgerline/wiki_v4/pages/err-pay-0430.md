---
title: "ERR-PAY-0430 Payment proposal approver cannot be proposer"
type: "error"
slug: "err-pay-0430"
summary: "Error raised on AP-PAY-03 when the payment proposal approver is the same user who created or amended the proposal."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-AP-003 Supplier Payment Run v1.4.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-PAY-0430 |
| message | Payment proposal approver cannot be proposer |
| raised_on | AP-PAY-03 |
| procedure | SOP-AP-003 |
| status | current |

Error ERR-PAY-0430 enforces segregation of duties during accounts payable settlement runs in Ledgerline [^r1]. It blocks approval if the user attempting to release the run also created or modified the underlying proposal [^r1]. Resolving it requires an independent approver to review and sign off the batch using their own account [^r2].

| Field | Value |
|---|---|
| Error code | ERR-PAY-0430 |
| Description | Payment proposal approver cannot be proposer |
| Screen | [[screen-ap-pay-03|AP-PAY-03]] |
| Related procedure | [[sop-ap-003|SOP-AP-003]] |

## Meaning
The system prevents self-approval of payment proposals to ensure an independent check on disbursements [^r1].

## Cause
ERR-PAY-0430 is raised when the user attempting to approve a payment proposal on [[screen-ap-pay-03|AP-PAY-03]] is the same user who created or amended the proposal [^r1].

## How to fix
The proposing user must log out of Ledgerline [^r2]. An independent accounts payable manager must then log in with their own credentials to conduct the review and sign-off [^r2].

## Raised by
The validation check is executed by the payment run approval routine on screen [[screen-ap-pay-03|AP-PAY-03]] under [[sop-ap-003|SOP-AP-003]] [^r1].

## See also
* [[screen-ap-pay-03|AP-PAY-03 Payment Run]]
* [[sop-ap-003|SOP-AP-003 Supplier Payment Run]]
* [[err-bnk-0101|ERR-BNK-0101 Supplier bank details unverified]]

## References

[^r1]: 02_procedures/SOP-AP-003 Supplier Payment Run v1.4.pdf, p. 3, §5. Procedure: notes and common mistakes
[^r2]: 02_procedures/SOP-AP-003 Supplier Payment Run v1.4.pdf, p. 4, Actions when something does not look right
