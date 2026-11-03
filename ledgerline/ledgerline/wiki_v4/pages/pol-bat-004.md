---
title: "POL-BAT-004 Battery Safety and Handling Policy"
type: "policy"
slug: "pol-bat-004"
summary: "Policy governing safety, handling, storage, quarantine, and transport rules for all lithium-cell components across Northbridge sites."
audience: "staff"
status: "current"
sources: ["07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf", "07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx", "01_policies/POL-BAT-004 Battery Safety and Handling Policy v1.2.pdf", "01_policies/POL-HSE-010 Health and Safety Policy v5.0.pdf", "02_procedures/SOP-INV-004 Battery Pack Storage and Handling v1.0.pdf", "11_training/BHT-01 Battery handling course slides.pdf", "11_training/QRC-07 Lithium battery labels.pdf", "11_training/intranet_export_2016/page_health_and_safety_in_the_warehouse.html", "10_meeting_notes/2022-10-15 Battery safety committee.md", "10_meeting_notes/2025-03-18 Leeds unit update.docx", "10_meeting_notes/2026-06-10 Health and safety committee.docx", "09_email_archive/2023/2023-02-27_Battery fire drill.eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | POL-BAT-004 |
| Title | Battery Safety and Handling Policy |
| Owner | Quality |
| Approver | Henrik Weber |
| Effective | 2025-11-01 |
| Status | current |
| Version | v1.2 |

POL-BAT-004 defines safety, storage, handling, quarantine, and transport rules for all lithium-cell components across Northbridge sites [^r4][^r5]. Approved by plant head [[user-hweber|Henrik Weber]], it establishes fire-cell limits, mandatory state of charge controls, and hazardous goods transport classifications [^r4][^r8][^r9][^r11]. Compliance is mandatory for all personnel working in battery storage and assembly zones [^r6][^r12].

| Field | Value |
|---|---|
| Document code | POL-BAT-004 |
| Version | v1.2 |
| Owner | Quality |
| Approver | [[user-hweber|Henrik Weber]] |
| Effective date | 2025-11-01 |
| Status | current |

## Clauses

### 1. Purpose and scope
The policy applies to all lithium-cell items at Northbridge, including [[items-bat|battery packs]], cells, hub and mid-drive motors, chargers, and any component flagged as a lithium cell in the item master [^r5]. In the Manchester plant, all covered parts must move directly to designated bunded battery cages [^r6]. At the Leeds site, items remain in the segregated storage area until required on sub-assembly benches [^r6].

### 2. Storage
Battery packs must be booked in Ledgerline to warehouse WH-MAN-STR within the Manchester main stores fire-cell area across bin zones BAT-Z1 to BAT-Z4, and must not use the legacy warehouse code WH-MAN-BAT [^r7]. Each fire cell has a strict limit of 1,500 battery packs, setting the total storage capacity of the Manchester fire-cell area to 6,000 packs [^r8][^r15]. Packs in stores must maintain a state of charge between 30% and 50% [^r9][^r16]. Charging packs inside the store boundary is strictly prohibited for stores personnel [^r9].

### 3. Damaged packs
Any battery pack that is damaged, swollen, wet, or dropped must be transferred immediately using heat-resistant gloves into the red quarantine bin containing vermiculite granules located in fire cell BAT-Z4 [^r10][^r17]. Staff must report the incident to Quality within the same shift by raising a non-conformance report on screen [[screen-qa-ncr-02|QA-NCR-02]] [^r10].

### 4. Transport
Battery packs dispatched alone must be declared as UN3480, whereas packs fitted to or packaged with a bicycle must be declared as UN3481 [^r11][^r18]. Every parcel containing a battery pack must display lithium battery handling label PKG-LBL-UN affixed flat [^r11][^r20]. Outbound shipments require carrier service DGX; missing labels trigger Ledgerline error [[err-dlv-0320|ERR-DLV-0320]], and unapproved freight carrier bookings fail with error ERR-FRT-0510 [^r2][^r3][^r18][^r20].

### 5. Training
All personnel handling battery packs must complete battery-handling training course BHT-01 before beginning their first shift in the fire-cell area [^r12]. Certification under BHT-01 must be renewed every 24 months [^r12][^r19].

## Versions and conflicts

* **Warehouse code booking**: Current policy requires battery stock to be booked in Ledgerline under warehouse WH-MAN-STR [^r7]. The legacy code WH-MAN-BAT was merged in 2019 and is superseded (`superseded`) [^r7].

## See also

* [[sop-inv-004|SOP-INV-004 Battery Pack Storage and Handling]]
* [[sop-qua-002|SOP-QUA-002 Damaged Battery Pack Quarantine]]
* [[pol-hse-010|POL-HSE-010 Health and Safety Policy]]
* [[screen-qa-ncr-02|QA-NCR-02 Non-Conformance Report Entry]]
* [[err-dlv-0320|ERR-DLV-0320 Lithium Battery Label Required]]
* [[items-bat|BAT-* items]]
* [[items-pkg|PKG-* items]]
* [[user-hweber|Henrik Weber (HWEBER)]]
* [[topic-un-38-3-certificates|UN 38.3 Certificates]]

## References

[^r4]: 01_policies/POL-BAT-004 Battery Safety and Handling Policy v1.2.pdf, p. 1, Battery Safety and Handling Policy
[^r5]: 01_policies/POL-BAT-004 Battery Safety and Handling Policy v1.2.pdf, p. 1, §1. Purpose and scope
[^r8]: 01_policies/POL-BAT-004 Battery Safety and Handling Policy v1.2.pdf, p. 2, §2. Storage
[^r9]: 01_policies/POL-BAT-004 Battery Safety and Handling Policy v1.2.pdf, p. 2, §2. Storage
[^r11]: 01_policies/POL-BAT-004 Battery Safety and Handling Policy v1.2.pdf, p. 4, §4. Transport
[^r6]: 01_policies/POL-BAT-004 Battery Safety and Handling Policy v1.2.pdf, p. 1, §1. Purpose and scope
[^r12]: 01_policies/POL-BAT-004 Battery Safety and Handling Policy v1.2.pdf, p. 4, §5. Training
[^r7]: 01_policies/POL-BAT-004 Battery Safety and Handling Policy v1.2.pdf, p. 2, §2. Storage
[^r15]: 02_procedures/SOP-INV-004 Battery Pack Storage and Handling v1.0.pdf, p. 3, §5. Procedure
[^r16]: 11_training/BHT-01 Battery handling course slides.pdf, p. 3, Storage
[^r10]: 01_policies/POL-BAT-004 Battery Safety and Handling Policy v1.2.pdf, p. 3, §3. Damaged packs
[^r17]: 11_training/BHT-01 Battery handling course slides.pdf, p. 4, Damaged packs
[^r18]: 11_training/BHT-01 Battery handling course slides.pdf, p. 5, Shipping
[^r20]: 11_training/QRC-07 Lithium battery labels.pdf, p. 1, Steps
[^r2]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-DLV-0320, SHEET Error codes
[^r3]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-FRT-0510, SHEET Error codes
[^r19]: 11_training/BHT-01 Battery handling course slides.pdf, p. 6, Refresher
