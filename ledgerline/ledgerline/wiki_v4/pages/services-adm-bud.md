---
title: "ADM bud services"
type: "service-group"
slug: "services-adm-bud"
summary: "Ledgerline ADM services for budget save, query, and transfer operations linked to screen FIN-BUD-02."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/admin/bud_query.yaml", "04_service_definitions/admin/bud_save.yaml", "04_service_definitions/admin/bud_transfer.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | ADM |
| Object | bud |
| Screen | FIN-BUD-02 |
| Version | Ledgerline 7.2 (available since 7.0) |
| Endpoint prefix | POST /ll72/svc/ |
| Header | X-LL-Session |
| Status | current |

The ADM bud service group comprises the Ledgerline ERP 7.2 administrative services managing budget entry, retrieval, and reallocation on screen [[screen-fin-bud-02|FIN-BUD-02]][^r1][^r4][^r14]. Introduced in Ledgerline version 7.0, these services execute underlying stored procedures to query or update cost-centre budget balances[^r1][^r4][^r9][^r14]. All endpoints require role-based authorisation and session authentication via the `X-LL-Session` request header[^r5][^r10][^r15].

## Services

### bud_query

The `bud_query` read service retrieves existing budget data associated with screen [[screen-fin-bud-02|FIN-BUD-02]][^r3][^r4]. It is exposed at endpoint `POST /ll72/svc/bud_query` and requires an authorised session token in header `X-LL-Session`[^r5].

* **Required fields**: None[^r3][^r6].
* **Optional fields**: `cc_cd` (str, CC CD), `period` (str, PERIOD), and `amount` (float, AMOUNT)[^r3][^r6].
* **Errors**: Specific domain error `ERR-BUD-0001` (BUDGET NOT FOUND), alongside common system errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503`[^r3][^r8].
* **Source file**: `04_service_definitions/admin/bud_query.yaml`[^r4].

The service returns an envelope with return code `rc` (`S | W | E`), error code `err_cd`, capitalised message `msg`, and `data` payload[^r7].

### bud_save

The `bud_save` write service creates or updates budget records from screen [[screen-fin-bud-02|FIN-BUD-02]] and executes database stored procedure `sp_bud_save`[^r1][^r9][^r12]. It is exposed at endpoint `POST /ll72/svc/bud_save` and requires an authorised session token in header `X-LL-Session`[^r10].

* **Required fields**: `cc_cd` (str, CC CD), `period` (str, PERIOD), and `amount` (float, AMOUNT)[^r1][^r11].
* **Optional fields**: None[^r11].
* **Errors**: Specific domain error [[err-cc-0009|ERR-CC-0009]] (COST CENTRE NOT FOUND), alongside common system errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503`[^r1][^r13].
* **Source file**: `04_service_definitions/admin/bud_save.yaml`[^r9].

The response envelope returns `rc`, `err_cd`, `msg`, and `data`[^r12].

### bud_transfer

The `bud_transfer` write service reallocates budget values on screen [[screen-fin-bud-02|FIN-BUD-02]] by calling database stored procedure `sp_bud_transfer`[^r2][^r14][^r18]. It is exposed at endpoint `POST /ll72/svc/bud_transfer` and requires role authorisation via header `X-LL-Session`[^r15].

* **Required fields**: `cc_cd` (str, CC CD)[^r2][^r16].
* **Optional fields**: `period` (str, PERIOD) and `amount` (float, AMOUNT)[^r2][^r16].
* **Errors**: Specific domain errors `ERR-BUD-0001`, [[err-cc-0009|ERR-CC-0009]], and `ERR-BUD-0207` (raised when budget is exceeded)[^r2][^r18].
* **Source file**: `04_service_definitions/admin/bud_transfer.yaml`[^r14].

The response envelope provides `rc` (`S | W | E`), `err_cd`, capitalised `msg`, and `data`[^r17].

## See also

* [[screen-fin-bud-02|FIN-BUD-02 Budget Entry]]
* [[err-cc-0009|ERR-CC-0009]]
* [[services-pur-bud|PUR bud services]]
* [[services-adm-par|ADM par services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 71, bud_save BUDGET SAVE
[^r4]: 04_service_definitions/admin/bud_query.yaml, service: bud_query
[^r14]: 04_service_definitions/admin/bud_transfer.yaml, whole file
[^r9]: 04_service_definitions/admin/bud_save.yaml, service: bud_save
[^r5]: 04_service_definitions/admin/bud_query.yaml, auth
[^r10]: 04_service_definitions/admin/bud_save.yaml, endpoint
[^r15]: 04_service_definitions/admin/bud_transfer.yaml, auth
[^r3]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 71, bud_query BUDGET QUERY
[^r6]: 04_service_definitions/admin/bud_query.yaml, request.fields
[^r8]: 04_service_definitions/admin/bud_query.yaml, errors
[^r7]: 04_service_definitions/admin/bud_query.yaml, response.envelope
[^r12]: 04_service_definitions/admin/bud_save.yaml, response.envelope
[^r11]: 04_service_definitions/admin/bud_save.yaml, request.fields
[^r13]: 04_service_definitions/admin/bud_save.yaml, errors
[^r2]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 71, bud_transfer BUDGET TRANSFER
[^r18]: 04_service_definitions/admin/bud_transfer.yaml, errors
[^r16]: 04_service_definitions/admin/bud_transfer.yaml, request.fields
[^r17]: 04_service_definitions/admin/bud_transfer.yaml, response.envelope
