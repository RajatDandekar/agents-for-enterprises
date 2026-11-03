---
title: "PRD-SHF-11 Shift"
type: "screen"
slug: "screen-prd-shf-11"
summary: "Production shift definition screen used to maintain shift start and end times via services shf_get and shf_save."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/production/shf_get.yaml", "04_service_definitions/production/shf_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | PRD-SHF-11 |
| Name | Shift |
| Menu path | Production > Shift |
| Allowed roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN |
| Services | shf_get, shf_save |
| Status | Current |

Screen PRD-SHF-11 (Shift) maintains shift definition records in Ledgerline [^r1][^r6]. Accessed through menu path Production > Shift, the screen is available to roles PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, and SYS-ADMIN [^r1][^r6]. It allows operators to retrieve and update shift timing records using underlying services [[services-prd-shf|shf_get]] and [[services-prd-shf|shf_save]] [^r1][^r8][^r9].

| Attribute | Value |
|---|---|
| Screen Code | PRD-SHF-11 [^r1][^r6] |
| Screen Name | Shift [^r1][^r6] |
| Menu Path | Production > Shift [^r1][^r6] |
| Roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN [^r6] |
| Read Service | shf_get [^r1][^r8] |
| Write Service | shf_save [^r1][^r9] |

## Fields

PRD-SHF-11 contains three mandatory fields [^r2][^r7]:

* **SHF CD** (`shf_cd`): Mandatory shift code identifier [^r2][^r7]. It serves as the primary database key; once saved, a shift code cannot be edited directly, and any corrections require clearing the screen and re-entering under the correct reference [^r5].
* **START** (`start`): Mandatory shift start time [^r2][^r7][^r9].
* **END** (`end`): Mandatory shift end time [^r2][^r7][^r9].

## Keys and services

The screen interacts with the production database through two standard functional keys and services [^r1][^r10]:

* **Get (F3)**: Executes the SHIFT GET action via read service `shf_get` using field `shf_cd` to retrieve production records and populate the `START` and `END` fields [^r3][^r8][^r10].
* **Save (F8)**: Executes the SHIFT SAVE action via write service `shf_save` at endpoint `POST /ll72/svc/shf_save` using mandatory parameters `shf_cd`, `start`, and `end` [^r4][^r9][^r10]. The service validates entries and commits additions or revisions to the core tables and audit trail [^r4].

## Messages

* `ERR-SHF-0001`: Shift Not Found; raised during get operations if the specified shift code does not exist in the database [^r10]. See [[err-shf-0001|ERR-SHF-0001 Invalid period definition / shift parameters]] [^r10].

## See also

* [[err-shf-0001|ERR-SHF-0001 Invalid period definition / shift parameters]]
* [[services-prd-shf|PRD shf services]]
* [[screen-prd-wc-10|PRD-WC-10 Work Centre]]
* [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 52, §16. Shift (PRD-SHF-11)
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 25, PRD-SHF-11 SHIFT
[^r8]: 04_service_definitions/production/shf_get.yaml, screen
[^r9]: 04_service_definitions/production/shf_save.yaml, whole file
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 52, §16. Shift (PRD-SHF-11)
[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 25, PRD-SHF-11 SHIFT
[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 55, Questions users ask
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 25, PRD-SHF-11 SHIFT
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 53, Screen layout and fields
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 53, Screen layout and fields
