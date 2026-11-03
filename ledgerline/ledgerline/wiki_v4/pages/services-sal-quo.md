---
title: "SAL quo services"
type: "service-group"
slug: "services-sal-quo"
summary: "Ledgerline SAL quotation service group covering quotation creation, retrieval, listing, conversion to sales orders, and cancellation."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/sales/quo_cancel.yaml", "04_service_definitions/sales/quo_convert.yaml", "04_service_definitions/sales/quo_get.yaml", "04_service_definitions/sales/quo_save.yaml", "04_service_definitions/sales/quo_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| group | services-sal-quo |
| module | SAL |
| screen | SAL-QUO-02 |
| version | Ledgerline ERP 7.2 (since 7.0) |
| services | quo_save, quo_get, quo_search, quo_convert, quo_cancel |
| status | current |

The `sal-quo` service group provides backend services for managing sales quotations within Ledgerline ERP's SAL module [^r11][^r26]. Exposed through the user interface on [[screen-sal-quo-02|SAL-QUO-02 Quotation Entry]], the group enables staff to generate new quotations, retrieve or search existing records, convert accepted quotes into sales orders, and cancel lapsed or rejected quotes [^r1][^r2][^r3][^r4][^r5]. All endpoints operate over HTTP POST, require session token authentication via the `X-LL-Session` header, and enforce role-based authorization [^r12][^r17][^r22][^r27][^r33].

## Services

### quo_save

The `quo_save` write service creates new sales quotations on [[screen-sal-quo-02|SAL-QUO-02]] by executing database procedure `sp_quo_save` [^r5][^r6][^r26][^r29]. The service validates header and line data, assigns a sequential quote number, and initializes the record with an open status [^r1]. It has been available since Ledgerline version 7.0 and is mapped to the endpoint `POST /ll72/svc/quo_save` with keyboard shortcut F8 [^r5][^r26].

* **Required fields:** `cust_cd` (string, CUST CD), `itm_cd` (string, ITEM CD), `qty` (integer, QTY), `price` (float, PRICE), and `valid_to` (date, VALID TO) [^r6][^r28].
* **Optional fields:** None [^r6][^r28].
* **Errors:** Specific business errors include `ERR-QUO-0201` ("QTY MUST BE > 0") from [[errors-quo|ERR-QUO quotation error codes]] and [[err-itm-0011|ERR-ITM-0011]] ("ITEM NOT FOUND OR INACTIVE"), alongside common infrastructure errors `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r6][^r30][^r31].
* **Source file:** `04_service_definitions/sales/quo_save.yaml` [^r26][^r27][^r28][^r29][^r30][^r31].

### quo_get

The `quo_get` read service retrieves sales quotations using a specific quotation number via endpoint `POST /ll72/svc/quo_get`, mapped to button Get (F3) on screen SAL-QUO-02 [^r2][^r5][^r7][^r21]. It returns a standard response envelope containing return code `rc` (`S | W | E`), error code `err_cd`, short text message `msg` in capitals, and the result record in `data` [^r24].

* **Required fields:** `quo_no` (string, QUO NO) [^r7][^r23].
* **Optional fields:** None [^r7][^r23].
* **Errors:** Business error `ERR-QUO-0001` (QUOTATION NOT FOUND), plus common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r7][^r25].
* **Source file:** `04_service_definitions/sales/quo_get.yaml` [^r21][^r22][^r23][^r24][^r25].

### quo_search

The `quo_search` read service lists historical and active sales quotations using search filters and is bound to Search (F2/Enter) on screen SAL-QUO-02 via endpoint `POST /ll72/svc/quo_search` [^r2][^r5][^r8][^r32]. Responses are returned in the standard envelope structure with fields `rc`, `err_cd`, `msg`, and `data` [^r35].

* **Required fields:** None [^r34].
* **Optional fields:** `cust_cd` (string), `itm_cd` (string), `qty` (integer), and `status` (string) [^r8][^r34].
* **Errors:** Business errors `ERR-QUO-0201` ("QTY MUST BE > 0") and [[err-itm-0011|ERR-ITM-0011]] ("ITEM NOT FOUND OR INACTIVE"), as well as common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r8][^r36][^r37].
* **Source file:** `04_service_definitions/sales/quo_search.yaml` [^r32][^r33][^r34][^r35][^r36][^r37].

### quo_convert

The `quo_convert` write service executes database procedure `sp_quo_convert` via endpoint `POST /ll72/svc/quo_convert` to transfer quotation lines into sales order tables and close the quotation [^r3][^r9][^r16][^r17]. It is accessible from the Convert button on screen SAL-QUO-02 [^r5][^r9].

* **Required fields:** `quo_no` (string, QUO NO) [^r9][^r18].
* **Optional fields:** `comment` (string, COMMENT) [^r9][^r18].
* **Errors:** Service-specific error `ERR-QUO-0001` (QUOTATION NOT FOUND), in addition to common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r20].
* **Source file:** `04_service_definitions/sales/quo_convert.yaml` [^r16][^r17][^r18][^r19][^r20].

### quo_cancel

The `quo_cancel` write service executes database procedure `sp_quo_cancel` via endpoint `POST /ll72/svc/quo_cancel` to cancel a quotation and lock all its fields, bound to Cancel (Shift+F8) on screen SAL-QUO-02 [^r4][^r5][^r10][^r11][^r12][^r14].

* **Required fields:** `quo_no` (string, QUO NO) and `reason` (string, REASON) [^r4][^r10][^r13].
* **Optional fields:** None [^r10][^r13].
* **Errors:** Business errors `ERR-QUO-0001` and `ERR-QUO-0801` [^r10].
* **Source file:** `04_service_definitions/sales/quo_cancel.yaml` [^r11][^r12][^r13][^r14][^r15].

## Versions and conflicts

* Service definition file `quo_convert.yaml` specifies `ERR-QUO-0001` along with common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503`, whereas manual `MAN-SVC-72` lists `ERR-ITM-0011` or `ERR-QUO-0001` [^r9][^r20]. (kind: `contradiction`)
* Service definition file `quo_search.yaml` defines both `ERR-QUO-0201` and `ERR-ITM-0011` as business errors, whereas manual `MAN-SVC-72` only lists `ERR-QUO-0201` [^r8][^r36]. (kind: `contradiction`)

