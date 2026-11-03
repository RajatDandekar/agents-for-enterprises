---
title: "PRD-ECN-06 Engineering Change Entry"
type: "screen"
slug: "screen-prd-ecn-06"
summary: "Ledgerline screen for initiating, approving, and releasing engineering change notes affecting bills of materials and routings across production works."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-PRD-002 Engineering Change v1.0.pdf", "03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/ecn_approve.yaml", "04_service_definitions/production/ecn_get.yaml", "04_service_definitions/production/ecn_release.yaml", "04_service_definitions/production/ecn_save.yaml", "04_service_definitions/production/ecn_search.yaml", "08_release_notes/RN-7.1 Ledgerline Release Notes.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | PRD-ECN-06 |
| Menu path | Production > Engineering change |
| Module | Production |
| Roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN |
| Primary services | ecn_save, ecn_get, ecn_search, ecn_approve, ecn_release |

Screen PRD-ECN-06 manages the initiation, technical sign-off, and release of engineering change notes across the Manchester works and Leeds unit [^r21]. Located under `Production > Engineering change`, it handles modifications to bills of materials and routing instructions [^r4][^r12][^r21]. Approving and releasing changes through this screen locks allocations against superseded parts, flags drawings on active assembly runs, and enforces revision rules on subsequent works orders [^r8][^r22].

| Field | Detail |
|---|---|
| Screen code | PRD-ECN-06 [^r4] |
| Screen title | Engineering Change Entry [^r12] |
| Menu path | Production > Engineering change [^r4][^r12] |
| Permitted roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN [^r12] |
| Backend services | [[services-prd-ecn\|ecn_save, ecn_get, ecn_search, ecn_approve, ecn_release]] [^r4][^r14] |

## Fields

PRD-ECN-06 presents header change data and technical authorization controls [^r1][^r2][^r5]:

* **ECN NO** (`ecn_no`): Change note reference identifier [^r5][^r12]. Leaving this field blank causes the system to allocate the number automatically upon saving [^r9].
* **ITEM CD** (`itm_cd`): Mandatory item code subject to the revision [^r5][^r6][^r12][^r19].
* **CHANGE TEXT** (`change`): Mandatory description detailing the engineering modification [^r1][^r5][^r6][^r12][^r19].
* **EFFECTIVE DT** (`eff_dt`): Mandatory effective cut-over date for the change [^r1][^r5][^r6][^r12][^r19].
* **STATUS** (`status`): Optional field updated across the lifecycle to indicate draft creation, technical approval, or full release [^r5][^r6][^r7][^r8][^r10].
* **REASON** (`reason`): Optional explanation justifying the change [^r5][^r6][^r12][^r19].
* **COMMENT** (`comment`): Optional notes, including approval feedback submitted during authorization [^r5][^r6][^r12][^r15].
* **Sign-off Indicators**: Displays completed markers for Quality and Purchasing that must show completed status before progression [^r2].
* **Documentation Reference & Attached File Flag**: For battery cell alterations, the reference field must contain the compliance report reference and the attached file flag must confirm the test report is in the technical archive [^r3].

## Keys and services

PRD-ECN-06 binds user keystrokes to five backend [[services-prd-ecn]] endpoints [^r4][^r13][^r14]:

* **Search (F2 / Enter)**: Calls `ecn_search` (POST `/ll72/svc/ecn_search`) to query change records using item code, change text, effective date, and status [^r13][^r20].
* **Get (F3)**: Calls `ecn_get` (POST `/ll72/svc/ecn_get`) requiring `ecn_no` to retrieve record details [^r13][^r16].
* **Save (F8)**: Calls `ecn_save` (POST `/ll72/svc/ecn_save`) submitting `itm_cd`, `change`, `eff_dt`, and optional `reason` to validate the entry, initialize status to draft, and return an allocated `ecn_no` [^r10][^r13][^r18][^r19].
* **Approve (F9)**: Calls `ecn_approve` (POST `/ll72/svc/ecn_approve`) using `ecn_no` and optional `comment` to validate security privileges and mark technical sign-off complete [^r7][^r13][^r15]. Approving triggers revision checks on active runs and displays revised flags beside drawing references [^r22].
* **Release (F9)**: Calls `ecn_release` (POST `/ll72/svc/ecn_release`) to update the status to fully released and apply revision rules to planning works orders [^r8][^r13][^r17]. Attempting release directly after draft creation triggers an error because approval is mandatory [^r11].

