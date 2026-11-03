---
title: "QA-NCR-02 Non-Conformance Report Entry"
type: "screen"
slug: "screen-qa-ncr-02"
summary: "Ledgerline screen for creating, searching, fetching, and closing production and quality non-conformance reports."
audience: "staff"
status: "current"
sources: ["01_policies/POL-BAT-004 Battery Safety and Handling Policy v1.2.pdf", "02_procedures/SOP-QUA-001 Incoming Inspection v2.0.pdf", "02_procedures/SOP-QUA-002 Damaged Battery Pack Quarantine v1.1.pdf", "03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/ncr_close.yaml", "04_service_definitions/production/ncr_get.yaml", "04_service_definitions/production/ncr_save.yaml", "04_service_definitions/production/ncr_search.yaml", "11_training/BHT-01 Battery handling course slides.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | QA-NCR-02 |
| Module | Production |
| Menu path | Production > Non-Conformance report |
| Roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN |
| Read services | ncr_get, ncr_search |
| Write services | ncr_save, ncr_close |
| Status | current |

QA-NCR-02 is the Ledgerline screen used to log, view, search, and close non-conformance reports across receiving, production, and battery handling [^r5][^r12]. Accessible via `Production > Non-Conformance report`, it captures defect details and isolates non-conforming items such as rejected inspection lots or damaged battery packs [^r1][^r2][^r5]. Raising an NCR on this screen is required during the same shift an issue is detected to enforce timely containment [^r1][^r22][^r23].

| Field | Code | Menu path | Roles | Read services | Write services | Status |
|---|---|---|---|---|---|---|
| Value | QA-NCR-02 | Production > Non-Conformance report | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN | ncr_get, ncr_search | ncr_save, ncr_close | current |

## Fields

Screen QA-NCR-02 contains the following header and detail fields [^r6]:
* **NCR NO** (`ncr_no`): Non-conformance report number (mandatory) [^r6][^r13].
* **ITEM CD** (`itm_cd`): Item identifier validated against the central master (mandatory) [^r6][^r7][^r13][^r20].
* **DEFECT CD** (`defect_cd`): Defect code describing the failure mode (mandatory) [^r6][^r13][^r20].
* **QTY** (`qty`): Defective quantity (mandatory) [^r6][^r13][^r20].
* **DESCRIPTION** (`descr`): Narrative detail of the defect (mandatory) [^r6][^r13][^r20].
* **GRN NO** (`grn_no`): Goods receipt note reference (optional) [^r6][^r13][^r20][^r21].
* **STATUS** (`status`): Processing status of the record (optional) [^r6][^r13][^r21].
* **COMMENT** (`comment`): Additional notes (optional) [^r6][^r13].

When logging incoming inspection failures under [[sop-qua-001|SOP-QUA-001]], the delivery reference, part identification, and specific failure reasons populate from the [[screen-qa-ins-01|QA-INS-01]] inspection sheet [^r2][^r3]. If a single consignment contains multiple defective item codes, an individual report must be created for each item reference rather than combining them [^r11].

Under [[pol-bat-004|POL-BAT-004]], [[sop-qua-002|SOP-QUA-002]], and BHT-01, team leaders must enter damaged, dropped, wet, or swollen [[items-bat|battery packs]] before the shift ends, uploading photographs of the damage, serial plate, and terminal condition [^r1][^r22][^r23]. Users must verify that the serial number in the header matches the casing label exactly and select defect classifications such as casing rupture, terminal shorting, or swelling [^r24]. If a casing serial number is defaced or illegible, the batch reference is entered on QA-NCR-02, the illegibility is noted in the narrative box, and a physical inspection is requested from the quality team [^r1][^r4].

## Keys and services

Screen QA-NCR-02 interacts with backend [[services-prd-ncr|PRD ncr services]] via four primary operations [^r5][^r14][^r15]:
* **ncr_search** (`F2` / `Enter`): Read service (`POST /ll72/svc/ncr_search`) that queries NCR records using optional filters `grn_no`, `itm_cd`, `defect_cd`, and `status` [^r14][^r21].
* **ncr_get** (`F3`): Read service (`POST /ll72/svc/ncr_get`) that retrieves an existing report record by `ncr_no` [^r14][^r17].
* **ncr_save** (`F8`): Write service (`POST /ll72/svc/ncr_save`) that creates or updates a non-conformance record using `itm_cd`, `defect_cd`, `qty`, `descr`, and optional `grn_no` [^r14][^r19][^r20].
* **ncr_close**: Write service (`POST /ll72/svc/ncr_close`) that closes an open non-conformance report [^r14][^r16].

## Messages

The screen validates entries against the following error messages:
* [[err-itm-0011|ERR-ITM-0011]]: Displayed when an item code entered in `ITEM CD` is missing, obsolete, or inactive in the central master [^r7][^r14].
* **ERR-NCR-0001**: Displayed during `ncr_save` when mandatory fields (`ITEM CD`, `DEFECT CD`, `QTY`) are missing, or when `QTY` is zero or negative [^r8][^r14]. The service definition for `ncr_get` also assigns ERR-NCR-0001 to indicate report not found [^r18].
* **ERR-NCR-0201**: Displayed when attempting to retrieve, modify, or close an `NCR NO` that does not exist in the database [^r10][^r14].
* **ERR-NCR-0801**: Displayed when attempting to modify or execute `ncr_save` or `ncr_close` against an already closed non-conformance report [^r9][^r14].

## Versions and conflicts

* **ERR-NCR-0001 error definition**: Screen user manuals define ERR-NCR-0001 as a validation failure on `ncr_save` when mandatory fields are omitted or quantity is non-positive (MAN-PRD-72, MAN-SCR-72) [^r8][^r14]. However, the backend definition for `ncr_get` defines ERR-NCR-0001 as "NON-CONFORMANCE REPORT NOT FOUND" (`ncr_get.yaml`) [^r18]. (kind: `contradiction`).
* **ncr_no field requirement**: Screen references designate `ncr_no` as a mandatory field on QA-NCR-02 (MAN-PRD-72, MAN-SCR-72) [^r6][^r13], whereas the `ncr_save` service schema lists only `itm_cd`, `defect_cd`, `qty`, and `descr` as required input parameters (`ncr_save.yaml`) [^r20]. (kind: `contradiction`).

## See also

* [[screen-qa-ins-01|QA-INS-01 Incoming Inspection Entry]]
* [[services-prd-ncr|PRD ncr services]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[sop-qua-001|SOP-QUA-001 Incoming Inspection]]
* [[sop-qua-002|SOP-QUA-002 Damaged Battery Pack Quarantine]]
* [[pol-bat-004|POL-BAT-004 Battery Safety and Handling Policy]]
* [[items-bat|BAT-* items]]

## References

[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 37, §12. Non-Conformance Report (QA-NCR-02)
[^r12]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 32, QA-NCR-02 NON-CONFORMANCE REPORT ENTRY
[^r1]: 01_policies/POL-BAT-004 Battery Safety and Handling Policy v1.2.pdf, p. 3, §3. Damaged packs
[^r2]: 02_procedures/SOP-QUA-001 Incoming Inspection v2.0.pdf, p. 3, §5. Procedure
[^r22]: 11_training/BHT-01 Battery handling course slides.pdf, p. 4, Damaged packs
[^r23]: 02_procedures/SOP-QUA-002 Damaged Battery Pack Quarantine v1.1.pdf, p. 3, §5. Procedure: notes and common mistakes
[^r6]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 37, §12. Non-Conformance Report (QA-NCR-02)
[^r13]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 32, QA-NCR-02 NON-CONFORMANCE REPORT ENTRY
[^r7]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 39, Messages
[^r20]: 04_service_definitions/production/ncr_save.yaml, request.fields
[^r21]: 04_service_definitions/production/ncr_search.yaml, service: ncr_search
[^r3]: 02_procedures/SOP-QUA-001 Incoming Inspection v2.0.pdf, p. 4, §5. Procedure: notes and common mistakes
[^r11]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 40, Tips
[^r24]: 02_procedures/SOP-QUA-002 Damaged Battery Pack Quarantine v1.1.pdf, p. 4, §5. Procedure: notes and common mistakes
[^r4]: 02_procedures/SOP-QUA-002 Damaged Battery Pack Quarantine v1.1.pdf, p. 4, §5. Procedure: notes and common mistakes
[^r14]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 32, QA-NCR-02 NON-CONFORMANCE REPORT ENTRY
[^r15]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 60, ncr_save NON-CONFORMANCE REPORT SAVE
[^r17]: 04_service_definitions/production/ncr_get.yaml, screen
[^r19]: 04_service_definitions/production/ncr_save.yaml, service: ncr_save
[^r16]: 04_service_definitions/production/ncr_close.yaml, service
[^r8]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 39, Messages
[^r18]: 04_service_definitions/production/ncr_get.yaml, errors
[^r10]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 39, Messages
[^r9]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 39, Messages
