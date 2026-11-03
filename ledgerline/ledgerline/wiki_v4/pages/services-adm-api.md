---
title: "ADM api services"
type: "service-group"
slug: "services-adm-api"
summary: "Administration services for service account API key issuance, revocation, and listing on screen SYS-API-14 in Ledgerline 7.2."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/admin/api_key_issue.yaml", "04_service_definitions/admin/api_key_list.yaml", "04_service_definitions/admin/api_key_revoke.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Service group | services-adm-api |
| Module | ADM |
| Screen | SYS-API-14 |
| Available since | 7.2.0 |
| Operations | api_key_issue, api_key_revoke, api_key_list |

The `services-adm-api` service group encompasses Ledgerline administration module services used to issue, revoke, and query service account API keys [^r1][^r5]. All three services operate against screen [[screen-sys-api-14|SYS-API-14]] and were introduced in Ledgerline version 7.2.0 [^r1][^r2][^r3][^r4]. Requests require standard authentication via an authorised role and a session token passed in the `X-LL-Session` header [^r6][^r11][^r16].

## Services

### api_key_issue

A write service titled "SERVICE ACCOUNT KEY KEY ISSUE" accessed via endpoint `POST /ll72/svc/api_key_issue` on screen [[screen-sys-api-14|SYS-API-14]] [^r1][^r2][^r5]. The call executes stored procedure `sp_api_key_issue` [^r2][^r6].

* **Required fields:** `key_id` (string) [^r2][^r7].
* **Optional fields:** `comment` (string) [^r7].
* **Specific errors:** ERR-API-0001 (SERVICE ACCOUNT KEY NOT FOUND) and ERR-API-0120 (SERVICE ACCOUNT HAS NO OWNER) [^r2][^r8].
* **Common errors:** ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r9].
* **Source file:** `04_service_definitions/admin/api_key_issue.yaml` [^r5].

### api_key_revoke

A write service titled "SERVICE ACCOUNT KEY KEY REVOKE" accessed via endpoint `POST /ll72/svc/api_key_revoke` on screen [[screen-sys-api-14|SYS-API-14]] [^r1][^r3][^r15][^r16]. The operation executes database stored procedure `sp_api_key_revoke` [^r3][^r18]. The standard response envelope contains `rc` (`S | W | E`), `err_cd` (populated when `rc` is `E`), message `msg` in capitals, and `data` [^r19].

* **Required fields:** `key_id` (KEY ID, string) [^r3][^r17].
* **Optional fields:** `reason` (REASON, string) [^r3][^r17].
* **Specific errors:** ERR-API-0001 (SERVICE ACCOUNT KEY NOT FOUND) [^r3][^r18].
* **Common errors:** ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r20].
* **Source file:** `04_service_definitions/admin/api_key_revoke.yaml` [^r15].

### api_key_list

A read service titled "SERVICE ACCOUNT KEY KEY LIST" accessed via endpoint `POST /ll72/svc/api_key_list` on screen [[screen-sys-api-14|SYS-API-14]] [^r1][^r4][^r10][^r11]. The response envelope returns `rc` (`S | W | E`), `err_cd`, short message `msg` in capitals, and `data` [^r13].

* **Required fields:** None [^r4][^r12].
* **Optional fields:** `user_id` (string, representing the service account) [^r4][^r12].
* **Specific errors:** ERR-API-0001 (SERVICE ACCOUNT KEY NOT FOUND) [^r4][^r14].
* **Common errors:** ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r14].
* **Source file:** `04_service_definitions/admin/api_key_list.yaml` [^r10].

## See also

* [[screen-sys-api-14|SYS-API-14 Service Account Key Key Issue]]
* [[services-adm-dlg|ADM dlg services]]
* [[services-adm-imp|ADM imp services]]
* [[services-adm-par|ADM par services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 40, SYS-API-14 SERVICE ACCOUNT KEY KEY ISSUE
[^r5]: 04_service_definitions/admin/api_key_issue.yaml, service: api_key_issue
[^r2]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 73, api_key_issue SERVICE ACCOUNT KEY KEY ISSUE
[^r3]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 74, api_key_revoke SERVICE ACCOUNT KEY KEY REVOKE
[^r4]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 74, api_key_list SERVICE ACCOUNT KEY KEY LIST
[^r6]: 04_service_definitions/admin/api_key_issue.yaml, auth
[^r11]: 04_service_definitions/admin/api_key_list.yaml, endpoint
[^r16]: 04_service_definitions/admin/api_key_revoke.yaml, endpoint
[^r7]: 04_service_definitions/admin/api_key_issue.yaml, request.fields
[^r8]: 04_service_definitions/admin/api_key_issue.yaml, errors
[^r9]: 04_service_definitions/admin/api_key_issue.yaml, common_errors
[^r15]: 04_service_definitions/admin/api_key_revoke.yaml, service
[^r18]: 04_service_definitions/admin/api_key_revoke.yaml, errors
[^r19]: 04_service_definitions/admin/api_key_revoke.yaml, response.envelope
[^r17]: 04_service_definitions/admin/api_key_revoke.yaml, request.fields
[^r20]: 04_service_definitions/admin/api_key_revoke.yaml, common_errors
[^r10]: 04_service_definitions/admin/api_key_list.yaml, service
[^r13]: 04_service_definitions/admin/api_key_list.yaml, response.envelope
[^r12]: 04_service_definitions/admin/api_key_list.yaml, request.fields
[^r14]: 04_service_definitions/admin/api_key_list.yaml, errors
