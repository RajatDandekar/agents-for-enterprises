---
title: "SYS-PRT-12 Print Forms"
type: "screen"
slug: "screen-sys-prt-12"
summary: "Ledgerline screen SYS-PRT-12 manages print form configurations, accessible by system administrators via the ADM prt services."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/admin/prt_form_get.yaml", "04_service_definitions/admin/prt_list.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen Code | SYS-PRT-12 |
| Title | Print Forms |
| Navigation | System > Print forms |
| Roles | IT-ADMIN, SYS-ADMIN |
| Read Services | prt_form_get, prt_list |
| Status | Current |

Screen SYS-PRT-12 provides the interface for querying and viewing print form configurations in Ledgerline [^r1][^r4][^r5]. It is accessed through the menu path System > Print forms and is restricted to IT-ADMIN and SYS-ADMIN roles [^r1]. The screen interacts with backend [[services-adm-prt|ADM prt services]] to locate and retrieve form definitions [^r4][^r5].

| Field | Value |
|---|---|
| Screen Code | SYS-PRT-12 |
| Title | Print Forms |
| Navigation | System > Print forms |
| Access Roles | IT-ADMIN, SYS-ADMIN |
| Primary Services | prt_form_get, prt_list |
| Status | Current |

## Fields

* `form_cd`: Print form code, used to specify or retrieve a particular print form configuration [^r4][^r5][^r6].

## Keys and services

* **List**: Calls the read service `prt_list` with an optional `form_cd` parameter to query and display the print forms list [^r5][^r6].
* **Form Get**: Calls the read service `prt_form_get` using `form_cd` to retrieve print forms details [^r4][^r6].

Both operations run against the [[services-adm-prt|ADM prt services]] group [^r4][^r5].

## Messages

* `ERR-PRT-0001`: Print Forms Not Found (or PRINT FORMS NOT FOUND) [^r2][^r3]. This error is raised by SYS-PRT-12 when the `prt_form_get` service fails to find the specified print form [^r2][^r3].

## See also

* [[services-adm-prt|ADM prt services]]
* [[screen-sys-api-14|SYS-API-14 Service Account Key Key Issue]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 43, SYS-PRT-12 PRINT FORMS
[^r4]: 04_service_definitions/admin/prt_form_get.yaml, service: prt_form_get
[^r5]: 04_service_definitions/admin/prt_list.yaml, whole file
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 44, SYS-PRT-12 PRINT FORMS
[^r2]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 44, SYS-PRT-12 PRINT FORMS
[^r3]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 73, prt_form_get PRINT FORMS FORM GET
