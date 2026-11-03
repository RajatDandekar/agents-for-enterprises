---
title: "PUR sup services"
type: "service-group"
slug: "services-pur-sup"
summary: "Ledgerline PUR supplier services covering master lookup, supplier registration, certificate storage, and rate contract retrieval."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-PUR-001 Supplier Onboarding v3.1.pdf", "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/purchase/sup_cert_get.yaml", "04_service_definitions/purchase/sup_cert_upload.yaml", "04_service_definitions/purchase/sup_create.yaml", "04_service_definitions/purchase/sup_get.yaml", "04_service_definitions/purchase/sup_rate_get.yaml", "04_service_definitions/purchase/sup_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | PUR |
| Object | sup |
| Services | sup_search, sup_get, sup_create, sup_cert_get, sup_cert_upload, sup_rate_get |
| Available since | Ledgerline 7.0 |
| Endpoint prefix | /ll72/svc/ |
| Screens | PUR-SUP-01, PUR-SUP-03 |
| Status | current |

The Ledgerline PUR supplier service group provides API operations for searching, retrieving, creating, and maintaining supplier master data, compliance certificates, and item rate contracts [^r6][^r7][^r8][^r9]. These services back frontend screens including [[screen-pur-sup-01|PUR-SUP-01]] and [[screen-pur-sup-03|PUR-SUP-03]], as well as procurement workflows outlined in [[sop-pur-001|SOP-PUR-001]] [^r1][^r6][^r7]. All services authenticate through a session token passed in header `X-LL-Session` and require a user role authorized for the specific service [^r11][^r16][^r21][^r26][^r32][^r37]. Responses follow a standard envelope containing return code `rc` (`S`, `W`, or `E`), message code `err_cd`, short text `msg`, and the payload `data` [^r13][^r18][^r23][^r28][^r34][^r39].

## Services

### sup_search
* Description: Supplier enquiry read service linked to screen [[screen-pur-sup-03|PUR-SUP-03]] and available since version 7.0 [^r6][^r36].
* Endpoint: POST `/ll72/svc/sup_search` [^r37].
* Required fields: `q` (string representing supplier name pattern `NAME LIKE`) [^r6][^r38].
* Optional fields: None [^r38].
* Errors: [[errors-sup|ERR-SEC-0001]] (ACCESS DENIED), ERR-SYS-0421 (`<FIELD> MANDATORY`), ERR-SYS-0422 (`UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>`), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r3][^r40].
* Source file: `04_service_definitions/purchase/sup_search.yaml` [^r36].

### sup_get
* Description: Read service titled `SUPPLIER MASTER GET` used to retrieve supplier master data, available since version 7.0 [^r6][^r25].
* Endpoint: POST `/ll72/svc/sup_get` [^r25].
* Required fields: `sup_cd` (SUP CD, string) [^r6][^r27].
* Optional fields: None [^r27].
* Errors: [[err-sup-0030|ERR-SUP-0030]] (SUPPLIER NOT FOUND), [[errors-sup|ERR-SEC-0001]] (ACCESS DENIED), ERR-SYS-0421 (`<FIELD> MANDATORY`), ERR-SYS-0422 (`UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>`), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r3][^r4][^r29][^r30].
* Source file: `04_service_definitions/purchase/sup_get.yaml` [^r25].

### sup_create
* Description: Write service titled `SUPPLIER CREATE` invoked from screen [[screen-pur-sup-01|PUR-SUP-01]] to register new supplier records, available since version 7.0 [^r7][^r20]. Upon creation, it generates a supplier code and displays status message `SUPPLIER <code> CREATED` [^r1]. Duplicate supplier records are checked solely by VAT number; records entered without a VAT number are never checked for duplicates [^r24].
* Endpoint: POST `/ll72/svc/sup_create` [^r20].
* Required fields: `name` (SUP NAME, string), `city` (CITY, string), and `state` (COUNTRY CD (2), string) [^r1][^r7][^r22].
* Optional fields: `vat_no` (VAT number, string) and `pt_cd` (PAY TERM CD, string) [^r1][^r7][^r22].
* Errors: [[err-sup-0118|ERR-SUP-0118]] (VAT NO ALREADY REGISTERED), [[errors-sup|ERR-SEC-0001]] (ACCESS DENIED), ERR-SYS-0421, and ERR-SYS-0422 [^r3][^r5][^r7][^r24].
* Source file: `04_service_definitions/purchase/sup_create.yaml` [^r20].

### sup_cert_get
* Description: Read service titled `SUPPLIER CERT LIST` that lists compliance certificates attached to a supplier, available since version 7.0 [^r8][^r10].
* Endpoint: POST `/ll72/svc/sup_cert_get` [^r10].
* Required fields: `sup_cd` (supplier code, string) [^r8][^r12].
* Optional fields: None [^r12].
* Errors: [[errors-sup|ERR-SEC-0001]] (ACCESS DENIED), ERR-SYS-0421 (`<FIELD> MANDATORY`), ERR-SYS-0422 (`UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>`), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r3][^r14].
* Source file: `04_service_definitions/purchase/sup_cert_get.yaml` [^r10].

