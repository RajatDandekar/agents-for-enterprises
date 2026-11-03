---
title: "ADM imp services"
type: "service-group"
slug: "services-adm-imp"
summary: "Ledgerline ADM module data import services (imp_upload, imp_validate, imp_post, imp_status) linked to screen SYS-IMP-13."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/admin/imp_post.yaml", "04_service_definitions/admin/imp_status.yaml", "04_service_definitions/admin/imp_upload.yaml", "04_service_definitions/admin/imp_validate.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | ADM |
| Object | imp |
| Screen | [[screen-sys-imp-13|SYS-IMP-13]] |
| Available since | Ledgerline 7.0 |
| Status | Current |

The ADM data import service group comprises four services in Ledgerline that manage staged file uploads, validation, posting, and status tracking [^r2][^r7][^r13][^r19][^r24]. All services in this group are linked to screen [[screen-sys-imp-13|SYS-IMP-13 Data Import Upload]] and have been available since Ledgerline version 7.0 [^r2][^r3][^r7][^r13][^r19][^r24]. Every endpoint requires authentication using a session token supplied in the `X-LL-Session` request header along with authorized role permissions [^r8][^r14][^r20][^r25].

## Services

### imp_upload

* **Title**: DATA IMPORT UPLOAD [^r3]
* **Kind**: write [^r3][^r19]
* **Endpoint**: `POST /ll72/svc/imp_upload` [^r19]
* **Stored procedure**: `sp_imp_upload` [^r3][^r23]
* **Source file**: `04_service_definitions/admin/imp_upload.yaml` [^r19]
* **Required fields**: `imp_type` (string, import type) and `file_ref` (string, file ref) [^r3][^r21]
* **Optional fields**: None [^r21]
* **Response envelope**: Returns `rc` (`S | W | E`), `err_cd` (error code when rc is E), `msg` (short message in capitals), and `data` (result) [^r22].
* **Errors**: Common errors include `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r23].

### imp_validate

* **Title**: DATA IMPORT VALIDATE [^r4]
* **Kind**: write [^r4][^r24]
* **Endpoint**: `POST /ll72/svc/imp_validate` [^r24]
* **Stored procedure**: `sp_imp_validate` [^r4][^r27]
* **Source file**: `04_service_definitions/admin/imp_validate.yaml` [^r24]
* **Required fields**: `imp_id` (string, IMP ID) [^r4][^r26]
* **Optional fields**: `comment` (string, COMMENT) [^r4][^r26]
* **Response envelope**: Standard envelope structure [^r24].
* **Errors**: `ERR-IMP-0001` (DATA IMPORT NOT FOUND) [^r4][^r28], `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r28].

### imp_post

* **Title**: DATA IMPORT POST [^r5][^r7]
* **Kind**: write [^r5][^r7]
* **Screen shortcut**: Mapped to function key F9 on screen [[screen-sys-imp-13|SYS-IMP-13]] [^r2].
* **Endpoint**: `POST /ll72/svc/imp_post` [^r8]
* **Stored procedure**: `sp_imp_post` [^r5][^r10]
* **Source file**: `04_service_definitions/admin/imp_post.yaml` [^r7]
* **Required fields**: `imp_id` (string, IMP ID) [^r5][^r9]
* **Optional fields**: `comment` (string, COMMENT) [^r5][^r9]
* **Response envelope**: Returns `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r10].
* **Errors**: `ERR-IMP-0001` (DATA IMPORT NOT FOUND) [^r1][^r2][^r5][^r11], `ERR-IMP-0007` (DATA IMPORT NOT IN DRAFT (<status>)) [^r1][^r2][^r5][^r11], `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r12].

### imp_status

* **Title**: DATA IMPORT STATUS [^r6][^r13]
* **Kind**: read [^r6][^r13]
* **Endpoint**: `POST /ll72/svc/imp_status` [^r14]
* **Source file**: `04_service_definitions/admin/imp_status.yaml` [^r13]
* **Required fields**: `imp_id` (string, import ID) [^r6][^r15]
* **Optional fields**: None [^r15]
* **Response envelope**: Returns `rc` (`S | W | E`), `err_cd` (error code when rc is E), `msg` (short message in capitals), and `data` (result) [^r16].
* **Errors**: `ERR-IMP-0001` (DATA IMPORT NOT FOUND) [^r6][^r17], `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r18].

## See also

* [[screen-sys-imp-13|SYS-IMP-13 Data Import Upload]]
* [[services-adm-dlg|ADM dlg services]]
* [[services-adm-par|ADM par services]]
* [[services-adm-usr|ADM usr services]]

## References

[^r2]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 41, SYS-IMP-13 DATA IMPORT UPLOAD
[^r7]: 04_service_definitions/admin/imp_post.yaml, service
[^r13]: 04_service_definitions/admin/imp_status.yaml, service: imp_status
[^r19]: 04_service_definitions/admin/imp_upload.yaml, service: imp_upload
[^r24]: 04_service_definitions/admin/imp_validate.yaml, whole file
[^r3]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 73, imp_upload DATA IMPORT UPLOAD
[^r8]: 04_service_definitions/admin/imp_post.yaml, endpoint
[^r14]: 04_service_definitions/admin/imp_status.yaml, endpoint
[^r20]: 04_service_definitions/admin/imp_upload.yaml, auth
[^r25]: 04_service_definitions/admin/imp_validate.yaml, auth
[^r23]: 04_service_definitions/admin/imp_upload.yaml, common_errors
[^r21]: 04_service_definitions/admin/imp_upload.yaml, request
[^r22]: 04_service_definitions/admin/imp_upload.yaml, response
[^r4]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 73, imp_validate DATA IMPORT VALIDATE
[^r27]: 04_service_definitions/admin/imp_validate.yaml, procedures
[^r26]: 04_service_definitions/admin/imp_validate.yaml, request.fields
[^r28]: 04_service_definitions/admin/imp_validate.yaml, errors
[^r5]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 73, imp_post DATA IMPORT POST
[^r10]: 04_service_definitions/admin/imp_post.yaml, response.envelope
[^r9]: 04_service_definitions/admin/imp_post.yaml, request.fields
[^r1]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 11
[^r11]: 04_service_definitions/admin/imp_post.yaml, errors
[^r12]: 04_service_definitions/admin/imp_post.yaml, common_errors
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 73, imp_status DATA IMPORT STATUS
[^r15]: 04_service_definitions/admin/imp_status.yaml, request.fields
[^r16]: 04_service_definitions/admin/imp_status.yaml, response.envelope
[^r17]: 04_service_definitions/admin/imp_status.yaml, errors
[^r18]: 04_service_definitions/admin/imp_status.yaml, common_errors
