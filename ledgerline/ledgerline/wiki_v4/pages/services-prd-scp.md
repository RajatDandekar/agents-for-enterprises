---
title: "PRD scp services"
type: "service-group"
slug: "services-prd-scp"
summary: "Production scrap services in module PRD handling draft creation, scrap retrieval, and ledger posting on screen PRD-SCP-12."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/scp_get.yaml", "04_service_definitions/production/scp_post.yaml", "04_service_definitions/production/scp_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| group | services-prd-scp |
| module | PRD |
| screen | PRD-SCP-12 |
| available_since | 7.0 |
| endpoint_base | /ll72/svc/ |

The `services-prd-scp` group encompasses the production scrap operations within the PRD module invoked by screen [[screen-prd-scp-12|PRD-SCP-12 Production Scrap Entry]][^r8][^r12]. Available since Ledgerline version 7.0, these services handle querying works orders, recording draft scrap entries, retrieving scrap records, and committing final scrap transactions to manufacturing ledgers and inventory[^r1][^r7][^r12][^r17][^r24]. All endpoints require session authentication via the `X-LL-Session` header and appropriate role authorisation[^r13][^r18][^r25].

## Services

### scp_get

The `scp_get` service (PRODUCTION SCRAP GET) is a read service under module PRD that retrieves scrap details on screen [[screen-prd-scp-12|PRD-SCP-12]][^r10][^r12]. It queries the production database to verify that the specified works order is open and valid, returning order header details[^r1]. Its endpoint is `POST /ll72/svc/scp_get` and calls require an active session token in header `X-LL-Session` with an authorized role[^r13]. The response envelope contains `rc` (S | W | E), `err_cd`, `msg`, and `data`[^r15].

* **Required fields:** `scp_no` (str, SCP NO)[^r14]
* **Optional fields:** none[^r14]
* **Errors:** [[err-scp-0001|ERR-SCP-0001]] (PRODUCTION SCRAP NOT FOUND), ERR-SCP-0007 (works order closed, cancelled, on hold, not released, or invalid REASON CD), ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER)[^r5][^r10][^r16]
* **Source file:** `04_service_definitions/production/scp_get.yaml`[^r12]

### scp_save

The `scp_save` service (PRODUCTION SCRAP SAVE) is a write service linked to screen [[screen-prd-scp-12|PRD-SCP-12]] that writes scrap records using stored procedure `sp_scp_save`[^r9][^r24][^r25]. It validates mandatory data, verifies that the item is on the active works order bill of materials or is the parent assembly, and generates a scrap number (SCP NO) in draft status without altering inventory[^r2][^r7]. Its endpoint is `POST /ll72/svc/scp_save` and requires a valid session token in header `X-LL-Session`[^r25].

* **Required fields:** `wo_no` (str, WO NO), `itm_cd` (str, ITEM CD), `qty` (int, QTY), and `reason_cd` (str, REASON CD)[^r9][^r26]
* **Optional fields:** none[^r26]
* **Errors:** [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE), [[err-scp-0001|ERR-SCP-0001]] (mandatory header or line details missing), ERR-SCP-0201 (QTY MUST BE > 0 / scrap quantity exceeds permitted threshold or allocation), ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503[^r2][^r4][^r9][^r27][^r28]
* **Source file:** `04_service_definitions/production/scp_save.yaml`[^r24]

### scp_post

The `scp_post` service (PRODUCTION SCRAP POST) is a write service linked to screen [[screen-prd-scp-12|PRD-SCP-12]] executing stored procedure `sp_scp_post`[^r11][^r17][^r21]. It finalises scrap transactions by reducing works order component balances, updating scrap status, and permanently decrementing stock while issuing postings to the works order ledger and stock records[^r3][^r7][^r11]. Requests are sent to endpoint `POST /ll72/svc/scp_post` authenticated by the `X-LL-Session` header[^r18]. The response envelope returns `rc`, `err_cd`, `msg`, and `data`[^r20].

