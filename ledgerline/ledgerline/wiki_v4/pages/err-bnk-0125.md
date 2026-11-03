---
title: "ERR-BNK-0125 Record locked by another user or concurrent payment process"
type: "error"
slug: "err-bnk-0125"
summary: "Error raised when an AP vendor record is locked by another user session or an active payment generation run."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-BNK-0125 |
| module | Accounts Payable |
| type | Error |
| source_document | MAN-AP-72 |

Error code ERR-BNK-0125 blocks modifications to a vendor bank or accounts payable record while it is currently in use elsewhere in Ledgerline ERP. It prevents data corruption by ensuring concurrent sessions cannot edit vendor details simultaneously. In daily operations, this lock is typically triggered either by a colleague editing the record or by an executing payment cycle that is evaluating the vendor for disbursements.

## Meaning
ERR-BNK-0125 indicates that the target record is actively locked by another user session or by an active Accounts Payable payment generation run interrogating the vendor [^r1].

## Cause
The error occurs when a user attempts to update or access a vendor bank record while another user holds an open edit lock on that same record [^r1]. It also arises when a concurrent Accounts Payable payment run is interrogating or processing that vendor [^r1].

## How to fix
Users must wait until the concurrent user session terminates or the active Accounts Payable payment generation run finishes processing the vendor [^r1]. Once the lock is released, the transaction can be re-attempted.

## Raised by
This error is raised by vendor bank maintenance and payment routines documented in [[man-ap-72|MAN-AP-72]] [^r1].

## See also
* [[errors-bnk|Errors BNK]]
* [[screen-ap-bnk-06|AP-BNK-06 Supplier Bank Details Entry]]
* [[services-ap-bnk|AP bnk services]]
* [[screen-ap-pay-03|AP-PAY-03 Payment Run]]
* [[sop-ap-004|SOP-AP-004 Supplier Bank Detail Changes]]
* [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 24, Messages
