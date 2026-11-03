---
title: "UN 38.3 Certificates"
type: "topic"
slug: "topic-un-38-3-certificates"
summary: "UN 38.3 lithium battery transport certification rules, manual PO controls, renewal tracking, and ERP validation across Northbridge Cycles operations."
audience: "staff"
status: "mixed"
sources: ["05_master_data/SUPPLIER_MASTER.xlsx", "07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf", "01_policies/AMD-SUP-2026-02 Amendment 2 Supplier Policy.pdf", "01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf", "01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf", "01_policies/POL-SUP-003 Supplier Policy v2.3.pdf", "01_policies/old/Purchase Policy v4.0.docx", "01_policies/old/Supplier_Policy_v2.2.docx", "01_policies/old/purchase_policy_v3_2019.docx", "02_procedures/SOP-PRD-002 Engineering Change v1.0.pdf", "02_procedures/SOP-PUR-001 Supplier Onboarding v3.1.pdf", "02_procedures/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf", "02_procedures/SOP-PUR-006 Quotations and Supplier Selection v1.0.pdf", "02_procedures/forms/Final_FINAL_onboarding checklist NBC-F-113.docx", "02_procedures/old/SOP-PUR-001 Supplier onboarding v2.0 (2021).docx", "08_release_notes/RN-7.2.3-P4 Ledgerline Patch Notes.pdf", "08_release_notes/RN-7.3 PREVIEW (planned March 2027).pdf", "11_training/New starter - Purchasing (2024) deck export.pdf", "11_training/QRC-05 Uploading a supplier certificate.pdf", "10_meeting_notes/2026-09-17 Supplier review - Voltway Cells.docx", "10_meeting_notes/2026-10-19 Weekly purchasing meeting.md", "09_email_archive/2026/2026-06-15_Voltway battery packs - receive straight into main stores.eml", "09_email_archive/2026/2026-07-28_Failed battery lot - incoming abuse test.eml", "09_email_archive/2026/2026-09-02_Approving orders for lithium-cell parts - CERT OK in the approval comment.eml", "09_email_archive/2026/2026-09-29_UN 38.3 report renewal.eml", "09_email_archive/2026/2026-10-01_CERT EXPIRED - DO NOT ORDER_ Nordic Cell Co. (NC-GDA-0063).eml", "09_email_archive/2026/2026-10-22_Quotation Q-BE-26-0917 - Brightcell Energy.eml", "09_email_archive/2026/2026-10-23_RE_ Brightcell quote - can we switch from Voltway_.eml", "06_transactions/reports/Certificate expiry report 2026-10-01.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Topic | UN 38.3 Lithium Battery Certificates |
| Lead policy | POL-SUP-003, AMD-SUP-2026-02 |
| Scope | Lithium-cell parts (BAT-*, hub motors, chargers) |
| ERP table | sup_cert (cert_type UN38.3) |
| Approval mandate | CERT OK comment on PO release |
| Current system status | Manual enforcement (PUR.CERT_CHK is N) |

UN 38.3 certificates verify compliance with United Nations transport safety testing for lithium-cell components across Northbridge Cycles [^r8][^r35]. Since 1 September 2026, Northbridge requires all suppliers of lithium-cell items to hold a UN 38.3 report issued within the preceding 12 months and valid for at least 60 days beyond the purchase order date [^r5][^r13]. Because automated blocking is inactive in Ledgerline ERP, purchasing staff and approvers must manually verify valid certificates before placing orders [^r11][^r14][^r47].

## Scope and Supplier Requirements

A verified UN 38.3 test report from an accredited testing laboratory, such as an ISO/IEC 17025 accredited facility, is mandatory for all vendors supplying lithium-cell parts [^r35]. This requirement applies to [[items-bat|battery packs]], [[items-mtr|hub motors]], [[items-chg|chargers]], and any item flagged with `cell_safety = 1` or marked lithium-cell in the item master [^r8][^r35]. Transport verification specifically requires the UN 38.3 test summary containing the accredited laboratory identification and manufacturer authorized signature rather than the full factory test report [^r15].

Certificates apply at the supplier level, but any change to part design, cell chemistry, casing seals, or battery management firmware invalidates existing testing and mandates a fresh UN 38.3 test report [^r10][^r16]. Under [[sop-prd-002|SOP-PRD-002]], an engineering change order introducing an alternative cell maker or altered pack design requires a verified UN 38.3 report logged in the technical archive prior to ECN release; failure to provide it halts pack sub-assembly at Leeds and quarantines incoming packs at Manchester [^r12]. Physical copies of UN 38.3 summaries must be maintained in dispatch office dangerous goods binders at both Manchester and Leeds, while superseded versions are moved to an archive directory [^r19].

## Purchasing and Quotation Controls

Prospective battery pack suppliers must submit a UN 38.3 transportation test summary report during onboarding evaluations [^r39]. Under [[sop-pur-006|SOP-PUR-006]], quotations for lithium-cell parts may only be compared among suppliers holding a valid UN 38.3 test certificate, and price alone must never determine selection [^r20]. A verified certificate must be attached to the supplier master record or entered against the quotation in Ledgerline before the quote can be marked acceptable [^r22]. If a quotation contains an expired, incomplete, or ambiguous certificate, the offer must be set aside immediately until verified by quality engineering [^r21]. Prospective supplier Brightcell Energy currently lacks an active UN 38.3 test report while renewing with their laboratory, leaving their quotation pending until replacement documentation arrives [^r48].

Under onboarding checklist NBC-F-113, the proposer uploads the certificate with document reference and validity dates, which the senior buyer verifies before sign-off [^r23][^r24][^r30]. Following an incident on 28 July 2026 where an incoming abuse test failed on 400 battery packs with a 22-month-old test report from an unnotified cell maker change, Quality Manager [[user-pjansen|Pieter Jansen]] recommended tightening certificate validity [^r42][^r43][^r44]. Order approval now mandates entering `CERT OK` and the certificate reference (such as `CERT OK UN38.3-TR/VC/2026/118`) into the purchase order approval comment [^r45].

## ERP Records and System Enforcement

In Ledgerline ERP 7.2, certificate records are stored in the `sup_cert` table under `cert_type`, containing `doc_ref`, `valid_to`, `uploaded_by`, and `uploaded_on` [^r4]. Data is recorded in the supplier master under type `UN38.3` alongside the scanned attachment [^r29]. Active records in [[data-supplier-master|SUPPLIER_MASTER]] include [[user-lmoreno|Luis Moreno]]'s uploads for CC-SAL-0031 (certificate UN38.3-TR/CC/2026/044, valid to 2027-01-31) and AM-BIR-0008 (certificate UN38.3-TR/AM/2026/301, valid to 2027-06-30) [^r1][^r2]. [[sup-vc-ein-0042|Voltway Cells]] holds active certificate UN38.3-TR/VC/2026/118 valid through 31 March 2027, permitting direct receipt into WH-MAN-STR without quarantine and supporting technical construction files in Leeds [^r37][^r41].

Because Ledgerline parameter `PUR.CERT_CHK` is set to `N`, the ERP does not block purchase order entry on [[screen-pur-po-01|PUR-PO-01]] when certificates are missing or expired [^r14][^r47][^r49]. Release [[rn-7-2-3-p4|RN-7.2.3-P4]] introduced an automated check raising advisory warning W-SUP-0207, but it does not evaluate original issue dates or the 60-day margin, leaving senior buyer review on checklist NBC-F-113 as the operative control [^r14][^r25][^r26].

## Expiry Monitoring and Supplier Status

Under [[pol-pur-001|POL-PUR-001]] §6.2, an expired UN 38.3 certificate counts as no certificate, requiring an immediate freeze on purchasing activities for regulated items [^r9][^r40]. Certificate expiry is tracked via batch job JOB-PUR-022 run on the first working day of each month with a 90-day horizon using the [[man-pur-72|MAN-PUR-72]] §22.6 report, which accepts a certificate type parameter [^r7][^r17][^r27]. Buyers issue template NBC-L-07 and enforce an order freeze at 60 days before expiry per [[amd-sup-2026-02|AMD-SUP-2026-02]] [^r17].

If a certificate expires without renewal, buyers receive notification under subject `CERT EXPIRED - DO NOT ORDER`, and incoming consignments without active certification are quarantined on receipt [^r18]. As of October 2026, certificate expiry reporting highlights several suppliers:
* [[sup-nc-gda-0063|Nordic Cell Co. (NC-GDA-0063)]]: Certificate UN38.3-TR/NC/2025/090 expired on 2026-09-30, with lab renewal delayed until late November 2026; lithium orders remain manually halted [^r3][^r31][^r46][^r47].
* Tamar Energy Storage (TES-PLY-0144): Certificate UN38.3-TR/TE/2025/069 expires on 2026-11-30 [^r32].
* Saddleworth Charger Co. (SCC-BOL-0183): Certificate UN38.3-TR/SC/2025/067 expires on 2026-11-30 [^r33].
* Rheinfeld Cell Systems (RCS-STU-0151): Certificate UN38.3-TR/RC/2025/213 expires on 2026-12-15 [^r34].
* Voltway Cells: Quality is scheduled to request renewal documentation in January 2027 ahead of its March 2027 expiration [^r38].

## Versions and conflicts

* **Certificate issue age and validity margin (superseded):** Today, under AMD-SUP-2026-02 and [[sop-pur-001|SOP-PUR-001]], certificates must be issued within the preceding 12 months with a `valid_to` date at least 60 days past the purchase order date [^r5][^r13]. Certificates between 12 and 24 months old became invalid for new purchase orders on 1 September 2026 [^r6]. Previously, [[pol-sup-003|POL-SUP-003]] §4 and superseded POL-SUP-003 v2.2 accepted certificates issued within 24 months [^r36][^r51][^r54], and legacy procedure SOP-PUR-001 v2.0 allowed suppliers to provide reports within three months after their first order [^r57].
* **System enforcement vs manual controls (future_dated):** Today, Ledgerline parameter `PUR.CERT_CHK` is set to `N`, and the ERP only provides advisory warning W-SUP-0207 under 7.2.3-P4 without blocking saves, requiring manual verification and approval comments [^r11][^r14][^r25][^r26][^r45][^r49]. In planned Ledgerline ERP 7.3 (effective 2027-03-01), missing or expired certificates will trigger hard blocking error [[err-sup-0207|ERR-SUP-0207]] [^r50].
* **Regulated component scope (superseded):** Today, UN 38.3 rules apply across all lithium-cell parts including packs, hub motors, and chargers [^r8][^r35]. Under superseded policy POL-PUR-001 v3.0, only battery packs required UN 38.3 certificates, excluding hub motors and chargers [^r56].

## See also

* [[amd-sup-2026-02|AMD-SUP-2026-02 Amendment 2 to the Supplier Policy]]
* [[pol-sup-003|POL-SUP-003 Supplier Policy]]
* [[pol-pur-001|POL-PUR-001 Purchase Policy]]
* [[sop-pur-001|SOP-PUR-001 Supplier Onboarding]]
* [[sop-pur-005|SOP-PUR-005 Certificate Renewal (UN 38.3)]]
* [[sop-pur-006|SOP-PUR-006 Quotations and Supplier Selection]]
* [[sop-prd-002|SOP-PRD-002 Engineering Change (ECN)]]
* [[sup-nc-gda-0063|Nordic Cell Co. (NC-GDA-0063)]]
* [[sup-vc-ein-0042|Voltway Cells (VC-EIN-0042)]]
* [[items-bat|BAT-* items]]
* [[err-sup-0207|ERR-SUP-0207 Missing or Expired UN 38.3 Certificate]]

## References

[^r8]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 2, §6. Supplier qualification
[^r35]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 2, §4. UN 38.3 certificates
[^r5]: 01_policies/AMD-SUP-2026-02 Amendment 2 Supplier Policy.pdf, p. 1, §1. What changes
[^r13]: 02_procedures/SOP-PUR-001 Supplier Onboarding v3.1.pdf, p. 3, §5. Procedure
[^r11]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 2, §4. UN 38.3 certificates
[^r14]: 02_procedures/SOP-PUR-001 Supplier Onboarding v3.1.pdf, p. 5, §6. Timing and system checks
[^r47]: 09_email_archive/2026/2026-10-01_CERT EXPIRED - DO NOT ORDER_ Nordic Cell Co. (NC-GDA-0063).eml, body
[^r15]: 02_procedures/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf, p. 1, Common errors
[^r10]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 2, §4. UN 38.3 certificates
[^r16]: 02_procedures/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf, p. 1, Common errors
[^r12]: 02_procedures/SOP-PRD-002 Engineering Change v1.0.pdf, p. 3, §5. Procedure: notes and common mistakes
[^r19]: 02_procedures/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf, p. 4, §6. Records
[^r39]: 10_meeting_notes/2026-10-19 Weekly purchasing meeting.md, Discussion
[^r20]: 02_procedures/SOP-PUR-006 Quotations and Supplier Selection v1.0.pdf, p. 3, §5. Procedure
[^r22]: 02_procedures/SOP-PUR-006 Quotations and Supplier Selection v1.0.pdf, p. 4, What to check on the screen
[^r21]: 02_procedures/SOP-PUR-006 Quotations and Supplier Selection v1.0.pdf, p. 4, What to do when something does not look right
[^r48]: 09_email_archive/2026/2026-10-22_Quotation Q-BE-26-0917 - Brightcell Energy.eml, body
[^r23]: 02_procedures/forms/Final_FINAL_onboarding checklist NBC-F-113.docx, Supplier Onboarding Checklist (NBC-F-113)
[^r24]: 02_procedures/forms/Final_FINAL_onboarding checklist NBC-F-113.docx, Supplier Onboarding Checklist (NBC-F-113)
[^r30]: 11_training/QRC-05 Uploading a supplier certificate.pdf, p. 1, Verification and sign-off
[^r42]: 09_email_archive/2026/2026-07-28_Failed battery lot - incoming abuse test.eml, body
[^r43]: 09_email_archive/2026/2026-07-28_Failed battery lot - incoming abuse test.eml, body
[^r44]: 09_email_archive/2026/2026-07-28_Failed battery lot - incoming abuse test.eml, body
[^r45]: 09_email_archive/2026/2026-09-02_Approving orders for lithium-cell parts - CERT OK in the approval comment.eml, body
[^r4]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 3, Module PUR/core
[^r29]: 11_training/QRC-05 Uploading a supplier certificate.pdf, p. 1, Steps
[^r1]: 05_master_data/SUPPLIER_MASTER.xlsx, sheet Certificates, row CC-SAL-0031/UN38.3/UN38.3-TR/CC/2026/044, SHEET Certificates
[^r2]: 05_master_data/SUPPLIER_MASTER.xlsx, sheet Certificates, row AM-BIR-0008/UN38.3/UN38.3-TR/AM/2026/301, SHEET Certificates
[^r37]: 10_meeting_notes/2026-09-17 Supplier review - Voltway Cells.docx, Certificate
[^r41]: 09_email_archive/2026/2026-06-15_Voltway battery packs - receive straight into main stores.eml, body
[^r49]: 09_email_archive/2026/2026-10-23_RE_ Brightcell quote - can we switch from Voltway_.eml, body
[^r25]: 08_release_notes/RN-7.2.3-P4 Ledgerline Patch Notes.pdf, p. 1, Upgrade Notes for Key Users
[^r26]: 08_release_notes/RN-7.2.3-P4 Ledgerline Patch Notes.pdf, p. 1, Upgrade Notes for Key Users
[^r9]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 2, §6. Supplier qualification
[^r40]: 10_meeting_notes/2026-10-19 Weekly purchasing meeting.md, Discussion
[^r7]: 01_policies/AMD-SUP-2026-02 Amendment 2 Supplier Policy.pdf, p. 1, §3. What purchase staff must do
[^r17]: 02_procedures/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf, p. 3, §5. Procedure
[^r27]: 08_release_notes/RN-7.2.3-P4 Ledgerline Patch Notes.pdf, p. 3, §3. Details
[^r18]: 02_procedures/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf, p. 3, §5. Procedure
[^r3]: 05_master_data/SUPPLIER_MASTER.xlsx, sheet Certificates, row NC-GDA-0063/UN38.3/UN38.3-TR/NC/2025/090, SHEET Certificates
[^r31]: 06_transactions/reports/Certificate expiry report 2026-10-01.pdf, row NC-GDA-0063, p. 3, PUR-R022 CERTIFICATE EXPIRY DAYS=90
[^r46]: 09_email_archive/2026/2026-09-29_UN 38.3 report renewal.eml, body
[^r32]: 06_transactions/reports/Certificate expiry report 2026-10-01.pdf, row TES-PLY-0144, p. 4, PUR-R022 CERTIFICATE EXPIRY DAYS=90
[^r33]: 06_transactions/reports/Certificate expiry report 2026-10-01.pdf, row SCC-BOL-0183, p. 4, PUR-R022 CERTIFICATE EXPIRY DAYS=90
[^r34]: 06_transactions/reports/Certificate expiry report 2026-10-01.pdf, row RCS-STU-0151, p. 4, PUR-R022 CERTIFICATE EXPIRY DAYS=90
[^r38]: 10_meeting_notes/2026-09-17 Supplier review - Voltway Cells.docx, Actions
[^r6]: 01_policies/AMD-SUP-2026-02 Amendment 2 Supplier Policy.pdf, p. 1, §1. What changes
[^r36]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 2, §4. UN 38.3 certificates
[^r51]: 01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf, p. 2, §4. UN 38.3 certificates
[^r54]: 01_policies/old/Supplier_Policy_v2.2.docx, §4. UN 38.3 certificates
[^r57]: 02_procedures/old/SOP-PUR-001 Supplier onboarding v2.0 (2021).docx, §5. Procedure
[^r50]: 08_release_notes/RN-7.3 PREVIEW (planned March 2027).pdf, p. 1, Blocking certificate check on lithium-cell items
[^r56]: 01_policies/old/purchase_policy_v3_2019.docx, §6. Supplier qualification
