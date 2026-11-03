---
title: "PRD bkf services"
type: "service-group"
slug: "services-prd-bkf"
summary: "Ledgerline production backflush services providing work order retrieval, posting, and reversal functions."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/bkf_get.yaml", "04_service_definitions/production/bkf_post.yaml", "04_service_definitions/production/bkf_reverse.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | PRD |
| Object | bkf |
| Screen | PRD-BKF-08 |
| Services | bkf_get, bkf_post, bkf_reverse |
| Introduced | Ledgerline 7.0 |
| Status | Current |

The PRD bkf service group controls production backflushing in Ledgerline against work order records [^r5][^r9]. It provides services to query work order details and bill of materials components, post finished goods output while consuming line store inventory, and reverse posted backflush transactions [^r1][^r2][^r3]. All services operate under module PRD, interface directly with screen [[screen-prd-bkf-08|PRD-BKF-08]], and require session-token authentication [^r5][^r9][^r10].

## Services

### bkf_get

The bkf_get service (BACKFLUSH GET) is a read service in module PRD available since Ledgerline version 7.0 and associated with screen [[screen-prd-bkf-08|PRD-BKF-08]] [^r9]. It queries the database to verify the works order header, check operational status, and populate open and component usage quantities [^r1]. The service is exposed via endpoint POST `/ll72/svc/bkf_get` and requires an active session token in the `X-LL-Session` header with an authorised role [^r10]. It is invoked on screen [[screen-prd-bkf-08|PRD-BKF-08]] via key F3 [^r5].

* **Required fields**: `wo_no` (string) [^r7][^r11].
* **Optional fields**: None [^r11].
* **Errors**: [[err-bkf-0001|ERR-BKF-0001]] (BACKFLUSH NOT FOUND), ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (`<FIELD>` MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD `<FIELD>` / BAD VALUE FOR `<FIELD>`), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r7][^r13].
* **Response**: Envelope returning `rc` (S | W | E), `err_cd`, `msg`, and `data` [^r12].
* **Source file**: `04_service_definitions/production/bkf_get.yaml` [^r9].

### bkf_post

The bkf_post service (BACKFLUSH POST) is a write service in module PRD introduced in version 7.0 that calls database stored procedure `sp_bkf_post` via endpoint POST `/ll72/svc/bkf_post` [^r6][^r14]. It verifies component stock levels across line stores, immediately updates inventory ledgers, and generates a finished goods movement ticket [^r2]. The service is mapped to key F9 on screen [[screen-prd-bkf-08|PRD-BKF-08]] and requires session token authentication in the `X-LL-Session` header [^r5][^r15].

* **Required fields**: `wo_no` (string) [^r6][^r16].
* **Optional fields**: `comment` (string) [^r6][^r16].
* **Errors**: [[err-bkf-0001|ERR-BKF-0001]] (BACKFLUSH NOT FOUND), [[err-bkf-0007|ERR-BKF-0007]] (BACKFLUSH NOT IN DRAFT (`<status>`) / component inventory balances at the line warehouse insufficient to meet bill of materials requirements), ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r4][^r6][^r18][^r19].
* **Response**: Envelope returning `rc` ('S | W | E'), `err_cd`, `msg`, and `data` [^r17].
* **Source file**: `04_service_definitions/production/bkf_post.yaml` [^r14].

### bkf_reverse

The bkf_reverse service (BACKFLUSH REVERSE) is a write-kind service in module PRD available since Ledgerline 7.0 that executes stored procedure `sp_bkf_reverse` via endpoint POST `/ll72/svc/bkf_reverse` [^r8][^r20][^r21][^r24]. It cancels the finished goods booking, restores lineside component stock at standard cost, and reverses absorption journals in the general ledger [^r3]. It is executed from screen [[screen-prd-bkf-08|PRD-BKF-08]] and requires session authentication using header `X-LL-Session` [^r5][^r21].

* **Required fields**: `wo_no` (string) [^r8][^r22].
* **Optional fields**: `reason` (string) [^r8][^r22].
* **Errors**: [[err-bkf-0001|ERR-BKF-0001]] (BACKFLUSH NOT FOUND), ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (`<FIELD>` MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD `<FIELD>` / BAD VALUE FOR `<FIELD>`), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r24][^r25].
* **Response**: Envelope returning `rc` ('S | W | E'), `err_cd`, `msg`, and `data` [^r23].
* **Source file**: `04_service_definitions/production/bkf_reverse.yaml` [^r20].

## See also

* [[screen-prd-bkf-08|PRD-BKF-08 Backflush]]
* [[err-bkf-0001|ERR-BKF-0001: Works order invalid or not in valid state for backflush]]
* [[err-bkf-0007|ERR-BKF-0007: Component inventory shortage during backflush]]
* [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]
* [[services-prd-wo|PRD wo services]]
* [[screen-prd-bom-02|PRD-BOM-02 Bill Of Materials]]
* [[services-prd-bom|PRD bom services]]

## References

[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 21, PRD-BKF-08 BACKFLUSH
[^r9]: 04_service_definitions/production/bkf_get.yaml, service: bkf_get
[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 16, Retrieving the works order details
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 16, Adding narrative and posting the transaction
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 17, Messages
[^r10]: 04_service_definitions/production/bkf_get.yaml, endpoint
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 56, §6. Production services
[^r11]: 04_service_definitions/production/bkf_get.yaml, request
[^r13]: 04_service_definitions/production/bkf_get.yaml, errors
[^r12]: 04_service_definitions/production/bkf_get.yaml, response
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 55, §6. Production services
[^r14]: 04_service_definitions/production/bkf_post.yaml, service: bkf_post
[^r15]: 04_service_definitions/production/bkf_post.yaml, auth
[^r16]: 04_service_definitions/production/bkf_post.yaml, request.fields
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 17, Messages
[^r18]: 04_service_definitions/production/bkf_post.yaml, errors
[^r19]: 04_service_definitions/production/bkf_post.yaml, common_errors
[^r17]: 04_service_definitions/production/bkf_post.yaml, response.envelope
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 56, §6. Production services
[^r20]: 04_service_definitions/production/bkf_reverse.yaml, service
[^r21]: 04_service_definitions/production/bkf_reverse.yaml, endpoint
[^r24]: 04_service_definitions/production/bkf_reverse.yaml, errors
[^r22]: 04_service_definitions/production/bkf_reverse.yaml, request.fields
[^r25]: 04_service_definitions/production/bkf_reverse.yaml, common_errors
[^r23]: 04_service_definitions/production/bkf_reverse.yaml, response.envelope