Posting obsolete components against an unrevised works order presents a blocking dialogue requiring supervisory sign-off, and only designated engineering leads can clear revision warning flags [^r23].

## Messages

The screen validates actions against the following message codes [^r13]:

* [[err-itm-0011|ERR-ITM-0011]]: Item not found or inactive [^r13].
* ERR-ECN-0105: Date in past [^r13]; also raised when clicking `ecn_release` directly from draft without intermediate approval [^r11].
* ERR-ECN-0001: Engineering change validation error [^r13].
* ERR-ECN-0007: Engineering change validation error [^r13].
* [[err-apr-0003|ERR-APR-0003]]: Self-approval not permitted [^r13].
* [[err-apr-0004|ERR-APR-0004]]: Approval validation failure [^r13].
* [[err-ecn-0220|ERR-ECN-0220]]: Open work orders on old revision [^r13].

## Versions and conflicts

* **ECN NO input requirement**: In system execution and workflow descriptions, `ECN NO` may be omitted when creating an ECN and is automatically allocated by `ecn_save` [^r9][^r10]. In screen reference specifications `MAN-PRD-72` and `MAN-SCR-72`, `ECN NO` (`ecn_no`) is tabulated alongside mandatory fields (`itm_cd`, `change`, `eff_dt`) rather than optional fields (`superseded` / `contradiction`) [^r6][^r9][^r12].

## See also

* [[sop-prd-002|SOP-PRD-002 Engineering Change (ECN)]]
* [[services-prd-ecn|PRD ecn services]]
* [[screen-prd-bom-02|PRD-BOM-02 Bill Of Materials]]
* [[screen-prd-rtg-03|PRD-RTG-03 Routing]]
* [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]
* [[errors-ecn|ERR-ECN Error Codes Reference]]

## References

[^r21]: 08_release_notes/RN-7.1 Ledgerline Release Notes.pdf, p. 3, Production: Engineering change notes (PRD-ECN-06)
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 29, §10. Engineering Change (PRD-ECN-06)
[^r12]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 22, PRD-ECN-06 ENGINEERING CHANGE ENTRY
[^r8]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 31, Step by step
[^r22]: 08_release_notes/RN-7.1 Ledgerline Release Notes.pdf, p. 3, Production: Engineering change notes (PRD-ECN-06)
[^r14]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 58, ecn_save ENGINEERING CHANGE SAVE
[^r1]: 02_procedures/SOP-PRD-002 Engineering Change v1.0.pdf, p. 3, §5. Procedure
[^r2]: 02_procedures/SOP-PRD-002 Engineering Change v1.0.pdf, p. 3, §5. Procedure: notes and common mistakes
[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 30, Screen layout
[^r9]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 32, Worked example
[^r6]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 29, §10. Engineering Change (PRD-ECN-06)
[^r19]: 04_service_definitions/production/ecn_save.yaml, request
[^r7]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 31, Step by step
[^r10]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 33, Worked example
[^r15]: 04_service_definitions/production/ecn_approve.yaml, screen
[^r3]: 02_procedures/SOP-PRD-002 Engineering Change v1.0.pdf, p. 3, §5. Procedure: notes and common mistakes
[^r13]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 22, PRD-ECN-06 ENGINEERING CHANGE ENTRY
[^r20]: 04_service_definitions/production/ecn_search.yaml, screen
[^r16]: 04_service_definitions/production/ecn_get.yaml, service: ecn_get
[^r18]: 04_service_definitions/production/ecn_save.yaml, whole file
[^r17]: 04_service_definitions/production/ecn_release.yaml, service: ecn_release
[^r11]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 32, Tips
[^r23]: 08_release_notes/RN-7.1 Ledgerline Release Notes.pdf, p. 3, Production: Engineering change notes (PRD-ECN-06)
