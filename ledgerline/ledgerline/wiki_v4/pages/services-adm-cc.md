---
title: "ADM cc services"
type: "service-group"
slug: "services-adm-cc"
summary: "Ledgerline ADM services for cost centre creation, closure, and reopening on screen FIN-CC-01."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/admin/cc_close.yaml", "04_service_definitions/admin/cc_reopen.yaml", "04_service_definitions/admin/cc_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | ADM |
| Object | Cost Centre (cc) |
| Screen | FIN-CC-01 |
| Introduced | Ledgerline 7.0 |
| Endpoints | POST /ll72/svc/cc_save, POST /ll72/svc/cc_close, POST /ll72/svc/cc_reopen |
| Services | cc_save, cc_close, cc_reopen |

The `cc` service group provides administrative write services in the Ledgerline ADM module for managing cost centres on screen [[screen-fin-cc-01|FIN-CC-01]][^r1][^r4][^r11][^r18]. It comprises `cc_save`, `cc_close`, and `cc_reopen`, which execute underlying database stored procedures to maintain cost centre records and enforce lifecycle states[^r1][^r2][^r3][^r8][^r15][^r21]. All endpoints require role-based authorisation and session authentication passed via the `X-LL-Session` HTTP header[^r5][^r12][^r19].

## Services

### cc_save

`cc_save` (COST CENTRE SAVE) is a write service introduced in Ledgerline 7.0 that creates or updates cost centre records on screen [[screen-fin-cc-01|FIN-CC-01]][^r1][^r18]. It is exposed at endpoint `POST /ll72/svc/cc_save` and requires a session token in the `X-LL-Session` header authorized by the user's role[^r19]. The service executes stored procedure `sp_cc_save` and returns an envelope containing `rc` (`S | W | E`), `err_cd`, `msg`, and `data`[^r1][^r21].

* **Required fields:** `cc_cd` (str), `name` (str), `owner` (str)[^r1][^r20].
* **Optional fields:** `ou_cd` (str)[^r1][^r20].
* **Errors:** [[err-cc-0009]] (COST CENTRE NOT FOUND), along with common errors ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (`<FIELD>` MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD `<FIELD>` / BAD VALUE FOR `<FIELD>`), and ERR-SYS-0503 (SERVER BUSY, TRY LATER)[^r1][^r22].
* **Source file:** `04_service_definitions/admin/cc_save.yaml`[^r18].

### cc_close

`cc_close` (COST CENTRE CLOSE) is a write service introduced in Ledgerline 7.0 that closes an active cost centre[^r2][^r4]. It is exposed at endpoint `POST /ll72/svc/cc_close` and requires a valid session token in header `X-LL-Session` authorized by role access[^r4][^r5]. The service executes database procedure `sp_cc_close` and returns an envelope with `rc` (`S | W | E`), `err_cd`, `msg`, and `data`[^r2][^r7][^r8].

* **Required fields:** `cc_cd` (str)[^r2][^r6].
* **Optional fields:** `comment` (str)[^r6].
* **Errors:** ERR-CC-0001 (COST CENTRE NOT FOUND), ERR-CC-0801 (COST CENTRE CLOSED (`<status>`)), [[err-cc-0009]] (COST CENTRE NOT FOUND), [[err-cc-0310]] (OPEN DOCUMENTS ON COST CENTRE), and common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503[^r2][^r9][^r10].
* **Source file:** `04_service_definitions/admin/cc_close.yaml`[^r4].

### cc_reopen

`cc_reopen` (COST CENTRE REOPEN) is a write service introduced in Ledgerline 7.0 associated with screen [[screen-fin-cc-01|FIN-CC-01]][^r11]. It is exposed at endpoint `POST /ll72/svc/cc_reopen` and requires session authentication using the `X-LL-Session` header with an authorized user role[^r12]. It executes database procedure `sp_cc_reopen` and returns an envelope with `rc` (`S | W | E`), `err_cd`, `msg`, and `data`[^r3][^r14][^r15].

* **Required fields:** `cc_cd` (str)[^r3][^r13].
* **Optional fields:** `comment` (str)[^r3][^r13].
* **Errors:** ERR-CC-0001 (COST CENTRE NOT FOUND), [[err-cc-0009]] (COST CENTRE NOT FOUND), and common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503[^r3][^r16][^r17].
* **Source file:** `04_service_definitions/admin/cc_reopen.yaml`[^r11].

## Versions and conflicts

* **`comment` field requirement on `cc_close`:** Under the service definition YAML, `comment` is an optional string field (`request.fields`)[^r6]. The service reference manual MAN-SVC-72 lists `comment` as mandatory[^r2].

## See also

* [[screen-fin-cc-01|FIN-CC-01 Cost Centre Entry]]
* [[errors-cc|Cost Centre Error Codes (ERR-CC-*)]]
* [[err-cc-0009|ERR-CC-0009]]
* [[err-cc-0310|ERR-CC-0310 Cost centre has open documents]]
* [[services-adm-par|ADM par services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 70, cc_save COST CENTRE SAVE
[^r4]: 04_service_definitions/admin/cc_close.yaml, service: cc_close
[^r11]: 04_service_definitions/admin/cc_reopen.yaml, service: cc_reopen
[^r18]: 04_service_definitions/admin/cc_save.yaml, service: cc_save
[^r2]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 70, cc_close COST CENTRE CLOSE
[^r3]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 71, cc_reopen COST CENTRE REOPEN
[^r8]: 04_service_definitions/admin/cc_close.yaml, procedures
[^r15]: 04_service_definitions/admin/cc_reopen.yaml, procedures
[^r21]: 04_service_definitions/admin/cc_save.yaml, response.envelope
[^r5]: 04_service_definitions/admin/cc_close.yaml, auth
[^r12]: 04_service_definitions/admin/cc_reopen.yaml, auth
[^r19]: 04_service_definitions/admin/cc_save.yaml, endpoint
[^r20]: 04_service_definitions/admin/cc_save.yaml, request.fields
[^r22]: 04_service_definitions/admin/cc_save.yaml, errors
[^r7]: 04_service_definitions/admin/cc_close.yaml, response.envelope
[^r6]: 04_service_definitions/admin/cc_close.yaml, request.fields
[^r9]: 04_service_definitions/admin/cc_close.yaml, errors
[^r10]: 04_service_definitions/admin/cc_close.yaml, common_errors
[^r14]: 04_service_definitions/admin/cc_reopen.yaml, response.envelope
[^r13]: 04_service_definitions/admin/cc_reopen.yaml, request.fields
[^r16]: 04_service_definitions/admin/cc_reopen.yaml, errors
[^r17]: 04_service_definitions/admin/cc_reopen.yaml, common_errors
