---
title: "W-BNK-120 Supplier Bank Detail Verification Pending Hold"
type: "error"
slug: "w-bnk-120"
summary: "Ledgerline warning placed on supplier accounts upon bank change requests, holding payments until verification via bnk_verify."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-AP-004 Supplier Bank Detail Changes v2.0.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | W-BNK-120 |
| type | warning |
| module | AP |
| status | current |

Warning W-BNK-120 is a system warning that places a hold on all outgoing payments to a supplier account upon receipt of a bank change request [^r1]. It remains active until formal verification is completed in Ledgerline [^r1]. Staff are strictly prohibited from attempting to bypass or clear this warning if any doubts exist about the validity of the request [^r2].

| Key | Value |
|---|---|
| Code | W-BNK-120 |
| Type | Warning |
| Module | AP |
| Status | Current |

## Meaning
Warning W-BNK-120 indicates that a supplier bank change request has been received and verification is pending, resulting in a payment hold on the supplier account [^r1].

## Cause
The warning attaches automatically to a supplier account upon receipt of a bank detail change request [^r1].

## How to fix
Verification must be formally recorded using service `bnk_verify` in [[services-ap-bnk|AP bnk services]] [^r1]. Under no circumstances should staff attempt to bypass or clear warning W-BNK-120 when doubts exist regarding a bank change request [^r2].

## Raised by
Raised by Ledgerline upon logging a bank detail modification under [[sop-ap-004|SOP-AP-004]] [^r1].

## See also
* [[sop-ap-004|SOP-AP-004 Supplier Bank Detail Changes]]
* [[services-ap-bnk|AP bnk services]]

## References

[^r1]: 02_procedures/SOP-AP-004 Supplier Bank Detail Changes v2.0.pdf, p. 4, What to check on the screen
[^r2]: 02_procedures/SOP-AP-004 Supplier Bank Detail Changes v2.0.pdf, p. 4, What to do when something does not look right
