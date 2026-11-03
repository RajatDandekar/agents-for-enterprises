---
title: "PRD ncr services"
type: "service-group"
slug: "services-prd-ncr"
summary: "PRD module services for non-conformance records, supporting report creation, lookup, search, and closure from screen QA-NCR-02."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/ncr_close.yaml", "04_service_definitions/production/ncr_get.yaml", "04_service_definitions/production/ncr_save.yaml", "04_service_definitions/production/ncr_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | PRD |
| Screen | QA-NCR-02 |
| Services | ncr_save, ncr_get, ncr_search, ncr_close |
| Since | Ledgerline 7.0 |
| Status | current |

The PRD non-conformance record services support logging, searching, retrieving, and closing defect records in Ledgerline ERP [^r5][^r10][^r21]. Operating against screen [[screen-qa-ncr-02|QA-NCR-02]], these services handle defect reporting, status transitions, and associated inventory quality holds [^r1][^r4][^r5]. All four services execute over HTTP POST endpoints requiring session token authentication and appropriate role authorisation [^r10][^r11][^r17][^r22][^r29].

## Services

### ncr_save

The `ncr_save` service is a write service in the PRD module available since Ledgerline 7.0 that runs stored procedure `sp_ncr_save` via endpoint `POST /ll72/svc/ncr_save` from screen [[screen-qa-ncr-02|QA-NCR-02]] [^r6][^r21][^r22][^r24]. It validates header and defect data, assigns a sequential NCR NO, sets STATUS to open, and places an inventory hold on rejected parts [^r1]. Callers must authenticate using a session token in header `X-LL-Session` with an authorised user role [^r22]. The service response returns standard envelope fields `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r25].

* **Required fields:** `itm_cd` (string), `defect_cd` (string), `qty` (integer), `descr` (string) [^r6][^r23]
* **Optional fields:** `grn_no` (string) [^r6][^r23]
* **Errors:** `ERR-NCR-0201` (QTY MUST BE > 0), [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE), `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r26][^r27]
* **Source file:** `04_service_definitions/production/ncr_save.yaml` [^r21]

### ncr_get

The `ncr_get` service is a PRD read service available since Ledgerline 7.0 that retrieves an existing non-conformance record on screen [[screen-qa-ncr-02|QA-NCR-02]] via endpoint `POST /ll72/svc/ncr_get` [^r5][^r7][^r16][^r17]. It retrieves records by NCR NO into fields GRN NO, ITEM CD, DEFECT CD, QTY, DESCRIPTION, STATUS, and COMMENT [^r2]. The caller must supply a session token in header `X-LL-Session` and have a role permitted to run the service [^r17]. Responses use the envelope structure with `rc`, `err_cd`, `msg`, and `data` [^r19].

* **Required fields:** `ncr_no` (string) [^r7][^r18]
* **Optional fields:** none [^r18]
* **Errors:** `ERR-NCR-0001` (NON-CONFORMANCE REPORT NOT FOUND), `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r19][^r20]
* **Source file:** `04_service_definitions/production/ncr_get.yaml` [^r16]

### ncr_search

The `ncr_search` service is a read service (NON-CONFORMANCE REPORT LIST) introduced in Ledgerline 7.0 that executes search queries across non-conformance records on screen [[screen-qa-ncr-02|QA-NCR-02]] via endpoint `POST /ll72/svc/ncr_search` [^r3][^r5][^r8][^r28][^r29]. It requires a valid session token in header `X-LL-Session` and appropriate role permission [^r29]. The response envelope returns `rc`, `err_cd`, `msg`, and `data` [^r31].

* **Required fields:** none [^r30]
* **Optional fields:** `grn_no` (string), `itm_cd` (string), `defect_cd` (string), `status` (string) [^r8][^r30]
* **Errors:** [[err-itm-0011|ERR-ITM-0011]], `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, `ERR-SYS-0503` [^r31]
* **Source file:** `04_service_definitions/production/ncr_search.yaml` [^r28]

### ncr_close

The `ncr_close` service is a PRD write service introduced in Ledgerline 7.0 that invokes stored procedure `sp_ncr_close` via endpoint `POST /ll72/svc/ncr_close` from screen [[screen-qa-ncr-02|QA-NCR-02]] [^r9][^r10]. It releases pending quality holds where applicable, appends resolution notes from COMMENT, and sets STATUS to closed [^r4]. Requests require header `X-LL-Session` and role authorisation [^r11]. Responses provide `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r13].

* **Required fields:** `ncr_no` (string) [^r9][^r12]
* **Optional fields:** `comment` (string) [^r9][^r12]
* **Errors:** `ERR-NCR-0001` (NON-CONFORMANCE REPORT NOT FOUND), `ERR-NCR-0801` (NON-CONFORMANCE REPORT CLOSED (<status>)), `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r9][^r14][^r15]
* **Source file:** `04_service_definitions/production/ncr_close.yaml` [^r10]

## See also

* [[screen-qa-ncr-02|QA-NCR-02 Non-Conformance Report Entry]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[screen-inv-qch-11|INV-QCH-11 Quality Hold Entry]]
* [[services-prd-qin|PRD qin services]]

## References

[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 32, QA-NCR-02 NON-CONFORMANCE REPORT ENTRY
[^r10]: 04_service_definitions/production/ncr_close.yaml, service
[^r21]: 04_service_definitions/production/ncr_save.yaml, service: ncr_save
[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 38, Raising a new non-conformance record
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 39, Closing an existing record
[^r11]: 04_service_definitions/production/ncr_close.yaml, auth
[^r17]: 04_service_definitions/production/ncr_get.yaml, endpoint / auth
[^r22]: 04_service_definitions/production/ncr_save.yaml, endpoint
[^r29]: 04_service_definitions/production/ncr_search.yaml, auth
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 59, ncr_save NON-CONFORMANCE REPORT SAVE
[^r24]: 04_service_definitions/production/ncr_save.yaml, procedures
[^r25]: 04_service_definitions/production/ncr_save.yaml, response.envelope
[^r23]: 04_service_definitions/production/ncr_save.yaml, request.fields
[^r26]: 04_service_definitions/production/ncr_save.yaml, errors
[^r27]: 04_service_definitions/production/ncr_save.yaml, common_errors
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 60, ncr_get NON-CONFORMANCE REPORT GET
[^r16]: 04_service_definitions/production/ncr_get.yaml, ncr_get
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 39, Retrieving an existing record
[^r19]: 04_service_definitions/production/ncr_get.yaml, errors
[^r18]: 04_service_definitions/production/ncr_get.yaml, request.fields
[^r20]: 04_service_definitions/production/ncr_get.yaml, common_errors
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 39, Searching for records
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 60, ncr_search NON-CONFORMANCE REPORT LIST
[^r28]: 04_service_definitions/production/ncr_search.yaml, service: ncr_search
[^r31]: 04_service_definitions/production/ncr_search.yaml, errors
[^r30]: 04_service_definitions/production/ncr_search.yaml, request.fields
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 60, ncr_close NON-CONFORMANCE REPORT CLOSE
[^r13]: 04_service_definitions/production/ncr_close.yaml, response.envelope
[^r12]: 04_service_definitions/production/ncr_close.yaml, request.fields
[^r14]: 04_service_definitions/production/ncr_close.yaml, errors
[^r15]: 04_service_definitions/production/ncr_close.yaml, common_errors
