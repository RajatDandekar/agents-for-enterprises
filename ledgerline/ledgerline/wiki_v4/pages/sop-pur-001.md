---
title: "SOP-PUR-001 Supplier Onboarding"
type: "procedure"
slug: "sop-pur-001"
summary: "Standard operating procedure for onboarding suppliers in Ledgerline, including mandatory vendor documentation, manager approvals, and manual UN 38.3 compliance checks."
audience: "staff"
status: "mixed"
sources: ["01_policies/POL-SUP-003 Supplier Policy v2.3.pdf", "02_procedures/SOP-PUR-001 Supplier Onboarding v3.1.pdf", "02_procedures/SOP-PUR-006 Quotations and Supplier Selection v1.0.pdf", "02_procedures/forms/Final_FINAL_onboarding checklist NBC-F-113.docx", "02_procedures/old/SOP-PUR-001 Supplier onboarding v2.0 (2021).docx", "11_training/intranet_export_2016/supplier_list.html", "10_meeting_notes/2026-10-07 CAB minutes (CR-2026-031 certificate check).docx", "10_meeting_notes/2026-10-19 Weekly purchasing meeting.md", "09_email_archive/2025/2025-09-15_How to search for a supplier properly.eml", "09_email_archive/2026/2026-10-07_Certificate check in Ledgerline (PUR.CERT_CHK) - stays off for now.eml", "09_email_archive/2026/2026-10-23_RE_ Brightcell quote - can we switch from Voltway_.eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | SOP-PUR-001 |
| title | Supplier Onboarding |
| owner | Purchase Department |
| author | Luis Moreno |
| approver | Daniel Okafor |
| version | 3.1 |
| effective | 2026-09-01 |
| status | current |

SOP-PUR-001 defines the operational workflow for qualifying and creating new vendor accounts in Ledgerline [^r6]. As of 26 October 2026, version 3.1 governs all onboarding, enforcing mandatory documentation, anti-duplicate directory queries, and explicit purchase manager authorization [^r6][^r11]. Because automated Ledgerline certificate verification remains disabled under parameter PUR.CERT_CHK, manual verification of [[topic-un-38-3-certificates|UN 38.3 certificates]] via physical checklist form NBC-F-113 serves as the primary compliance control for [[items-bat|lithium-cell]] suppliers [^r18][^r33][^r40].

## Steps

1. **Pre-screening and Duplicate Check:** Before compiling an onboarding file, the proposer must query [[screen-pur-sup-03|PUR-SUP-03]] by company name, city, and VAT number, appending printed results to the dossier to prevent duplicate accounts [^r2][^r7][^r23][^r35]. Proposers should search using one short, distinctive word of the name with wildcard strings around key terms, checking variations and reviewing active and suspended records as well as postal locations [^r7][^r36][^r37][^r38]. Transaction histories of potential matches must be verified against past purchase orders [^r39].
2. **Onboarding Proposal:** A prospective vendor not currently in the master must be onboarded using form NBC-F-112 (Supplier Onboarding Request) when approaching Northbridge or submitting a quotation [^r8][^r19][^r34]. The request requires at least one written quotation and an operational justification demonstrating why existing master suppliers cannot fulfill the requirement [^r1][^r8]. Quotations cannot be formally accepted, and prospective purchase orders must be held from release, until onboarding completes [^r19][^r20].
3. **Document Collation:** The proposer must collate the mandatory paperwork specified in [[pol-sup-003|POL-SUP-003]] §3.2: company registration number, VAT registration certificate, bank letter detailing account information, proof of insurance, and a signed Supplier Code of Conduct [^r3][^r9][^r25][^r30].
4. **UN 38.3 Test Report Collation:** For suppliers of lithium-cell parts, the proposer must obtain a UN 38.3 test report and test summary for each part issued within the last 12 months, with a valid-to date at least 60 days past the planned first order date as required by [[amd-sup-2026-02|AMD-SUP-2026-02]] [^r10][^r26].
5. **Manager Approval:** The purchase executive or proposer submits the completed onboarding pack to [[user-dokafor|Daniel Okafor]], who must sign box 7 of form NBC-F-112 before any ledger record is generated [^r4][^r11][^r24][^r41].
6. **Master Record Creation:** Following manager sign-off, the proposer creates the vendor on [[screen-pur-sup-01|PUR-SUP-01]] using service sup_create in [[services-pur-sup|services-pur-sup]], entering the legal name, city, two-letter country code, payment terms, and VAT number without spaces [^r5][^r12]. The system issues a supplier code and displays `SUPPLIER <code> CREATED`, activating the account immediately [^r12][^r18].
7. **Certificate Upload and Verification:** For lithium-cell components, the proposer uploads the UN 38.3 documentation on [[screen-pur-sup-01|PUR-SUP-01]] via the Certificates tab using service sup_cert_upload, specifying certificate type UN38.3, document reference, valid-to date, and the scanned test report until confirmed with `CERT SAVED` [^r13][^r27]. Senior buyer [[user-lmoreno|Luis Moreno]] must inspect the uploaded certificate against the report and initial checklist form NBC-F-113; no purchase order may be raised until this check is signed off [^r5][^r14][^r26].
8. **Bank Detail Verification:** Accounts payable must verify supplier bank details by telephoning the supplier using an independently confirmed number from its letterhead or website, never from the supplied bank letter or an email, pursuant to [[sop-ap-004|SOP-AP-004]] [^r15][^r28].
9. **Rate Contract Setup:** The purchase manager's office must establish the rate contract under [[sop-pur-004|SOP-PUR-004]] before purchase orders can retrieve pricing via Fetch on [[screen-pur-po-01|PUR-PO-01]] [^r16][^r29].

Standard onboarding requires five working days from receipt of a complete dossier, but lithium-cell suppliers require at least ten working days due to testing laboratory queries [^r17].

## Forms and screens

* **NBC-F-112 (Supplier Onboarding Request):** Form submitted with vendor quotations and justification, requiring approval in box 7 by the purchase manager [^r8][^r11][^r24].
* **NBC-F-113 (Supplier Onboarding Checklist):** Version 2.1 checklist owned by the Purchase department, recording supplier name, city, country, and VAT number, and tracking steps 1 through 7 [^r21][^r22][^r23][^r24][^r25][^r26][^r27][^r28][^r29]. It serves as the sole operational control for certificate checks while PUR.CERT_CHK is disabled [^r18].
* **[[screen-pur-sup-03|PUR-SUP-03]] (Supplier Enquiry):** Screen used for pre-screening searches by keyword, city, and VAT number [^r2][^r7].
* **[[screen-pur-sup-01|PUR-SUP-01]] (Supplier Master Create):** Screen used for record generation via sup_create and certificate attachment via sup_cert_upload [^r12][^r13].
* **[[screen-pur-po-01|PUR-PO-01]] (Purchase Order Entry):** Screen where price retrieval depends on completed rate contracts [^r16].

## Versions and conflicts

* **Superseded record creation and turnaround (2026-09-01 vs legacy):** Under SOP-PUR-001 v3.1, the purchase proposer creates the account directly on PUR-SUP-01 upon purchase manager sign-off, turnaround is five days (ten for lithium parts), and UN 38.3 test summaries must be validated prior to any order placement [^r5][^r11][^r12][^r17]. Under superseded v2.0 (effective 2021-02-01) and legacy intranet guidelines, packs were forwarded to finance/accounts to create records on screen SUPP-ENT (or legacy SUPP-ENQ search), turnaround was three working days, and battery suppliers were permitted three months post-order to provide UN 38.3 reports [^r31][^r42][^r43][^r45][^r46]. Kind: `superseded`.
* **System certificate enforcement vs manual control (2026-10-07):** Ledgerline parameter PUR.CERT_CHK is set to `N` at Northbridge, meaning the ERP does not block purchase orders for missing or expired certificates [^r18]. Although [[rn-7-2-3-p4|RN-7.2.3-P4]] introduced automated checks, change decision CR-2026-031 deferred activation until at least January 2027, leaving physical checklist NBC-F-113 as the governing operational control [^r18][^r33][^r40]. Kind: `email_overrides_sop`.

## See also

* [[pol-sup-003|POL-SUP-003 Supplier Policy]]
* [[amd-sup-2026-02|AMD-SUP-2026-02 Amendment 2 to the Supplier Policy]]
* [[sop-pur-004|SOP-PUR-004 Rate Contract Maintenance]]
* [[sop-pur-006|SOP-PUR-006 Quotations and Supplier Selection]]
* [[sop-ap-004|SOP-AP-004 Supplier Bank Detail Changes]]
* [[topic-un-38-3-certificates|UN 38.3 Certificates]]
* [[screen-pur-sup-01|PUR-SUP-01 Supplier Master Create]]
* [[screen-pur-sup-03|PUR-SUP-03 Supplier Enquiry]]
* [[decision-2026-10-07-cr-2026-031-cert-check|Decision 2026-10-07: Deferral of PUR.CERT_CHK activation (CR-2026-031)]]

## References

[^r6]: 02_procedures/SOP-PUR-001 Supplier Onboarding v3.1.pdf, p. 1, Supplier Onboarding
[^r11]: 02_procedures/SOP-PUR-001 Supplier Onboarding v3.1.pdf, p. 3, §5. Procedure
[^r18]: 02_procedures/SOP-PUR-001 Supplier Onboarding v3.1.pdf, p. 5, §6. Timing and system checks
[^r33]: 10_meeting_notes/2026-10-07 CAB minutes (CR-2026-031 certificate check).docx, CR-2026-031 Enable PUR.CERT_CHK (patch 7.2.3-P4)
[^r40]: 09_email_archive/2026/2026-10-07_Certificate check in Ledgerline (PUR.CERT_CHK) - stays off for now.eml, body
[^r2]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 3, Appendix A. Guidance for proposers
[^r7]: 02_procedures/SOP-PUR-001 Supplier Onboarding v3.1.pdf, p. 3, §5. Procedure
[^r23]: 02_procedures/forms/Final_FINAL_onboarding checklist NBC-F-113.docx, Supplier Onboarding Checklist (NBC-F-113)
[^r35]: 09_email_archive/2025/2025-09-15_How to search for a supplier properly.eml, How to search for a supplier properly
[^r36]: 09_email_archive/2025/2025-09-15_How to search for a supplier properly.eml, How to search for a supplier properly
[^r37]: 09_email_archive/2025/2025-09-15_How to search for a supplier properly.eml, How to search for a supplier properly
[^r38]: 09_email_archive/2025/2025-09-15_How to search for a supplier properly.eml, How to search for a supplier properly
[^r39]: 09_email_archive/2025/2025-09-15_How to search for a supplier properly.eml, How to search for a supplier properly
[^r8]: 02_procedures/SOP-PUR-001 Supplier Onboarding v3.1.pdf, p. 3, §5. Procedure
[^r19]: 02_procedures/SOP-PUR-006 Quotations and Supplier Selection v1.0.pdf, p. 3, §5. Procedure
[^r34]: 10_meeting_notes/2026-10-19 Weekly purchasing meeting.md, Suppliers
[^r1]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 3, Appendix A. Guidance for proposers
[^r20]: 02_procedures/SOP-PUR-006 Quotations and Supplier Selection v1.0.pdf, p. 4, What to do when something does not look right
[^r3]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 3, Appendix A. Guidance for proposers
[^r9]: 02_procedures/SOP-PUR-001 Supplier Onboarding v3.1.pdf, p. 3, §5. Procedure
[^r25]: 02_procedures/forms/Final_FINAL_onboarding checklist NBC-F-113.docx, Supplier Onboarding Checklist (NBC-F-113)
[^r30]: 11_training/intranet_export_2016/supplier_list.html, Supplier list
[^r10]: 02_procedures/SOP-PUR-001 Supplier Onboarding v3.1.pdf, p. 3, §5. Procedure
[^r26]: 02_procedures/forms/Final_FINAL_onboarding checklist NBC-F-113.docx, Supplier Onboarding Checklist (NBC-F-113)
[^r4]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 4, Appendix A. Guidance for proposers
[^r24]: 02_procedures/forms/Final_FINAL_onboarding checklist NBC-F-113.docx, Supplier Onboarding Checklist (NBC-F-113)
[^r41]: 09_email_archive/2026/2026-10-23_RE_ Brightcell quote - can we switch from Voltway_.eml, body
[^r5]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 4, Appendix A. Guidance for proposers
[^r12]: 02_procedures/SOP-PUR-001 Supplier Onboarding v3.1.pdf, p. 3, §5. Procedure
[^r13]: 02_procedures/SOP-PUR-001 Supplier Onboarding v3.1.pdf, p. 3, §5. Procedure
[^r27]: 02_procedures/forms/Final_FINAL_onboarding checklist NBC-F-113.docx, Supplier Onboarding Checklist (NBC-F-113)
[^r14]: 02_procedures/SOP-PUR-001 Supplier Onboarding v3.1.pdf, p. 3, §5. Procedure
[^r15]: 02_procedures/SOP-PUR-001 Supplier Onboarding v3.1.pdf, p. 3, §5. Procedure
[^r28]: 02_procedures/forms/Final_FINAL_onboarding checklist NBC-F-113.docx, Supplier Onboarding Checklist (NBC-F-113)
[^r16]: 02_procedures/SOP-PUR-001 Supplier Onboarding v3.1.pdf, p. 3, §5. Procedure
[^r29]: 02_procedures/forms/Final_FINAL_onboarding checklist NBC-F-113.docx, Supplier Onboarding Checklist (NBC-F-113)
[^r17]: 02_procedures/SOP-PUR-001 Supplier Onboarding v3.1.pdf, p. 5, §6. Timing and system checks
[^r21]: 02_procedures/forms/Final_FINAL_onboarding checklist NBC-F-113.docx, Supplier Onboarding Checklist (NBC-F-113)
[^r22]: 02_procedures/forms/Final_FINAL_onboarding checklist NBC-F-113.docx, Supplier Onboarding Checklist (NBC-F-113)
[^r31]: 11_training/intranet_export_2016/supplier_list.html, Supplier list
[^r42]: 02_procedures/old/SOP-PUR-001 Supplier onboarding v2.0 (2021).docx, §1. Purpose > Routine Practice
[^r43]: 02_procedures/old/SOP-PUR-001 Supplier onboarding v2.0 (2021).docx, §5. Procedure
[^r45]: 02_procedures/old/SOP-PUR-001 Supplier onboarding v2.0 (2021).docx, §5. Procedure
[^r46]: 02_procedures/old/SOP-PUR-001 Supplier onboarding v2.0 (2021).docx, §5. Procedure
