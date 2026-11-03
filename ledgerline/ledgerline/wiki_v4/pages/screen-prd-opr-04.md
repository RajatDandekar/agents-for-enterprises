---
title: "PRD-OPR-04 Operation Confirmation Entry"
type: "screen"
slug: "screen-prd-opr-04"
summary: "Screen PRD-OPR-04 records production operation confirmations, updates routing progress, triggers backflushing, and links to opr_save, opr_get, and opr_search services."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/opr_get.yaml", "04_service_definitions/production/opr_save.yaml", "04_service_definitions/production/opr_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | PRD-OPR-04 |
| Title | Operation Confirmation Entry |
| Module | Production |
| Menu path | Production > Operation confirmation |
| Authorized roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN |
| Read services | opr_get, opr_search |
| Write service | opr_save |
| Status | Current |

Screen PRD-OPR-04 (Operation Confirmation Entry) is the Ledgerline interface used to confirm completion and report quantities against work order operations [^r1][^r8]. It is accessed via the menu path Production > Operation confirmation by authorised production, quality, and system administration roles [^r1][^r8]. The screen operates identically across both the Manchester and Leeds sites, handling sub-assemblies built in Leeds for Manchester final assembly as well as main line runs [^r7]. Saving an entry commits operation progress, deducts backflushed inventory, and prevents direct in-screen overwriting of confirmed quantities [^r5][^r6].

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `wo_no` | String | Mandatory | Work order number against which the operation is recorded [^r2][^r8][^r11]. |
| `op_no` | Integer | Mandatory | Operation number within the work order routing [^r2][^r8][^r12]. |
| `qty_ok` | Integer | Mandatory | Quantity of acceptable units completed at the operation [^r2][^r8][^r12]. |
| `qty_rej` | Integer | Optional | Quantity of rejected units identified during the operation [^r2][^r8][^r12]. |
| `status` | String | Optional | Status code assigned to the operation confirmation [^r2][^r8]. |

Users should always retrieve the operation record before populating the `qty_ok` or `qty_rej` fields [^r4]. Once posted, confirmed quantities cannot be modified directly on screen PRD-OPR-04; any subsequent adjustment requires contacting the production control office in Manchester or the unit supervisor in Leeds to initiate a reversal confirmation or an adjusting movement [^r6].

## Keys and services

Screen PRD-OPR-04 executes transaction logic via the [[services-prd-opr|PRD opr services]] group [^r1][^r10]:

* **Search (`opr_search`)**: Triggered by pressing `F2` or `Enter`, invoking `POST /ll72/svc/opr_search` to open the operation confirmation list and retrieve open operations queued at a specific line or work centre [^r3][^r9][^r13].
* **Get (`opr_get`)**: Triggered by pressing `F3`, calling `POST /ll72/svc/opr_get` using `wo_no` to retrieve existing operation confirmation details from the database [^r4][^r9][^r11].
* **Save (`opr_save`)**: Triggered by pressing `F8`, posting the confirmation dataset (`wo_no`, `op_no`, `qty_ok`, and optional `qty_rej`) to update order routing progress and trigger backflushed material deductions [^r5][^r9][^r12].

The screen is accessible to the Ledgerline roles `PRD-PLAN`, `PRD-SUP`, `QA-INSP`, `QA-MGR`, and `SYS-ADMIN` [^r8].

## Messages

* `ERR-OPR-0001`: Raised when an operation confirmation cannot be located or encounters conflicting data [^r9].

## See also

* [[err-opr-0001|ERR-OPR-0001: Operation confirmation conflict or invalid data]]
* [[services-prd-opr|PRD opr services]]
* [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]
* [[screen-prd-rtg-03|PRD-RTG-03 Routing]]
* [[screen-prd-bkf-08|PRD-BKF-08 Backflush]]
* [[screen-prd-mrp-09|PRD-MRP-09 Mrp Run]]
* [[screen-prd-wc-10|PRD-WC-10 Work Centre]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 19, §7. Operation Confirmation (PRD-OPR-04)
[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 24, PRD-OPR-04 OPERATION CONFIRMATION ENTRY
[^r7]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 22, §8. Mrp Run (PRD-MRP-09)
[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 20, Step by step
[^r6]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 22, §8. Mrp Run (PRD-MRP-09)
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 19, §7. Operation Confirmation (PRD-OPR-04)
[^r11]: 04_service_definitions/production/opr_get.yaml, screen
[^r12]: 04_service_definitions/production/opr_save.yaml, screen
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 21, Tips
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 56, §6. Production services
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 19, Search and retrieval
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 24, PRD-OPR-04 OPERATION CONFIRMATION ENTRY
[^r13]: 04_service_definitions/production/opr_search.yaml, whole file
