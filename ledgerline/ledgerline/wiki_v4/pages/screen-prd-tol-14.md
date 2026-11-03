---
title: "PRD-TOL-14 Tool Master"
type: "screen"
slug: "screen-prd-tol-14"
summary: "Ledgerline Tool Master screen PRD-TOL-14 for maintaining tooling records, station allocations, and allowable operational life cycles."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/production/tool_get.yaml", "04_service_definitions/production/tool_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | PRD-TOL-14 |
| name | Tool Master |
| menu | Production > Tool master |
| roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN |
| services | tool_get, tool_save |
| status | current |

Screen PRD-TOL-14 provides master record maintenance for production tooling in Ledgerline, accessible under Menu Production > Tool master [^r7]. It is authorized for roles PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, and SYS-ADMIN [^r7]. The screen records tool identifiers, descriptions with station allocations, and rated operational life cycles [^r1][^r3]. If a tool is decommissioned after historical production lots exist, its record must be retained rather than deleted, and its description updated with an out-of-service note [^r5].

## Fields

* **TOOL CD** (`tool_cd`): Mandatory tool identifier acting as the primary record key in the underlying database table [^r1][^r3][^r8][^r11][^r12].
* **DESCR** (`descr`): Mandatory physical description and functional title specifying station allocation [^r1][^r3][^r8][^r11][^r12].
* **LIFE** (`life_cycles`): Optional integer field designating operational life rating in allowable cycles, operations, or working duration [^r1][^r3][^r8][^r11][^r12].

## Keys and services

PRD-TOL-14 interacts with the backend tool services [[services-prd-tool|PRD tool services]] [^r2][^r4]:

* **Get (F3)**: Executes command button `tool_get` calling service `TOOL MASTER GET` to retrieve existing tooling records [^r2][^r4][^r9][^r13].
* **Save (F8)**: Executes command button `tool_save` calling service `TOOL MASTER SAVE` at endpoint `POST /ll72/svc/tool_save` to commit new or amended tooling data [^r2][^r4][^r10][^r13].

## Messages

* `ERR-TOL-0001`: Displayed on the lower message line during get or save processing failures, such as Tool Master Not Found [^r6][^r13]. See [[err-tol-0001|ERR-TOL-0001 Tool Master Validation Failure]].

## See also

* [[err-tol-0001|ERR-TOL-0001 Tool Master Validation Failure]]
* [[services-prd-tool|PRD tool services]]
* [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]
* [[screen-prd-wc-10|PRD-WC-10 Work Centre]]
* [[screen-prd-mnt-07|PRD-MNT-07 Maintenance Order Entry]]

## References

[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 25, PRD-TOL-14 TOOL MASTER
[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 66, Screen layout
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 67, PART 14 of 15 (pp. 67-71)
[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 68, Tips
[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 25, PRD-TOL-14 TOOL MASTER
[^r11]: 04_service_definitions/production/tool_save.yaml, request.fields
[^r12]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 65, §20. Tool Master (PRD-TOL-14)
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 66, Screen layout
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 67, PART 14 of 15 (pp. 67-71)
[^r9]: 04_service_definitions/production/tool_get.yaml, whole file
[^r13]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 26, PRD-TOL-14 TOOL MASTER
[^r10]: 04_service_definitions/production/tool_save.yaml, service: tool_save
[^r6]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 68, Messages
