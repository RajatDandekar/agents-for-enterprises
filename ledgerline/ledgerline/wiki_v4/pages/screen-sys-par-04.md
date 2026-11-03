---
title: "SYS-PAR-04 System Parameter"
type: "screen"
slug: "screen-sys-par-04"
summary: "Ledgerline screen used by administrators to view, update, list, and review the audit history of global system parameters."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/admin/par_get.yaml", "04_service_definitions/admin/par_hist.yaml", "04_service_definitions/admin/par_list.yaml", "04_service_definitions/admin/par_set.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen | SYS-PAR-04 |
| Title | System Parameter |
| Module | System Administration |
| Menu path | System > System parameter |
| Roles | IT-ADMIN, SYS-ADMIN |
| Status | Current |

Screen SYS-PAR-04 is the Ledgerline administrative interface for maintaining and reviewing global system parameters [^r1]. Accessed under System > System parameter by users with the IT-ADMIN and SYS-ADMIN roles, it governs core configuration values across the installation [^r4]. Any update requires a documented change request reference and approving manager details, and all changes are automatically archived to a permanent audit history table [^r2][^r3].

| Field | Details |
|---|---|
| Screen | SYS-PAR-04 |
| Title | System Parameter |
| Module | System Administration |
| Menu path | System > System parameter |
| Roles | IT-ADMIN, SYS-ADMIN |
| Status | Current |

## Fields

SYS-PAR-04 provides the following input and configuration fields:
* `par_cd`: Mandatory string field representing the parameter code [^r5].
* `value`: Mandatory string field holding the parameter value [^r5].
* `ou_cd`: Optional field specifying the operating unit code [^r5].
* Mandatory narrative prompt: Requires entry of the change request reference, business justification, and approving manager initials whenever parameter changes are saved [^r2].

The screen automatically records and archives the previous value, new value, system date, and user login ID into the permanent parameter history table upon updating a record [^r3].

## Keys and services

Screen actions interface with the ADM module backend services:
* **Get** (`F3`): Executes read service `par_get` via endpoint `POST /ll72/svc/par_get` to retrieve an individual system parameter [^r6][^r8].
* **Set**: Invokes write service `par_set` using database stored procedure `sp_par_set` to apply updates [^r6][^r11].
* **List**: Calls read service `par_list` through endpoint `POST /ll72/svc/par_list` to list parameters [^r6][^r10].
* **Hist**: Invokes read service `par_hist` to retrieve the historical audit log of parameter changes [^r6][^r9].

These services are documented collectively under [[services-adm-par|ADM par services]] [^r1][^r8][^r9][^r10][^r11].

## Messages

The following system error codes may be raised during operations on SYS-PAR-04:
* `ERR-PAR-0001`: System Parameter Not Found [^r7].
* `ERR-PAR-0101`: Unknown Parameter [^r7].
* `ERR-PAR-0110`: Value Out Of Range [^r7].

## See also

* [[man-adm-72|MAN-ADM-72 Ledgerline ERP 7.2 System Administration]]
* [[services-adm-par|ADM par services]]
* [[screen-sys-usr-01|SYS-USR-01 User]]
* [[screen-sys-dlg-03|SYS-DLG-03 Approval Delegation Entry]]
* [[screen-sys-job-06|SYS-JOB-06 Batch Job Submit]]
* [[screen-sys-api-14|SYS-API-14 Service Account Key Key Issue]]

## References

[^r1]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 5, §4. System parameters
[^r4]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 43, SYS-PAR-04 SYSTEM PARAMETER
[^r2]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 6, §4. System parameters
[^r3]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 6, §4. System parameters
[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 43, SYS-PAR-04 SYSTEM PARAMETER
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 43, SYS-PAR-04 SYSTEM PARAMETER
[^r8]: 04_service_definitions/admin/par_get.yaml, whole file
[^r11]: 04_service_definitions/admin/par_set.yaml, screen: SYS-PAR-04
[^r10]: 04_service_definitions/admin/par_list.yaml, whole file
[^r9]: 04_service_definitions/admin/par_hist.yaml, service: par_hist
[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 43, SYS-PAR-04 SYSTEM PARAMETER
