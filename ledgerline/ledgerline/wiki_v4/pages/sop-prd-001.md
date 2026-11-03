---
title: "SOP-PRD-001 Work Order Release and Backflush"
type: "procedure"
slug: "sop-prd-001"
summary: "Standard operating procedure governing the formal release of production work orders, component availability checks, manual battery issue, and backflushing in Ledgerline ERP."
audience: "staff"
status: "current"
sources: ["07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf", "02_procedures/SOP-PRD-001 Work Order Release and Backflush v1.5.pdf", "04_service_definitions/production/wo_release.yaml", "10_meeting_notes/2024-10-01 Stores and logistics meeting.md", "10_meeting_notes/2025-10-08 Continuous improvement workshop.docx", "10_meeting_notes/2026-04-18 Stores and logistics meeting.docx", "09_email_archive/2021/2021-04-04_End-of-line test rig downtime.eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Document code | SOP-PRD-001 |
| Title | Work Order Release and Backflush |
| Version | 1.5 |
| Effective date | 2024-11-01 |
| Owner | Stefan Berg (SBERG) |
| Approver | Henrik Weber (HWEBER) |
| Classification | INTERNAL |

SOP-PRD-001 governs the formal release of production work orders and subsequent component backflushing across Northbridge Cycles' assembly lines [^r2][^r3]. It requires production planning to confirm full component availability before release and enforces manual serial tracking for battery packs rather than automated backflush [^r4][^r6]. The procedure ensures accurate cycle counts and inventory posting across the Manchester plant and the Leeds sub-assembly unit [^r3][^r11].

| Field | Value |
|---|---|
| Document code | SOP-PRD-001 [^r2] |
| Version | 1.5 [^r2] |
| Effective date | 2024-11-01 [^r2] |
| Author | [[user-sberg|Stefan Berg]] [^r2] |
| Approver | [[user-hweber|Henrik Weber]] [^r2] |
| Classification | INTERNAL [^r2] |

## Steps

Production order release and backflushing apply to assembly operations at the Manchester plant and the Leeds sub-assembly facility for standard electric bicycle builds, frame prep operations, and battery housing assemblies [^r3].

1. **Pre-release component check**: Production planning must verify component availability before advancing any work order to released status, and work orders must never be released if shortages exist [^r4]. Work order release executes in Ledgerline ERP 7.2 through service `wo_release` via stored procedure `sp_wo_release`, which validates that the order is in DRAFT status and that an active BOM and all components are available [^r9].
2. **Work order release**: Work orders must be formally released at least two days before the scheduled start date [^r5]. If shortages exist during the release attempt, the transaction fails and raises error [[err-wo-0310|ERR-WO-0310]] [^r5].
3. **Pre-line material issue**: Stores personnel must enter issue records or stores issue dockets against job orders on the system before moving raw castings, bought-in electrical sub-assemblies, or other materials out of holding pens to the assembly line, avoiding false line shortages and cycle count variances [^r10][^r12].
4. **Battery pack issue**: [[items-bat|Battery packs]] are exempt from automated backflushing and must be issued individually by serial number [^r6].
5. **Backflushing and completion posting**: Finished bicycles cannot be signed off or booked into stock without completing final safety and torque checks on the end-of-line test rig [^r13]. Electronic work order sign-offs must not be held until week end, as delayed postings postpone the automated issue of fasteners, wiring clips, and motor mount brackets, leading to inventory variances [^r11]. When completions are posted, batch job JOB-PRD-015 issues backflushed components into table `bkf_hdr`, while work order header details remain tracked in table `wo_hdr` [^r1][^r6].
6. **Order closure and archiving**: Work orders must be closed within five working days of the final completion [^r7]. Paper records—including the traveller document, manual component issue slips, inspection sheets, and final completion tickets—must be boxed by production run and archived in the site records room [^r8].

## Forms and screens

* [[screen-prd-wo-01|PRD-WO-01]] (Work Order Entry): Used to release production work orders at least two days prior to start date [^r5].
* [[screen-inv-mrn-08|INV-MRN-08]] (Material Issue Entry): Used to record manual component issues by serial number for battery packs [^r6].
* Table `wo_hdr`: Stores work order header data including work order number (`wo_no`), item code (`itm_cd`), quantity (`qty`), start date (`start_dt`), work centre code (`wc_cd`), and cost centre code (`cc_cd`) [^r1].
* Table `bkf_hdr`: Records component backflushing entries posted upon work order completion [^r1].

## See also

* [[err-wo-0310|ERR-WO-0310 Component Shortage on Work Order Release]]
* [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]
* [[screen-inv-mrn-08|INV-MRN-08 Material Issue Entry]]
* [[services-prd-wo|PRD wo services]]
* [[items-bat|BAT-* items]]
* [[man-dd-72-all|MAN-DD-72-ALL Ledgerline ERP 7.2 Data Dictionary: all]]
* [[decision-2024-10-01-stores-logistics|Stores and Logistics Meeting Decisions (2024-10-01)]]
* [[decision-2026-04-18-stores-and-logistics|Stores and Logistics Meeting Decisions 2026-04-18]]
* [[topic-continuous-improvement-2025-10-08|Continuous Improvement Workshop (2025-10-08)]]
* [[user-sberg|Stefan Berg (SBERG)]]
* [[user-hweber|Henrik Weber (HWEBER)]]

## References

[^r2]: 02_procedures/SOP-PRD-001 Work Order Release and Backflush v1.5.pdf, p. 1, Work Order Release and Backflush
[^r3]: 02_procedures/SOP-PRD-001 Work Order Release and Backflush v1.5.pdf, p. 2, §2. Scope
[^r4]: 02_procedures/SOP-PRD-001 Work Order Release and Backflush v1.5.pdf, p. 2, §3. Responsibilities
[^r6]: 02_procedures/SOP-PRD-001 Work Order Release and Backflush v1.5.pdf, p. 3, §5. Procedure
[^r11]: 10_meeting_notes/2025-10-08 Continuous improvement workshop.docx, Discussion
[^r9]: 04_service_definitions/production/wo_release.yaml, procedures
[^r5]: 02_procedures/SOP-PRD-001 Work Order Release and Backflush v1.5.pdf, p. 3, §5. Procedure
[^r10]: 10_meeting_notes/2024-10-01 Stores and logistics meeting.md, Discussion
[^r12]: 10_meeting_notes/2026-04-18 Stores and logistics meeting.docx, Discussion
[^r13]: 09_email_archive/2021/2021-04-04_End-of-line test rig downtime.eml, body
[^r1]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 17, Table wo_hdr
[^r7]: 02_procedures/SOP-PRD-001 Work Order Release and Backflush v1.5.pdf, p. 3, §5. Procedure
[^r8]: 02_procedures/SOP-PRD-001 Work Order Release and Backflush v1.5.pdf, p. 4, §6. Records
