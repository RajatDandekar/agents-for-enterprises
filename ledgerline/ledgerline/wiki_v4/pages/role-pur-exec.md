---
title: "Role PUR-EXEC"
type: "role"
slug: "role-pur-exec"
summary: "Ledgerline role for purchase executives with an approval limit of £250,000 gross and standard buying permissions."
audience: "staff"
status: "mixed"
sources: ["05_master_data/Users_and_approval_limits.xlsx", "01_policies/POL-APR-002 Approval Matrix v3.0.pdf", "01_policies/POL-SUP-003 Supplier Policy v2.3.pdf", "01_policies/old/Approval_Matrix_v2.0_2024.docx", "11_training/New starter - Purchasing (2024) deck export.pdf", "11_training/intranet_export_2016/approval_limits.html", "09_email_archive/2019/2019-08-07_New starters in purchasing.eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Role code | PUR-EXEC |
| Role name | Purchase Executive |
| Approval limit | £250,000 gross (inc. VAT) |
| Status | current |

Role PUR-EXEC represents the standard purchase executive in Ledgerline ERP, holding an operational approval limit of £250,000 gross including VAT [^r1][^r2][^r3]. Users assigned this role, such as [[user-eclarke|Emma Clarke]], can execute everyday procurement transactions and initiate vendor onboarding proposals [^r1][^r4]. It provides buyers with core system capabilities while restricting sensitive vendor financial updates and high-value authorisations to more senior roles [^r10].

## Responsibilities and permissions

Users with the PUR-EXEC role are authorised to initiate supplier onboarding proposals by obtaining written quotations and drafting business justifications [^r4]. When proposing a new vendor, the purchase executive must check for duplicate records in [[screen-pur-sup-03|PUR-SUP-03]] and collate all statutory and commercial documentation [^r5].

In daily Ledgerline operations, standard buyer permissions allow PUR-EXEC users to raise purchase requisitions, generate purchase orders, and amend delivery schedules against active supply contracts [^r8]. Standard buyers are granted enquiry access to current stock balances, goods received notes, and supplier master records so they can track outstanding consignments without contacting stores clerks [^r9].

Users in this role cannot authorise purchase orders above the PUR-EXEC threshold and are strictly restricted from altering vendor bank details, which remain reserved for senior staff and finance [^r10].

## Approval limits

Under the current approval matrix in [[pol-apr-002|POL-APR-002]], the approval limit for role PUR-EXEC is £250,000 gross including VAT [^r2][^r3]. Configured users in the user master holding this role, including [[user-eclarke|Emma Clarke]], share this £250,000 gross ceiling [^r1].

## Versions and conflicts

* **Gross limit of £250,000 vs. prior £200,000 limit**: Under [[pol-apr-002|POL-APR-002]] v3.0 (effective 2026-04-01) and the current [[data-users-and-approval-limits|user master]], the PUR-EXEC approval limit is £250,000 gross including VAT [^r1][^r2][^r3]. Under superseded policy POL-APR-002 v2.0 (effective 2024-04-01) and the 2024 new starter training deck, the purchase executive approval limit was set at £200,000 gross, above which manager approval was required [^r6][^r11]. Kind: `superseded`.
* **Gross calculation vs. 2016 net threshold**: Under current policy, limits are strictly evaluated on gross value including VAT [^r3]. Under the 2016 intranet approval limits, the Purchase executive role had an approval limit of £150,000 net before VAT [^r7]. Kind: `superseded`.

## See also

* [[pol-apr-002|POL-APR-002 Approval Matrix for Purchasing]]
* [[pol-sup-003|POL-SUP-003 Supplier Policy]]
* [[role-pur-mgr|Role PUR-MGR]]
* [[role-pur-sr|Role PUR-SR]]
* [[screen-pur-sup-03|PUR-SUP-03 Supplier Enquiry]]
* [[user-eclarke|Emma Clarke (ECLARKE)]]
* [[data-users-and-approval-limits|Users_and_approval_limits]]

## References

[^r1]: 05_master_data/Users_and_approval_limits.xlsx, sheet Users, row ECLARKE, SHEET Users
[^r2]: 05_master_data/Users_and_approval_limits.xlsx, sheet Matrix, row PUR-EXEC, SHEET Matrix
[^r3]: 01_policies/POL-APR-002 Approval Matrix v3.0.pdf, p. 1, §3. The limits
[^r4]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 3, Appendix A. Guidance for proposers
[^r10]: 09_email_archive/2019/2019-08-07_New starters in purchasing.eml, body
[^r5]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 1, §3. Onboarding a new supplier
[^r8]: 09_email_archive/2019/2019-08-07_New starters in purchasing.eml, body
[^r9]: 09_email_archive/2019/2019-08-07_New starters in purchasing.eml, body
[^r6]: 11_training/New starter - Purchasing (2024) deck export.pdf, p. 4, Your limit
[^r11]: 01_policies/old/Approval_Matrix_v2.0_2024.docx, Status | SUPERSEDED
[^r7]: 11_training/intranet_export_2016/approval_limits.html, Approval limits (2016)
