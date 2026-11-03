---
title: "ERR-APR-0009 No approver found"
type: "error"
slug: "err-apr-0009"
summary: "Error code displayed by Ledgerline when an order value exceeds the plant head approval ceiling of £5,000,000."
audience: "staff"
status: "current"
sources: ["01_policies/POL-APR-002 Approval Matrix v3.0.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | ERR-APR-0009 |
| Message | No approver found |
| Module | Approvals (APR) |
| Severity | Error |
| Policy | POL-APR-002 |
| Threshold | > £5,000,000 |

Ledgerline raises error `ERR-APR-0009` when an approval workflow cannot determine an eligible approver for a purchase transaction [^r1]. As of 26 October 2026, this occurs when an order exceeds the £5,000,000 approval ceiling defined for the [[role-plant-head|plant head]] [^r1]. Because system approval routing stops at this threshold, such orders require external written approval from the Managing Director prior to being entered [^r1].

## Meaning

`ERR-APR-0009` indicates that no user role in the Ledgerline purchasing hierarchy holds system authority to approve the submitted order value [^r1].

## Cause

The order value exceeds £5,000,000, which is the maximum purchasing authorization limit assigned to the [[role-plant-head|plant head]] under [[pol-apr-002|POL-APR-002]] [^r1].

## How to fix

Orders over £5,000,000 require external written approval from the Managing Director [^r1]. Once that written authorization is granted, the transaction is recorded by the office of the [[role-plant-head|plant head]] [^r1].

## Raised by

Raised by Ledgerline approval validation services during order routing when the order total exceeds £5,000,000 [^r1].

## See also

* [[pol-apr-002|POL-APR-002 Approval Matrix for Purchasing]]
* [[role-plant-head|Role PLANT-HEAD]]
* [[errors-apr|Errors APR]]
* [[err-apr-0003|ERR-APR-0003 Self-approval not permitted]]

## References

[^r1]: 01_policies/POL-APR-002 Approval Matrix v3.0.pdf, p. 1, §3. The limits
