---
title: "PRD-MRP-09 Mrp Run"
type: "screen"
slug: "screen-prd-mrp-09"
summary: "Production screen used to execute MRP batch calculations, view exceptions, and firm planned orders into purchase orders and works orders."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/mrp_exceptions.yaml", "04_service_definitions/production/mrp_firm.yaml", "04_service_definitions/production/mrp_get.yaml", "04_service_definitions/production/mrp_run.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | PRD-MRP-09 |
| Menu path | Production > Mrp run |
| Access roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN |
| Primary service | mrp_run |
| Supported services | mrp_run, mrp_get, mrp_exceptions, mrp_firm |

Screen PRD-MRP-09 executes material requirements planning (MRP) batch calculations and handles generated planned orders in Ledgerline [^r1][^r8]. It allows authorised users to trigger batch runs, inspect planning exceptions, and firm planned records into provisional works orders and unapproved purchase records [^r2][^r4][^r6]. Before executing a run on this screen, inventory movements across Manchester and Leeds, purchase orders, sales orders, and active structures must be posted and confirmed [^r3].

## Fields

The screen contains three primary parameter fields [^r1][^r6]:

| Field | Parameter | Type | Required | Notes |
|---|---|---|---|---|
| RUN ID | `run_id` | String | Yes | MRP run identifier [^r1][^r6][^r11]. |
| COMMENT | `comment` | String | No | Optional narrative comment for the run [^r1][^r6][^r11]. |
| HORIZON | `horizon_days` | Integer | No | Optional planning horizon evaluated in days [^r1][^r6][^r10]. |

Before launching the calculation via PRD-MRP-09, users must post all daily inventory movements across both the Manchester and Leeds sites, confirm active bill of materials (BOM) and routing structures, update purchase orders, finalise sales orders, and confirm that no concurrent batch or valuation updates are in progress [^r3].

## Keys and services

PRD-MRP-09 is accessible to roles PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, and SYS-ADMIN [^r6]. The screen exposes four action buttons linked to underlying [[services-prd-mrp|PRD mrp services]] [^r2][^r6][^r7][^r9]:

* **Run (`mrp_run`)**: Invokes write service `mrp_run` to execute batch processing for the run [^r2][^r6][^r7][^r8][^r13].
* **Get (`mrp_get`)**: Assigned to function key `F3`, invoking read service `mrp_get` to retrieve existing MRP run records [^r2][^r6][^r7][^r9][^r12].
* **Exceptions (`mrp_exceptions`)**: Invokes read service `mrp_exceptions` to inspect run exceptions across an optional `horizon_days` parameter [^r2][^r6][^r7][^r9][r10].
* **Firm (`mrp_firm`)**: Invokes write service `mrp_firm` with `run_id` and optional `comment` to convert system-suggested purchase orders into unapproved purchase records and provisional production batches into allocated works orders [^r2][^r4][^r6][^r7][^r9][^r11].

Users should never proceed directly from running an MRP batch to executing `mrp_firm` without first reviewing exception notices via `mrp_exceptions` to prevent duplicate purchasing [^r5].

## Messages

The screen raises the following error during run retrieval and maintenance [^r7]:

* [[err-mrp-0001|ERR-MRP-0001]]: Raised if the specified MRP run is not found [^r7].

## See also

* [[services-prd-mrp|PRD mrp services]]
* [[err-mrp-0001|ERR-MRP-0001]]
* [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]
* [[screen-prd-mps-05|PRD-MPS-05 Master Schedule Entry]]
* [[screen-prd-bom-02|PRD-BOM-02 Bill Of Materials]]
* [[screen-prd-rtg-03|PRD-RTG-03 Routing]]
* [[services-pur-po|PUR po services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 22, §8. Mrp Run (PRD-MRP-09)
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 56, §6. Production services
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 23, Screen layout and fields
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 24, Step by step
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 23, PRD-MRP-09 MRP RUN
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 22, Before you start
[^r11]: 04_service_definitions/production/mrp_firm.yaml, whole file
[^r10]: 04_service_definitions/production/mrp_exceptions.yaml, service
[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 23, PRD-MRP-09 MRP RUN
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 57, mrp_get MRP RUN GET
[^r13]: 04_service_definitions/production/mrp_run.yaml, whole file
[^r12]: 04_service_definitions/production/mrp_get.yaml, service: mrp_get
[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 24, Tips
