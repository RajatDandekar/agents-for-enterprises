---
title: "PRD-SCP-12 Production Scrap Entry"
type: "screen"
slug: "screen-prd-scp-12"
summary: "Production Scrap Entry screen for capturing and posting works order scrap transactions against inventory balances."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/production/scp_get.yaml", "04_service_definitions/production/scp_post.yaml", "04_service_definitions/production/scp_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | PRD-SCP-12 |
| Title | Production Scrap Entry |
| Module | Production |
| Menu path | Production > Production scrap |
| Roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN |
| Read service | scp_get |
| Write services | scp_save, scp_post |

Screen PRD-SCP-12 is the Ledgerline interface used to record, validate, and post scrap generated during works order operations [^r1]. It operates from the menu path Production > Production scrap and is accessible to users with roles PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, and SYS-ADMIN [^r1][^r9]. Once posted via the screen, scrap transactions directly decrement component balances and update inventory records, after which they cannot be amended or reversed from the screen [^r5][^r8].

| Field | Value |
|---|---|
| Screen code | PRD-SCP-12 |
| Title | Production Scrap Entry |
| Module | Production |
| Menu path | Production > Production scrap |
| Roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN |
| Read service | scp_get |
| Write services | scp_save, scp_post |

## Fields

Screen PRD-SCP-12 contains five mandatory fields and one optional field [^r2][^r10]:

* **WO NO** (`wo_no`): Works order identifier; mandatory [^r2][^r10]. Entered to fetch works order header details using `scp_get` and required when saving via `scp_save` [^r3][^r16].
* **ITEM CD** (`itm_cd`): Item code of the scrapped component; mandatory [^r2][^r10]. Must exist on the active works order bill of materials [^r6][^r16].
* **QTY** (`qty`): Quantity of material scrapped; mandatory [^r2][^r10][^r16].
* **REASON CD** (`reason_cd`): Scrap reason code; mandatory [^r2][^r10][^r16].
* **SCP NO** (`scp_no`): Production scrap document number; mandatory [^r2][^r10]. Automatically generated and populated when draft records are saved using `scp_save`, and required as a parameter to query existing scrap records with `scp_get` [^r4][^r13].
* **COMMENT** (`comment`): Free-text remark regarding the scrap instance; optional [^r2][^r10].

## Keys and services

PRD-SCP-12 interacts with three backend services under [[services-prd-scp]] [^r1]:

* **Get (F3)** invokes `scp_get` (`POST /ll72/svc/scp_get`): A read service requiring parameter `scp_no` to retrieve existing production scrap records, or used with `wo_no` to populate works order header details [^r3][^r11][^r13].
* **Save (F8)** invokes `scp_save`: A write service requiring `wo_no`, `itm_cd`, `qty`, and `reason_cd` that runs field validation, persists the record, generates the document identifier, and populates `scp_no` in an unposted draft state [^r4][^r11][^r15][^r16].
* **Post (F9)** invokes `scp_post` (`POST /ll72/svc/scp_post`): A write service executing stored procedure `sp_scp_post` to post the scrap transaction [^r11][^r14]. Posting reduces the works order component balance, issues the scrap entry to the works order ledger, updates stock records, and finalises the transaction [^r5]. Transactions posted by `scp_post` cannot be reversed or edited on the screen and require manual inventory adjustment journals for correction [^r8].

## Messages

The screen surfaces several error codes during validation and processing:

* [[err-itm-0011]]: Item Not Found Or Inactive; raised when the entered `itm_cd` does not exist, is inactive, or is not part of the active works order bill of materials [^r6][^r12].
* [[err-scp-0001]]: Production Scrap Not Found [^r12].
* `ERR-SCP-0007`: Production Scrap Not In Draft [^r12].
* `ERR-SCP-0201`: Raised when the entered scrap quantity exceeds remaining unposted quantities or issue limits on the works order, or when `qty` is not greater than zero [^r7][^r12].

## Versions and conflicts

* **ERR-SCP-0201 definition**: Under MAN-PRD-72, `ERR-SCP-0201` is triggered when scrap volume exceeds remaining unposted quantities or issue limits on the works order [^r7]. Under MAN-SCR-72, the message text is defined as "Qty Must Be > 0" [^r12]. Both sources are dated 2025-01-15 (contradiction).

## See also

* [[services-prd-scp|PRD scp services]]
* [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]
* [[screen-prd-bom-02|PRD-BOM-02 Bill Of Materials]]
* [[screen-qa-ncr-02|QA-NCR-02 Non-Conformance Report Entry]]
* [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[err-scp-0001|ERR-SCP-0001 Mandatory scrap header or line details missing]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 55, §17. Production Scrap (PRD-SCP-12)
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 25, PRD-SCP-12 PRODUCTION SCRAP ENTRY
[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 56, Step by step
[^r8]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 58, Questions users ask
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 55, §17. Production Scrap (PRD-SCP-12)
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 25, PRD-SCP-12 PRODUCTION SCRAP ENTRY
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 56, Step by step
[^r16]: 04_service_definitions/production/scp_save.yaml, request
[^r6]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 57, Worked example: Production Scrap
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 56, Step by step
[^r13]: 04_service_definitions/production/scp_get.yaml, screen
[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 25, PRD-SCP-12 PRODUCTION SCRAP ENTRY
[^r15]: 04_service_definitions/production/scp_save.yaml, whole file
[^r14]: 04_service_definitions/production/scp_post.yaml, service: scp_post
[^r12]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 25, PRD-SCP-12 PRODUCTION SCRAP ENTRY
[^r7]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 58, Worked example: Production Scrap