## See also

* [[screen-sal-quo-02|SAL-QUO-02 Quotation Entry]]
* [[screen-sal-so-01|SAL-SO-01 Sales Order]]
* [[services-sal-so|SAL so services]]
* [[errors-quo|ERR-QUO quotation error codes]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]

## References

[^r11]: 04_service_definitions/sales/quo_cancel.yaml, service: quo_cancel
[^r26]: 04_service_definitions/sales/quo_save.yaml, service: quo_save
[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 12, Raising a new quotation
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 12, Retrieving an existing quotation
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 13, Converting a quotation to a firm order
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 13, Cancelling or recording a lapsed quotation
[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 38, SAL-QUO-02 QUOTATION ENTRY
[^r12]: 04_service_definitions/sales/quo_cancel.yaml, auth
[^r17]: 04_service_definitions/sales/quo_convert.yaml, endpoint
[^r22]: 04_service_definitions/sales/quo_get.yaml, auth
[^r27]: 04_service_definitions/sales/quo_save.yaml, auth
[^r33]: 04_service_definitions/sales/quo_search.yaml, auth
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 41, quo_save QUOTATION SAVE
[^r29]: 04_service_definitions/sales/quo_save.yaml, response.envelope
[^r28]: 04_service_definitions/sales/quo_save.yaml, request.fields
[^r30]: 04_service_definitions/sales/quo_save.yaml, errors
[^r31]: 04_service_definitions/sales/quo_save.yaml, common_errors
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 41, quo_get QUOTATION GET
[^r21]: 04_service_definitions/sales/quo_get.yaml, whole file
[^r24]: 04_service_definitions/sales/quo_get.yaml, response.envelope
[^r23]: 04_service_definitions/sales/quo_get.yaml, request.fields
[^r25]: 04_service_definitions/sales/quo_get.yaml, errors
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 41, quo_search QUOTATION LIST
[^r32]: 04_service_definitions/sales/quo_search.yaml, service: quo_search
[^r35]: 04_service_definitions/sales/quo_search.yaml, response
[^r34]: 04_service_definitions/sales/quo_search.yaml, request
[^r36]: 04_service_definitions/sales/quo_search.yaml, errors
[^r37]: 04_service_definitions/sales/quo_search.yaml, common_errors
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 42, quo_convert QUOTATION CONVERT
[^r16]: 04_service_definitions/sales/quo_convert.yaml, service: quo_convert
[^r18]: 04_service_definitions/sales/quo_convert.yaml, request.fields
[^r20]: 04_service_definitions/sales/quo_convert.yaml, errors
[^r19]: 04_service_definitions/sales/quo_convert.yaml, response.envelope
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 42, quo_cancel QUOTATION CANCEL
[^r14]: 04_service_definitions/sales/quo_cancel.yaml, procedures
[^r13]: 04_service_definitions/sales/quo_cancel.yaml, request.fields
[^r15]: 04_service_definitions/sales/quo_cancel.yaml, response.envelope
