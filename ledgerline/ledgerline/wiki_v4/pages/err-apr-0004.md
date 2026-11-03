---
title: "ERR-APR-0004 Advance amount exceeds PO unbilled commitment"
type: "error"
slug: "err-apr-0004"
summary: "Ledgerline error raised during advance approval when the requested amount exceeds the remaining unbilled commitment on the purchase order."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | ERR-APR-0004 |
| Module | AP (Accounts Payable) |
| Severity | Error |
| Raised by service | adv_approve |
| Source document | MAN-AP-72 |

ERR-APR-0004 is a Ledgerline Accounts Payable error raised when an advance payment request exceeds the unbilled commitment remaining on a purchase order [^r1]. It blocks approval of the advance until the requested amount is brought within the purchase order's open commitment balance [^r1]. The check is enforced by the advance approval process documented in [[man-ap-72|MAN-AP-72]] [^r1].

## Meaning

The error indicates that the value submitted in the AMOUNT field is greater than the purchase order's remaining unbilled commitment [^r1]. Ledgerline rejects the transaction to prevent paying advances that exceed the committed contract value [^r1].

## Cause

The error occurs when an approver executes `adv_approve` against an advance request where AMOUNT exceeds the balance of the linked purchase order that remains unbilled [^r1].

## How to fix

Review the linked purchase order commitment balance to verify open, unbilled amounts against the requested advance [^r1]. Adjust the advance request AMOUNT so that it does not exceed the remaining unbilled commitment on the purchase order before re-attempting approval [^r1].

## Raised by

Raised by the `adv_approve` service within [[services-ap-adv|AP adv services]] when evaluating advance approvals initiated from [[screen-ap-adv-07|AP-ADV-07 Advance Payment Entry]] [^r1].

## See also

* [[errors-apr|Errors APR]]
* [[err-apr-0003|ERR-APR-0003 Self-approval not permitted]]
* [[services-ap-adv|AP adv services]]
* [[screen-ap-adv-07|AP-ADV-07 Advance Payment Entry]]
* [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 28, Messages
