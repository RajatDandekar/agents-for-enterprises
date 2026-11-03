---
title: "SOP-QUA-001 Incoming Inspection"
type: "procedure"
slug: "sop-qua-001"
summary: "Standard operating procedure for goods inwards quality inspection, AQL sampling, battery open-circuit testing, and non-conformance handling across manufacturing sites."
audience: "staff"
status: "current"
sources: ["07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf", "01_policies/POL-QUA-005 Quality Policy v3.0.pdf", "02_procedures/SOP-QUA-001 Incoming Inspection v2.0.pdf", "03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "11_training/intranet_export_2016/index.html", "11_training/intranet_export_2016/page_goods_receipt_tips.html", "11_training/intranet_export_2016/page_ledgerline_tips_and_tricks.html", "11_training/intranet_export_2016/page_purchasing_team_news__spring_2016.html", "11_training/intranet_export_2016/page_quality_notices.html", "10_meeting_notes/2026-01-11 IT steering.docx", "09_email_archive/2019/2019-01-19_Supplier quality review for the third quarter.eml", "09_email_archive/2021/2021-01-18_Damaged cartons from the carrier.eml", "09_email_archive/2022/2022-08-26_Delivery without a purchase order number.eml", "09_email_archive/2024/2024-07-03_Incoming inspection backlog.eml", "09_email_archive/2026/2026-06-15_Voltway battery packs - receive straight into main stores.eml", "09_email_archive/2026/2026-07-23_Partial delivery of brake pads.eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | SOP-QUA-001 |
| title | Incoming Inspection |
| owner | [[user-pjansen|Pieter Jansen]] |
| approver | [[user-hweber|Henrik Weber]] |
| version | 2.0 |
| effective | 2024-04-01 |
| status | current |

SOP-QUA-001 governs the receiving quality examination of bought-in production parts, raw materials, and sub-assemblies across Northbridge Cycles delivery bays [^r7]. Effective from 2024-04-01, it defines mandatory Acceptable Quality Level (AQL) verification, specialized open-circuit voltage testing for lithium battery packs, and immediate non-conformance logging in Ledgerline ERP [^r3][^r4][^r6][^r11]. Uninspected production inventory is strictly barred from active assembly lines until an inspector completes verification and applies green acceptance tags [^r8][^r29].

| Field | Value |
|---|---|
| Document code | SOP-QUA-001 [^r6] |
| Version | 2.0 [^r6] |
| Effective date | 2024-04-01 [^r6] |
| Document owner | [[user-pjansen|Pieter Jansen]] (Quality Manager) [^r6] |
| Approver | [[user-hweber|Henrik Weber]] (Plant Head) [^r6] |
| Governing policy | [[pol-qua-005|POL-QUA-005]] [^r9] |
| System screens | [[screen-qa-ins-01|QA-INS-01]], [[screen-qa-ncr-02|QA-NCR-02]] [^r9][^r11] |

## Steps

### 1. Delivery intake and staging
Deliveries arriving at either the Manchester plant or the Leeds warehouse must be processed through designated goods inwards bays [^r18]. Stores personnel endorse the carrier manifest, noting any wet, crushed, or torn outer packaging as well as carton shortages rather than signing as clear [^r20][^r21][^r50]. Consignments with damaged outer cartons, missing paperwork, or unverified order references must be segregated into the receiving quarantine bay while notifying the responsible buyer, and cannot be booked directly onto active warehouse racks [^r23][^r51][^r52]. Warehouse intake requires an active purchase order record, as Ledgerline ERP prevents receipts without an open order [^r54].

### 2. Inspection preparation
Before starting quality intake, the inspector must assemble the Goods Received Note (GRN) documentation, position the physical consignment in the yellow-marked quality inspection holding area, retrieve the inspection drawing or standard sheet, and ensure calibrated test instruments are ready [^r14]. Consignments remain physically staged in quarantine until quality approval is posted in the system [^r8][^r56]. Batch certificates for structural tubing and electrical sub-assemblies must be validated before stock is cleared [^r25].

### 3. Sampling and measurement
The inspector accesses [[screen-qa-ins-01|QA-INS-01]], enters the GRN number, and executes `qin_get` to retrieve line details [^r15]. Sample quantities must be drawn in accordance with [[pol-qua-005|POL-QUA-005]] standard tables [^r3][^r15]:
* **Lithium-cell components:** Sampled at AQL 0.65 [^r3].
* **All other production components:** Sampled at AQL 1.5 [^r3].

For every sample battery pack ([[items-bat|BAT-* items]]), the inspector must measure and record the individual open-circuit voltage using a calibrated test meter [^r4][^r10]. Under [[pol-bat-004|POL-BAT-004]] §2.3, each sampled pack must fall within a 30% to 50% state-of-charge window; any sample outside this range fails the test [^r10]. If any sample pack fails, the entire lot is declared non-conforming without re-sampling or testing additional units [^r12].

### 4. Posting inspection results
On [[screen-qa-ins-01|QA-INS-01]], the inspector enters the sample quantity, selects the applicable AQL tier, and records the pass/fail determination [^r15]. Quality inspection headers are stored in Ledgerline table `qin_hdr` referencing the GRN number, sample quantity, AQL, and inspection outcome [^r1].

* **Accepted lots:** The inspector applies physical green acceptance tags to all cleared cartons and clicks `qin_post`, which updates stock records and releases the batch from quarantine staging to stores racking [^r8][^r16].
* **Rejected lots:** The inspector clicks `qin_reject`, applies physical red rejection labels to all containers, and quarantines the entire delivery [^r13][^r16]. For electrical components, failure of a single unit requires quarantining the entire carton [^r5]. The inspector must immediately raise a Non-Conformance Report (NCR) on screen [[screen-qa-ncr-02|QA-NCR-02]] [^r11].

### 5. Non-conformance resolution
Reject entries made in the comment field on [[screen-qa-ins-01|QA-INS-01]] transfer automatically to formal supplier debit notes and return paperwork generated by the purchasing department [^r17]. Non-conformance details are written to Ledgerline table `ncr_hdr` with the NCR number, GRN reference, item code, defect code, rejected quantity, and narrative description [^r2]. The inspector notifies the purchasing team, who review contract terms, issue root-cause analysis requests to the vendor, and initiate supplier debit notes [^r13][^r41]. Outright rejected stock remains quarantined in the receiving holding area until the vendor provides return carriage or issues written destruction authorisation [^r43].

## Forms and screens

* **[[screen-qa-ins-01|QA-INS-01]] (Incoming Inspection Entry):** Used by inspection staff to query pending receipts via `qin_get`, record sample sizes and AQL standards, and submit disposition via `qin_post` or `qin_reject` [^r15][^r16]. Updates table `qin_hdr` [^r1].
* **[[screen-qa-ncr-02|QA-NCR-02]] (Non-Conformance Report Entry):** Used immediately upon lot rejection to generate formal NCR records logged in table `ncr_hdr` [^r2][^r11].
* **Physical Tags:** Green acceptance labels denote stock cleared for stores racking; red rejection tags denote quarantined lots awaiting return, debit, or scrap agreements [^r8][^r13][^r16].

## Versions and conflicts

* **Staging location for Voltway battery packs:** Under an operational decision effective 15 June 2026, [[items-bat|BAT-*]] battery packs supplied by [[sup-vc-ein-0042|Voltway Cells]] bypass physical quarantine staging in location `WH-MAN-QC` and are received straight into main stores `WH-MAN-STR`, with required AQL sampling performed directly in the receiving bay before put-away [^r57]. This overrides the general baseline rule in SOP-QUA-001 v2.0 §2, which requires all incoming production goods to remain held in the designated quarantine bay until system release is posted [^r8]. Non-Voltway lithium-cell parts remain subject to standard routing into `WH-MAN-QC` [^r58] (`email_overrides_sop`).

## See also

* [[items-bat|BAT-* items]]
* [[man-dd-72-all|MAN-DD-72-ALL Ledgerline ERP 7.2 Data Dictionary: all]]
* [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]]
* [[pol-bat-004|POL-BAT-004 Battery Safety and Handling Policy]]
* [[pol-qua-005|POL-QUA-005 Quality Policy]]
* [[screen-qa-ins-01|QA-INS-01 Incoming Inspection Entry]]
* [[screen-qa-ncr-02|QA-NCR-02 Non-Conformance Report Entry]]
* [[sup-vc-ein-0042|Voltway Cells (VC-EIN-0042)]]
* [[user-hweber|Henrik Weber (HWEBER)]]
* [[user-pjansen|Pieter Jansen (PJANSEN)]]

