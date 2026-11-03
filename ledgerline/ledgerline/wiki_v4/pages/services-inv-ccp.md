---
title: "INV ccp services"
type: "service-group"
slug: "services-inv-ccp"
summary: "Ledgerline inventory cycle count plan services providing creation, retrieval, listing, and order generation via screen INV-CCP-14."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/ccp_generate.yaml", "04_service_definitions/inventory/ccp_get.yaml", "04_service_definitions/inventory/ccp_save.yaml", "04_service_definitions/inventory/ccp_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| service_group | services-inv-ccp |
| module | INV |
| screen | INV-CCP-14 |
| services | ccp_save, ccp_get, ccp_search, ccp_generate |
| available_since | Ledgerline 7.0 |
| status | current |

The `services-inv-ccp` service group comprises backend operations for managing cycle count plans in Ledgerline's inventory module [^r11][^r16]. These services operate on screen [[screen-inv-ccp-14|INV-CCP-14]] to create, search, fetch, and execute count schedules based on warehouse locations and classification rules [^r1][^r2][^r3]. All endpoints have been available since Ledgerline 7.0 and require an authorized role along with an active session token [^r7][^r11][^r12][^r16][^r17].

## Services

### ccp_save
Service `ccp_save` (CYCLE COUNT PLAN SAVE) is a write operation that validates warehouse location and inventory classification before automatically assigning a sequential `CCP NO` and setting plan status to active [^r1][^r4][^r7][^r21]. It operates at endpoint `POST /ll72/svc/ccp_save`, executes backend stored procedure `sp_ccp_save`, and has been available since Ledgerline 7.0 [^r7][^r21][^r25]. Authentication requires a session token in header `X-LL-Session` and an authorized user role [^r22].
* **Required fields**: `whs_cd` (string, WHS CD), `freq_days` (integer, FREQUENCY) [^r23].
* **Optional fields**: `abc` (string, ABC CLASS) [^r23].
* **Response**: Standard envelope returning return code `rc` (`S | W | E`), `err_cd` when `rc` is `E`, uppercase text `msg`, and payload `data` [^r24].
* **Errors**: `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (`<FIELD> MANDATORY`), `ERR-SYS-0422` (`UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>`), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r25].
* **Source file**: `04_service_definitions/inventory/ccp_save.yaml` [^r21].

### ccp_get
Service `ccp_get` (CYCLE COUNT PLAN GET) is a read operation on screen [[screen-inv-ccp-14|INV-CCP-14]] that retrieves an existing cycle count plan record using its reference number [^r2][^r5][^r8][^r16]. It is accessed via endpoint `POST /ll72/svc/ccp_get`, requires an authorized role with header `X-LL-Session`, and has been available since version 7.0 [^r16][^r17].
* **Required fields**: `ccp_no` (string, CCP NO) [^r8][^r18].
* **Optional fields**: None [^r18].
* **Response**: Standard envelope containing `rc` (`S | W | E`), `err_cd`, uppercase message `msg`, and `data` [^r19].
* **Errors**: [[err-ccp-0001|ERR-CCP-0001]] (CYCLE COUNT PLAN NOT FOUND), `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r8][^r20].
* **Source file**: `04_service_definitions/inventory/ccp_get.yaml` [^r16].

