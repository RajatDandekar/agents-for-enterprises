---
title: "PRD qin services"
type: "service-group"
slug: "services-prd-qin"
summary: "Production services on screen QA-INS-01 for searching, retrieving, saving, posting, and rejecting incoming inspection records against goods receipt notes."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/qin_get.yaml", "04_service_definitions/production/qin_post.yaml", "04_service_definitions/production/qin_reject.yaml", "04_service_definitions/production/qin_save.yaml", "04_service_definitions/production/qin_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | PRD |
| Object | qin |
| Primary screen | QA-INS-01 |
| Kind | mixed (read/write) |
| Introduced | 7.0 |
| Endpoints | /ll72/svc/qin_* |

The `qin` service group handles incoming quality inspection workflows against goods receipt notes in the PRD module [^r1][^r6][^r12]. All transactions operate on screen [[screen-qa-ins-01|QA-INS-01 Incoming Inspection Entry]] via dedicated HTTP POST endpoints introduced in Ledgerline 7.0 [^r6][^r12][^r16]. They allow quality inspectors to look up pending deliveries, record inspection samples and test results, quarantine defective material, and post approved stock into inventory [^r1][^r2][^r4][^r5].

| Field | Value |
|---|---|
| Module | PRD [^r12] |
| Target object | qin [^r6][^r12] |
| Screen | [[screen-qa-ins-01|QA-INS-01]] [^r6] |
| Protocols | HTTP POST with `X-LL-Session` header [^r12][^r17][^r24][^r30][^r36] |
| Introduced | Ledgerline 7.0 [^r12][^r16][^r23][^r29][^r35] |

## Services

### qin_get

Retrieves incoming inspection line details for a goods receipt note, populates component and supplier details, and returns an assigned inspection number with status set to open [^r1][^r8]. It is a read service accessed via `POST /ll72/svc/qin_get` using session token authentication [^r12].

* **Required fields**: `qin_no` (string, QIN NO) [^r8][^r13].
* **Optional fields**: None [^r13].
* **Errors**: Specific error `ERR-QIN-0001` (INCOMING INSPECTION NOT FOUND), and common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r15].
* **Source file**: `04_service_definitions/production/qin_get.yaml` [^r12].

### qin_post

Commits incoming inspection results by executing stored procedure `sp_qin_post`, updating general ledger and inventory records [^r5][^r10][^r20]. It requires prior completion of pass/fail status, sample quantity, and an existing saved draft inspection record [^r5][^r21]. It is a write service accessed via `POST /ll72/svc/qin_post` [^r16][^r17].

* **Required fields**: `qin_no` (string, QIN NO) [^r10][^r18].
* **Optional fields**: `comment` (string, COMMENT) [^r10][^r18].
* **Errors**: Specific errors `ERR-QIN-0001` (INCOMING INSPECTION NOT FOUND), `ERR-QIN-0007` (INCOMING INSPECTION NOT IN DRAFT), `ERR-QIN-0230` (SAMPLE SIZE BELOW AQL PLAN), warning `W-QIN-231` (PASSED WITH CONCESSION), and common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r10][^r21][^r22].
* **Source file**: `04_service_definitions/production/qin_post.yaml` [^r16].

### qin_reject

Marks stock as rejected and sets the line status to quarantine for review via stored procedure `sp_qin_reject` [^r4][^r11][^r27]. It is a write service accessed via `POST /ll72/svc/qin_reject` [^r23][^r24].

* **Required fields**: `qin_no` (string, QIN NO), `reason` (string, REASON) [^r11][^r25].
* **Optional fields**: None [^r25].
* **Errors**: Specific error `ERR-QIN-0001` (INCOMING INSPECTION NOT FOUND), and common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r28]. Warning `W-QIN-231` may also be returned when non-critical defects or sample failure rates approach tolerance limits [^r4].
* **Source file**: `04_service_definitions/production/qin_reject.yaml` [^r23].

