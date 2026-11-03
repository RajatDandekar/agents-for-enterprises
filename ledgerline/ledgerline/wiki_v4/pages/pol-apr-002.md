---
title: "POL-APR-002 Approval Matrix for Purchasing"
type: "policy"
slug: "pol-apr-002"
summary: "Purchasing approval matrix establishing gross document authorization tiers up to £5,000,000, self-approval prohibitions, and service account restrictions."
audience: "staff"
status: "mixed"
sources: ["05_master_data/Users_and_approval_limits.xlsx", "07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf", "01_policies/POL-APR-002 Approval Matrix v3.0.pdf", "01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf", "01_policies/old/Approval_Matrix_v2.0_2024.docx", "02_procedures/SOP-IT-001 User Access Request v1.6.pdf", "02_procedures/SOP-IT-002 Service Account Management v1.0.pdf", "11_training/intranet_export_2016/approval_limits.html"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | POL-APR-002 |
| Owner | Plant head's office |
| Approver | Henrik Weber |
| Version | 3.0 |
| Effective | 2026-04-01 |
| Status | current |
| Audience | staff |

POL-APR-002 defines the financial approval matrix referenced in [[pol-pur-001|POL-PUR-001]] §5.2 for purchasing commitments across Northbridge Cycles [^r4]. It sets the gross authority limits including VAT for approving purchase requests and purchase orders up to £5,000,000 [^r4][^r8]. As of 26 October 2026, version 3.0 is in force, mandating strict controls against self-approval, order splitting, and the use of automated service accounts for authorization [^r3][^r7][^r12][^r13].

| Field | Value |
|---|---|
| Document Code | POL-APR-002 |
| Version | 3.0 |
| Owner | Plant head's office |
| Approver | [[user-hweber|Henrik Weber]] |
| Effective Date | 2026-04-01 |
| Status | current |

## Clauses

### 1. Purpose
POL-APR-002 is the purchasing approval matrix referred to in [[pol-pur-001|POL-PUR-001]] §5.2 and sets who may approve a purchase request or purchase order and up to what value [^r4].

### 2. How limits are measured
Every approval limit is evaluated on the gross value including VAT of one document, and any freight or packing charged on the order counts towards this gross value [^r5][^r26]. Under Ledgerline 7.2 table `usr_hdr`, the field `appr_limit` stores this user approval limit gross including VAT [^r2]. Approval limits apply per document, not per day or per supplier [^r6]. Splitting a single requirement into multiple orders to remain within an approval limit is prohibited, and orders for the same item from the same supplier raised within seven days of each other are treated as one requirement [^r7].

### 3. The limits
When IT configures a user role in Ledgerline, the financial ceiling is set strictly to the job title limits defined in POL-APR-002 [^r16]. The gross approval limits including VAT across the company are [^r1][^r8]:
* [[role-pur-exec|PUR-EXEC]] (Purchase executive): £250,000 [^r1][^r8]
* [[role-pur-sr|PUR-SR]] (Senior buyer): £500,000 [^r1][^r8]
* [[role-pur-mgr|PUR-MGR]] (Purchase manager): £1,000,000 [^r1][^r8]
* [[role-plant-head|PLANT-HEAD]] (Plant head): £5,000,000 [^r1][^r8]
* [[role-stores|STORES]]: £0 (no approval authority) [^r1][^r8]

If a document falls within the raiser's own approval limit, it is approved upon submission and Ledgerline records the raiser as the approver [^r9]. A document exceeding the raiser's limit routes to their manager, and if the manager's limit is insufficient, it escalates up the reporting line to the first person possessing adequate authority [^r10][^r27]. Orders exceeding £5,000,000 trigger Ledgerline error [[err-apr-0009|ERR-APR-0009]], requiring the Managing Director's written approval outside Ledgerline before the plant head's office records it [^r11].

### 4. Who may not approve
Under [[pol-pur-001|POL-PUR-001]] §5.3, no user may approve a document they raised, which Ledgerline enforces by throwing [[err-apr-0003|ERR-APR-0003]] [^r12][^r27]. In accordance with POL-APR-002 §4.2 and [[sop-it-002|SOP-IT-002]], integration and service accounts holding role SYS-ADMIN (such as [[user-svc-agent|SVC_AGENT]]) possess no approval authority regardless of technical permissions [^r13][^r17]. Any document approved by a service account is treated as unapproved and must be cancelled or re-approved by a person [^r13]. An approver on leave may delegate authority in writing to an individual of the same or higher role for a defined period, but delegation to a lower role is prohibited [^r14].

### 6. Review
The plant head reviews POL-APR-002 annually every April, as well as whenever organisational changes occur [^r15].

## Versions and conflicts

* **Gross vs. net evaluation**: Today, limits are evaluated on the gross document value including VAT and any packing or freight charges [^r5][^r26]. Under the legacy 2016 intranet authorisation tiers, limits were calculated strictly on net value before VAT [^r18][^r19] (`superseded`).
* **Revised role approval thresholds**: Effective 2026-04-01 under version 3.0, the limits are £250,000 for [[role-pur-exec|PUR-EXEC]], £500,000 for [[role-pur-sr|PUR-SR]], £1,000,000 for [[role-pur-mgr|PUR-MGR]], and £5,000,000 for [[role-plant-head|PLANT-HEAD]] [^r3][^r8]. Under superseded version 2.0 (effective 2024-04-01), the limits were £200,000 for PUR-EXEC, £400,000 for PUR-SR, £750,000 for PUR-MGR, and £5,000,000 for PLANT-HEAD [^r31][^r32][^r33][^r34] (`superseded`).

## See also

* [[pol-pur-001|POL-PUR-001 Purchase Policy]]
* [[role-pur-exec|Role PUR-EXEC]]
* [[role-pur-sr|Role PUR-SR]]
* [[role-pur-mgr|Role PUR-MGR]]
* [[role-plant-head|Role PLANT-HEAD]]
* [[role-stores|Role STORES]]
* [[err-apr-0003|ERR-APR-0003 Self-approval not permitted]]
* [[err-apr-0009|ERR-APR-0009 No approver found]]
* [[errors-apr|Errors APR]]
* [[sop-it-001|SOP-IT-001 User Access Request]]
* [[sop-it-002|SOP-IT-002 Service Account Management]]
* [[data-users-and-approval-limits|Users_and_approval_limits]]
* [[man-dd-72-all|MAN-DD-72-ALL Ledgerline ERP 7.2 Data Dictionary: all]]
* [[user-hweber|Henrik Weber (HWEBER)]]
* [[user-svc-agent|Integration service account (SVC_AGENT)]]

## References

[^r4]: 01_policies/POL-APR-002 Approval Matrix v3.0.pdf, p. 1, §1. Purpose
[^r8]: 01_policies/POL-APR-002 Approval Matrix v3.0.pdf, p. 1, §3. The limits
[^r3]: 01_policies/POL-APR-002 Approval Matrix v3.0.pdf, p. 1, Version history
[^r7]: 01_policies/POL-APR-002 Approval Matrix v3.0.pdf, p. 1, §2. How limits are measured
[^r12]: 01_policies/POL-APR-002 Approval Matrix v3.0.pdf, p. 2, §4. Who may not approve
[^r13]: 01_policies/POL-APR-002 Approval Matrix v3.0.pdf, p. 2, §4. Who may not approve
[^r5]: 01_policies/POL-APR-002 Approval Matrix v3.0.pdf, p. 1, §2. How limits are measured
[^r26]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 2, §5. Approval limits
[^r2]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 21, Table usr_hdr
[^r6]: 01_policies/POL-APR-002 Approval Matrix v3.0.pdf, p. 1, §2. How limits are measured
[^r16]: 02_procedures/SOP-IT-001 User Access Request v1.6.pdf, p. 3, §5. Procedure: notes and common mistakes
[^r1]: 05_master_data/Users_and_approval_limits.xlsx, sheet Matrix, row PUR-EXEC, SHEET Matrix
[^r9]: 01_policies/POL-APR-002 Approval Matrix v3.0.pdf, p. 1, §3. The limits
[^r10]: 01_policies/POL-APR-002 Approval Matrix v3.0.pdf, p. 1, §3. The limits
[^r27]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 2, §5. Approval limits
[^r11]: 01_policies/POL-APR-002 Approval Matrix v3.0.pdf, p. 1, §3. The limits
[^r17]: 02_procedures/SOP-IT-002 Service Account Management v1.0.pdf, p. 3, §5. Procedure
[^r14]: 01_policies/POL-APR-002 Approval Matrix v3.0.pdf, p. 2, §4. Who may not approve
[^r15]: 01_policies/POL-APR-002 Approval Matrix v3.0.pdf, p. 2, §6. Review
[^r18]: 11_training/intranet_export_2016/approval_limits.html, Approval limits (2016)
[^r19]: 11_training/intranet_export_2016/approval_limits.html, Approval limits (2016)
[^r31]: 01_policies/old/Approval_Matrix_v2.0_2024.docx, Status | SUPERSEDED
[^r32]: 01_policies/old/Approval_Matrix_v2.0_2024.docx, Status | SUPERSEDED
[^r33]: 01_policies/old/Approval_Matrix_v2.0_2024.docx, Status | SUPERSEDED
[^r34]: 01_policies/old/Approval_Matrix_v2.0_2024.docx, Status | SUPERSEDED
