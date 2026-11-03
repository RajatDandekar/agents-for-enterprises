---
title: "SOP-SAL-002 Warranty Claims from Bike Shops"
type: "procedure"
slug: "sop-sal-002"
summary: "Procedure for receiving, evaluating, and settling electric bicycle and component warranty claims submitted by independent bike shops."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-SAL-002 Warranty Claims (RMA) v1.1.pdf", "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "10_meeting_notes/2022-02-10 Sales meeting.docx", "10_meeting_notes/2022-10-15 Battery safety committee.md", "10_meeting_notes/2024-03-10 Sales meeting.md", "10_meeting_notes/2024-10-01 Stores and logistics meeting.md", "10_meeting_notes/2025-03-18 Leeds unit update.docx", "10_meeting_notes/2025-10-08 Continuous improvement workshop.docx", "10_meeting_notes/2026-01-11 IT steering.docx", "10_meeting_notes/2026-01-17 Warranty review.docx", "10_meeting_notes/2026-04-18 Stores and logistics meeting.docx", "10_meeting_notes/2026-05-23 Quality meeting.docx", "09_email_archive/2021/2021-12-25_Warranty claims trend.eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Document code | SOP-SAL-002 |
| Version | 1.1 |
| Effective date | 2025-03-01 |
| Status | current |
| Owner | Isla Morgan (Sales Manager) |
| Approver | Pieter Jansen (Quality Manager) |

SOP-SAL-002 governs how Northbridge Cycles receives, assesses, and settles warranty requests submitted by retail bike shops for electric bicycles manufactured at Manchester and sub-assemblies handled through Leeds[^r1][^r2]. Direct warranty claims submitted by retail end-consumers are excluded and must be redirected to the supplying bike shop[^r3]. The procedure establishes technical assessment requirements, dangerous-goods routing for batteries, and the conditions under which credit notes and replacement components are authorised[^r2][^r7][^r10].

| Key | Value |
|---|---|
| Document code | SOP-SAL-002[^r1] |
| Version | 1.1[^r1] |
| Effective date | 2025-03-01[^r1] |
| Status | current[^r1] |
| Owner | [[user-imorgan\|Isla Morgan]] (Sales Manager)[^r1] |
| Approver | [[user-pjansen\|Pieter Jansen]] (Quality Manager)[^r1] |

## Steps

### 1. Claim intake and serial validation
The Leeds sales office serves as the primary contact point for bike shops submitting warranty requests[^r4]. The bike shop must supply the frame or pack serial number, which must be registered in [[screen-sal-srl-16|SAL-SRL-16]][^r8]. During RMA approval (`rma_approve`), Ledgerline ERP validates the serial number and blocks unregistered units with [[err-rma-0210|ERR-RMA-0210]][^r8][^r15]. The system also verifies the original sale date against eligible warranty periods defined in [[pol-ret-006|POL-RET-006]] §3.1, raising ERR-RMA-0211 if the unit is out of warranty[^r9][^r16]. Warranty intake forms in the e-mail system require photographs of boxed bicycles before collection to prevent transit damage disputes regarding crushed cartons, damaged derailleur hangers, or paint scuffs[^r26]. If a retailer account is on hold, supervisor clearance is required before progressing warranty replacements[^r14].

### 2. Technical review and parts disposition
The technical services desk evaluates the reported defect and determines whether to authorise replacement components—such as motor units, battery casings, or wiring harnesses—or to request that the shop return the damaged assembly[^r5]. Common small electrical components, including wiring looms and brake sensors, are stocked as separate lines rather than bundled exclusively in service kits, and are binned in Leeds for direct dispatch to bike shops[^r20][^r21]. Technical guidance bulletins provide retailers with instructions regarding damping shims for down-tube battery terminal fretting, frame routing paths to avoid pinching handlebar display auxiliary cables, and wheel hub adjustments[^r27][^r30][^r31].

### 3. Shipping and receipt of returns
When physical returns are required, approved claims receive an RMA number[^r10]. Bike shops must return battery packs exclusively using an approved dangerous-goods carrier service, supported by mandatory carrier hazard notification advice sheets issued by customer service[^r10][^r19]. Upon carrier offloading at the Manchester plant warehouse or Leeds facility, every crate containing returns or defective display units must immediately receive a clear quarantine label, supported by prompt return paperwork from the sales office[^r6][^r22][^r23][^r28][^r29].

### 4. Physical inspection and settlement
The Manchester warehouse performs the physical inspection of returned assemblies[^r6]. Quality must decide whether to repair, replace, or refuse the claim within 10 working days of receiving the returned item[^r11]. Credit notes cannot be posted to the sales ledger until physical parts have been returned, booked in, and signed off by stores or technical services[^r7][^r17]. Following inspection sign-off, Manchester accounts staff apply the credit note to the sales ledger and authorise any agreed retailer labour contributions[^r7].

## Forms and screens

