---
title: "Role PUR-SR"
type: "role"
slug: "role-pur-sr"
summary: "Role PUR-SR (Senior Buyer) with a gross purchasing approval limit of £500,000, responsible for supplier onboarding, UN 38.3 compliance, and performance reviews."
audience: "staff"
status: "mixed"
sources: ["05_master_data/Users_and_approval_limits.xlsx", "01_policies/AMD-SUP-2026-02 Amendment 2 Supplier Policy.pdf", "01_policies/POL-APR-002 Approval Matrix v3.0.pdf", "01_policies/POL-SUP-003 Supplier Policy v2.3.pdf", "01_policies/old/Approval_Matrix_v2.0_2024.docx", "11_training/QRC-05 Uploading a supplier certificate.pdf", "11_training/intranet_export_2016/approval_limits.html"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Role code | PUR-SR |
| Title | Senior Buyer |
| Gross approval limit | £500,000 |
| Key responsibilities | Supplier onboarding, UN 38.3 certificate compliance, supplier performance reviews |
| Example users | LMORENO |
| Current policy | POL-APR-002 v3.0 |

Role PUR-SR is the Senior Buyer role in Ledgerline Purchasing, holding an individual gross purchasing approval limit of £500,000 including VAT [^r2][^r4]. It carries operational responsibility for supplier onboarding proposals, UN 38.3 certificate monitoring, and quarterly supplier performance assessments [^r3][^r5][^r7]. Active personnel assigned to this role include [[user-lmoreno|Luis Moreno]] [^r1].

## Limits and permissions

The approval limit for role PUR-SR is £500,000 gross including VAT [^r2][^r4]. Users configured with this role in the user master within [[data-users-and-approval-limits|Users_and_approval_limits]], such as [[user-lmoreno|Luis Moreno]], inherit this £500,000 gross ceiling [^r1].

## Responsibilities

Senior buyers holding role PUR-SR are authorized to initiate new supplier onboarding proposals alongside purchase executives [^r5]. They also review regular quarterly supplier performance covering on-time delivery, rejection rate, and pricing [^r7].

The role holds specific duties regarding [[topic-un-38-3-certificates|UN 38.3 certificates]]:
* Prior to raising an initial order for lithium parts, the senior buyer must inspect the uploaded UN 38.3 test certificate in Ledgerline [^r6].
* Per [[qrc-05|QRC-05]], the senior buyer must inspect the on-screen supplier certificate record alongside form NBC-F-113 and initial NBC-F-113 before any pending purchase orders can be released for delivery [^r8].
* Under [[amd-sup-2026-02|AMD-SUP-2026-02]], the senior buyer must run the certificate-expiry report per [[man-pur-72|MAN-PUR-72]] §22.6 on the first working day of each month using a 90-day window and write to suppliers whose UN 38.3 certificates expire within that period [^r3].

## Versions and conflicts

* **Approval limit threshold (superseded):** Today's rule under [[pol-apr-002|POL-APR-002]] v3.0 (effective 2026-04-01) and current master data is £500,000 gross including VAT [^r2][^r4]. Under superseded policy POL-APR-002 v2.0 (effective 2024-04-01), the limit was £400,000 gross including VAT [^r10]. Under the 2016 intranet export, the limit was £300,000 net before VAT [^r9].

## See also

* [[amd-sup-2026-02|AMD-SUP-2026-02 Amendment 2 to the Supplier Policy]]
* [[data-users-and-approval-limits|Users_and_approval_limits]]
* [[man-pur-72|MAN-PUR-72 Ledgerline ERP 7.2 User Manual, Purchasing]]
* [[pol-apr-002|POL-APR-002 Approval Matrix for Purchasing]]
* [[pol-sup-003|POL-SUP-003 Supplier Policy]]
* [[qrc-05|QRC-05 Uploading a supplier certificate]]
* [[role-pur-exec|Role PUR-EXEC]]
* [[role-pur-mgr|Role PUR-MGR]]
* [[topic-un-38-3-certificates|UN 38.3 Certificates]]
* [[user-lmoreno|Luis Moreno (LMORENO)]]

## References

[^r2]: 05_master_data/Users_and_approval_limits.xlsx, sheet Matrix, row PUR-SR, SHEET Matrix
[^r4]: 01_policies/POL-APR-002 Approval Matrix v3.0.pdf, p. 1, §3. The limits
[^r3]: 01_policies/AMD-SUP-2026-02 Amendment 2 Supplier Policy.pdf, p. 1, §3. What purchase staff must do
[^r5]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 1, §3. Onboarding a new supplier
[^r7]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 3, §8. Supplier performance
[^r1]: 05_master_data/Users_and_approval_limits.xlsx, sheet Users, row LMORENO, SHEET Users
[^r6]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 2, §4. UN 38.3 certificates
[^r8]: 11_training/QRC-05 Uploading a supplier certificate.pdf, p. 1, Verification and sign-off
[^r10]: 01_policies/old/Approval_Matrix_v2.0_2024.docx, Status | SUPERSEDED
[^r9]: 11_training/intranet_export_2016/approval_limits.html, Approval limits (2016)
