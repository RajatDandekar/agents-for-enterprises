---
title: "SOP-QUA-002 Damaged Battery Pack Quarantine"
type: "procedure"
slug: "sop-qua-002"
summary: "Standard operating procedure for immediate physical isolation, tagging, and Ledgerline ERP quality hold entry of damaged or compromised battery packs."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-INV-004 Battery Pack Storage and Handling v1.0.pdf", "02_procedures/SOP-QUA-002 Damaged Battery Pack Quarantine v1.1.pdf", "02_procedures/sop_inv_001_goods_receipt_v2.docx", "11_training/BHT-01 Battery handling course slides.pdf", "10_meeting_notes/2022-10-15 Battery safety committee.md", "10_meeting_notes/2026-07-30 Battery incident review.md", "09_email_archive/2026/2026-07-28_Failed battery lot - incoming abuse test.eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | SOP-QUA-002 |
| Title | Damaged Battery Pack Quarantine |
| Owner | [[user-pjansen|Pieter Jansen]] |
| Approver | [[user-hweber|Henrik Weber]] |
| Effective | 2025-11-01 |
| Status | current |
| Classification | INTERNAL |
| Version | 1.1 |

SOP-QUA-002 defines the mandatory procedure for isolating and logging damaged or compromised battery packs across Northbridge Cycles facilities [^r2][^r6]. Any unit that has suffered an impact, shows structural or packaging damage, or exhibits thermal abnormalities must be immediately withdrawn from production or storage and placed into designated quarantine containment [^r1][^r3][^r8]. It governs physical containment in fire-rated storage, emergency bench evacuation protocols, and inventory locking within Ledgerline ERP to prevent compromised [[items-bat|BAT-* items]] from being allocated to builds [^r3][^r4][^r12].

| Key | Value |
|---|---|
| Document code | SOP-QUA-002 [^r2] |
| Owner | [[user-pjansen|Pieter Jansen]] (Quality Manager) [^r2] |
| Approved by | [[user-hweber|Henrik Weber]] (Plant Head) [^r2] |
| Version | 1.1 [^r2] |
| Effective date | 2025-11-01 [^r2] |
| Classification | INTERNAL [^r2] |
| Status | Current [^r2] |

## Steps

### 1. Immediate identification and containment
* **Impacted and dropped cartons**: Under [[sop-inv-004|SOP-INV-004]] and SOP-QUA-002, any dropped battery carton must be quarantined immediately even if it appears undamaged, tagged with a red physical tag, and updated in Ledgerline ERP to remove it from available stock [^r1].
* **Delivery bay rejections**: Under [[sop-inv-001|SOP-INV-001]] and SOP-QUA-002, any battery delivery showing outer carton damage such as tears, dents, dampness, or crushed corners must be refused at the carrier vehicle, photographed, and reported to Quality immediately [^r16]. Warehouse goods-in staff must reject affected items at the bay, place them directly into quarantine, and sign the delivery sheet accordingly when crushed cartons or torn moisture barriers are detected [^r10].
* **Retailer returns**: If an email notification arrives regarding a returned pack from an independent bike shop, staff must inspect the carrier transit box outside the main roller door before signing the delivery sheet [^r6][^r7].
* **Line-side detection**: Shop floor operators and assembly staff detecting a dropped, dented, weeping, or hot pack must halt work immediately, raise the physical quarantine flag, notify the line supervisor without leaving the area unattended, and apply an initial warning label [^r8].
* **Thermal emergency**: Staff must treat any pack that feels warm to the touch or emits an unusual sweet smell as an active emergency and evacuate the immediate bench area [^r4]. If a battery pack in the red bin exhibits signs of active heat, smoke, or hissing, operatives must close the fire cell door, alert the shift supervisor immediately, and sound the local alarm without attempting photographs or screen work [^r14].

### 2. Physical transfer and isolation
* Suspect packs must be withdrawn from production or storage immediately and transferred directly into the dedicated external quarantine container using an approved fire-retardant transit drum and vermiculite bedding [^r3].
* Packs awaiting testing after transit damage must be isolated immediately into the fire-rated store rather than accumulating near the main assembly floor [^r18].
* Line supervisors must arrange the safe physical transfer of suspect packs to the designated outdoor fire-rated quarantine locker using heavy-duty transit containers and protective gloves, without attempting to test, charge, or dismantle them [^r9].
* Operatives must move the pack to the red quarantine bin in fire cell BAT-Z4 at once wearing gloves and eye protection [^r13][^r17].
* Storekeepers must complete a physical handwritten tie-on card attached to the container, and update the battery store quarantine register with pack serial number, reporting department, defect, and handler initials [^r15].

### 3. ERP logging and quarantine hold
* Quarantine status updates flagging damaged battery stock for isolation in the ERP system must not be delayed until following shifts [^r19].
* Quality engineers apply quarantine holds to inventory lots in Ledgerline ERP, issue formal vendor defect notifications, liaise with approved chemical waste carriers, and authorise final scrap or return transactions [^r11].
* If the quality engineer is off-site, the shift supervisor must execute the quarantine transaction in Ledgerline ERP to prevent the pack being allocated to a build order by the overnight planning run [^r12].
* When raising a scrap or return hold movement in Ledgerline ERP, vendor batch details must be transcribed directly from carrier consignment notes into the system notes field [^r5].
* Book the pack to quality hold on [[screen-inv-qch-11|INV-QCH-11]] [^r13].
* Raise an NCR on [[screen-qa-ncr-02|QA-NCR-02]] during the same shift, complete with photographs [^r13][^r17].

