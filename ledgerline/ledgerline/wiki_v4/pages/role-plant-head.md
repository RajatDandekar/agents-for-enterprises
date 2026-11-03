---
title: "Role PLANT-HEAD"
type: "role"
slug: "role-plant-head"
summary: "Ledgerline role for the Plant Head with a £5,000,000 gross approval limit, oversight of high-value stock adjustments, and corporate hospitality approvals."
audience: "staff"
status: "mixed"
sources: ["05_master_data/Users_and_approval_limits.xlsx", "01_policies/POL-ABC-011 Anti-Bribery and Gifts Policy v1.3.pdf", "01_policies/POL-APR-002 Approval Matrix v3.0.pdf", "01_policies/old/Approval_Matrix_v2.0_2024.docx", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "11_training/intranet_export_2016/approval_limits.html"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Role code | PLANT-HEAD |
| Role title | Plant Head |
| Gross approval limit | £5,000,000 |
| Current holder | Henrik Weber (HWEBER) |
| Governing policy | POL-APR-002 |
| Status | current |

The PLANT-HEAD role represents the Plant Head in Ledgerline and sets executive operational sign-off across manufacturing, purchasing, and inventory control [^r1][^r4][^r5]. It carries a gross approval limit of £5,000,000 including VAT, currently assigned to users including [[user-hweber|Henrik Weber]] [^r1][^r2][^r4]. In addition to commercial purchasing authority, the role is required for high-value stock adjustment approvals and anti-bribery hospitality authorisations [^r3][^r5].

| Field | Value |
|---|---|
| Role Code | PLANT-HEAD [^r2] |
| Description | Plant Head [^r4] |
| Approval Limit | £5,000,000 gross (including VAT) [^r2][^r4] |
| Assigned Users | [[user-hweber|Henrik Weber (HWEBER)]] [^r1] |

## Responsibilities and approval limits

Under [[pol-apr-002|POL-APR-002]], the PLANT-HEAD role holds a gross purchasing approval threshold of £5,000,000 including VAT, recorded in both the approval matrix and the user master [[data-users-and-approval-limits|Users_and_approval_limits.xlsx]] [^r1][^r2][^r4].

The role also acts as the escalation authority across other plant operational workflows:
* **Stock adjustments:** When an inventory adjustment exceeds the standard threshold for [[role-stores|stores]], the system raises error ERR-ADJ-0420 requiring PLANT-HEAD approval before the adjustment can be posted [^r5].
* **Hospitality pre-approvals:** Under [[pol-abc-011|POL-ABC-011]], any corporate hospitality exceeding £150 per head requires advance approval from the PLANT-HEAD role via internal e-mail [^r3].

## Versions and conflicts

* **Approval limit definition:** Today's rule under POL-APR-002 v3.0 (effective 2026-04-01) sets the limit at £5,000,000 gross including VAT, which was also the limit in superseded policy POL-APR-002 v2.0 effective 2024-04-01 [^r4][^r7]. The historical 2016 intranet guidance set an approval limit of £2,000,000 net before VAT, which is superseded [^r6]. Kind: `superseded` [^r4][^r6].

## See also

* [[data-users-and-approval-limits|Users_and_approval_limits]]
* [[pol-abc-011|POL-ABC-011 Anti-Bribery and Gifts Policy]]
* [[pol-apr-002|POL-APR-002 Approval Matrix for Purchasing]]
* [[role-pur-mgr|Role PUR-MGR]]
* [[role-stores|Role STORES]]
* [[user-hweber|Henrik Weber (HWEBER)]]

## References

[^r1]: 05_master_data/Users_and_approval_limits.xlsx, sheet Users, row HWEBER, SHEET Users
[^r4]: 01_policies/POL-APR-002 Approval Matrix v3.0.pdf, p. 1, §3. The limits
[^r5]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 11, adj_approve STOCK ADJUSTMENT APPROVE
[^r2]: 05_master_data/Users_and_approval_limits.xlsx, sheet Matrix, row PLANT-HEAD, SHEET Matrix
[^r3]: 01_policies/POL-ABC-011 Anti-Bribery and Gifts Policy v1.3.pdf, p. 3, Practical Application
[^r7]: 01_policies/old/Approval_Matrix_v2.0_2024.docx, Status | SUPERSEDED
[^r6]: 11_training/intranet_export_2016/approval_limits.html, Approval limits (2016)
