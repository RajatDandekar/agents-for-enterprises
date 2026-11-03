---
title: "Role STORES"
type: "role"
slug: "role-stores"
summary: "Ledgerline role for warehouse and stores personnel with £0 approval limit, covering goods receipt, discrepancy logging, quarantine, and perpetual inventory counts."
audience: "staff"
status: "current"
sources: ["05_master_data/Users_and_approval_limits.xlsx", "01_policies/POL-APR-002 Approval Matrix v3.0.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "11_training/intranet_export_2016/page_working_with_stores.html"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Role code | STORES |
| Role name | Stores |
| Gross approval limit | £0 |
| Approval authority | None (purchasing and stock adjustments) |
| Scope | Goods receipt, quarantine bays, discrepancy logging, stock counts |

The STORES role is assigned to warehouse and inventory staff responsible for goods inward handling, stock management, and discrepancy reporting across Northbridge Cycles sites. Under system matrices and purchasing controls, the role carries a gross approval limit of £0 and has no independent approval authority for purchasing or stock adjustments. Operational duties include maintaining quarantine cages and loading bays for rejected deliveries as well as executing routine perpetual counts and formal stocktakes.

| Attribute | Details |
|---|---|
| Role code | STORES |
| Role name | Stores |
| Approval limit (gross) | £0 |
| Purchasing approval authority | None |

## Responsibilities and permissions

Stores personnel across the Manchester and Leeds sites log goods inward discrepancies directly in the system [^r5]. The role manages quarantine cages and loading bays designated for rejected items, and carries out periodic perpetual inventory counts alongside scheduled formal stocktakes [^r5].

## Approval limits and escalation

Under the purchasing approval matrix in [[pol-apr-002|POL-APR-002]], the Stores role has no purchasing approval authority [^r3]. In the [[data-users-and-approval-limits|user master]] and system limits matrix, users holding the STORES role—such as [[user-atanaka|Aiko Tanaka]]—are configured with a gross approval limit of £0 [^r1][^r2].

Stock adjustments that exceed the stores limit cannot be approved by stores staff and trigger error code `ERR-ADJ-0420`, requiring sign-off by the [[role-plant-head|Plant Head]] [^r4].

## See also

* [[data-users-and-approval-limits|Users_and_approval_limits]]
* [[pol-apr-002|POL-APR-002 Approval Matrix for Purchasing]]
* [[role-plant-head|Role PLANT-HEAD]]
* [[user-atanaka|Aiko Tanaka (ATANAKA)]]

## References

[^r5]: 11_training/intranet_export_2016/page_working_with_stores.html, Handling goods inward discrepancies
[^r3]: 01_policies/POL-APR-002 Approval Matrix v3.0.pdf, p. 1, §3. The limits
[^r1]: 05_master_data/Users_and_approval_limits.xlsx, sheet Users, row ATANAKA, SHEET Users
[^r2]: 05_master_data/Users_and_approval_limits.xlsx, sheet Matrix, row STORES, SHEET Matrix
[^r4]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 11, adj_approve STOCK ADJUSTMENT APPROVE
