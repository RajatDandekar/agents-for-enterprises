---
title: "ERR-APR-0003 Self-approval not permitted"
type: "error"
slug: "err-apr-0003"
summary: "Error raised in Ledgerline when a user attempts self-approval of a purchase document or when advance payment approval authority is exceeded."
audience: "staff"
status: "current"
sources: ["01_policies/POL-APR-002 Approval Matrix v3.0.pdf", "03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | ERR-APR-0003 |
| Type | Error |
| Module | Purchasing / Accounts Payable |
| Trigger | Self-approval or insufficient approval authority |

Error ERR-APR-0003 is a Ledgerline system validation message that prevents users from approving purchase documents they raised themselves under [[pol-apr-002|POL-APR-002]][^r1]. It also serves in accounts payable to block advance payment approvals where a user lacks sufficient authority or exceeds an individual approval threshold[^r2]. In both contexts, the action is stopped until routed to a qualifying approver[^r1][^r2].

## Meaning
The error indicates that the user is not permitted to complete the approval action on the specified document[^r1][^r2]. Under purchasing controls, it enforces separation of duties by disallowing self-approval[^r1]. Under accounts payable workflows, it indicates that the user's authority limit is insufficient for the transaction amount[^r2].

## Cause
The error occurs when:
* A user attempts to approve a purchase document that they raised themselves[^r1].
* The advance payment transaction exceeds the individual approval limit assigned to the user[^r2].
* The user lacks sufficient approval authority during the execution of the advance approval service[^r2].

## How to fix
If the document was raised by the logged-in user, route the document to another authorised approver in accordance with [[pol-apr-002|POL-APR-002]][^r1]. If the error occurs during an advance payment approval, route the transaction to an approver holding an approval limit high enough to cover the advance amount[^r2].

## Raised by
* Document approval validation in Ledgerline purchasing workflows[^r1].
* Service `adv_approve` in [[services-ap-adv|AP adv services]] (accessed via [[screen-ap-adv-07|AP-ADV-07 Advance Payment Entry]] and documented in [[man-ap-72|MAN-AP-72]])[^r2].

## Versions and conflicts
* **Contradiction**: Under [[pol-apr-002|POL-APR-002]] (effective 2026-04-01), ERR-APR-0003 specifically restricts self-approval where a user attempts to approve their own purchase document[^r1]. In contrast, the Accounts Payable manual [[man-ap-72|MAN-AP-72]] (v7.2.3, dated 2025-01-15) defines ERR-APR-0003 as being triggered during `adv_approve` when a user lacks sufficient approval authority or the advance payment exceeds their individual approval limit[^r2].

## See also
* [[pol-apr-002|POL-APR-002 Approval Matrix for Purchasing]]
* [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]]
* [[screen-ap-adv-07|AP-ADV-07 Advance Payment Entry]]
* [[services-ap-adv|AP adv services]]

## References

[^r1]: 01_policies/POL-APR-002 Approval Matrix v3.0.pdf, p. 2, §4. Who may not approve
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 28, Messages
