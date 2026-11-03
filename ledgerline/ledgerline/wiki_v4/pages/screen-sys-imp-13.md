---
title: "SYS-IMP-13 Data Import Upload"
type: "screen"
slug: "screen-sys-imp-13"
summary: "Ledgerline screen for staging, validating, and posting batch data imports, executed by administrators using underlying ADM imp services."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/admin/imp_post.yaml", "04_service_definitions/admin/imp_status.yaml", "04_service_definitions/admin/imp_upload.yaml", "04_service_definitions/admin/imp_validate.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen Code | SYS-IMP-13 |
| Screen Title | Data Import Upload |
| Module | System / Admin |
| Menu Path | System > Data import |
| Roles | IT-ADMIN, SYS-ADMIN |
| Key Service | imp_upload |
| Shortcut Keys | F9 (imp_post) |
| Status | Current |

SYS-IMP-13 (Data Import Upload) is the Ledgerline administrative interface used to upload, validate, and post batch data imports into the system [^r1][^r3][^r5]. Accessible under the System > Data import navigation path, access is restricted to the IT-ADMIN and SYS-ADMIN roles [^r1]. It manages the staging lifecycle of import jobs prior to committing database changes via underlying stored procedures [^r5].

## Fields

SYS-IMP-13 includes the following user input and key reference fields:

* **imp_type**: Mandatory string specifying the import category or target entity type [^r2][^r10].
* **file_ref**: Mandatory string referencing the staged import file location [^r2][^r10].
* **imp_id**: Mandatory string identifying the import batch record [^r2][^r8].
* **comment**: Optional string field for operational notes [^r2].

## Keys and services

Screen actions are powered by the [[services-adm-imp|ADM imp services]] group:

* **imp_upload**: Write service executed at endpoint `POST /ll72/svc/imp_upload` to create the initial import record using stored procedure `sp_imp_upload` with mandatory fields `imp_type` and `file_ref` [^r3][^r5][^r9][^r10].
* **imp_validate**: Write service triggered by button action to validate import data entries against business rules via stored procedure `sp_imp_validate` [^r3][^r5][^r11].
* **imp_post**: Write service mapped to the **F9** function key to commit validated imports through stored procedure `sp_imp_post` [^r3][^r5][^r7].
* **imp_status**: Read service executed at endpoint `POST /ll72/svc/imp_status` using parameter `imp_id` to query import job progress [^r3][^r5][^r8].

## Messages

The screen displays the following validation and processing messages:

* **ERR-IMP-0001**: Data Import Not Found [^r4][^r6].
* **ERR-IMP-0007**: Data Import Not In Draft (`<status>`) [^r4][^r6].

## See also

* [[services-adm-imp|ADM imp services]]
* [[screen-sys-api-14|SYS-API-14 Service Account Key Key Issue]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 41, SYS-IMP-13 DATA IMPORT UPLOAD
[^r3]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 41, SYS-IMP-13 DATA IMPORT UPLOAD
[^r5]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 73, imp_upload DATA IMPORT UPLOAD
[^r2]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 41, SYS-IMP-13 DATA IMPORT UPLOAD
[^r10]: 04_service_definitions/admin/imp_upload.yaml, request
[^r8]: 04_service_definitions/admin/imp_status.yaml, service: imp_status
[^r9]: 04_service_definitions/admin/imp_upload.yaml, service: imp_upload
[^r11]: 04_service_definitions/admin/imp_validate.yaml, whole file
[^r7]: 04_service_definitions/admin/imp_post.yaml, screen
[^r4]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 41, SYS-IMP-13 DATA IMPORT UPLOAD
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 73, imp_post DATA IMPORT POST