## References

[^r7]: 02_procedures/SOP-QUA-001 Incoming Inspection v2.0.pdf, p. 2, §2. Scope
[^r3]: 01_policies/POL-QUA-005 Quality Policy v3.0.pdf, p. 2, §3. Incoming inspection
[^r4]: 01_policies/POL-QUA-005 Quality Policy v3.0.pdf, p. 2, §3. Incoming inspection
[^r6]: 02_procedures/SOP-QUA-001 Incoming Inspection v2.0.pdf, p. 1, Field Value
[^r11]: 02_procedures/SOP-QUA-001 Incoming Inspection v2.0.pdf, p. 3, §5. Procedure
[^r8]: 02_procedures/SOP-QUA-001 Incoming Inspection v2.0.pdf, p. 2, §2. Scope
[^r29]: 11_training/intranet_export_2016/page_goods_receipt_tips.html, Discrepancies and quality holds
[^r9]: 02_procedures/SOP-QUA-001 Incoming Inspection v2.0.pdf, p. 3, §5. Procedure
[^r18]: 11_training/intranet_export_2016/index.html, Purchasing home
[^r20]: 11_training/intranet_export_2016/page_goods_receipt_tips.html, Goods receipt tips
[^r21]: 11_training/intranet_export_2016/page_goods_receipt_tips.html, Goods receipt tips
[^r50]: 09_email_archive/2021/2021-01-18_Damaged cartons from the carrier.eml, body
[^r23]: 11_training/intranet_export_2016/page_goods_receipt_tips.html, Booking in materials
[^r51]: 09_email_archive/2021/2021-01-18_Damaged cartons from the carrier.eml, body
[^r52]: 09_email_archive/2021/2021-01-18_Damaged cartons from the carrier.eml, body
[^r54]: 09_email_archive/2022/2022-08-26_Delivery without a purchase order number.eml, Delivery without a purchase order number
[^r14]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 34, Before you start
[^r56]: 09_email_archive/2024/2024-07-03_Incoming inspection backlog.eml, body
[^r25]: 11_training/intranet_export_2016/page_goods_receipt_tips.html, Booking in materials
[^r15]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 35, Step by step
[^r10]: 02_procedures/SOP-QUA-001 Incoming Inspection v2.0.pdf, p. 3, §5. Procedure
[^r12]: 02_procedures/SOP-QUA-001 Incoming Inspection v2.0.pdf, p. 4, §5. Procedure: notes and common mistakes
[^r1]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 19, Table qin_hdr
[^r16]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 35, Step by step
[^r13]: 02_procedures/SOP-QUA-001 Incoming Inspection v2.0.pdf, p. 2, §3. Responsibilities
[^r5]: 01_policies/POL-QUA-005 Quality Policy v3.0.pdf, p. 4, Non-conformance
[^r17]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 36, Tips
[^r2]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 19, Table ncr_hdr
[^r41]: 11_training/intranet_export_2016/page_quality_notices.html, Procedure for raising and managing notices
[^r43]: 11_training/intranet_export_2016/page_quality_notices.html, Procedure for raising and managing notices
[^r57]: 09_email_archive/2026/2026-06-15_Voltway battery packs - receive straight into main stores.eml, body
[^r58]: 09_email_archive/2026/2026-06-15_Voltway battery packs - receive straight into main stores.eml, body
