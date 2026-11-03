---
title: "PUR whs services"
type: "service-group"
slug: "services-pur-whs"
summary: "Ledgerline PUR warehouse services group covering whs_list for retrieving warehouse definitions."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/purchase/whs_list.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | PUR |
| Object | whs |
| Services | whs_list |
| Introduced | Ledgerline 7.0 |
| Status | current |

The PUR whs services group provides programmatic access to warehouse reference information within Ledgerline's purchase module [^r1][^r2]. It currently contains the `whs_list` read operation, which allows clients to retrieve warehouse listings without supplying input parameters [^r1][^r4]. The service has been operational since Ledgerline version 7.0 and remains current across v7.2 environments [^r1][^r2].

## Services

### whs_list

The `whs_list` service is a read operation entitled WAREHOUSE LIST that returns a complete list of configured warehouses [^r1][^r2]. Requests are made via `POST /ll72/svc/whs_list` and authenticate using a valid session token passed in the `X-LL-Session` header, requiring appropriate user role permissions [^r3].

* **Required fields:** None [^r1][^r4].
* **Optional fields:** None [^r4].
* **Errors:** ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r5].
* **Source file:** `04_service_definitions/purchase/whs_list.yaml` [^r2].

The response envelope structure returns standard `rc`, `err_cd`, `msg`, and `data` fields [^r4].

## See also

* [[services-pur-po|PUR po services]]
* [[services-pur-stk|PUR stk services]]
* [[services-pur-sup|PUR sup services]]
* [[services-pur-bud|PUR bud services]]
* [[screen-sys-api-14|SYS-API-14 Service Account Key Key Issue]]
* [[role-stores|Role STORES]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 3, §2. Purchase services
[^r2]: 04_service_definitions/purchase/whs_list.yaml, service: whs_list
[^r4]: 04_service_definitions/purchase/whs_list.yaml, request
[^r3]: 04_service_definitions/purchase/whs_list.yaml, auth
[^r5]: 04_service_definitions/purchase/whs_list.yaml, common_errors
