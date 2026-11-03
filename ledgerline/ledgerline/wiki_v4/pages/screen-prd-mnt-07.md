---
title: "PRD-MNT-07 Maintenance Order Entry"
type: "screen"
slug: "screen-prd-mnt-07"
summary: "Screen PRD-MNT-07 enables production and QA roles to create, search, fetch, and close maintenance orders in Ledgerline."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/production/mnt_close.yaml", "04_service_definitions/production/mnt_get.yaml", "04_service_definitions/production/mnt_save.yaml", "04_service_definitions/production/mnt_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | PRD-MNT-07 |
| Name | Maintenance Order Entry |
| Menu path | Production > Maintenance order |
| Module | Production |
| Authorized roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN |
| Key services | mnt_save, mnt_get, mnt_search, mnt_close |

Screen PRD-MNT-07 provides maintenance order creation, retrieval, search, and closure within Ledgerline for production and quality teams [^r1][^r5]. Accessible under Production > Maintenance order, it serves roles PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, and SYS-ADMIN [^r5]. The screen coordinates with underlying maintenance services to track asset breakdowns and permanently lock completed orders against further changes or time bookings [^r3][^r4].

## Fields

The screen layout consists of both system-generated and user-entered fields [^r1][^r2]:

* `mno_no` (MNO NO): Mandatory maintenance order number, automatically assigned by Ledgerline upon order creation [^r1][^r2][^r5].
* `asset_cd` (ASSET): Mandatory string field designating the affected equipment [^r1][^r5][^r10].
* `fault` (FAULT): Mandatory string field specifying the issue or breakdown reason [^r1][^r5][^r10].
* `cc_cd` (CC CD): Mandatory string field for the cost centre charged [^r1][^r5][^r10].
* `priority` (PRIORITY): Optional string field indicating maintenance urgency [^r1][^r5][^r10].
* `status` (STATUS): Optional on input, this field is maintained directly by Ledgerline and cannot be typed into by the user [^r1][^r2][^r5].
* `comment` (COMMENT): Optional string field for additional maintenance remarks [^r1][^r5].

## Keys and services

PRD-MNT-07 interfaces with the [[services-prd-mnt|PRD mnt services]] group to process order entries and state transitions [^r3][^r6]:

* **Save** (F8): Calls `mnt_save` (`POST /ll72/svc/mnt_save`) running stored procedure `sp_mnt_save` to create or update a record using mandatory fields `asset_cd`, `fault`, and `cc_cd`, alongside optional `priority` [^r3][^r6][^r9][^r10].
* **Get** (F3): Invokes `mnt_get` (`POST /ll72/svc/mnt_get`) using key parameter `mno_no` to retrieve existing maintenance order records [^r3][^r6][^r8].
* **Search** (F2 / Enter): Executes read service `mnt_search` (`POST /ll72/svc/mnt_search`) to query maintenance order lists by optional filters `asset_cd`, `fault`, `priority`, and `status` [^r3][^r6][^r11].
* **Close**: Triggers write service `mnt_close` running stored procedure `sp_mnt_close`, updating `status` to closed and locking the order against subsequent edits and labor time bookings [^r4][^r6][^r7].

## Messages

The screen validates entries against the following application message codes [^r6]:

* [[err-cc-0009]]: Validates cost centre existence and authorization [^r6].
* `ERR-MNO-0001`: Maintenance order validation error [^r6].
* `ERR-MNO-0801`: Maintenance order processing error [^r6].

## Versions and conflicts

* **contradiction**: The underlying service definition `mnt_save.yaml` defines mandatory save request fields as `asset_cd`, `fault`, and `cc_cd`, with `mno_no` auto-assigned by the system on creation [^r2][^r10]. User manuals MAN-PRD-72 (p. 62) and MAN-SCR-72 (p. 22) instead list `mno_no` among the mandatory user-entered screen fields alongside `asset_cd`, `fault`, and `cc_cd` [^r1][^r5].

## See also

* [[services-prd-mnt|PRD mnt services]]
* [[err-cc-0009|ERR-CC-0009]]
* [[screen-fin-cc-01|FIN-CC-01 Cost Centre Entry]]
* [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]
* [[screen-prd-wc-10|PRD-WC-10 Work Centre]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 62, §19. Maintenance Order (PRD-MNT-07)
[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 22, PRD-MNT-07 MAINTENANCE ORDER ENTRY
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 63, Step by step
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 64, Closing a completed order:
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 63, Screen layout and fields
[^r10]: 04_service_definitions/production/mnt_save.yaml, request.fields
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 23, PRD-MNT-07 MAINTENANCE ORDER ENTRY
[^r9]: 04_service_definitions/production/mnt_save.yaml, screen
[^r8]: 04_service_definitions/production/mnt_get.yaml, service: mnt_get
[^r11]: 04_service_definitions/production/mnt_search.yaml, whole file
[^r7]: 04_service_definitions/production/mnt_close.yaml, service: mnt_close