### qin_save

Writes or updates an in-progress incoming inspection record via database procedure `sp_qin_save`, keeping the record status as open while reserving the inspection number during testing [^r2][^r7][^r33]. It is a write service accessed via `POST /ll72/svc/qin_save` [^r29][^r30].

* **Required fields**: `grn_no` (string), `sample_qty` (integer) [^r7][^r31].
* **Optional fields**: `aql` (string), `result` (string, PASS/FAIL) [^r7][^r31].
* **Errors**: Common errors `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r34].
* **Source file**: `04_service_definitions/production/qin_save.yaml` [^r29].

### qin_search

Queries inspection headers to present the incoming inspection lookup list of pending goods received notes awaiting examination [^r3][^r9][^r35]. It is a read service accessed via `POST /ll72/svc/qin_search` [^r35][^r36].

* **Required fields**: None [^r37].
* **Optional fields**: `grn_no` (string, GRN NO), `sample_qty` (integer, SAMPLE QTY), `aql` (string, AQL), and `status` (string, STATUS) [^r9][^r37].
* **Errors**: Common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r39].
* **Source file**: `04_service_definitions/production/qin_search.yaml` [^r35].

## See also

* [[screen-qa-ins-01|QA-INS-01 Incoming Inspection Entry]]
* [[screen-qa-ncr-02|QA-NCR-02 Non-Conformance Report Entry]]
* [[services-prd-ncr|PRD ncr services]]
* [[screen-inv-grn-03|INV-GRN-03 Goods Receipt Note (Grn)]]
* [[screen-inv-qch-11|INV-QCH-11 Quality Hold Entry]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 35, Step by step
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 32, QA-INS-01 INCOMING INSPECTION ENTRY
[^r12]: 04_service_definitions/production/qin_get.yaml, whole file
[^r16]: 04_service_definitions/production/qin_post.yaml, whole file
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 35, Step by step
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 37, Questions users ask
[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 37, Questions users ask
[^r17]: 04_service_definitions/production/qin_post.yaml, auth
[^r24]: 04_service_definitions/production/qin_reject.yaml, auth
[^r30]: 04_service_definitions/production/qin_save.yaml, auth
[^r36]: 04_service_definitions/production/qin_search.yaml, auth
[^r23]: 04_service_definitions/production/qin_reject.yaml, service: qin_reject
[^r29]: 04_service_definitions/production/qin_save.yaml, whole file
[^r35]: 04_service_definitions/production/qin_search.yaml, service: qin_search
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 59, qin_get INCOMING INSPECTION GET
[^r13]: 04_service_definitions/production/qin_get.yaml, request.fields
[^r15]: 04_service_definitions/production/qin_get.yaml, errors
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 59, qin_post INCOMING INSPECTION POST
[^r20]: 04_service_definitions/production/qin_post.yaml, procedures
[^r21]: 04_service_definitions/production/qin_post.yaml, errors
[^r18]: 04_service_definitions/production/qin_post.yaml, request.fields
[^r22]: 04_service_definitions/production/qin_post.yaml, common_errors
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 59, qin_reject INCOMING INSPECTION REJECT
[^r27]: 04_service_definitions/production/qin_reject.yaml, procedures
[^r25]: 04_service_definitions/production/qin_reject.yaml, request.fields
[^r28]: 04_service_definitions/production/qin_reject.yaml, errors
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 59, qin_save INCOMING INSPECTION SAVE
[^r33]: 04_service_definitions/production/qin_save.yaml, procedures
[^r31]: 04_service_definitions/production/qin_save.yaml, request.fields
[^r34]: 04_service_definitions/production/qin_save.yaml, common_errors
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 35, Step by step
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 59, qin_search INCOMING INSPECTION LIST
[^r37]: 04_service_definitions/production/qin_search.yaml, request.fields
[^r39]: 04_service_definitions/production/qin_search.yaml, common_errors
