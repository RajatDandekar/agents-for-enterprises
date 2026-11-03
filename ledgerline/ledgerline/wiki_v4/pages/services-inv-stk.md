---
title: "INV stk services"
type: "service-group"
slug: "services-inv-stk"
summary: "Ledgerline Inventory module services for stock valuation, aging, ABC classification, movement history, and audit snapshots on screen INV-STK-03."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/stk_abc_run.yaml", "04_service_definitions/inventory/stk_age_query.yaml", "04_service_definitions/inventory/stk_move_query.yaml", "04_service_definitions/inventory/stk_snapshot.yaml", "04_service_definitions/inventory/stk_val_query.yaml", "04_service_definitions/inventory/stk_val_run.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | INV |
| Object | stk |
| Screen | [[screen-inv-stk-03|INV-STK-03]] |
| Version available | 7.0 |
| Endpoints base | POST /ll72/svc/ |
| Authentication | X-LL-Session |
| Common input | itm_cd (mandatory), comment (optional) |

The `stk` service group provides inventory valuation, movement tracking, stock aging analysis, and audit snapshot capabilities within the Inventory (`INV`) module of Ledgerline [^r8]. The operations primarily execute against screen [[screen-inv-stk-03|INV-STK-03]] (STOCK VAL), while warehouse cover and status enquiries are separated into service `stk_query` on screen [[screen-inv-stk-02|INV-STK-02]] [^r6][^r7]. All services in this group have been available since Ledgerline 7.0 and require authentication using a session token passed in the `X-LL-Session` header from an authorised user role [^r10][^r11][^r15][^r16][^r21][^r22][^r27][^r28][^r32][^r33][^r38][^r39].

| Field | Value |
|---|---|
| Module | INV [^r8][^r10] |
| Object | stk [^r8] |
| Primary screen | [[screen-inv-stk-03|INV-STK-03]] [^r6][^r8] |
| Secondary screen | [[screen-inv-stk-02|INV-STK-02]] (stk_query) [^r7] |
| Introduction | Ledgerline 7.0 [^r10][^r15][^r21][^r27][^r32][^r38] |
| Endpoint root | `/ll72/svc/` [^r10][^r16][^r21][^r27][^r33][^r39] |
| Auth header | `X-LL-Session` [^r11][^r16][^r22][^r28][^r33][^r39] |

## Services

Across screen [[screen-inv-stk-03|INV-STK-03]], all services take the mandatory string field `itm_cd` and accept the optional string field `comment` [^r9][^r12][^r17][^r23][^r29][^r34][^r40]. Every service responds using the standard envelope containing return code `rc` (`S | W | E`), `err_cd`, short uppercase text `msg`, and the payload `data` [^r13][^r18][^r24][^r30][^r35]. Specific error failures across these services include [[err-stk-0001|ERR-STK-0001]] (STOCK NOT FOUND) and [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE) [^r9][^r14][^r19][^r25][^r31][^r36][^r41].

### stk_val_query

A read service that retrieves stock quantities on hand, allocated stock, free stock, unit cost, and extended inventory valuation in pounds [^r1][^r8][^r32].

* **Type**: Read [^r8][^r32]
* **Endpoint**: `POST /ll72/svc/stk_val_query` [^r33]
* **Required fields**: `itm_cd` (string) [^r34]
* **Optional fields**: `comment` (string) [^r34]
* **Specific errors**: [[err-stk-0001|ERR-STK-0001]], [[err-itm-0011|ERR-ITM-0011]] [^r36]
* **Common errors**: `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (`<FIELD> MANDATORY`), `ERR-SYS-0422` (`UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>`), `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r37]
* **Source definition**: `04_service_definitions/inventory/stk_val_query.yaml` [^r32]

### stk_val_run

A write service that recalculates stock valuation records by executing stored procedure `sp_stk_val_run` [^r8][^r38][^r39].

