---
title: "PRD-PKB-15 Production Kanban Entry"
type: "screen"
slug: "screen-prd-pkb-15"
summary: "Ledgerline screen for managing electronic production kanban cards and triggering container replenishment signals between consuming and feeder work centres."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/production/pkb_get.yaml", "04_service_definitions/production/pkb_save.yaml", "04_service_definitions/production/pkb_signal.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | PRD-PKB-15 |
| Screen title | Production Kanban Entry |
| Menu path | Production and Quality > Production kanban |
| Roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN |
| Services | pkb_get, pkb_save, pkb_signal |
| Status | current |

Screen PRD-PKB-15 manages electronic kanban tracking cards and logs container demand replenishment signals between consuming and feeder work centres at Manchester and Leeds [^r1]. It is accessed from the main menu under Production and Quality via Production > Production kanban [^r5][^r10]. Authorised roles include PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, and SYS-ADMIN [^r10].

## Fields

| Field label | Technical name | Type | Mandatory | Description |
|---|---|---|---|---|
| ITEM CD | itm_cd | String | Yes | Approved sub-assembly item code validated against the active BOM [^r2][^r6][^r7][^r10][^r13]. |
| WORK CENTRE | wc_cd | String | Yes | Designated consuming or feeder production line or cell code [^r2][^r6][^r10][^r13]. |
| QTY | qty | Integer | Yes | Standard container batch quantity [^r2][^r6][^r10][^r13]. |
| PKB NO | pkb_no | String | Yes | Kanban ticket or card reference number [^r2][^r8][^r10][^r12][^r15]. |
| COMMENT | comment | String | No | Operational remarks or notes regarding the signal [^r2][^r6][^r10][^r15]. |

## Keys and services

* **Get** (`F3`): Invokes read service `pkb_get` using `pkb_no` to populate the screen with previously recorded work centre and quantity details [^r8][^r11][^r12].
* **Save** (`F8`): Invokes write service `pkb_save` passing `itm_cd`, `wc_cd`, and `qty` to validate the item against the active BOM and generate the electronic kanban record [^r3][^r7][^r11][^r13].
* **Signal**: Invokes write service `pkb_signal` requiring `PKB NO` and optional `COMMENT` to mark an empty container as active, alerting the feeder department that replenishment is due [^r3][^r9][^r11][^r14][^r15].

## Messages

* `[[err-itm-0011]]`: Displayed on the status line when an entered item code is unrecognised, inactive, or not found on the active BOM during `pkb_save` [^r4][^r7][^r11].
* `[[err-pkb-0001]]`: Primary validation error returned on the status line when an empty container signal is rejected because it has already been signalled [^r4][^r9][^r11].
* `[[err-pkb-0201]]`: Displayed on the status line during validation for duplicate active kanban cycles [^r4][^r11].

## Versions and conflicts

* **Mandatory status of PKB NO**: In the field specification sections of MAN-SCR-72 and MAN-PRD-72, `PKB NO` is designated as mandatory [^r2][^r10]. In the MAN-PRD-72 worked example for card creation, `PKB NO` is described as optional, with the user entering an existing reference only if applicable [^r6]. Kind: `contradiction`.

## See also

* `[[services-prd-pkb|PRD pkb services]]`
* `[[screen-prd-wc-10|PRD-WC-10 Work Centre]]`
* `[[screen-prd-bom-02|PRD-BOM-02 Bill Of Materials]]`
* `[[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]`
* `[[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]`
* `[[err-pkb-0001|ERR-PKB-0001 Primary Kanban Validation Failure]]`
* `[[err-pkb-0201|ERR-PKB-0201 Duplicate Active Kanban Cycle]]`

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 69, Production Kanban (PRD-PKB-15)
[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 72, Worked example
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 24, PRD-PKB-15 PRODUCTION KANBAN ENTRY
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 69, §21. Production Kanban (PRD-PKB-15)
[^r6]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 72, Worked example
[^r7]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 72, Worked example
[^r13]: 04_service_definitions/production/pkb_save.yaml, screen
[^r8]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 72, Worked example
[^r12]: 04_service_definitions/production/pkb_get.yaml, whole file
[^r15]: 04_service_definitions/production/pkb_signal.yaml, request.fields
[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 24, PRD-PKB-15 PRODUCTION KANBAN ENTRY
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 70, Logging a new replenishment signal
[^r9]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 72, Worked example
[^r14]: 04_service_definitions/production/pkb_signal.yaml, screen
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 71, Messages
