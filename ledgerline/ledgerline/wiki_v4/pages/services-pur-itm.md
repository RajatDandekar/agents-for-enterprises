---
title: "PUR itm services"
type: "service-group"
slug: "services-pur-itm"
summary: "Ledgerline item enquiry and master retrieval services in the PUR module."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/purchase/itm_get.yaml", "04_service_definitions/purchase/itm_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | PUR |
| Object | itm |
| Type | Read services |
| Version introduced | Ledgerline 7.0 |
| Endpoints | POST /ll72/svc/itm_get, POST /ll72/svc/itm_search |
| Auth header | X-LL-Session |
| Associated screen | INV-ITM-03 |

The PUR itm service group provides read-only access to item master records and item search queries within Ledgerline [^r1][^r2][^r3][^r8]. Both services operate under the PUR module, have been available since Ledgerline version 7.0, and authenticate requests using an active session token passed in the `X-LL-Session` header [^r3][^r4][^r8][^r9]. They form the foundational lookups used by item search screens such as [[screen-inv-itm-03|INV-ITM-03 Item Enquiry]] [^r1][^r8].

## Services

### itm_get

The `itm_get` service (ITEM MASTER GET) retrieves item master data for a specified item code [^r2][^r3]. It is exposed at endpoint `POST /ll72/svc/itm_get` and requires an authorized role with access rights granted in session header `X-LL-Session` [^r3][^r4]. Responses follow the standard envelope containing `rc` ('S | W | E'), `err_cd`, `msg`, and `data` [^r6].

* **Source file:** `04_service_definitions/purchase/itm_get.yaml` [^r3]
* **Required fields:**
  * `itm_cd` (str): ITEM CD [^r2][^r5]
* **Optional fields:** none [^r5]
* **Errors:**
  * `ERR-ITM-0010`: ITEM NOT FOUND [^r2][^r7]
  * `ERR-SEC-0001`: ACCESS DENIED [^r7]
  * `ERR-SYS-0421`: `<FIELD>` MANDATORY [^r7]
  * `ERR-SYS-0422`: UNKNOWN FIELD `<FIELD>` / BAD VALUE FOR `<FIELD>` [^r7]
  * `ERR-SYS-0503`: SERVER BUSY, TRY LATER [^r7]

### itm_search

The `itm_search` service (ITEM ENQUIRY) executes text search queries against item records for [[screen-inv-itm-03|INV-ITM-03 Item Enquiry]] [^r1][^r8]. It operates at endpoint `POST /ll72/svc/itm_search` and checks role authorization via the `X-LL-Session` header [^r9]. The response envelope returns `rc` ('S | W | E'), `err_cd`, `msg`, and `data` [^r11].

* **Source file:** `04_service_definitions/purchase/itm_search.yaml` [^r8]
* **Required fields:**
  * `q` (str): Search text [^r1][^r10]
* **Optional fields:** none [^r10]
* **Errors:**
  * `ERR-SEC-0001`: ACCESS DENIED [^r12]
  * `ERR-SYS-0421`: `<FIELD>` MANDATORY [^r12]
  * `ERR-SYS-0422`: UNKNOWN FIELD `<FIELD>` / BAD VALUE FOR `<FIELD>` [^r12]
  * `ERR-SYS-0503`: SERVER BUSY, TRY LATER [^r12]

## See also

* [[screen-inv-itm-03|INV-ITM-03 Item Enquiry]]
* [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]]
* [[services-pur-stk|PUR stk services]]
* [[services-pur-po|PUR po services]]
* [[services-pur-sup|PUR sup services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 2, §2. Purchase services
[^r2]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 2, §2. Purchase services
[^r3]: 04_service_definitions/purchase/itm_get.yaml, service: itm_get
[^r8]: 04_service_definitions/purchase/itm_search.yaml, service: itm_search
[^r4]: 04_service_definitions/purchase/itm_get.yaml, auth
[^r9]: 04_service_definitions/purchase/itm_search.yaml, endpoint
[^r6]: 04_service_definitions/purchase/itm_get.yaml, response.envelope
[^r5]: 04_service_definitions/purchase/itm_get.yaml, request.fields
[^r7]: 04_service_definitions/purchase/itm_get.yaml, errors
[^r11]: 04_service_definitions/purchase/itm_search.yaml, response
[^r10]: 04_service_definitions/purchase/itm_search.yaml, request
[^r12]: 04_service_definitions/purchase/itm_search.yaml, common_errors
