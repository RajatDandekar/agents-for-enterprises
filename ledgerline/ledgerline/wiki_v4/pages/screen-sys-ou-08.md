---
title: "SYS-OU-08 Organisation Unit"
type: "screen"
slug: "screen-sys-ou-08"
summary: "Screen SYS-OU-08 defines and maintains Ledgerline organisation units, mapping codes, names, country codes, and cities for system administrative roles."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/admin/ou_get.yaml", "04_service_definitions/admin/ou_list.yaml", "04_service_definitions/admin/ou_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen Code | SYS-OU-08 |
| Screen Name | Organisation Unit |
| Module | System (SYS) |
| Navigation | System > Organisation unit |
| Allowed Roles | IT-ADMIN, SYS-ADMIN |
| Read Services | ou_get, ou_list |
| Write Service | ou_save |
| Status | Current |

Screen SYS-OU-08 is the Ledgerline administrative interface used to maintain organisation unit records across Northbridge Cycles [^r1]. Accessed under System > Organisation unit, the screen is restricted to users with the IT-ADMIN and SYS-ADMIN roles [^r1]. It captures unit identifiers and location parameters required for administrative entity configuration [^r2][^r7].

## Fields

SYS-OU-08 captures the following data fields:

* **OU CD (`ou_cd`)**: Mandatory string field holding the unique organisation unit code [^r2][^r7].
* **NAME (`name`)**: Mandatory string field recording the organisation unit name [^r2][^r7].
* **COUNTRY CD (2) (`state`)**: Mandatory string field storing the two-character country code [^r2][^r7].
* **CITY (`city`)**: Optional string field specifying the organisation unit city [^r2][^r7].

## Keys and services

Screen actions interface with the ADM service group via [[services-adm-ou]]:

* **F3 (Get)**: Invokes the read service `ou_get` (endpoint `POST /ll72/svc/ou_get`) using parameter `ou_cd` to retrieve organisation unit details [^r3][^r4].
* **F8 (Save)**: Invokes the write service `ou_save` (endpoint `POST /ll72/svc/ou_save`) to commit the mandatory `ou_cd`, `name`, and `state` fields alongside optional `city` data [^r3][^r6][^r7].
* **List**: Calls the read service `ou_list` (endpoint `POST /ll72/svc/ou_list`) to display organisation units [^r3][^r5].

## Messages

* **ERR-OU-0001**: "Organisation Unit Not Found", raised when an organisation unit lookup fails during retrieval operations [^r3].

## See also

* [[services-adm-ou|ADM ou services]]
* [[screen-sys-usr-01|SYS-USR-01 User]]
* [[screen-sys-par-04|SYS-PAR-04 System Parameter]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 43, SYS-OU-08 ORGANISATION UNIT
[^r2]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 43, SYS-OU-08 ORGANISATION UNIT
[^r7]: 04_service_definitions/admin/ou_save.yaml, request.fields
[^r3]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 43, SYS-OU-08 ORGANISATION UNIT
[^r4]: 04_service_definitions/admin/ou_get.yaml, service: ou_get
[^r6]: 04_service_definitions/admin/ou_save.yaml, whole file
[^r5]: 04_service_definitions/admin/ou_list.yaml, screen