* **Required fields:** `scp_no` (str, SCP NO)[^r19]
* **Optional fields:** `comment` (str, COMMENT)[^r19]
* **Errors:** [[err-scp-0001|ERR-SCP-0001]] (PRODUCTION SCRAP NOT FOUND / missing mandatory details), ERR-SCP-0007 (PRODUCTION SCRAP NOT IN DRAFT (<status>) / works order closed, cancelled, on hold, or invalid REASON CD), ERR-SCP-0201 (scrap quantity exceeds threshold or allocation), ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER)[^r4][^r5][^r6][^r11][^r22][^r23]
* **Source file:** `04_service_definitions/production/scp_post.yaml`[^r17]

## Versions and conflicts

* **ERR-SCP-0201 definition:** The service definition for `scp_save` defines ERR-SCP-0201 as `QTY MUST BE > 0`[^r27]. Manual MAN-PRD-72 defines ERR-SCP-0201 as occurring when the scrap quantity in QTY exceeds the permitted scrap threshold or remaining allocation on the works order (kind: `contradiction`)[^r6][^r27].
* **ERR-SCP-0001 usage:** The service definitions for `scp_get` and `scp_post` map ERR-SCP-0001 strictly to `PRODUCTION SCRAP NOT FOUND`, reserving `ERR-SYS-0421` for missing mandatory fields[^r16][^r22][^r23]. Manual MAN-PRD-72 states that `scp_save` and `scp_post` raise ERR-SCP-0001 when mandatory header or line details such as WO NO or ITEM CD are missing, while MAN-SVC-72 associates it with absent scrap numbers on `scp_get` (kind: `contradiction`)[^r4][^r10][^r16][^r22].

## See also

* [[screen-prd-scp-12|PRD-SCP-12 Production Scrap Entry]]
* [[services-prd-wo|PRD wo services]]
* [[services-prd-bom|PRD bom services]]
* [[services-prd-bkf|PRD bkf services]]
* [[err-scp-0001|ERR-SCP-0001 Mandatory scrap header or line details missing]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]

## References

[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 25, PRD-SCP-12 PRODUCTION SCRAP ENTRY
[^r12]: 04_service_definitions/production/scp_get.yaml, service: scp_get
[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 56, Step by step
[^r7]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 58, Worked example: Production Scrap
[^r17]: 04_service_definitions/production/scp_post.yaml, service: scp_post
[^r24]: 04_service_definitions/production/scp_save.yaml, whole file
[^r13]: 04_service_definitions/production/scp_get.yaml, endpoint
[^r18]: 04_service_definitions/production/scp_post.yaml, auth
[^r25]: 04_service_definitions/production/scp_save.yaml, whole file
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 62, scp_get PRODUCTION SCRAP GET
[^r15]: 04_service_definitions/production/scp_get.yaml, response.envelope
[^r14]: 04_service_definitions/production/scp_get.yaml, request.fields
[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 57, Tips
[^r16]: 04_service_definitions/production/scp_get.yaml, errors
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 62, scp_save PRODUCTION SCRAP SAVE
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 56, Messages
[^r26]: 04_service_definitions/production/scp_save.yaml, request
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 56, Messages
[^r27]: 04_service_definitions/production/scp_save.yaml, errors
[^r28]: 04_service_definitions/production/scp_save.yaml, common_errors
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 62, scp_post PRODUCTION SCRAP POST
[^r21]: 04_service_definitions/production/scp_post.yaml, procedures
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 56, Step by step
[^r20]: 04_service_definitions/production/scp_post.yaml, response
[^r19]: 04_service_definitions/production/scp_post.yaml, request
[^r6]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 57, Tips
[^r22]: 04_service_definitions/production/scp_post.yaml, errors
[^r23]: 04_service_definitions/production/scp_post.yaml, common_errors
