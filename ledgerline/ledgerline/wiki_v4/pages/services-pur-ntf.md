---
title: "PUR ntf services"
type: "service-group"
slug: "services-pur-ntf"
summary: "Ledgerline notification services in the purchase module for enqueuing outbound emails and SMS alerts via background queue procedures."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/purchase/ntf_send.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | PUR |
| Object | ntf |
| Kind | write |
| Available since | Ledgerline 7.0 |
| Backend procedure | sp_ntf_enqueue |

The `ntf` service group in the purchase module provides automated outbound messaging facilities across Northbridge Cycles' Ledgerline system [^r2]. As of 26 October 2026, it exposes the write service `ntf_send` to enqueue outbound email and SMS messages to designated recipients [^r1][^r2][^r4]. The service operates without an associated user interface screen and executes direct database procedures for asynchronous delivery [^r1][^r2].

## Services

### ntf_send

The `ntf_send` service (titled NOTIFICATION SEND) belongs to module PUR, has kind write, is associated with screen null, and has been available since Ledgerline version 7.0 [^r2]. The service enqueues notifications via backend procedure `sp_ntf_enqueue` taking mandatory channel, recipient, and message parameters [^r1][^r6].

* **Endpoint**: `POST /ll72/svc/ntf_send` [^r3]
* **Authentication**: Requires a session token in header `X-LL-Session` and a role permitted to execute the service [^r3]
* **Source file**: `04_service_definitions/purchase/ntf_send.yaml` [^r2]
* **Required fields**:
  * `channel` (string, `EMAIL/SMS`) [^r4]
  * `recipient` (string, `TO`) [^r4]
  * `msg` (string, `TEXT`) [^r4]
* **Optional fields**: None [^r4]
* **Response envelope**:
  * `rc` (`S | W | E`) [^r5]
  * `err_cd` (error code when `rc` is `E`) [^r5]
  * `msg` (short message in capitals) [^r5]
  * `data` (result) [^r5]
* **Errors and warnings**: Declares no specific errors or warnings beyond common system errors [^r6]

## See also

* [[services-pur-po|PUR po services]]
* [[services-pur-sup|PUR sup services]]
* [[services-pur-bud|PUR bud services]]
* [[services-pur-stk|PUR stk services]]
* [[screen-sys-api-14|SYS-API-14 Service Account Key Key Issue]]

## References

[^r2]: 04_service_definitions/purchase/ntf_send.yaml, service: ntf_send
[^r1]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 8, ntf_send NOTIFICATION SEND
[^r4]: 04_service_definitions/purchase/ntf_send.yaml, request.fields
[^r6]: 04_service_definitions/purchase/ntf_send.yaml, procedures
[^r3]: 04_service_definitions/purchase/ntf_send.yaml, endpoint
[^r5]: 04_service_definitions/purchase/ntf_send.yaml, response.envelope
