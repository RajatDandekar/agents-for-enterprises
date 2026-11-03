---
title: "PUR pt services"
type: "service-group"
slug: "services-pur-pt"
summary: "Ledgerline ERP 7.2 purchase payment terms services providing pt_list to retrieve configured payment terms."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/purchase/pt_list.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | PUR |
| Object | pt |
| Kind | read |
| API endpoint | POST /ll72/svc/pt_list |
| Authentication | X-LL-Session |
| Version added | 7.0 |
| Status | current |

The PUR pt service group contains read services for payment terms lookup within Ledgerline ERP 7.2 [^r1][^r2]. Available since version 7.0, it allows callers to list standard payment terms configured across the system without passing query parameters [^r1][^r2][^r4]. It is used across purchasing transactions and master records to populate valid payment terms [^r1][^r2].

## Services

### pt_list

The `pt_list` service provides PAY TERM LIST functionality in the PUR module as a read service [^r1][^r2].

* **Endpoint**: `POST /ll72/svc/pt_list` [^r3]
* **Authentication**: Session token passed via HTTP header `X-LL-Session` with role authorization required [^r3]
* **Required fields**: None [^r1][^r4]
* **Optional fields**: None [^r1][^r4]
* **Response structure**: The response envelope contains `rc` ('S | W | E'), `err_cd` ('error code when rc is E'), `msg` ('short message in capitals'), and `data` ('result') [^r5].
* **Errors**: Common errors returned include `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r6].
* **Source file**: `04_service_definitions/purchase/pt_list.yaml` [^r2]

## See also

* [[services-pur-po|PUR po services]]
* [[services-pur-sup|PUR sup services]]
* [[services-pur-bud|PUR bud services]]
* [[services-pur-stk|PUR stk services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 3, §2. Purchase services
[^r2]: 04_service_definitions/purchase/pt_list.yaml, service: pt_list
[^r4]: 04_service_definitions/purchase/pt_list.yaml, request
[^r3]: 04_service_definitions/purchase/pt_list.yaml, auth
[^r5]: 04_service_definitions/purchase/pt_list.yaml, response
[^r6]: 04_service_definitions/purchase/pt_list.yaml, common_errors
