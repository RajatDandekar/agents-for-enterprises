---
title: "POL-SUP-003 Supplier Policy"
type: "policy"
slug: "pol-sup-003"
summary: "Governing policy for Ledgerline supplier master records, onboarding documentation, UN 38.3 battery certification, supplier blocking, and duplicate prevention."
audience: "staff"
status: "mixed"
sources: ["01_policies/AMD-SUP-2026-02 Amendment 2 Supplier Policy.pdf", "01_policies/POL-QUA-005 Quality Policy v3.0.pdf", "01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf", "01_policies/POL-SUP-003 Supplier Policy v2.3.pdf", "01_policies/old/Supplier_Policy_v2.2.docx", "02_procedures/SOP-PRD-002 Engineering Change v1.0.pdf", "02_procedures/SOP-PUR-004 Rate Contract Maintenance v2.0.pdf", "10_meeting_notes/2026-07-30 Battery incident review.md"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Document code | POL-SUP-003 |
| Version | 2.3 (amended by AMD-SUP-2026-02) |
| Owner | Purchase department |
| Approved by | Daniel Okafor (purchase manager) |
| Effective date | 2026-04-01 (amendment effective 2026-09-01) |
| Classification | Internal |
| Status | current |

POL-SUP-003 governs how supplier records are created, documented, maintained, and blocked in the Ledgerline master under [[pol-pur-001|POL-PUR-001]] §6 [^r5][^r6][^r38]. Version 2.3 became effective on 1 April 2026, approved by Purchase Manager [[user-dokafor|Daniel Okafor]] [^r5][^r38]. Effective 1 September 2026, clause §4.4 is amended by [[amd-sup-2026-02|AMD-SUP-2026-02]] to require [[topic-un-38-3-certificates|UN 38.3 certificates]] to be issued within the last 12 months with a valid-to date at least 60 days post-order placement, following a battery incident review [^r1][^r3][^r37].

| Field | Value |
|---|---|
| Document code | POL-SUP-003 |
| Version | 2.3 (with [[amd-sup-2026-02|AMD-SUP-2026-02]]) |
| Owner | Purchase department |
| Approved by | [[user-dokafor|Daniel Okafor]], purchase manager |
| Effective date | 2026-04-01 (amended 2026-09-01) |
| Classification | Internal |
| Status | Current |

## Clauses

### 1. Purpose
The policy governs how a supplier enters the supplier master in Ledgerline, what documentation it must provide, when it is blocked, and how duplicate registrations are prevented, sitting under Purchase Policy [[pol-pur-001|POL-PUR-001]] §6 [^r6][^r38].

### 2. Scope
The policy applies to every supplier of materials, components, packing, and services to the Manchester plant (NBC-MAN-01) and the Leeds unit (NBC-LDS-01) [^r7][^r39]. One-time cash purchases under £5,000 made from the petty-cash imprest are excluded from POL-SUP-003 and follow the Finance petty-cash note [^r8][^r39].

### 3. Onboarding a new supplier
A new supplier must be proposed by a purchase executive ([[role-pur-exec|Role PUR-EXEC]]) or senior buyer ([[role-pur-sr|Role PUR-SR]]) with at least one written quotation and an explanation of why an existing supplier cannot meet the need [^r9][^r40]. Before a supplier is created in Ledgerline screen [[screen-pur-sup-01|PUR-SUP-01]], the proposer must collect the VAT registration certificate (VAT number), company registration number, bank letter confirming the account, proof of insurance, and signed Supplier Code of Conduct [^r10][^r41]. The proposer must search the supplier master in Ledgerline using screen [[screen-pur-sup-03|PUR-SUP-03]] by name, city, and VAT number, and attach the search result to the onboarding file [^r11][^r42]. The purchase manager ([[role-pur-mgr|Role PUR-MGR]]) must approve the onboarding file before the supplier may be created in Ledgerline [^r12][^r43]. A supplier is ACTIVE from the day it is created in Ledgerline, but no purchase order may be placed until all mandatory documents and, for lithium-cell parts, the UN 38.3 certificate are on file [^r13][^r44]. Supplier onboarding normally takes five working days from receipt of a complete file, and urgency does not justify skipping any onboarding steps [^r14][^r45].

### 4. UN 38.3 certificates
Suppliers of any lithium-cell part (including battery packs [[items-bat|BAT-*]], hub motors, chargers, and any item marked lithium-cell in the item master) must hold a UN 38.3 certificate as referenced in [[pol-pur-001|POL-PUR-001]] §6.2 [^r15][^r46]. The UN 38.3 certificate must be an official test report from an accredited lithium-cell testing laboratory, such as an ISO/IEC 17025 accredited facility [^r16][^r46]. The UN 38.3 certificate is uploaded in Ledgerline against the supplier under certificate type UN38.3 with its document reference and valid-to date, and must be checked by the senior buyer before the first order [^r17][^r47]. Effective 1 September 2026 under [[amd-sup-2026-02|AMD-SUP-2026-02]], UN 38.3 certificates must be issued within the last 12 months with a valid-to date at least 60 days after the purchase order placement date [^r1]. Any certificate meeting the legacy POL-SUP-003 requirement (issued within 24 months and not expired) is treated as having no certificate for new purchase orders from 1 September 2026 [^r2]. An expired UN 38.3 certificate counts as no certificate; while the supplier remains ACTIVE in the master, no lithium-cell parts may be ordered until a valid certificate is uploaded and checked [^r19][^r48]. A UN 38.3 certificate covers the supplier rather than a single item, but if the supplier changes cells or design (such as a new cell maker or chemistry), it must provide a fresh test report for that part [^r20][^r35][^r49]. Ledgerline does not automatically stop an order to a supplier lacking a UN 38.3 certificate, so the check must be manually performed by both the order raiser and the approver [^r21][^r50]. Apart from the replacement of clause §4.4 by [[amd-sup-2026-02|AMD-SUP-2026-02]], the remainder of POL-SUP-003 §4 remains unaltered [^r3].

### 5. Blocking and unblocking
A supplier is marked BLOCKED in the master when replaced by a new code, when it fails two consecutive quality audits, or when requested by Finance due to unpaid debit notes [^r22][^r51]. Ledgerline retains the code and history of a blocked supplier but blocks creation of new orders with error code [[err-sup-0031|ERR-SUP-0031]] [^r23][^r52]. Only the purchase manager may request IT in writing to unblock a supplier, specifying the business reason [^r24][^r53]. When a supplier receives a new code, the old code is blocked and renamed '(old code, do not use)', as was done for [[sup-vc-ein-0009|Voltway Cells code VC-EIN-0009]] [^r25][^r54].

### 6. Duplicate suppliers
A legal supplier must have exactly one active code, and matching VAT numbers define whether two records represent the same supplier [^r26][^r55]. A supplier name closely matching an existing supplier in the same city must be treated as that existing supplier until proven otherwise [^r27][^r56]. A near-matching name in a different city or with a different VAT number represents a different supplier, such as [[sup-vpc-rot-0107|Voltway Paints & Coatings in Rotterdam]] versus [[sup-vc-ein-0042|Voltway Cells in Eindhoven]] [^r28][^r56]. Ledgerline raises [[err-sup-0118|ERR-SUP-0118]] when an attempt is made to register an existing VAT number, but does not block duplicate names entered without a VAT number [^r29][^r57]. Any accidental duplicate supplier must be reported to the purchase manager the same day, set to BLOCKED, and have its open documents transferred to the valid code [^r30][^r58].

### 7. Rate contracts
Every regular supplier of a regular item has a rate contract in Ledgerline defined with valid-from and valid-to dates [^r31][^r59]. A new rate contract supersedes an older contract from its valid-from date, while historical rates remain stored for reference [^r32]. Under §7.3, rate contracts are formally reviewed every six months, specifically in March and September, supported by the rate-contract expiry report (JOB-PUR-031) listing contracts ending within 45 days [^r33][^r36][^r59].

### 8. Supplier performance
The senior buyer evaluates regular suppliers every quarter based on on-time delivery, rejection rate, and pricing [^r34][^r60]. Under §8.2 and [[pol-qua-005|POL-QUA-005]] §4, a supplier whose rejection rate exceeds 2% for two consecutive quarters is placed on watch status, triggering a corrective action request from purchasing and Quality inspections [^r4][^r60].

## Versions and conflicts

* **UN 38.3 certificate validity (§4.4)**: Effective 1 September 2026 under [[amd-sup-2026-02|AMD-SUP-2026-02]], UN 38.3 test certificates must be issued within the last 12 months with a valid-to date at least 60 days after the purchase order placement date; any certificate issued within 24 months but over 12 months old is treated as having no certificate for new orders [^r1][^r2]. Under the unamended text of POL-SUP-003 v2.3 §4.4 (effective 2026-04-01) and superseded v2.2, certificates were accepted if issued within the prior 24 months and not past their valid-to date [^r18][^r48][^r70]. Kind: `superseded` [^r1][^r2][^r18][^r48][^r70].

## See also

* [[amd-sup-2026-02|AMD-SUP-2026-02 Amendment 2 to the Supplier Policy]]
* [[pol-pur-001|POL-PUR-001 Purchase Policy]]
* [[pol-qua-005|POL-QUA-005 Quality Policy]]
* [[sop-pur-001|SOP-PUR-001 Supplier Onboarding]]
* [[sop-pur-004|SOP-PUR-004 Rate Contract Maintenance]]
* [[sop-pur-005|SOP-PUR-005 Certificate Renewal (UN 38.3)]]
* [[sop-prd-002|SOP-PRD-002 Engineering Change (ECN)]]
* [[topic-un-38-3-certificates|UN 38.3 Certificates]]
* [[decision-2026-07-30-battery-incident-review|Battery Incident Review and Supplier Policy Amendment Decision (2026-07-30)]]
* [[screen-pur-sup-01|PUR-SUP-01 Supplier Master Create]]
* [[screen-pur-sup-03|PUR-SUP-03 Supplier Enquiry]]
* [[err-sup-0031|ERR-SUP-0031 Supplier is blocked]]
* [[err-sup-0118|ERR-SUP-0118 VAT number already registered]]
* [[errors-sup|ERR-SUP Error Codes]]
* [[sup-vc-ein-0042|Voltway Cells (VC-EIN-0042)]]
* [[sup-vc-ein-0009|Voltway Cells (old code, do not use) (VC-EIN-0009)]]
* [[sup-vpc-rot-0107|Voltway Paints & Coatings (VPC-ROT-0107)]]
* [[items-bat|BAT-* items]]

## References

[^r5]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 1, Version history
[^r6]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 1, §1. Purpose
[^r38]: 01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf, p. 1, Supplier Policy
[^r1]: 01_policies/AMD-SUP-2026-02 Amendment 2 Supplier Policy.pdf, p. 1, §1. What changes
[^r3]: 01_policies/AMD-SUP-2026-02 Amendment 2 Supplier Policy.pdf, p. 1, §3. What purchase staff must do
[^r37]: 10_meeting_notes/2026-07-30 Battery incident review.md, Discussion
[^r7]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 1, §2. Scope
[^r39]: 01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf, p. 1, §2. Scope
[^r8]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 1, §2. Scope
[^r9]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 1, §3. Onboarding a new supplier
[^r40]: 01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf, p. 1, §3. Onboarding a new supplier
[^r10]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 1, §3. Onboarding a new supplier
[^r41]: 01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf, p. 1, §3. Onboarding a new supplier
[^r11]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 1, §3. Onboarding a new supplier
[^r42]: 01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf, p. 1, §3. Onboarding a new supplier
[^r12]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 1, §3. Onboarding a new supplier
[^r43]: 01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf, p. 1, §3. Onboarding a new supplier
[^r13]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 1, §3. Onboarding a new supplier
[^r44]: 01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf, p. 1, §3. Onboarding a new supplier
[^r14]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 1, §3. Onboarding a new supplier
[^r45]: 01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf, p. 1, §3. Onboarding a new supplier
[^r15]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 2, §4. UN 38.3 certificates
[^r46]: 01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf, p. 2, §4. UN 38.3 certificates
[^r16]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 2, §4. UN 38.3 certificates
[^r17]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 2, §4. UN 38.3 certificates
[^r47]: 01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf, p. 2, §4. UN 38.3 certificates
[^r2]: 01_policies/AMD-SUP-2026-02 Amendment 2 Supplier Policy.pdf, p. 1, §1. What changes
[^r19]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 2, §4. UN 38.3 certificates
[^r48]: 01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf, p. 2, §4. UN 38.3 certificates
[^r20]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 2, §4. UN 38.3 certificates
[^r35]: 02_procedures/SOP-PRD-002 Engineering Change v1.0.pdf, p. 3, §5. Procedure
[^r49]: 01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf, p. 2, §4. UN 38.3 certificates
[^r21]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 2, §4. UN 38.3 certificates
[^r50]: 01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf, p. 2, §4. UN 38.3 certificates
[^r22]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 2, §5. Blocking and unblocking
[^r51]: 01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf, p. 2, §5. Blocking and unblocking
[^r23]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 2, §5. Blocking and unblocking
[^r52]: 01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf, p. 2, §5. Blocking and unblocking
[^r24]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 2, §5. Blocking and unblocking
[^r53]: 01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf, p. 2, §5. Blocking and unblocking
[^r25]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 2, §5. Blocking and unblocking
[^r54]: 01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf, p. 2, §5. Blocking and unblocking
[^r26]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 2, §6. Duplicate suppliers
[^r55]: 01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf, p. 2, §6. Duplicate suppliers
[^r27]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 2, §6. Duplicate suppliers
[^r56]: 01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf, p. 2, §6. Duplicate suppliers
[^r28]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 2, §6. Duplicate suppliers
[^r29]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 2, §6. Duplicate suppliers
[^r57]: 01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf, p. 2, §6. Duplicate suppliers
[^r30]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 2, §6. Duplicate suppliers
[^r58]: 01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf, p. 2, §6. Duplicate suppliers
[^r31]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 3, §7. Rate contracts
[^r59]: 01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf, p. 3, §7. Rate contracts
[^r32]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 3, §7. Rate contracts
[^r33]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 3, §7. Rate contracts
[^r36]: 02_procedures/SOP-PUR-004 Rate Contract Maintenance v2.0.pdf, p. 3, §5. Procedure
[^r34]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 3, §8. Supplier performance
[^r60]: 01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf, p. 3, §8. Supplier performance
[^r4]: 01_policies/POL-QUA-005 Quality Policy v3.0.pdf, p. 3, §4. Supplier quality
[^r18]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 2, §4. UN 38.3 certificates
[^r70]: 01_policies/old/Supplier_Policy_v2.2.docx, §4. UN 38.3 certificates
