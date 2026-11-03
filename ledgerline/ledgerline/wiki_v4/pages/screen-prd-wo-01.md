---
title: "PRD-WO-01 Work Order Entry"
type: "screen"
slug: "screen-prd-wo-01"
summary: "Screen PRD-WO-01 creates, searches, releases, closes, and cancels shop floor production work orders in Ledgerline."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-PRD-001 Work Order Release and Backflush v1.5.pdf", "03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/wo_cancel.yaml", "04_service_definitions/production/wo_close.yaml", "04_service_definitions/production/wo_get.yaml", "04_service_definitions/production/wo_release.yaml", "04_service_definitions/production/wo_save.yaml", "04_service_definitions/production/wo_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen Code | PRD-WO-01 |
| Screen Name | Work Order Entry |
| Menu Path | Production > Work order |
| Roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN |
| Services | wo_save, wo_get, wo_search, wo_release, wo_close, wo_cancel |

Screen PRD-WO-01 provides the user interface for creating, managing, releasing, closing, and cancelling shop floor work orders in Ledgerline [^r2][^r8][^r12]. Accessible via menu path Production > Work order, the screen is maintained for roles PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, and SYS-ADMIN [^r2][^r8]. Production operations require work orders to be released on PRD-WO-01 at least two days before scheduled start dates, subject to full component stock availability [^r1].

| Property | Value |
|---|---|
| Screen Code | PRD-WO-01 [^r8] |
| Screen Name | Work Order Entry [^r8] |
| Menu Path | Production > Work order [^r2][^r8] |
| Permitted Roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN [^r8] |
| Primary Services | wo_save, wo_get, wo_search, wo_release, wo_close, wo_cancel [^r2][^r10][^r12] |

## Fields

Screen PRD-WO-01 contains the following mandatory and optional fields:

* **ITEM CD (`itm_cd`)**: Mandatory assembly item code to manufacture; validates item status and active bill of materials [^r3][^r4][^r9][^r19].
* **QTY (`qty`)**: Mandatory order production quantity, which must be strictly greater than zero [^r3][^r9][^r11][^r19].
* **START DT (`start_dt`)**: Mandatory scheduled production start date [^r3][^r9][^r19].
* **CC CD (`cc_cd`)**: Mandatory cost centre code charged for the production order [^r3][^r4][^r9][^r19].
* **WO NO (`wo_no`)**: Mandatory work order identifier generated as a unique internal sequence upon saving or supplied to fetch, release, close, or cancel an order [^r3][^r4][^r9][^r13][^r15][^r17].
* **REASON (`reason`)**: Mandatory field used to enter operational explanations when cancelling a work order [^r3][^r7][^r9][^r13].
* **WORK CENTRE (`wc_cd`)**: Optional manufacturing work centre code [^r3][^r9][^r19].
* **STATUS (`status`)**: Optional status display field tracking the order lifecycle from unreleased draft to released, closed, or cancelled [^r3][^r4][^r5][^r6][^r7][^r9].
* **COMMENT (`comment`)**: Optional operational comment passed during order actions or release [^r3][^r9][^r17].

## Keys and services

PRD-WO-01 provides keyboard shortcuts and interface button actions mapping directly to the production backend services:

* **Save (F8)**: Invokes write service `wo_save` (endpoint `POST /ll72/svc/wo_save`) using fields `itm_cd`, `qty`, `start_dt`, `cc_cd`, and optional `wc_cd` [^r4][^r10][^r18][^r19]. It validates the item status, confirms active BOM existence, checks the cost centre, allocates a unique sequence number in `wo_no`, and sets `status` to unreleased [^r4].
* **Get (F3)**: Invokes read service `wo_get` to retrieve an existing work order record by `wo_no` [^r10][^r15].
* **Search (F2 / Enter)**: Invokes read service `wo_search` (endpoint `POST /ll72/svc/wo_search`) to query work order records [^r10][^r20].
* **Release (F9)**: Invokes write service `wo_release` (endpoint `POST /ll72/svc/wo_release`) using `wo_no` and optional `comment`, executing database procedure `sp_wo_release` [^r5][^r10][^r16][^r17]. This verifies component stock availability, creates inventory balance reservations, locks order quantities against alteration, and updates `status` to released [^r5]. Releases must occur at least two days prior to the start date according to [[sop-prd-001]] [^r1].
* **Close**: Invokes write service `wo_close` to finalise completed work orders [^r6][^r10][^r14]. It verifies that outstanding component reservations are cleared, calculates job variances, and updates `status` to closed to block further stock issues and direct labour postings [^r6].
* **Cancel (Shift+F8)**: Invokes write service `wo_cancel` requiring `wo_no` and `reason` [^r7][^r10][^r13]. It relieves component reservations, sets `status` to cancelled, and archives the order [^r7].

## Messages

The screen triggers the following system messages and validation error codes:

* **[[err-wo-0310]]**: Component Shortage; raised during release when raw materials or sub-assemblies show a stock deficit [^r1][^r11].
* **[[err-wo-0201]]**: Qty Must Be > 0 [^r11].
* **[[err-itm-0011]]**: Item Not Found Or Inactive [^r11].
* **[[err-cc-0009]]**: Cost Centre Not Found [^r11].
* **[[err-wo-0105]]**: Date In Past [^r11].
* **[[err-wo-0001]]**: Work Order Not Found [^r11].
* **[[err-wo-0007]]**: Work Order Not In Draft [^r11].
* **[[err-bom-0001]]**: No Active Bom [^r11].
* **[[err-wo-0801]]**: Work Order Closed [^r11].

## See also

* [[sop-prd-001|SOP-PRD-001 Work Order Release and Backflush]]
* [[services-prd-wo|PRD wo services]]
* [[errors-wo|ERR-WO error codes]]
* [[err-wo-0310|ERR-WO-0310 Component Shortage on Work Order Release]]
* [[err-bom-0001|ERR-BOM-0001 Parent assembly not found on bill of materials master]]
* [[err-cc-0009|ERR-CC-0009]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[screen-prd-bom-02|PRD-BOM-02 Bill Of Materials]]
* [[screen-prd-rtg-03|PRD-RTG-03 Routing]]
* [[screen-prd-wc-10|PRD-WC-10 Work Centre]]
* [[screen-prd-bkf-08|PRD-BKF-08 Backflush]]
* [[screen-prd-opr-04|PRD-OPR-04 Operation Confirmation Entry]]

## References

[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 3, §3. Work Order (PRD-WO-01)
[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 26, PRD-WO-01 WORK ORDER ENTRY
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 52, §6. Production services
[^r1]: 02_procedures/SOP-PRD-001 Work Order Release and Backflush v1.5.pdf, p. 4, §5. Procedure: notes and common mistakes
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 26, PRD-WO-01 WORK ORDER ENTRY
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 3, §3. Work Order (PRD-WO-01)
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 4, Creating a New Work Order
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 26, PRD-WO-01 WORK ORDER ENTRY
[^r19]: 04_service_definitions/production/wo_save.yaml, request.fields
[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 26, PRD-WO-01 WORK ORDER ENTRY
[^r13]: 04_service_definitions/production/wo_cancel.yaml, service: wo_cancel
[^r15]: 04_service_definitions/production/wo_get.yaml, whole file
[^r17]: 04_service_definitions/production/wo_release.yaml, request.fields
[^r7]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 5, Cancelling an Order
[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 5, Releasing an Order to the Shop Floor
[^r6]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 5, Closing a Completed Order
[^r18]: 04_service_definitions/production/wo_save.yaml, service: wo_save
[^r20]: 04_service_definitions/production/wo_search.yaml, service: wo_search
[^r16]: 04_service_definitions/production/wo_release.yaml, service: wo_release
[^r14]: 04_service_definitions/production/wo_close.yaml, service: wo_close