### 4. Disposition and resolution
* Quality must decide within 24 hours whether to return the pack to the supplier, refurbish it via [[cc-prd-09|PRD-09]], or send it for recycling [^r13].
* Packs failing incoming abuse verification must remain segregated in the quarantine holding bay and cannot be moved to general stores or released until collected by the vendor [^r20]. A lot of 400 battery packs was quarantined under these controls on 28 July 2026 after failing incoming abuse testing following an unannounced change in cell maker [^r21].
* Disposal consignment notes must be cross-referenced upon receipt against the register [^r15].

## Forms and screens

* [[screen-qa-ncr-02|QA-NCR-02]] (Non-Conformance Report Entry): Used to raise the formal NCR with attached defect photographs during the same shift [^r13][^r17].
* [[screen-inv-qch-11|INV-QCH-11]] (Quality Hold Entry): Used to execute the inventory hold movement, locking the suspect lots from production allocation and capturing vendor consignment details in system notes [^r5][^r12][^r13].
* Physical Tie-On Quarantine Card: Handwritten red physical tag attached directly to the transit container on the floor [^r1][^r15].
* Battery Store Quarantine Register: Physical register logging the pack serial number, defect, reporting department, and handler initials [^r15].

## See also

* [[items-bat|BAT-* items]]
* [[man-bht-01|BHT-01 Battery Handling Training Slides]]
* [[cc-prd-09|PRD-09 Battery refurbishment]]
* [[screen-inv-qch-11|INV-QCH-11 Quality Hold Entry]]
* [[screen-qa-ncr-02|QA-NCR-02 Non-Conformance Report Entry]]
* [[sop-inv-001|SOP-INV-001 Goods Receipt]]
* [[sop-inv-004|SOP-INV-004 Battery Pack Storage and Handling]]
* [[decision-2026-07-30-battery-incident-review|Battery Incident Review and Supplier Policy Amendment Decision (2026-07-30)]]
* [[user-hweber|Henrik Weber (HWEBER)]]
* [[user-pjansen|Pieter Jansen (PJANSEN)]]

## References

[^r2]: 02_procedures/SOP-QUA-002 Damaged Battery Pack Quarantine v1.1.pdf, p. 1, Damaged Battery Pack Quarantine
[^r6]: 02_procedures/SOP-QUA-002 Damaged Battery Pack Quarantine v1.1.pdf, p. 2, §2. Scope
[^r1]: 02_procedures/SOP-INV-004 Battery Pack Storage and Handling v1.0.pdf, p. 3, §5. Procedure
[^r3]: 02_procedures/SOP-QUA-002 Damaged Battery Pack Quarantine v1.1.pdf, p. 1, §1. Purpose
[^r8]: 02_procedures/SOP-QUA-002 Damaged Battery Pack Quarantine v1.1.pdf, p. 2, §3. Responsibilities
[^r4]: 02_procedures/SOP-QUA-002 Damaged Battery Pack Quarantine v1.1.pdf, p. 1, §1. Purpose
[^r12]: 02_procedures/SOP-QUA-002 Damaged Battery Pack Quarantine v1.1.pdf, p. 3, §3. Responsibilities
[^r16]: 02_procedures/sop_inv_001_goods_receipt_v2.docx, §5. Procedure: notes and common mistakes
[^r10]: 02_procedures/SOP-QUA-002 Damaged Battery Pack Quarantine v1.1.pdf, p. 2, §3. Responsibilities
[^r7]: 02_procedures/SOP-QUA-002 Damaged Battery Pack Quarantine v1.1.pdf, p. 2, §2. Scope
[^r14]: 02_procedures/SOP-QUA-002 Damaged Battery Pack Quarantine v1.1.pdf, p. 4, §5. Procedure: notes and common mistakes
[^r18]: 10_meeting_notes/2022-10-15 Battery safety committee.md, Discussion
[^r9]: 02_procedures/SOP-QUA-002 Damaged Battery Pack Quarantine v1.1.pdf, p. 2, §3. Responsibilities
[^r13]: 02_procedures/SOP-QUA-002 Damaged Battery Pack Quarantine v1.1.pdf, p. 3, §5. Procedure
[^r17]: 11_training/BHT-01 Battery handling course slides.pdf, p. 4, Damaged packs
[^r15]: 02_procedures/SOP-QUA-002 Damaged Battery Pack Quarantine v1.1.pdf, p. 5, §6. Records
[^r19]: 10_meeting_notes/2022-10-15 Battery safety committee.md, Discussion
[^r11]: 02_procedures/SOP-QUA-002 Damaged Battery Pack Quarantine v1.1.pdf, p. 2, §3. Responsibilities
[^r5]: 02_procedures/SOP-QUA-002 Damaged Battery Pack Quarantine v1.1.pdf, p. 1, §1. Purpose
[^r20]: 10_meeting_notes/2026-07-30 Battery incident review.md, Discussion
[^r21]: 09_email_archive/2026/2026-07-28_Failed battery lot - incoming abuse test.eml, body
