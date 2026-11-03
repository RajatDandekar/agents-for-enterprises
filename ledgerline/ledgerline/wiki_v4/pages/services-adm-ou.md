---
title: "ADM ou services"
type: "service-group"
slug: "services-adm-ou"
summary: "Administration services for organisation units supporting retrieval, listing, and saving against screen SYS-OU-08 in Ledgerline."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/admin/ou_get.yaml", "04_service_definitions/admin/ou_list.yaml", "04_service_definitions/admin/ou_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | ADM |
| Object | ou |
| Screen | SYS-OU-08 |
| Available since | 7.0 |
| Service count | 3 |

The ADM ou service group provides operations for managing organisation units in Ledgerline [^r1][^r4]. It encompasses three services linked to screen [[screen-sys-ou-08|SYS-OU-08]]: `ou_get`, `ou_list`, and `ou_save` [^r1][^r2][^r3]. All services in this group operate under the ADM module and have been available since Ledgerline version 7.0 [^r4][^r9][^r14].

## Services

### ou_get

The `ou_get` read service retrieves details for a single organisation unit, mapped to function key F3 on screen [[screen-sys-ou-08|SYS-OU-08]] [^r1][^r2][^r4]. It is hosted at endpoint POST `/ll72/svc/ou_get` and requires an authentication session token in header `X-LL-Session` along with a permitted user role [^r4][^r5]. The response envelope returns `rc` ('S | W | E'), `err_cd` ('error code when rc is E'), `msg` ('short message in capitals'), and `data` ('result') [^r7].

* **Required fields:** `ou_cd` (str) [^r2][^r6]
* **Optional fields:** none [^r6]
* **Errors:** `ERR-OU-0001` (ORGANISATION UNIT NOT FOUND), `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r1][^r8]
* **Source file:** `04_service_definitions/admin/ou_get.yaml` [^r4]

### ou_list

The `ou_list` read service provides ORGANISATION UNIT LIST functionality on screen [[screen-sys-ou-08|SYS-OU-08]] [^r1][^r2][^r9]. It is exposed at endpoint POST `/ll72/svc/ou_list` and authenticates requests using the `X-LL-Session` header and role authorization [^r10]. Its response envelope provides `rc` (S | W | E), `err_cd` (error code when rc is E), `msg` (short message in capitals), and `data` (result) [^r12].

* **Required fields:** none [^r11]
* **Optional fields:** `ou_cd` (str) [^r2][^r11]
* **Errors:** `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r13]
* **Source file:** `04_service_definitions/admin/ou_list.yaml` [^r9]

### ou_save

The `ou_save` write service creates or updates an organisation unit on screen [[screen-sys-ou-08|SYS-OU-08]], triggered by function key F8 [^r1][^r3][^r14]. It connects to endpoint POST `/ll72/svc/ou_save`, requiring an `X-LL-Session` token and role clearance, and executes the underlying database stored procedure `sp_ou_save` [^r3][^r15][^r18]. The response envelope returns `rc` ('S | W | E'), `err_cd` ('error code when rc is E'), `msg` ('short message in capitals'), and `data` ('result') [^r17].

* **Required fields:** `ou_cd` (str), `name` (str), `state` (str, country code 2) [^r3][^r16]
* **Optional fields:** `city` (str) [^r3][^r16]
* **Errors:** `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r19]
* **Source file:** `04_service_definitions/admin/ou_save.yaml` [^r14]

## See also

* [[screen-sys-ou-08|SYS-OU-08 Organisation Unit]]
* [[services-adm-dlg|ADM dlg services]]
* [[services-adm-par|ADM par services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 43, SYS-OU-08 ORGANISATION UNIT
[^r4]: 04_service_definitions/admin/ou_get.yaml, service: ou_get
[^r2]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 70, ou_get ORGANISATION UNIT GET
[^r3]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 70, ou_save ORGANISATION UNIT SAVE
[^r9]: 04_service_definitions/admin/ou_list.yaml, service: ou_list
[^r14]: 04_service_definitions/admin/ou_save.yaml, whole file
[^r5]: 04_service_definitions/admin/ou_get.yaml, auth
[^r7]: 04_service_definitions/admin/ou_get.yaml, response
[^r6]: 04_service_definitions/admin/ou_get.yaml, request
[^r8]: 04_service_definitions/admin/ou_get.yaml, errors
[^r10]: 04_service_definitions/admin/ou_list.yaml, endpoint
[^r12]: 04_service_definitions/admin/ou_list.yaml, response
[^r11]: 04_service_definitions/admin/ou_list.yaml, request
[^r13]: 04_service_definitions/admin/ou_list.yaml, common_errors
[^r15]: 04_service_definitions/admin/ou_save.yaml, whole file
[^r18]: 04_service_definitions/admin/ou_save.yaml, procedures
[^r17]: 04_service_definitions/admin/ou_save.yaml, response.envelope
[^r16]: 04_service_definitions/admin/ou_save.yaml, request.fields
[^r19]: 04_service_definitions/admin/ou_save.yaml, common_errors