* **Type**: Write [^r8][^r38]
* **Endpoint**: `POST /ll72/svc/stk_val_run` [^r39]
* **Required fields**: `itm_cd` (string) [^r40]
* **Optional fields**: `comment` (string) [^r40]
* **Specific errors**: [[err-stk-0001|ERR-STK-0001]], [[err-itm-0011|ERR-ITM-0011]] [^r41]
* **Source definition**: `04_service_definitions/inventory/stk_val_run.yaml` [^r38]

### stk_age_query

A read service that interrogates goods receipt logs to report inventory distributed across aging bands [^r2][^r8][^r15].

* **Type**: Read [^r8][^r15]
* **Endpoint**: `POST /ll72/svc/stk_age_query` [^r16]
* **Required fields**: `itm_cd` (string) [^r17]
* **Optional fields**: `comment` (string) [^r17]
* **Specific errors**: [[err-stk-0001|ERR-STK-0001]], [[err-itm-0011|ERR-ITM-0011]] [^r19]
* **Common errors**: `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, `ERR-SYS-0503` [^r20]
* **Source definition**: `04_service_definitions/inventory/stk_age_query.yaml` [^r15]

### stk_abc_run

A write service that assesses historical usage to calculate annual consumption value in pounds for each item and updates ABC classification categories via database procedure `sp_stk_abc_run` [^r3][^r8][^r10][^r13].

* **Type**: Write [^r8][^r10]
* **Endpoint**: `POST /ll72/svc/stk_abc_run` [^r10]
* **Required fields**: `itm_cd` (string) [^r12]
* **Optional fields**: `comment` (string) [^r12]
* **Specific errors**: [[err-stk-0001|ERR-STK-0001]], [[err-itm-0011|ERR-ITM-0011]] [^r14]
* **Common errors**: `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, `ERR-SYS-0503` [^r14]
* **Source definition**: `04_service_definitions/inventory/stk_abc_run.yaml` [^r10]

### stk_move_query

A read service providing a chronological audit trail of stock movements, detailing transaction types, reference numbers, source locations, destination stores, quantities moved, and resulting stock balances [^r4][^r8][^r21].

