---
title: "SOP-PRD-002 Engineering Change (ECN)"
type: "procedure"
slug: "sop-prd-002"
summary: "Standard operating procedure governing permanent engineering change notices across Manchester and Leeds facilities, including Ledgerline workflow and UN 38.3 test requirements."
audience: "staff"
status: "current"
sources: ["07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf", "02_procedures/SOP-PRD-002 Engineering Change v1.0.pdf", "03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "04_service_definitions/production/ecn_approve.yaml", "04_service_definitions/production/ecn_release.yaml", "04_service_definitions/production/ecn_save.yaml", "08_release_notes/RN-7.1 Ledgerline Release Notes.pdf", "10_meeting_notes/2025-10-08 Continuous improvement workshop.docx", "10_meeting_notes/2026-09-18 Ledgerline key users.docx"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | SOP-PRD-002 |
| Title | Engineering Change (ECN) |
| Type | procedure |
| Owner | Stefan Berg |
| Approver | Henrik Weber |
| Effective date | 2024-02-01 |
| Status | current |

SOP-PRD-002 defines the mandatory procedure for managing permanent engineering change notices across production facilities at Northbridge Cycles [^r2][^r3]. It establishes the change control workflow in Ledgerline ERP, covering creation, dual-department approval, and bill of materials release [^r5][^r13][^r14][^r15]. Adherence ensures that open work orders on superseded revisions are resolved and that battery components maintain valid compliance certification before revised specifications reach the assembly lines [^r6][^r7][^r17].

| Field | Detail |
|---|---|
| Document Code | SOP-PRD-002 [^r2] |
| Version | v1.0 [^r2] |
| Author | [[user-sberg\|Stefan Berg]] [^r2] |
| Approved By | [[user-hweber\|Henrik Weber]] [^r2] |
| Effective Date | 2024-02-01 [^r2] |
| Primary Screen | [[screen-prd-ecn-06\|PRD-ECN-06]] [^r5] |
| Database Table | ecn_hdr [^r1] |

## Scope

The procedure governs all permanent alterations made to bicycle frames, electrical drive assemblies, sub-assemblies, and bought-in components used at the Manchester works and the Leeds unit [^r3]. Temporary workshop deviations and immediate safety stops fall outside this SOP and follow separate reporting channels [^r4].

## Steps

### 1. Pre-Change Technical Preparation
Before entering an engineering change notice (ECN) into the system, the proposed change must be discussed through technical channels and supported by revised drawings, vendor bulletins, or inspection reports [^r10]. If the change replaces an active component, staff must check warehouse stock levels to establish whether existing stock will be used up or quarantined immediately [^r11]. In addition, the effective date must be coordinated between production planning and quality to ensure adequate lead time for tooling and jigs in Manchester or Leeds [^r12].

### 2. ECN Creation in Ledgerline
Staff raise the change on screen [[screen-prd-ecn-06\|PRD-ECN-06]] by executing service `ecn_save` from [[services-prd-ecn|PRD ecn services]] [^r5][^r13][^r18]:
1. Open [[screen-prd-ecn-06\|PRD-ECN-06]] and leave the ECN NO field blank for system assignment [^r13].
2. Enter the ITEM CD, select the REASON, and provide the CHANGE TEXT and COMMENT [^r13].
3. Set the EFFECTIVE DT, ensuring the date is not in the past [^r13][^r18].
4. Click `ecn_save` to record the change in the `ecn_hdr` table [^r1][^r13].

### 3. Review and Approval Sign-Off
Approval requires formal sign-off from both Quality and Purchasing [^r5]. An authorised technical manager retrieves the draft record using `ecn_get` or `ecn_search` on [[screen-prd-ecn-06\|PRD-ECN-06]] and executes `ecn_approve` [^r14][^r16]. Ledgerline validates user credentials to prevent self-approval ([[err-apr-0003\|ERR-APR-0003]]) and ensure the transaction does not exceed approval limits ([[err-apr-0004\|ERR-APR-0004]]) [^r16]. Under Ledgerline 7.1, approved ECN records trigger an immediate revision check on active assembly runs, updating pick lists and restricting storekeepers from backflushing discontinued stock without a supervisory override [^r19]. Floor supervisors may authorise overrides for alternate parts during a block, and each override is logged in the audit trail [^r20].

### 4. Special Compliance for Lithium-Cell Parts
Where an engineering change affects a lithium-cell component—such as introducing an alternate cell manufacturer or altering the pack design—the change coordinator must verify that a fresh UN 38.3 test report is obtained prior to release in accordance with [[pol-sup-003\|POL-SUP-003]] §4.6 [^r6].

### 5. Release to Active Bills of Materials
Once all required sign-offs are complete, the change coordinator retrieves the approved record via `ecn_get` on [[screen-prd-ecn-06\|PRD-ECN-06]] and clicks `ecn_release` [^r15][^r17]. The system requires the ECN to be in DRAFT status prior to release execution and verifies that no active work orders remain committed to the superseded bill of materials (BOM) revision [^r17]. If open work orders exist on the old revision, Ledgerline blocks release and raises error [[err-ecn-0220\|ERR-ECN-0220]] [^r7].

### 6. Post-Release Archiving and Production Tracking
After release sign-off, the engineering department files the signed master paper pack in the engineering archives [^r8]. The systems administrator archives the superseded BOM and locks the active revision in Ledgerline [^r8]. Finally, production personnel must record the serial number of the first completed bicycle manufactured with the revised component directly onto the signed paper ECN record [^r9].

## Forms and screens

* [[screen-prd-ecn-06\|PRD-ECN-06]] (Engineering Change Entry): Primary interface used to draft, approve, and release engineering change records [^r5][^r13][^r14][^r15].
* [[services-prd-ecn|PRD ecn services]]: Service group managing backend calls including `ecn_save` (record entry), `ecn_approve` (sign-off validation), and `ecn_release` (BOM revision update) [^r13][^r14][^r15][^r16][^r17][^r18].
* Master ECN Paper Pack: Physical document retained in engineering archives bearing approvals and the first-built bicycle serial number [^r8][^r9].

## Operational Notes

* In October 2025, continuous improvement workshops identified the need for a formal sign-off step between engineering and stock control before revised component listings are released for active production orders [^r21].
* Key user reviews in September 2026 noted that when altering motor housing bracket BOM lines, failing to remove obsolete component lines causes superseded hardware to pull into Manchester assembly pick lists [^r22].

## See also

* [[err-ecn-0220|ERR-ECN-0220 Open Work Orders on Revision]]
* [[errors-ecn|ERR-ECN Error Codes Reference]]
* [[man-dd-72-all|MAN-DD-72-ALL Ledgerline ERP 7.2 Data Dictionary: all]]
* [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]]
* [[pol-sup-003|POL-SUP-003 Supplier Policy]]
* [[screen-prd-ecn-06|PRD-ECN-06 Engineering Change Entry]]
* [[services-prd-ecn|PRD ecn services]]
* [[sop-prd-001|SOP-PRD-001 Work Order Release and Backflush]]

