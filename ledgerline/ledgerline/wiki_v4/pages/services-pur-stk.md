---
title: "PUR stk services"
type: "service-group"
slug: "services-pur-stk"
summary: "Ledgerline purchasing stock services for stock status enquiry, stock ledger retrieval, and items below reorder level."
audience: "staff"
status: "current"
sources: ["05_master_data/Stock_on_hand_2026-10-26_0900.xlsx", "03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/purchase/stk_ledger.yaml", "04_service_definitions/purchase/stk_query.yaml", "04_service_definitions/purchase/stk_reorder_list.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| module | PUR |
| services | stk_query, stk_ledger, stk_reorder_list |
| availability | since Ledgerline 7.0 |
| protocol | HTTP POST JSON |
| auth | header X-LL-Session |
| status | current |

The `services-pur-stk` group provides read-only stock enquiry services under the Ledgerline PUR module [^r14][^r19][^r25]. These services allow users and automated batch processes to check current stock levels, view stock ledger movements, and identify items falling below reorder thresholds [^r11][^r12][^r13]. Stock balance figures reflect real-time on-hand, allocated, and on-order inventory across warehouses, which fluctuate continuously throughout the working day [^r5][^r10].

## Services

### stk_query
Service `stk_query` (STOCK STATUS ENQUIRY) is a read service available since version 7.0 at endpoint `POST /ll72/svc/stk_query`, associated with screen [[screen-inv-stk-02|INV-STK-02]] [^r12][^r19]. Authentication requires a valid session token in header `X-LL-Session` and a role permitted to run the service [^r20]. It generates stock status snapshots displaying item code, warehouse code, on-hand quantity, allocated stock, and on-order quantities [^r2][^r9]. The service calculates `cover_days` as `(on_hand - allocated) / avg_daily_issue`, rounded down [^r23]. The response envelope returns `rc` ('S | W | E'), `err_cd`, `msg`, and `data` [^r22].
* **Required fields:** `itm_cd` (ITEM CD, string) [^r21].
* **Optional fields:** `whs_cd` (WHS CD, string) [^r21].
* **Errors:** [[err-stk-0001|ERR-STK-0001]] (NO STOCK RECORD), ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r24].
* **Source file:** `04_service_definitions/purchase/stk_query.yaml` [^r19].

### stk_ledger
Service `stk_ledger` is a read-only service under module PUR available since version 7.0 at endpoint `POST /ll72/svc/stk_ledger`, having no associated screen [^r14]. It retrieves stock ledger entries for a specified item [^r13]. Authentication requires a session token in header `X-LL-Session` and a permitted user role [^r15]. The response envelope provides `rc` ('S | W | E'), `err_cd`, `msg`, and `data` [^r17].
* **Required fields:** `itm_cd` (ITEM CD, string) [^r16].
* **Optional fields:** none [^r16].
* **Errors:** ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r18].
* **Source file:** `04_service_definitions/purchase/stk_ledger.yaml` [^r14].

### stk_reorder_list
Service `stk_reorder_list` (ITEMS BELOW REORDER LEVEL) is a read service under module PUR available since version 7.0 at endpoint `POST /ll72/svc/stk_reorder_list` [^r25][^r26]. Authentication requires a session token in header `X-LL-Session` and an authorized user role [^r26]. It retrieves items currently below their reorder level, executing the same underlying logic as daily batch job JOB-INV-040 which runs at 06:15 for warehouses WH-MAN-STR and WH-LDS-STR [^r11][^r13]. The response envelope contains `rc` ('S | W | E'), `err_cd`, `msg`, and `data` [^r27].
* **Required fields:** none [^r27].
* **Optional fields:** none [^r27].
* **Errors:** ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r28].
* **Source file:** `04_service_definitions/purchase/stk_reorder_list.yaml` [^r25].

## See also
* [[data-stock-on-hand|data-stock-on-hand]]
* [[err-stk-0001|err-stk-0001]]
* [[man-pur-72|man-pur-72]]
* [[screen-inv-stk-02|screen-inv-stk-02]]

## References

[^r14]: 04_service_definitions/purchase/stk_ledger.yaml, service: stk_ledger
[^r19]: 04_service_definitions/purchase/stk_query.yaml, service: stk_query
[^r25]: 04_service_definitions/purchase/stk_reorder_list.yaml, service: stk_reorder_list
[^r11]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 3, §2. Job details
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 4, §2. Purchase services
[^r13]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 4, §2. Purchase services
[^r5]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, SHEET Stock
[^r10]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, SHEET Stock
[^r20]: 04_service_definitions/purchase/stk_query.yaml, auth
[^r2]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, SHEET Stock: 2338 data rows, 6 columns
[^r9]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, SHEET Stock
[^r23]: 04_service_definitions/purchase/stk_query.yaml, notes
[^r22]: 04_service_definitions/purchase/stk_query.yaml, response.envelope
[^r21]: 04_service_definitions/purchase/stk_query.yaml, request.fields
[^r24]: 04_service_definitions/purchase/stk_query.yaml, errors
[^r15]: 04_service_definitions/purchase/stk_ledger.yaml, auth
[^r17]: 04_service_definitions/purchase/stk_ledger.yaml, response.envelope
[^r16]: 04_service_definitions/purchase/stk_ledger.yaml, request.fields
[^r18]: 04_service_definitions/purchase/stk_ledger.yaml, common_errors
[^r26]: 04_service_definitions/purchase/stk_reorder_list.yaml, endpoint
[^r27]: 04_service_definitions/purchase/stk_reorder_list.yaml, request
[^r28]: 04_service_definitions/purchase/stk_reorder_list.yaml, common_errors