### ccp_search
Service `ccp_search` (CYCLE COUNT PLAN LIST) is a read operation that queries and lists existing cycle count plans matching specified filter criteria on screen [[screen-inv-ccp-14|INV-CCP-14]] [^r2][^r6][^r9][^r26]. The endpoint is `POST /ll72/svc/ccp_search`, available since Ledgerline 7.0, and requires header `X-LL-Session` with an authorized role [^r26][^r27].
* **Required fields**: None [^r28].
* **Optional fields**: `whs_cd` (string, WHS CD), `abc` (string, ABC CLASS), `freq_days` (integer, FREQUENCY), and `status` (string, STATUS) [^r9][^r28].
* **Response**: Envelope returning `rc` (`S | W | E`), `err_cd`, uppercase message `msg`, and `data` [^r29].
* **Errors**: `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (`<FIELD> MANDATORY`), `ERR-SYS-0422` (`UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>`), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r30].
* **Source file**: `04_service_definitions/inventory/ccp_search.yaml` [^r26].

### ccp_generate
Service `ccp_generate` (CYCLE COUNT PLAN GENERATE) is a write operation tied to screen [[screen-inv-ccp-14|INV-CCP-14]] that generates cycle count orders by evaluating warehouse items, ABC class, and count history against plan frequency [^r3][^r10][^r11]. Available since Ledgerline 7.0 at endpoint `POST /ll72/svc/ccp_generate`, it calls stored procedure `sp_ccp_generate` and requires session authentication via `X-LL-Session` under an authorized role [^r10][^r11][^r12][^r15].
* **Required fields**: `ccp_no` (string, CCP NO) [^r10][^r13].
* **Optional fields**: `comment` (string) [^r10][^r13].
* **Response**: Envelope returning `rc` (`S | W | E`), `err_cd`, short uppercase message `msg`, and `data` [^r14].
* **Errors**: [[err-ccp-0001|ERR-CCP-0001]] [^r10].
* **Source file**: `04_service_definitions/inventory/ccp_generate.yaml` [^r11].

## Versions and conflicts
* **Plan numbering and status progression**: In current Ledgerline 7.2.3, `ccp_save` validates input, assigns the sequential `CCP NO`, and activates the plan, while `ccp_generate` evaluates inventory history and generates count orders [^r1][^r3][^r4]. In superseded manual [[man-inv-72|MAN-INV-72]] v7.2.2 (2024-06-10), `ccp_generate` generated the sequential `CCP NO` in draft status, and `ccp_save` committed the record to confirmed status (`superseded`) [^r31][^r32].

## See also
* [[screen-inv-ccp-14|INV-CCP-14 Cycle Count Plan Entry]]
* [[services-inv-cnt|INV cnt services]]
* [[screen-inv-cnt-06|INV-CNT-06 Stock Count Entry]]
* [[err-ccp-0001|ERR-CCP-0001 Cycle count plan parameter error]]
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]

## References

[^r11]: 04_service_definitions/inventory/ccp_generate.yaml, service
[^r16]: 04_service_definitions/inventory/ccp_get.yaml, service: ccp_get
[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 54, Creating a new cycle count plan
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 54, Retrieving an existing cycle count plan
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 55, Messages
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 21, ccp_save CYCLE COUNT PLAN SAVE
[^r12]: 04_service_definitions/inventory/ccp_generate.yaml, auth
[^r17]: 04_service_definitions/inventory/ccp_get.yaml, service: ccp_get
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 56, Worked example
[^r21]: 04_service_definitions/inventory/ccp_save.yaml, service: ccp_save
[^r25]: 04_service_definitions/inventory/ccp_save.yaml, common_errors
[^r22]: 04_service_definitions/inventory/ccp_save.yaml, auth
[^r23]: 04_service_definitions/inventory/ccp_save.yaml, request.fields
[^r24]: 04_service_definitions/inventory/ccp_save.yaml, response.envelope
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 56, Worked example
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 22, ccp_get CYCLE COUNT PLAN GET
[^r18]: 04_service_definitions/inventory/ccp_get.yaml, request
[^r19]: 04_service_definitions/inventory/ccp_get.yaml, response
[^r20]: 04_service_definitions/inventory/ccp_get.yaml, errors
[^r6]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 56, Worked example
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 22, ccp_search CYCLE COUNT PLAN LIST
[^r26]: 04_service_definitions/inventory/ccp_search.yaml, service: ccp_search
[^r27]: 04_service_definitions/inventory/ccp_search.yaml, service: ccp_search
[^r28]: 04_service_definitions/inventory/ccp_search.yaml, request
[^r29]: 04_service_definitions/inventory/ccp_search.yaml, response
[^r30]: 04_service_definitions/inventory/ccp_search.yaml, common_errors
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 22, ccp_generate CYCLE COUNT PLAN GENERATE
[^r15]: 04_service_definitions/inventory/ccp_generate.yaml, procedures
[^r13]: 04_service_definitions/inventory/ccp_generate.yaml, request
[^r14]: 04_service_definitions/inventory/ccp_generate.yaml, response
[^r31]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 23, Step by step
[^r32]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 23, Step by step
