---
title: "INV-CCP-14 Cycle Count Plan Entry"
type: "screen"
slug: "screen-inv-ccp-14"
summary: "Ledgerline screen for configuring warehouse cycle count plans by ABC classification, generating count sheets, and managing count frequency."
audience: "staff"
status: "mixed"
sources: ["02_procedures/SOP-INV-003 Stock Count v1.2.pdf", "03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/ccp_generate.yaml", "04_service_definitions/inventory/ccp_get.yaml", "04_service_definitions/inventory/ccp_save.yaml", "04_service_definitions/inventory/ccp_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | INV-CCP-14 |
| Title | Cycle Count Plan Entry |
| Menu | Inventory > Cycle count |
| Roles | STORES, STORES-MGR, PUR-EXEC, SYS-ADMIN |
| Read services | ccp_get, ccp_search |
| Write services | ccp_save, ccp_generate |
| Status | current |

Screen INV-CCP-14 (Cycle Count Plan Entry) configures inventory cycle counting schedules based on warehouse code and ABC classification [^r1][^r2]. Under current operating procedure, it schedules category A items monthly, category B items quarterly, and category C items twice yearly [^r1]. Saving a new plan automatically assigns a sequential plan reference number and marks it active, after which count sheets can be generated for stores personnel [^r3][^r5][^r6]. The screen is located under menu Inventory > Cycle count and is accessible to roles STORES, STORES-MGR, PUR-EXEC, and SYS-ADMIN [^r9].

| Field | Description | Mandatory / Optional |
|---|---|---|
| Screen code | INV-CCP-14 | — |
| Title | Cycle Count Plan Entry | — |
| Menu path | Inventory > Cycle count | — |
| Allowed roles | STORES, STORES-MGR, PUR-EXEC, SYS-ADMIN | — |
| Write services | ccp_save, ccp_generate | — |
| Read services | ccp_get, ccp_search | — |

## Fields

* **Warehouse Code (`whs_cd`)**: Mandatory warehouse location code for the cycle count plan [^r2][^r15].
* **ABC Classification (`abc`)**: Optional ABC inventory classification code used to filter items [^r2][^r15].
* **Frequency in Days (`freq_days`)**: Mandatory count recurrence interval in days [^r15]. This field is locked against modification once count sheets have been generated via `ccp_generate` [^r8].
* **Plan Number (`ccp_no`)**: Cycle count plan reference identifier [^r3][^r14]. When creating a new plan, this field must be left blank so Ledgerline can assign it automatically on save [^r3][^r5]. It is mandatory when retrieving an existing plan via `ccp_get` [^r14].
* **Status (`status`)**: System status of the plan, set to active upon successful save [^r3][^r5].

## Keys and services

Screen INV-CCP-14 interacts with the [[services-inv-ccp|INV ccp services]] group through the following endpoints:

* **`ccp_save`**: Write service executed at `POST /ll72/svc/ccp_save` via stored procedure `sp_ccp_save` (available since Ledgerline 7.0) [^r11][^r15]. It validates entered parameters, automatically populates `ccp_no` with a sequential plan reference, sets `status` to active, and persists mandatory `whs_cd`, mandatory `freq_days`, and optional `abc` [^r3][^r5][^r11][^r15].
* **`ccp_generate`**: Write service executed at `POST /ll72/svc/ccp_generate` calling CYCLE COUNT PLAN GENERATE [^r6][^r12][^r13]. It evaluates inventory matching `whs_cd` and `abc` to generate cycle count sheets for stores staff [^r6].
* **`ccp_get`**: Read service executed at `POST /ll72/svc/ccp_get` that retrieves an existing plan using mandatory field `ccp_no` [^r4][^r12][^r14].
* **`ccp_search`**: Read service that queries and lists cycle count plans by warehouse or ABC classification filters [^r4][^r12][^r16].

## Messages

* **[[err-ccp-0001|ERR-CCP-0001]]** (Cycle Count Plan Not Found / Parameter Error): Raised if required parameters are missing, if the specified warehouse code is invalid or locked, if an active plan already exists for the selected warehouse and ABC classification combination, or when a specified plan cannot be found [^r7][^r10].

## Versions and conflicts

* **Plan numbering and status lifecycle** (`superseded`): Under current Ledgerline 7.2.3 behaviour, saving via `ccp_save` validates parameters, assigns the sequential plan number to `ccp_no`, and sets `status` directly to active, after which `ccp_generate` generates count sheets [^r3][^r5][^r6]. Under superseded manual MAN-INV-72 v7.2.2 (dated 2024-06-10), pressing `ccp_generate` populated `ccp_no` and set status to draft, while `ccp_save` committed the record and set status to confirmed [^r18].

## See also

* [[err-ccp-0001|ERR-CCP-0001 Cycle count plan parameter error]]
* [[services-inv-ccp|INV ccp services]]
* [[screen-inv-cnt-06|INV-CNT-06 Stock Count Entry]]
* [[screen-inv-whs-01|INV-WHS-01 Warehouse Master]]

## References

[^r1]: 02_procedures/SOP-INV-003 Stock Count v1.2.pdf, p. 3, §5. Procedure
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 54, Creating a new cycle count plan
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 54, Creating a new cycle count plan
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 56, Worked example
[^r6]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 56, Worked example
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 12, INV-CCP-14 CYCLE COUNT PLAN ENTRY
[^r15]: 04_service_definitions/inventory/ccp_save.yaml, service: ccp_save
[^r8]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 56, Questions users ask
[^r14]: 04_service_definitions/inventory/ccp_get.yaml, service: ccp_get
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 21, ccp_save CYCLE COUNT PLAN SAVE
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 22, ccp_generate CYCLE COUNT PLAN GENERATE
[^r13]: 04_service_definitions/inventory/ccp_generate.yaml, screen
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 54, Retrieving an existing cycle count plan
[^r16]: 04_service_definitions/inventory/ccp_search.yaml, service: ccp_search
[^r7]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 56, Questions users ask
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 13, INV-CCP-14 CYCLE COUNT PLAN ENTRY
[^r18]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 23, Step by step