* **Type**: Read [^r8][^r21]
* **Endpoint**: `POST /ll72/svc/stk_move_query` [^r21]
* **Required fields**: `itm_cd` (string) [^r23]
* **Optional fields**: `comment` (string) [^r23]
* **Specific errors**: [[err-stk-0001|ERR-STK-0001]], [[err-itm-0011|ERR-ITM-0011]] [^r25]
* **Common errors**: `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, `ERR-SYS-0503` [^r26]
* **Source definition**: `04_service_definitions/inventory/stk_move_query.yaml` [^r21]

### stk_snapshot

A read service that freezes current stock balances and copies quantities and valuations into snapshot storage tables, tagged with the audit note provided in `comment` [^r5][^r8][^r27].

* **Type**: Read [^r8][^r27]
* **Endpoint**: `POST /ll72/svc/stk_snapshot` [^r27]
* **Required fields**: `itm_cd` (string) [^r29]
* **Optional fields**: `comment` (string) [^r29]
* **Specific errors**: [[err-stk-0001|ERR-STK-0001]], [[err-itm-0011|ERR-ITM-0011]] [^r31]
* **Source definition**: `04_service_definitions/inventory/stk_snapshot.yaml` [^r27]

## Versions and conflicts

* **Valuation and movement query details**: Today's rule from MAN-INV-72 v7.2.3 (effective 2025-01-15) specifies that `stk_val_query` returns quantities on hand, allocated quantities, free stock, unit cost, and extended inventory valuation in pounds, while `stk_move_query` details transaction types, reference numbers, source locations, destination stores, quantities moved, and balances [^r1][^r4]. In superseded manual MAN-INV-72 v7.2.2 (2024-06-10), `stk_val_query` populated current unit costs, quantities on hand, and total valuation, while `stk_move_query` displayed receipts, issues, and adjustments [^r42] (`superseded`).
* **Aging query mechanism**: Today's rule from MAN-INV-72 v7.2.3 states that `stk_age_query` interrogates goods receipt logs to break down stock across aging bands [^r2]. In superseded manual MAN-INV-72 v7.2.2 (2024-06-10), `stk_age_query` was described as calculating elapsed storage time to populate aging buckets [^r43] (`superseded`).

## See also

* [[screen-inv-stk-03|INV-STK-03 Stock Val]]
* [[screen-inv-stk-02|INV-STK-02 Stock Status Enquiry]]
* [[errors-stk|ERR-STK Error Codes]]
* [[err-stk-0001|ERR-STK-0001]]
* [[errors-itm|ERR-ITM error codes]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[services-inv-itm|INV itm services]]
* [[services-inv-adj|INV adj services]]

## References

[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 19, stk_val_query STOCK VAL QUERY
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 20, INV-STK-03 STOCK VAL
[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 20, INV-STK-02 STOCK STATUS ENQUIRY
[^r10]: 04_service_definitions/inventory/stk_abc_run.yaml, service: stk_abc_run
[^r11]: 04_service_definitions/inventory/stk_abc_run.yaml, auth
[^r15]: 04_service_definitions/inventory/stk_age_query.yaml, stk_age_query
[^r16]: 04_service_definitions/inventory/stk_age_query.yaml, endpoint / auth
[^r21]: 04_service_definitions/inventory/stk_move_query.yaml, service: stk_move_query
[^r22]: 04_service_definitions/inventory/stk_move_query.yaml, auth
[^r27]: 04_service_definitions/inventory/stk_snapshot.yaml, service: stk_snapshot
[^r28]: 04_service_definitions/inventory/stk_snapshot.yaml, auth
[^r32]: 04_service_definitions/inventory/stk_val_query.yaml, whole file
[^r33]: 04_service_definitions/inventory/stk_val_query.yaml, whole file
[^r38]: 04_service_definitions/inventory/stk_val_run.yaml, service: stk_val_run
[^r39]: 04_service_definitions/inventory/stk_val_run.yaml, endpoint
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 20, stk_val_run STOCK VAL RUN
[^r12]: 04_service_definitions/inventory/stk_abc_run.yaml, request
[^r17]: 04_service_definitions/inventory/stk_age_query.yaml, request.fields
[^r23]: 04_service_definitions/inventory/stk_move_query.yaml, request
[^r29]: 04_service_definitions/inventory/stk_snapshot.yaml, request
[^r34]: 04_service_definitions/inventory/stk_val_query.yaml, request
[^r40]: 04_service_definitions/inventory/stk_val_run.yaml, request.fields
[^r13]: 04_service_definitions/inventory/stk_abc_run.yaml, response
[^r18]: 04_service_definitions/inventory/stk_age_query.yaml, response.envelope
[^r24]: 04_service_definitions/inventory/stk_move_query.yaml, response
[^r30]: 04_service_definitions/inventory/stk_snapshot.yaml, response
[^r35]: 04_service_definitions/inventory/stk_val_query.yaml, response
[^r14]: 04_service_definitions/inventory/stk_abc_run.yaml, errors
[^r19]: 04_service_definitions/inventory/stk_age_query.yaml, errors
[^r25]: 04_service_definitions/inventory/stk_move_query.yaml, errors
[^r31]: 04_service_definitions/inventory/stk_snapshot.yaml, errors
[^r36]: 04_service_definitions/inventory/stk_val_query.yaml, errors
[^r41]: 04_service_definitions/inventory/stk_val_run.yaml, errors
[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 46, Step by step
[^r37]: 04_service_definitions/inventory/stk_val_query.yaml, common_errors
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 46, Step by step
[^r20]: 04_service_definitions/inventory/stk_age_query.yaml, common_errors
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 47, Step by step
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 47, Step by step
[^r26]: 04_service_definitions/inventory/stk_move_query.yaml, common_errors
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 47, Step by step
[^r42]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 20, Step by step
[^r43]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 20, Step by step