* [[screen-sal-srl-16|SAL-SRL-16]] (Serial Registration Reg): Validates frame and pack serial numbers during RMA approval[^r8][^r15].
* RMA Approval (`rma_approve`): Ledgerline transaction that verifies serial registration and warranty terms, generating [[err-rma-0210|ERR-RMA-0210]] or ERR-RMA-0211 on validation failure[^r15][^r16].
* Return Tracking Sheet: Internal tracking document circulated between the service desk and the warehouse to monitor retailer returns[^r18].
* Intake Form: E-mail intake form capturing defect details and pre-collection packaging photographs[^r26].

## What to do when something does not look right

* **Battery arrived via standard parcel carrier**: If a battery pack arrives through an ordinary parcel carrier instead of an approved dangerous-goods service, staff must immediately notify the safety officer and log the safety incident on the claim file before unpacking[^r12].
* **Mismatched serial number or goods**: If the physical items received do not match the serial number or description on the RMA record, staff must pause the claim, retain the package in the returns bay, and refer the matter to Quality without moving mismatched components into the workshop[^r13].

## See also

* [[err-rma-0210|ERR-RMA-0210 Serial not registered]]
* [[man-err-72|MAN-ERR-72 Ledgerline ERP 7.2 Message and Error Code]]
* [[pol-bat-004|POL-BAT-004 Battery Safety and Handling Policy]]
* [[pol-ret-006|POL-RET-006 Returns Policy]]
* [[screen-sal-srl-16|SAL-SRL-16 Serial Registration Reg]]
* [[sop-qua-002|SOP-QUA-002 Damaged Battery Pack Quarantine]]
* [[user-imorgan|Isla Morgan (IMORGAN)]]
* [[user-pjansen|Pieter Jansen (PJANSEN)]]

## References

[^r1]: 02_procedures/SOP-SAL-002 Warranty Claims (RMA) v1.1.pdf, p. 1, Field Value
[^r2]: 02_procedures/SOP-SAL-002 Warranty Claims (RMA) v1.1.pdf, p. 2, §2. Scope
[^r3]: 02_procedures/SOP-SAL-002 Warranty Claims (RMA) v1.1.pdf, p. 2, §2. Scope
[^r7]: 02_procedures/SOP-SAL-002 Warranty Claims (RMA) v1.1.pdf, p. 2, §3. Responsibilities
[^r10]: 02_procedures/SOP-SAL-002 Warranty Claims (RMA) v1.1.pdf, p. 3, §5. Procedure
[^r4]: 02_procedures/SOP-SAL-002 Warranty Claims (RMA) v1.1.pdf, p. 2, §3. Responsibilities
[^r8]: 02_procedures/SOP-SAL-002 Warranty Claims (RMA) v1.1.pdf, p. 3, §5. Procedure
[^r15]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 21
[^r9]: 02_procedures/SOP-SAL-002 Warranty Claims (RMA) v1.1.pdf, p. 3, §5. Procedure
[^r16]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 21
[^r26]: 10_meeting_notes/2026-01-17 Warranty review.docx, Discussion
[^r14]: 02_procedures/SOP-SAL-002 Warranty Claims (RMA) v1.1.pdf, p. 3, Practical tips
[^r5]: 02_procedures/SOP-SAL-002 Warranty Claims (RMA) v1.1.pdf, p. 2, §3. Responsibilities
[^r20]: 10_meeting_notes/2024-03-10 Sales meeting.md, Discussion
[^r21]: 10_meeting_notes/2024-03-10 Sales meeting.md, Discussion
[^r27]: 10_meeting_notes/2026-01-17 Warranty review.docx, Discussion
[^r30]: 10_meeting_notes/2026-05-23 Quality meeting.docx, Discussion
[^r31]: 10_meeting_notes/2026-05-23 Quality meeting.docx, Discussion
[^r19]: 10_meeting_notes/2022-10-15 Battery safety committee.md, Discussion
[^r6]: 02_procedures/SOP-SAL-002 Warranty Claims (RMA) v1.1.pdf, p. 2, §3. Responsibilities
[^r22]: 10_meeting_notes/2024-10-01 Stores and logistics meeting.md, Discussion
[^r23]: 10_meeting_notes/2025-03-18 Leeds unit update.docx, Discussion
[^r28]: 10_meeting_notes/2026-04-18 Stores and logistics meeting.docx, Discussion
[^r29]: 10_meeting_notes/2026-04-18 Stores and logistics meeting.docx, Discussion
[^r11]: 02_procedures/SOP-SAL-002 Warranty Claims (RMA) v1.1.pdf, p. 3, §5. Procedure
[^r17]: 10_meeting_notes/2022-02-10 Sales meeting.docx, Warranty Claims and Customer Feedback
[^r18]: 10_meeting_notes/2022-02-10 Sales meeting.docx, Warranty Claims and Customer Feedback
[^r12]: 02_procedures/SOP-SAL-002 Warranty Claims (RMA) v1.1.pdf, p. 4, What to do when something does not look right
[^r13]: 02_procedures/SOP-SAL-002 Warranty Claims (RMA) v1.1.pdf, p. 4, What to do when something does not look right
