---
title: "PRD-BOM-02 Bill Of Materials"
type: "screen"
slug: "screen-prd-bom-02"
summary: "Ledgerline screen for creating, copying, exploding, and searching bills of materials across production assemblies."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/bom_copy.yaml", "04_service_definitions/production/bom_explode.yaml", "04_service_definitions/production/bom_get.yaml", "04_service_definitions/production/bom_save.yaml", "04_service_definitions/production/bom_search.yaml", "04_service_definitions/production/bom_where_used.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | PRD-BOM-02 |
| Screen name | Bill Of Materials |
| Menu path | Production > Bill of |
| Roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN |
| Read services | bom_get, bom_search, bom_explode, bom_where_used |
| Write services | bom_save, bom_copy |
| Status | Current |

Screen PRD-BOM-02 is the Ledgerline bill of materials maintenance and inquiry screen accessed under Production > Bill of [^r2][^r7]. It allows planners, supervisors, inspectors, and administrators to define component structures, copy assemblies, calculate multilevel explosions, and run where-used analyses [^r2][^r4][^r5][^r7]. Parent items and all component items must exist with an active status in the item master before a bill of materials record can be created or modified on this screen [^r3].

| Attribute | Value |
|---|---|
| Screen code | PRD-BOM-02 [^r1] |
| Screen name | Bill Of Materials [^r1][^r7] |
| Menu path | Production > Bill of [^r2][^r7] |
| Authorized roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN [^r7] |

## Fields

Screen PRD-BOM-02 captures the following fields [^r1][^r7]:

* **PARENT** (`parent`): Mandatory parent item code [^r1][^r7].
* **COMPONENT** (`component`): Mandatory component item code [^r1][^r7].
* **QTY PER** (`qty`): Mandatory component quantity per parent assembly, stored as a float [^r1][^r7].
* **SCRAP %** (`scrap_pct`): Optional scrap allowance percentage, stored as a float [^r1][^r7].
* **STATUS** (`status`): Optional status field [^r1][^r7].

Parent and component codes entered into these fields must be active records in the item master prior to submission [^r3].

## Keys and services

The screen interacts with six production services mapped to keyboard shortcuts and interface actions [^r2][^r8][^r9]:

* **Get (F3)**: Executes the read service `bom_get` via endpoint `POST /ll72/svc/bom_get` to retrieve existing bill of materials records [^r2][^r8][^r9][^r12].
* **Save (F8)**: Executes the backend write service `bom_save` to commit parent, component, quantity, and scrap percentage data [^r2][^r8][^r9][^r13].
* **Search (F2 / Enter)**: Executes the read service `bom_search` to query bill of materials listings [^r2][^r8][^r9][^r14].
* **Copy**: Executes the write service `bom_copy` via endpoint `POST /ll72/svc/bom_copy`, prompting for a source parent item and duplicating its entire component hierarchy into the active working area [^r2][^r4][^r8][^r9][^r10].
* **Explode**: Executes the read service `bom_explode` to explode component structures for a designated parent item [^r2][^r8][^r9][^r11].
* **Where Used**: Executes the read service `bom_where_used`, which is initiated by populating the `COMPONENT` field while leaving `PARENT` blank to list all parent assemblies containing the specified part [^r2][^r5][^r8][^r9][^r15].

## Messages

Transactions processed on screen PRD-BOM-02 can return the following error messages [^r6][^r8]:

* [[err-bom-0001]]: Parent assembly not found on bill of materials master [^r6][^r8].
* [[err-bom-0120]]: Circular or recursive bill of materials structure detected [^r6][^r8].
* [[err-bom-0201]]: Component line missing or invalid data [^r6][^r8].
* [[err-itm-0011]]: Item not found or inactive [^r6][^r8].

## See also

* [[services-prd-bom|PRD bom services]]
* [[errors-bom|ERR-BOM Error Code Reference]]
* [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]]
* [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]
* [[screen-prd-rtg-03|PRD-RTG-03 Routing]]
* [[screen-prd-ecn-06|PRD-ECN-06 Engineering Change Entry]]

## References

[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 7, §4. Bill Of Materials (PRD-BOM-02)
[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 21, PRD-BOM-02 BILL OF MATERIALS
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 9, Step by step
[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 9, Step by step
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 8, Before you start
[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 7, §4. Bill Of Materials (PRD-BOM-02)
[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 21, PRD-BOM-02 BILL OF MATERIALS
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 54, §6. Production services
[^r12]: 04_service_definitions/production/bom_get.yaml, service: bom_get
[^r13]: 04_service_definitions/production/bom_save.yaml, bom_save
[^r14]: 04_service_definitions/production/bom_search.yaml, screen
[^r10]: 04_service_definitions/production/bom_copy.yaml, service: bom_copy
[^r11]: 04_service_definitions/production/bom_explode.yaml, service: bom_explode
[^r15]: 04_service_definitions/production/bom_where_used.yaml, header
[^r6]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 9, Messages
