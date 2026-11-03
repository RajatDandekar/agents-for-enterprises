---
title: "QA-BTT-03 Battery End-Of-Line Test Entry"
type: "screen"
slug: "screen-qa-btt-03"
summary: "Production and quality screen capturing end-of-line electrical test results and quarantine holds for assembled electric bicycle power packs."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf", "03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/btt_get.yaml", "04_service_definitions/production/btt_save.yaml", "04_service_definitions/production/btt_search.yaml", "08_release_notes/RN-7.2.0 Ledgerline Release Notes.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen | QA-BTT-03 |
| Name | Battery End-Of-Line Test Entry |
| Menu | Production > Battery end-of-line |
| Roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN |
| Read service | btt_get, btt_search |
| Save service | btt_save |
| Batch job | JOB-PRD-022 |

Screen QA-BTT-03 captures open circuit voltage and internal resistance for assembled electric bicycle power packs at the Manchester plant and Leeds assembly unit before packs can be released to assembly lines or finished goods stores [^r4]. Manual entry fields for individual pack electrical readings are locked against manual typing, displaying imported values, overall pass/fail status, and serial references from automated test rig feeds [^r18]. Test-rig results from test rigs BTR-01 and BTR-02 are uploaded automatically into QA-BTT-03 every 15 minutes by batch job JOB-PRD-022 owned by Pieter Jansen [^r1][^r7]. If a test rig rejects a battery pack, QA-BTT-03 displays the failure category and automatically applies a quarantine hold to the finished assembly in inventory records, blocking allocation to sales orders and movement to despatch [^r19].

## Fields

Screen QA-BTT-03 is accessed from the Production and Quality menu via Production > Battery end-of-line by users with roles PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, and SYS-ADMIN [^r2][^r5][^r9].

The screen contains the following fields:
* **PACK SERIAL** (`serial_no`): Battery pack serial number; mandatory [^r3][^r5][^r10][^r13][^r16].
* **ITEM CD** (`itm_cd`): Item code; mandatory [^r3][^r5][^r10][^r16].
* **OCV (V)** (`ocv`): Open circuit voltage; mandatory [^r3][^r5][^r10][^r16].
* **IR (MOHM)** (`ir_mohm`): Internal resistance; mandatory [^r3][^r5][^r10][^r16].
* **PASS/FAIL** (`result`): Test verdict; mandatory [^r3][^r5][^r10][^r16].
* **STATUS** (`status`): Record status; optional [^r3][^r5].

Plant test rigs must drop standard text format test result files containing pack serial reference, individual cell outcomes, and final rig verdict into a designated network drop folder for automated polling and archiving [^r21]. Permitted adjustments can be made to saved battery records on QA-BTT-03 by recalling the pack with `btt_get` and saving, provided STATUS has not been locked by quality control [^r8]. Clearing an erroneous quarantine hold on a battery record in QA-BTT-03 requires supervisor sign-off [^r20].

## Keys and services

Screen QA-BTT-03 interfaces with the following [[services-prd-btt|PRD btt services]] [^r2][^r12]:
* **F2 / Enter**: Calls read service `btt_search` for BATTERY END-OF-LINE TEST LIST lookups [^r6][^r11][^r17].
* **F3**: Calls PRD read service `btt_get` (BATTERY END-OF-LINE TEST GET, endpoint POST `/ll72/svc/btt_get`) using mandatory parameter `serial_no` to retrieve battery end-of-line test details [^r6][^r11][^r13].
* **F8**: Calls POST service `btt_save` (BATTERY END-OF-LINE TEST SAVE) to commit battery end-of-line test entries [^r6][^r11][^r15].

## Messages

Screen QA-BTT-03 raises the following error codes:
* [[err-itm-0011]]: Raised when an item code is invalid or inactive [^r11].
* `ERR-BTT-0001`: 'BATTERY END-OF-LINE TEST NOT FOUND', raised when calling service `btt_get` [^r11][^r14].
* `ERR-BTT-0110`: Raised by screen transactions [^r11].
* `ERR-BTT-0120`: Raised by screen transactions [^r11].

## Versions and conflicts

* Today's rule: Manual entry fields for individual pack electrical readings are locked against manual typing and are populated by automated test rig feeds [^r18]. The older or general production manual lists the fields as standard screen fields without detailing the field-locking mechanism introduced in RN-7.2.0 [^r3]. Kind: contradiction.

## See also

* [[services-prd-btt|PRD btt services]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[screen-inv-lot-10|INV-LOT-10 Lot / Serial Entry]]
* [[screen-inv-qch-11|INV-QCH-11 Quality Hold Entry]]
* [[screen-qa-ins-01|QA-INS-01 Incoming Inspection Entry]]
* [[screen-qa-ncr-02|QA-NCR-02 Non-Conformance Report Entry]]

## References

[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 41, Purpose
[^r18]: 08_release_notes/RN-7.2.0 Ledgerline Release Notes.pdf, p. 3, Quality: Battery end-of-line test results (QA-BTT-03), loaded from the test rig
[^r1]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 4, §2. Job details
[^r7]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 44, Questions users ask
[^r19]: 08_release_notes/RN-7.2.0 Ledgerline Release Notes.pdf, p. 3, Quality: Battery end-of-line test results (QA-BTT-03), loaded from the test rig
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 41, §13. Battery End-Of-Line Test (QA-BTT-03)
[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 42, Step by step
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 31, QA-BTT-03 BATTERY END-OF-LINE TEST ENTRY
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 41, §13. Battery End-Of-Line Test (QA-BTT-03)
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 31, QA-BTT-03 BATTERY END-OF-LINE TEST ENTRY
[^r13]: 04_service_definitions/production/btt_get.yaml, service: btt_get
[^r16]: 04_service_definitions/production/btt_save.yaml, request
[^r21]: 08_release_notes/RN-7.2.0 Ledgerline Release Notes.pdf, p. 4, Quality: Battery end-of-line test results (QA-BTT-03), loaded from the test rig
[^r8]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 44, Questions users ask
[^r20]: 08_release_notes/RN-7.2.0 Ledgerline Release Notes.pdf, p. 3, Quality: Battery end-of-line test results (QA-BTT-03), loaded from the test rig
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 60, btt_save BATTERY END-OF-LINE TEST SAVE
[^r6]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 42, Step by step
[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 31, QA-BTT-03 BATTERY END-OF-LINE TEST ENTRY
[^r17]: 04_service_definitions/production/btt_search.yaml, screen: QA-BTT-03
[^r15]: 04_service_definitions/production/btt_save.yaml, service: btt_save
[^r14]: 04_service_definitions/production/btt_get.yaml, errors
