---
title: "ADM aud services"
type: "service-group"
slug: "services-adm-aud"
summary: "Administration audit trail read services for querying and exporting system audit logs on screen SYS-AUD-07."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/admin/aud_export.yaml", "04_service_definitions/admin/aud_query.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| service_group | ADM aud |
| module | ADM |
| object | aud |
| screen | SYS-AUD-07 |
| kind | read |
| services | aud_query, aud_export |
| status | current |

The ADM aud service group provides read services for auditing system activity within Ledgerline [^r1][^r4][^r9]. Exposed via screen [[screen-sys-aud-07|SYS-AUD-07]], these endpoints allow authorized users to query and export audit trail entries [^r1][^r5][^r10]. Both services have been available since Ledgerline version 7.0 and remain active under version 7.2.3 [^r1][^r4][^r9].

## Services

### aud_query

The `aud_query` service performs audit trail queries and belongs to the ADM module as a read service linked to screen [[screen-sys-aud-07|SYS-AUD-07]] [^r2][^r9]. It communicates via endpoint `POST /ll72/svc/aud_query`, authenticating calls with a session token passed in the `X-LL-Session` header and verifying that the user holds an authorized role [^r10].

* **Required fields:** None [^r2][^r11].
* **Optional fields:** `user_id` (string), `svc` (string), and `from_dt` (date) [^r2][^r11].
* **Response envelope:** Contains return code `rc` ('S | W | E'), `err_cd` ('error code when rc is E'), `msg` ('short message in capitals'), and `data` ('result') [^r12].
* **Errors:** Specific error `ERR-AUD-0001` (AUDIT TRAIL NOT FOUND), along with common errors `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r2][^r13].
* **Source file:** `04_service_definitions/admin/aud_query.yaml` [^r9].

### aud_export

The `aud_export` service handles audit trail exports under the ADM module for screen [[screen-sys-aud-07|SYS-AUD-07]] [^r3][^r4]. It is accessible through endpoint `POST /ll72/svc/aud_export`, requiring authentication via an `X-LL-Session` header and appropriate role authorization [^r5].

* **Required fields:** `id` (string, ID) [^r3][^r6].
* **Optional fields:** `comment` (string, COMMENT) [^r3][^r6].
* **Response envelope:** Contains return code `rc` ('S | W | E'), `err_cd` ('error code when rc is E'), `msg` ('short message in capitals'), and `data` ('result') [^r7].
* **Errors:** Specific error `ERR-AUD-0001` (AUDIT TRAIL NOT FOUND), alongside standard errors `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r3][^r8].
* **Source file:** `04_service_definitions/admin/aud_export.yaml` [^r4].

## See also

* [[screen-sys-aud-07|SYS-AUD-07 Audit Trail]]
* [[services-adm-dlg|ADM dlg services]]
* [[services-adm-imp|ADM imp services]]
* [[services-adm-par|ADM par services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 40, SYS-AUD-07 AUDIT TRAIL
[^r4]: 04_service_definitions/admin/aud_export.yaml, service: aud_export
[^r9]: 04_service_definitions/admin/aud_query.yaml, service: aud_query
[^r5]: 04_service_definitions/admin/aud_export.yaml, endpoint
[^r10]: 04_service_definitions/admin/aud_query.yaml, endpoint
[^r2]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 69, aud_query AUDIT TRAIL QUERY
[^r11]: 04_service_definitions/admin/aud_query.yaml, request.fields
[^r12]: 04_service_definitions/admin/aud_query.yaml, response.envelope
[^r13]: 04_service_definitions/admin/aud_query.yaml, errors
[^r3]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 70, aud_export AUDIT TRAIL EXPORT
[^r6]: 04_service_definitions/admin/aud_export.yaml, request.fields
[^r7]: 04_service_definitions/admin/aud_export.yaml, response.envelope
[^r8]: 04_service_definitions/admin/aud_export.yaml, errors