## References

[^r2]: 02_procedures/SOP-PRD-002 Engineering Change v1.0.pdf, p. 1, Version history
[^r3]: 02_procedures/SOP-PRD-002 Engineering Change v1.0.pdf, p. 2, §2. Scope
[^r5]: 02_procedures/SOP-PRD-002 Engineering Change v1.0.pdf, p. 3, §5. Procedure
[^r13]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 32, Worked example
[^r14]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 33, Worked example
[^r15]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 33, Worked example
[^r6]: 02_procedures/SOP-PRD-002 Engineering Change v1.0.pdf, p. 3, §5. Procedure
[^r7]: 02_procedures/SOP-PRD-002 Engineering Change v1.0.pdf, p. 3, §5. Procedure
[^r17]: 04_service_definitions/production/ecn_release.yaml, errors
[^r1]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 19, Table ecn_hdr
[^r4]: 02_procedures/SOP-PRD-002 Engineering Change v1.0.pdf, p. 2, §2. Scope
[^r10]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 30, Before you start
[^r11]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 30, Before you start
[^r12]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 31, Step by step
[^r18]: 04_service_definitions/production/ecn_save.yaml, errors
[^r16]: 04_service_definitions/production/ecn_approve.yaml, errors
[^r19]: 08_release_notes/RN-7.1 Ledgerline Release Notes.pdf, p. 3, Production: Engineering change notes (PRD-ECN-06)
[^r20]: 08_release_notes/RN-7.1 Ledgerline Release Notes.pdf, p. 4, Production: Engineering change notes (PRD-ECN-06)
[^r8]: 02_procedures/SOP-PRD-002 Engineering Change v1.0.pdf, p. 4, §6. Records
[^r9]: 02_procedures/SOP-PRD-002 Engineering Change v1.0.pdf, p. 5, §6. Records
[^r21]: 10_meeting_notes/2025-10-08 Continuous improvement workshop.docx, Discussion
[^r22]: 10_meeting_notes/2026-09-18 Ledgerline key users.docx, Discussion
