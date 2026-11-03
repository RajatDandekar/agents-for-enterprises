---
title: "PRD-WC-10 Work Centre"
type: "screen"
slug: "screen-prd-wc-10"
summary: "Ledgerline screen PRD-WC-10 maintains and queries work centre codes, descriptive names, and operating hours per day."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/wc_get.yaml", "04_service_definitions/production/wc_list.yaml", "04_service_definitions/production/wc_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | PRD-WC-10 |
| Screen title | Work Centre |
| Module | Production |
| Menu path | Production > Work centre |
| Authorized roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN |
| Read services | wc_get, wc_list |
| Write service | wc_save |
| Status | current |

Screen PRD-WC-10 (Work Centre) manages the definition, maintenance, and querying of production work centres in Ledgerline [^r1][^r8]. It is accessed via Menu Production > Work centre by roles PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, and SYS-ADMIN [^r6]. The screen enables users to view existing records or establish new work centres with operating capacity parameters using backend production services [^r2][^r4][^r8].

| Field | Value |
|---|---|
| Screen code | PRD-WC-10 |
| Name | Work Centre |
| Menu path | Production > Work centre |
| Permitted roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN |
| Services | [[services-prd-wc\|wc_get]], [[services-prd-wc\|wc_save]], [[services-prd-wc\|wc_list]] |

## Fields

PRD-WC-10 contains three data entry and inquiry fields [^r1][^r7]:

* **WC CD** (`wc_cd`): Mandatory work centre code identifier [^r1][^r7].
* **NAME** (`name`): Mandatory descriptive name for the work centre [^r1][^r7].
* **HRS/DAY** (`hrs_per_day`): Optional operating hours per working day [^r1][^r7].

When creating a new record, the user enters WC CD, NAME, and HRS/DAY before saving [^r4].

## Keys and services

Screen actions are executed via keyboard shortcuts and action pushbuttons backed by [[services-prd-wc|PRD wc services]] [^r2][^r13]:

* **WORK CENTRE GET** / **Get (F3)**: Executes service `wc_get` using `wc_cd` to retrieve specific work centre details [^r2][^r8][^r9][^r13].
* **WORK CENTRE SAVE** / **Save (F8)**: Executes service `wc_save` to create or update work centre codes, names, and daily working hours [^r2][^r4][^r8][^r12][^r13].
* **WORK CENTRE LIST** / **List**: Calls read service `wc_list` (endpoint `POST /ll72/svc/wc_list`) with an optional `wc_cd` filter to present an overview of existing work centres when the specific identifier is unknown [^r2][^r3][^r11][^r13].

## Messages

* [[err-wc-0001|ERR-WC-0001]]: Returned when a Work Centre is not found during a query via `wc_get`, or when a processing failure occurs during screen routines—most commonly during a save via `wc_save` due to blank mandatory fields, integrity violations, or duplicate records [^r5][^r10][^r13].

## See also

* [[services-prd-wc|PRD wc services]]
* [[err-wc-0001|ERR-WC-0001 Work Centre Processing Failure]]
* [[screen-prd-rtg-03|PRD-RTG-03 Routing]]
* [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 48, §15. Work Centre (PRD-WC-10)
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 61, wc_get WORK CENTRE GET
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 26, PRD-WC-10 WORK CENTRE
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 49, Screen layout and fields
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 50, Creating a new work centre
[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 26, PRD-WC-10 WORK CENTRE
[^r13]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 26, PRD-WC-10 WORK CENTRE
[^r9]: 04_service_definitions/production/wc_get.yaml, service: wc_get
[^r12]: 04_service_definitions/production/wc_save.yaml, screen
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 49, Retrieving an existing work centre record
[^r11]: 04_service_definitions/production/wc_list.yaml, screen
[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 50, Messages
[^r10]: 04_service_definitions/production/wc_get.yaml, errors
