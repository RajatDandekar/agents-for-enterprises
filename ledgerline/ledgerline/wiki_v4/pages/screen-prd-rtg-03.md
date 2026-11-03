---
title: "PRD-RTG-03 Routing"
type: "screen"
slug: "screen-prd-rtg-03"
summary: "Ledgerline screen PRD-RTG-03 defines and maintains production routing operations, work centres, and standard run times for manufactured items and sub-assemblies."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/rtg_get.yaml", "04_service_definitions/production/rtg_save.yaml", "04_service_definitions/production/rtg_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | PRD-RTG-03 |
| Title | Routing |
| Menu path | Production > Routing |
| Roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN |
| Services | rtg_get, rtg_save, rtg_search |
| Status | current |

Screen PRD-RTG-03 provides the interface for production planners, industrial engineers, and works supervisors to establish and maintain manufacturing routes for manufactured bicycles and sub-assemblies [^r3]. Accessed via menu path Production > Routing, the screen executes underlying services to retrieve, search, and commit sequential production operations [^r1][^r8]. It enforces work centre associations and standard processing times against registered manufactured items [^r2][^r7].

## Fields

Screen PRD-RTG-03 consists of a header query block and an operational detail block [^r4].

| Field label | Technical name | Type | Mandatory? | Notes |
|---|---|---|---|---|
| ITM CD | `itm_cd` | string | Yes | Manufactured item code; must exist as an active, non-bought-out item [^r2][^r7][^r8]. |
| OP NO | `op_no` | integer | Yes | Sequence number of the operation [^r2][^r8]. |
| WORK CENTRE | `wc_cd` | string | Yes | Code of the allocated work centre [^r2][^r8]. |
| STD MIN | `std_min` | float | Yes | Standard run time in minutes for the operation [^r2][^r8]. |
| STATUS | `status` | string | No | Operational routing status [^r2][^r4][^r8]. |

## Keys and services

The screen is accessible by user roles PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, and SYS-ADMIN [^r8]. It hosts three dedicated services in [[services-prd-rtg|PRD rtg services]] [^r1][^r9]:

* `rtg_get`: Invoked via `rtg_get` (POST `/ll72/svc/rtg_get`) using `itm_cd` to execute the ROUTING GET service and populate registered operational steps in the block [^r5][^r10].
* `rtg_save`: Invoked via `rtg_save` (POST `/ll72/svc/rtg_save`) to validate entered lines and commit the routing operational record using `itm_cd`, `op_no`, `wc_cd`, and `std_min` [^r6][^r11].
* `rtg_search`: Invoked via `rtg_search` to execute ROUTING LIST, querying routing records across items using optional filters for item code, operation number, work centre, and status [^r5][^r12].

## Messages

* [[err-itm-0011|ERR-ITM-0011]]: Returned when the entered `itm_cd` does not exist in the item master, is marked inactive, or is flagged as a bought-out item [^r7].
* [[err-rtg-0001|ERR-RTG-0001]]: Returned when operation sequence numbers conflict, required mandatory fields are missing, or `std_min` contains an invalid value [^r7].

## See also

* [[services-prd-rtg|PRD rtg services]]
* [[screen-prd-bom-02|PRD-BOM-02 Bill Of Materials]]
* [[screen-prd-wc-10|PRD-WC-10 Work Centre]]
* [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]
* [[screen-prd-opr-04|PRD-OPR-04 Operation Confirmation Entry]]
* [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]]
* [[err-rtg-0001|ERR-RTG-0001 Routing Save Failed]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]

## References

[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 11, Purpose
[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 11, §5. Routing (PRD-RTG-03)
[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 24, PRD-RTG-03 ROUTING
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 11, §5. Routing (PRD-RTG-03)
[^r7]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 13, Messages
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 12, Screen layout and fields
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 55, §6. Production services
[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 12, Step by step
[^r10]: 04_service_definitions/production/rtg_get.yaml, screen: PRD-RTG-03
[^r6]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 13, Step by step
[^r11]: 04_service_definitions/production/rtg_save.yaml, rtg_save
[^r12]: 04_service_definitions/production/rtg_search.yaml, service: rtg_search
