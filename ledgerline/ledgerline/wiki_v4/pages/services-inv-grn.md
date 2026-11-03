---
title: "INV grn services"
type: "service-group"
slug: "services-inv-grn"
summary: "Inventory module services for creating, retrieving, and listing goods receipt notes against released purchase orders on INV-GRN-03."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/inventory/grn_get.yaml", "04_service_definitions/inventory/grn_save.yaml", "04_service_definitions/inventory/grn_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | INV |
| Object | grn |
| Services | grn_save, grn_get, grn_search |
| Primary screen | INV-GRN-03 |
| Introduced | 7.0 |
| Transport | POST /ll72/svc/* |

The goods receipt note services in the Inventory module manage the receipt of purchased goods against released purchase orders [^r2][^r11][^r17]. They provide endpoints to save new receipts, retrieve individual goods receipt records by receipt number, and search receipts by purchase order [^r3][^r4][^r5]. All transactions validate purchase order status and ensure received quantities do not exceed outstanding order balances [^r1][^r2][^r15].

## Services

### grn_save

Service `grn_save` is a write service titled GOODS RECEIPT SAVE, available since version 7.0 and accessed via endpoint `POST /ll72/svc/grn_save` [^r11]. It is tied to screen [[screen-inv-grn-03|INV-GRN-03]] to record goods receipts against purchase orders [^r2][^r3][^r11]. Authentication requires a session token in header `X-LL-Session` and an authorised user role [^r12]. Only a released purchase order (RL) can be received, and receiving the full balance closes the purchase order (CL) [^r17].

* **Required fields:** `po_no` (string, PO NO), `qty` (integer, QTY RECD) [^r3][^r13].
* **Optional fields:** `whs_cd` (string, WHS CD), `remarks` (string, REMARKS) [^r13].
* **Response envelope:** `rc` ('S | W | E'), `err_cd` ('error code when rc is E'), `msg` ('short message in capitals'), and `data` ('result') [^r14].
* **Errors:** ERR-PO-0001 (PO NOT FOUND), [[err-grn-0102|ERR-GRN-0102]] (PO NOT RELEASED (<status>)), ERR-GRN-0105 (PO ALREADY FULLY RECEIVED), ERR-GRN-0201 (QTY MUST BE > 0), [[err-grn-0204|ERR-GRN-0204]] (QTY EXCEEDS PO BALANCE (<qty>)) [^r1][^r3][^r15].
* **Common errors:** ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r16].
* **Source file:** `04_service_definitions/inventory/grn_save.yaml` [^r11].

### grn_get

Service `grn_get` is a read service in module INV introduced in version 7.0, available at endpoint `POST /ll72/svc/grn_get` [^r6]. It retrieves an existing goods receipt record [^r4]. Requests require an `X-LL-Session` header and a role with execution permission [^r7].

* **Required fields:** `grn_no` (string, GRN NO) [^r8].
* **Optional fields:** None [^r8].
* **Response envelope:** `rc` ('S | W | E'), `err_cd` ('error code when rc is E'), `msg` ('short message in capitals'), and `data` ('result') [^r9].
* **Errors:** ERR-GRN-0001 (GRN not found) [^r4][^r10].
* **Common errors:** ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r10].
* **Source file:** `04_service_definitions/inventory/grn_get.yaml` [^r6].

### grn_search

Service `grn_search` is a read service in module INV titled GOODS RECEIPT LIST, available since Ledgerline 7.0 [^r18]. It runs at endpoint `POST /ll72/svc/grn_search` and requires a valid session token in header `X-LL-Session` with proper role permissions [^r19]. It lists goods receipt records matching query criteria [^r5].

* **Required fields:** None [^r20].
* **Optional fields:** `po_no` (string, PO NO) [^r5][^r20].
* **Response envelope:** `rc` ('S | W | E'), `err_cd`, `msg` in capitals, and `data` containing the result [^r21].
* **Errors:** None specific beyond common errors [^r22].
* **Common errors:** ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r22].
* **Source file:** `04_service_definitions/inventory/grn_search.yaml` [^r18].

## See also

* [[screen-inv-grn-03|INV-GRN-03 Goods Receipt Note (Grn)]]
* [[services-pur-po|PUR po services]]
* [[err-grn-0102|ERR-GRN-0102 Purchase order not released]]
* [[err-grn-0204|ERR-GRN-0204 Over-receipt exceeds order balance]]
* [[services-inv-rtv|INV rtv services]]
* [[services-inv-txf|INV txf services]]

## References

[^r2]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 14, INV-GRN-03 GOODS RECEIPT NOTE (GRN)
[^r11]: 04_service_definitions/inventory/grn_save.yaml, whole file
[^r17]: 04_service_definitions/inventory/grn_save.yaml, notes
[^r3]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 8, §3. Inventory services
[^r4]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 9, grn_get GOODS RECEIPT GET
[^r5]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 9, grn_search GOODS RECEIPT LIST
[^r1]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 10
[^r15]: 04_service_definitions/inventory/grn_save.yaml, errors
[^r12]: 04_service_definitions/inventory/grn_save.yaml, auth
[^r13]: 04_service_definitions/inventory/grn_save.yaml, request.fields
[^r14]: 04_service_definitions/inventory/grn_save.yaml, response.envelope
[^r16]: 04_service_definitions/inventory/grn_save.yaml, common_errors
[^r6]: 04_service_definitions/inventory/grn_get.yaml, service: grn_get
[^r7]: 04_service_definitions/inventory/grn_get.yaml, auth
[^r8]: 04_service_definitions/inventory/grn_get.yaml, request.fields
[^r9]: 04_service_definitions/inventory/grn_get.yaml, response.envelope
[^r10]: 04_service_definitions/inventory/grn_get.yaml, errors
[^r18]: 04_service_definitions/inventory/grn_search.yaml, whole file
[^r19]: 04_service_definitions/inventory/grn_search.yaml, whole file
[^r20]: 04_service_definitions/inventory/grn_search.yaml, request.fields
[^r21]: 04_service_definitions/inventory/grn_search.yaml, response.envelope
[^r22]: 04_service_definitions/inventory/grn_search.yaml, common_errors
