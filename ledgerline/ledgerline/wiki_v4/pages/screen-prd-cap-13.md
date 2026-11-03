---
title: "PRD-CAP-13 Capacity"
type: "screen"
slug: "screen-prd-cap-13"
summary: "Ledgerline screen PRD-CAP-13 calculates and queries shift capacity baselines and gross operational work centre loads across production weeks."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/production/cap_load.yaml", "04_service_definitions/production/cap_query.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen | PRD-CAP-13 |
| Title | Capacity |
| Module | Production |
| Menu path | Production > Capacity |
| Authorized roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN |
| Read service | cap_query |
| Write service | cap_load |

Screen PRD-CAP-13 is Ledgerline's production capacity management interface accessed under Production > Capacity [^r1][^r4]. It provides planners and supervisors with tools to query baseline shift capacities and compile gross operational loading from scheduled works orders [^r2]. As of 26 October 2026, the screen is authorized for roles PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, and SYS-ADMIN [^r4].

| Attribute | Value |
|---|---|
| Screen Code | PRD-CAP-13 [^r1] |
| Screen Name | Capacity [^r1][^r4] |
| Menu Path | Production > Capacity [^r1][^r4] |
| Authorized Roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN [^r4] |
| Read Service | cap_query (`POST /ll72/svc/cap_query`) [^r7] |
| Write Service | cap_load [^r6] |

## Fields

PRD-CAP-13 features three string fields, all of which are optional [^r1][^r4]:

* **WORK CENTRE** (`wc_cd`): Optional string field designating the specific work centre code to filter or load [^r1][^r4][^r8].
* **WEEK** (`week`): Optional string parameter designating the production week [^r1][^r4][^r8].
* **COMMENT** (`comment`): Optional string field for entering remarks or operational capacity notes [^r1][^r4].

## Keys and services

PRD-CAP-13 provides two primary action buttons that invoke underlying [[services-prd-cap|production capacity services]] [^r2][^r5]:

* **Query** (`cap_query`): Executes the read service `cap_query` at endpoint `POST /ll72/svc/cap_query` using optional parameters `wc_cd` and `week` to retrieve baseline shift capacity from the factory calendar and production database [^r2][^r5][^r7][^r8].
* **Load** (`cap_load`): Triggers write service `cap_load` (CAPACITY LOAD) to calculate and compile the gross operational load for a work centre based on live and scheduled works orders [^r2][^r5][^r6].

## Messages

The screen can raise the following system error [^r3][^r5]:

* **ERR-CAP-0001** (*Capacity Not Found*): Displayed when the entered WORK CENTRE (`wc_cd`) or WEEK (`week`) cannot be resolved against the production database or the factory calendar [^r3][^r5].

## See also

* [[services-prd-cap|PRD cap services]]
* [[screen-prd-wc-10|PRD-WC-10 Work Centre]]
* [[screen-prd-shf-11|PRD-SHF-11 Shift]]
* [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]
* [[screen-prd-mps-05|PRD-MPS-05 Master Schedule Entry]]
* [[screen-prd-mrp-09|PRD-MRP-09 Mrp Run]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 58, §18. Capacity (PRD-CAP-13)
[^r4]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 22, PRD-CAP-13 CAPACITY
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 59, Screen layout
[^r7]: 04_service_definitions/production/cap_query.yaml, whole file
[^r6]: 04_service_definitions/production/cap_load.yaml, service: cap_load
[^r8]: 04_service_definitions/production/cap_query.yaml, request.fields
[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 22, PRD-CAP-13 CAPACITY
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 60, Messages
