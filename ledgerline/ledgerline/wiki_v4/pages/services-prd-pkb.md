---
title: "PRD pkb services"
type: "service-group"
slug: "services-prd-pkb"
summary: "Ledgerline production kanban services (pkb_get, pkb_save, pkb_signal) backing screen PRD-PKB-15 for electronic replenishment card creation and signalling."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/pkb_get.yaml", "04_service_definitions/production/pkb_save.yaml", "04_service_definitions/production/pkb_signal.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | PRD |
| Object | pkb |
| Screen | PRD-PKB-15 |
| Services | pkb_get, pkb_save, pkb_signal |
| Introduced | Ledgerline 7.2.0 |
| Status | current |

The PRD pkb service group provides electronic production kanban retrieval, creation, and signalling capabilities within Ledgerline [^r11][^r16][^r23]. Operating behind screen [[screen-prd-pkb-15|PRD-PKB-15]], these services manage the replenishment lifecycle by validating card quantities against bills of materials, assigning card numbers, and broadcasting requests to feeding work centres [^r2][^r3][^r4][^r7]. All endpoints require session token authentication via the X-LL-Session header alongside an authorised user role [^r12][^r17][^r24].

## Services

### pkb_get

Service `pkb_get` (PRODUCTION KANBAN GET) is a read service introduced in Ledgerline 7.2.0 that retrieves details for an existing production kanban card on screen [[screen-prd-pkb-15|PRD-PKB-15]], including its item code, work centre, quantity, and comment [^r1][^r5][^r9][^r11]. It operates at endpoint `POST /ll72/svc/pkb_get` and returns the standard envelope containing `rc`, `err_cd`, `msg`, and `data` [^r11][^r14]. On screen [[screen-prd-pkb-15|PRD-PKB-15]], this service is triggered by key F3 [^r7].

* **Source file:** `04_service_definitions/production/pkb_get.yaml` [^r11]
* **Required fields:** `pkb_no` (string, PKB NO) [^r13]
* **Optional fields:** none [^r13]
* **Errors:** [[err-pkb-0001|ERR-PKB-0001]] (PRODUCTION KANBAN NOT FOUND), ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r9][^r15]

### pkb_save

Service `pkb_save` (PRODUCTION KANBAN SAVE) is a write service introduced in Ledgerline 7.2.0 that validates kanban entries against the current BOM, generates a unique PKB NO reference for new cards, sets card status to registered, and executes database stored procedure `sp_pkb_save` [^r2][^r4][^r8][^r16][^r20]. It operates at endpoint `POST /ll72/svc/pkb_save`, returns the standard response envelope (`rc`, `err_cd`, `msg`, `data`), and maps to key F8 on screen [[screen-prd-pkb-15|PRD-PKB-15]] [^r7][^r17][^r19].

* **Source file:** `04_service_definitions/production/pkb_save.yaml` [^r16]
* **Required fields:** `itm_cd` (string, ITEM CD), `wc_cd` (string, WORK CENTRE), `qty` (integer, QTY) [^r8][^r18]
* **Optional fields:** none [^r18]
* **Errors:** [[err-pkb-0201|ERR-PKB-0201]] (QTY MUST BE > 0), [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE), ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r8][^r21][^r22]

### pkb_signal

Service `pkb_signal` (PRODUCTION KANBAN SIGNAL) is a write service introduced in Ledgerline 7.2.0 that transitions an electronic kanban card from idle to active, locks the card from quantity changes, logs the transaction to the shift ledger, and transmits the replenishment signal to the feeding work centre's queue via stored procedure `sp_pkb_signal` [^r3][^r6][^r10][^r23][^r26]. It operates at endpoint `POST /ll72/svc/pkb_signal` on screen [[screen-prd-pkb-15|PRD-PKB-15]] and rejects duplicate outstanding signals [^r6][^r7][^r10][^r24].

* **Source file:** `04_service_definitions/production/pkb_signal.yaml` [^r23]
* **Required fields:** `pkb_no` (string, PKB NO) [^r10][^r25]
* **Optional fields:** `comment` (string, COMMENT) [^r10][^r25]
* **Errors:** [[err-pkb-0001|ERR-PKB-0001]] (PRODUCTION KANBAN NOT FOUND), ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r6][^r27]

## See also

* [[screen-prd-pkb-15|PRD-PKB-15 Production Kanban Entry]]
* [[err-pkb-0001|ERR-PKB-0001 Primary Kanban Validation Failure]]
* [[err-pkb-0201|ERR-PKB-0201 Duplicate Active Kanban Cycle]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[services-prd-wo|PRD wo services]]
* [[services-prd-wc|PRD wc services]]

## References

[^r11]: 04_service_definitions/production/pkb_get.yaml, whole file
[^r16]: 04_service_definitions/production/pkb_save.yaml, service
[^r23]: 04_service_definitions/production/pkb_signal.yaml, pkb_signal
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 70, Logging a new replenishment signal
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 70, Logging a new replenishment signal
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 72, Worked example
[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 24, PRD-PKB-15 PRODUCTION KANBAN ENTRY
[^r12]: 04_service_definitions/production/pkb_get.yaml, whole file
[^r17]: 04_service_definitions/production/pkb_save.yaml, endpoint
[^r24]: 04_service_definitions/production/pkb_signal.yaml, auth
[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 70, Step by step
[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 72, Worked example
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 64, pkb_get PRODUCTION KANBAN GET
[^r14]: 04_service_definitions/production/pkb_get.yaml, response.envelope
[^r13]: 04_service_definitions/production/pkb_get.yaml, request.fields
[^r15]: 04_service_definitions/production/pkb_get.yaml, errors
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 64, pkb_save PRODUCTION KANBAN SAVE
[^r20]: 04_service_definitions/production/pkb_save.yaml, procedures
[^r19]: 04_service_definitions/production/pkb_save.yaml, response.envelope
[^r18]: 04_service_definitions/production/pkb_save.yaml, request.fields
[^r21]: 04_service_definitions/production/pkb_save.yaml, errors
[^r22]: 04_service_definitions/production/pkb_save.yaml, common_errors
[^r6]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 72, Worked example
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 64, pkb_signal PRODUCTION KANBAN SIGNAL
[^r26]: 04_service_definitions/production/pkb_signal.yaml, procedures
[^r25]: 04_service_definitions/production/pkb_signal.yaml, request
[^r27]: 04_service_definitions/production/pkb_signal.yaml, errors
