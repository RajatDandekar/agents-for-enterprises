---
title: "PUR cc services"
type: "service-group"
slug: "services-pur-cc"
summary: "Ledgerline PUR module read services cc_list and cc_get for querying and retrieving cost centre master records."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/purchase/cc_get.yaml", "04_service_definitions/purchase/cc_list.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| group | services-pur-cc |
| module | PUR |
| kind | read |
| available_since | Ledgerline 7.0 |
| endpoint_base | POST /ll72/svc/ |
| auth | session token (X-LL-Session) |

The `PUR cc` service group comprises the read-only Ledgerline ERP services used to query and retrieve cost centre master records within the purchase module [^r1][^r2][^r6]. Both services have been available since Ledgerline 7.0 and operate under endpoint prefix `POST /ll72/svc/` [^r2][^r6][^r7]. Authenticated calls require an active session token passed in the `X-LL-Session` header by a user whose role is authorised for the service [^r2][^r7]. Standard responses use the standard envelope containing return code `rc` (`S | W | E`), error code `err_cd`, message `msg` in capitals, and payload `data` [^r4][^r8].

## Services

### cc_get

The `cc_get` service (COST CENTRE GET) is a read service in module `PUR` available since version 7.0, reachable at endpoint `POST /ll72/svc/cc_get` [^r2]. It retrieves a specific cost centre record [^r1].

* **Required fields:** `cc_cd` (string, CC CD) [^r1][^r3].
* **Optional fields:** none [^r3].
* **Errors:** specific error [[err-cc-0009|ERR-CC-0009]] (COST CENTRE NOT FOUND), along with common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r1][^r5].
* **Source file:** `04_service_definitions/purchase/cc_get.yaml` [^r2].

### cc_list

The `cc_list` service (COST CENTRE LIST) is a read service in module `PUR` available since version 7.0, reachable at endpoint `POST /ll72/svc/cc_list` [^r6][^r7]. It lists cost centres and is associated with no screen [^r1][^r6].

* **Required fields:** none [^r8].
* **Optional fields:** none [^r8].
* **Errors:** common errors ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r9].
* **Source file:** `04_service_definitions/purchase/cc_list.yaml` [^r6].

## See also

* [[err-cc-0009|ERR-CC-0009]]
* [[services-pur-bud|PUR bud services]]
* [[services-pur-po|PUR po services]]
* [[services-pur-stk|PUR stk services]]
* [[services-pur-sup|PUR sup services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 3, §2. Purchase services
[^r2]: 04_service_definitions/purchase/cc_get.yaml, service: cc_get
[^r6]: 04_service_definitions/purchase/cc_list.yaml, whole file
[^r7]: 04_service_definitions/purchase/cc_list.yaml, whole file
[^r4]: 04_service_definitions/purchase/cc_get.yaml, response
[^r8]: 04_service_definitions/purchase/cc_list.yaml, whole file
[^r3]: 04_service_definitions/purchase/cc_get.yaml, request
[^r5]: 04_service_definitions/purchase/cc_get.yaml, errors
[^r9]: 04_service_definitions/purchase/cc_list.yaml, common_errors
