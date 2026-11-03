---
title: "PRD-MPS-05 Master Schedule Entry"
type: "screen"
slug: "screen-prd-mps-05"
summary: "Ledgerline screen PRD-MPS-05 provides entry, retrieval, and maintenance of weekly master schedule production build plans for finished goods and assemblies."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/mps_get.yaml", "04_service_definitions/production/mps_save.yaml", "04_service_definitions/production/mps_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | PRD-MPS-05 |
| Screen name | Master Schedule Entry |
| Menu path | Production > Master schedule |
| Module | Production (PRD) |
| Roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN |
| Status | Current |

PRD-MPS-05 (Master Schedule Entry) provides the central Ledgerline mechanism for entering, reviewing, and maintaining the weekly build plan translating commercial forecasts and retailer orders into time-phased production statements [^r2]. Accessed via Production > Master schedule, the screen allows production planners and authorised roles to establish planned build volumes for finished goods and intermediate assemblies across aligned factory calendars in Manchester and Leeds [^r1][^r2][^r3][^r8]. Schedule lines remain uncommitted until saved and released, and lines locked by active shop floor routings cannot have their quantity or status modified [^r5][^r6].

| Property | Value |
|---|---|
| Screen Code | PRD-MPS-05 |
| Title | Master Schedule Entry |
| Menu Path | Production > Master schedule |
| Access Roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN |
| Handled Services | `mps_save`, `mps_get`, `mps_search` |

Before creating or altering records on PRD-MPS-05, target items must be active configured finished goods or intermediate assemblies, factory calendars must be aligned for Manchester and Leeds, and the operator must possess write/update group permissions [^r3].

## Fields

PRD-MPS-05 contains the following input and display fields [^r1][^r8][^r12]:

* **ITEM CD (`itm_cd`)**: Mandatory. Master identifier of the active finished good or intermediate assembly [^r1][^r8][^r12].
* **WEEK (`week`)**: Mandatory. Production schedule planning week identifier [^r1][^r8][^r12].
* **QTY (`qty`)**: Mandatory integer. Scheduled build volume for the specified item and week [^r1][^r4][^r8][^r12].
* **STATUS (`status`)**: Optional. Administrative state of the schedule line, which defaults to an uncommitted state on new records [^r1][^r4][^r5][^r8].

## Keys and services

PRD-MPS-05 interacts with the database through dedicated [[services-prd-mps|PRD mps services]] invoked by interface buttons and shortcut keys [^r9][^r10]:

* **Get (F3)**: Invokes read service `mps_get` to retrieve stored master schedule plan data based on `itm_cd` and `week`, populating scheduled build volume `qty` and administrative `status` [^r4][^r9][^r10][^r11].
* **Search (F2 / Enter)**: Invokes read service `mps_search` (endpoint `POST /ll72/svc/mps_search`) to query and retrieve master schedule lists [^r9][^r10][^r13].
* **Save (F8)**: Invokes write service `mps_save` (endpoint `POST /ll72/svc/mps_save`) to write schedule changes to the database and update production horizon flags [^r7][^r9][^r10][^r12].

Retrieved lines can have their `qty` or `status` amended unless locked by an active shop floor routing [^r6].

## Messages

The screen raises the following system error messages during data validation and service execution [^r9]:

* [[err-mps-0001|ERR-MPS-0001]]: Missing Mandatory Field or Invalid Format in MPS [^r9].
* [[err-itm-0011|ERR-ITM-0011]]: Item Not Found or Inactive [^r9].
* [[err-mps-0201|ERR-MPS-0201]]: Master Schedule Line Locked Against Modification [^r9].

## See also

* [[services-prd-mps|PRD mps services]]
* [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]
* [[screen-prd-mrp-09|PRD-MRP-09 Mrp Run]]
* [[screen-prd-bom-02|PRD-BOM-02 Bill Of Materials]]
* [[screen-prd-rtg-03|PRD-RTG-03 Routing]]
* [[err-mps-0001|ERR-MPS-0001 Missing Mandatory Field or Invalid Format in MPS]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[err-mps-0201|ERR-MPS-0201 Master Schedule Line Locked Against Modification]]

## References

[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 26, Purpose
[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 26, §9. Master Schedule (PRD-MPS-05)
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 26, Before you start
[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 23, PRD-MPS-05 MASTER SCHEDULE ENTRY
[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 27, Creating or amending schedule lines
[^r6]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 27, Creating or amending schedule lines
[^r12]: 04_service_definitions/production/mps_save.yaml, service: mps_save
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 27, Creating or amending schedule lines
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 23, PRD-MPS-05 MASTER SCHEDULE ENTRY
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 57, mps_save MASTER SCHEDULE SAVE
[^r11]: 04_service_definitions/production/mps_get.yaml, service: mps_get
[^r13]: 04_service_definitions/production/mps_search.yaml, screen
[^r7]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 27, Creating or amending schedule lines