### sup_cert_upload
* Description: Write service used to upload supplier compliance certificates, such as UN38.3, available since version 7.0 without a dedicated screen [^r2][^r15]. It returns message `CERT SAVED` upon completion, stores `cert_type` in uppercase, and does not validate certificate validity dates [^r2][^r19].
* Endpoint: POST `/ll72/svc/sup_cert_upload` [^r15].
* Required fields: `sup_cd` (string), `cert_type` (string), `doc_ref` (string), and `valid_to` (date) [^r8][^r17].
* Optional fields: None [^r17].
* Errors: [[err-sup-0030|ERR-SUP-0030]] (SUPPLIER NOT FOUND), [[errors-sup|ERR-SEC-0001]] (ACCESS DENIED), ERR-SYS-0421, and ERR-SYS-0422 [^r3][^r4][^r8].
* Source file: `04_service_definitions/purchase/sup_cert_upload.yaml` [^r15].

### sup_rate_get
* Description: Read service titled `RATE CONTRACT GET` to retrieve rate contract details for a specific supplier and item combination, available since version 7.0 without a screen [^r9][^r31].
* Endpoint: POST `/ll72/svc/sup_rate_get` [^r32].
* Required fields: `sup_cd` (SUP CD, string) and `itm_cd` (ITEM CD, string) [^r9][^r33].
* Optional fields: None [^r33].
* Errors: [[errors-sup|ERR-SEC-0001]] (ACCESS DENIED), ERR-SYS-0421 (`<FIELD> MANDATORY`), ERR-SYS-0422 (`UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>`), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r3][^r35].
* Source file: `04_service_definitions/purchase/sup_rate_get.yaml` [^r31].

## See also
* [[screen-pur-sup-01|PUR-SUP-01 Supplier Master Create]]
* [[screen-pur-sup-03|PUR-SUP-03 Supplier Enquiry]]
* [[sop-pur-001|SOP-PUR-001 Supplier Onboarding]]
* [[errors-sup|ERR-SUP Error Codes]]
* [[err-sup-0030|ERR-SUP-0030]]
* [[err-sup-0118|ERR-SUP-0118 VAT number already registered]]
* [[services-pur-po|PUR po services]]
* [[services-pur-pr|PUR pr services]]
* [[services-pur-bud|PUR bud services]]
* [[services-pur-stk|PUR stk services]]
* [[services-ap-sup|AP sup services]]

## References

[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 2, §2. Purchase services
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 2, §2. Purchase services
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 3, §2. Purchase services
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 3, §2. Purchase services
[^r1]: 02_procedures/SOP-PUR-001 Supplier Onboarding v3.1.pdf, p. 3, §5. Procedure
[^r11]: 04_service_definitions/purchase/sup_cert_get.yaml, auth
[^r16]: 04_service_definitions/purchase/sup_cert_upload.yaml, auth
[^r21]: 04_service_definitions/purchase/sup_create.yaml, auth
[^r26]: 04_service_definitions/purchase/sup_get.yaml, auth
[^r32]: 04_service_definitions/purchase/sup_rate_get.yaml, auth
[^r37]: 04_service_definitions/purchase/sup_search.yaml, endpoint
[^r13]: 04_service_definitions/purchase/sup_cert_get.yaml, response
[^r18]: 04_service_definitions/purchase/sup_cert_upload.yaml, response.envelope
[^r23]: 04_service_definitions/purchase/sup_create.yaml, response.envelope
[^r28]: 04_service_definitions/purchase/sup_get.yaml, response
[^r34]: 04_service_definitions/purchase/sup_rate_get.yaml, response.envelope
[^r39]: 04_service_definitions/purchase/sup_search.yaml, response
[^r36]: 04_service_definitions/purchase/sup_search.yaml, service: sup_search
[^r38]: 04_service_definitions/purchase/sup_search.yaml, request
[^r3]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 23, ERR-SEC-0001 ACCESS DENIED
[^r40]: 04_service_definitions/purchase/sup_search.yaml, common_errors
[^r25]: 04_service_definitions/purchase/sup_get.yaml, service: sup_get
[^r27]: 04_service_definitions/purchase/sup_get.yaml, request
[^r4]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 25, ERR-SUP-0030 SUPPLIER NOT FOUND
[^r29]: 04_service_definitions/purchase/sup_get.yaml, errors
[^r30]: 04_service_definitions/purchase/sup_get.yaml, common_errors
[^r20]: 04_service_definitions/purchase/sup_create.yaml, service: sup_create
[^r24]: 04_service_definitions/purchase/sup_create.yaml, notes
[^r22]: 04_service_definitions/purchase/sup_create.yaml, request.fields
[^r5]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 25, ERR-SUP-0118 VAT NO ALREADY REGISTERED
[^r10]: 04_service_definitions/purchase/sup_cert_get.yaml, service: sup_cert_get
[^r12]: 04_service_definitions/purchase/sup_cert_get.yaml, request
[^r14]: 04_service_definitions/purchase/sup_cert_get.yaml, common_errors
[^r2]: 02_procedures/SOP-PUR-001 Supplier Onboarding v3.1.pdf, p. 3, §5. Procedure
[^r15]: 04_service_definitions/purchase/sup_cert_upload.yaml, service: sup_cert_upload
[^r19]: 04_service_definitions/purchase/sup_cert_upload.yaml, notes
[^r17]: 04_service_definitions/purchase/sup_cert_upload.yaml, request.fields
[^r31]: 04_service_definitions/purchase/sup_rate_get.yaml, whole file
[^r33]: 04_service_definitions/purchase/sup_rate_get.yaml, request.fields
[^r35]: 04_service_definitions/purchase/sup_rate_get.yaml, common_errors
