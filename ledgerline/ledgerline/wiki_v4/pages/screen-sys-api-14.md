---
title: "SYS-API-14 Service Account Key Key Issue"
type: "screen"
slug: "screen-sys-api-14"
summary: "Ledgerline screen for issuing, listing, and revoking service account keys for background integrations, restricted to IT and system administrators."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-IT-002 Service Account Management v1.0.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/admin/api_key_issue.yaml", "04_service_definitions/admin/api_key_list.yaml", "04_service_definitions/admin/api_key_revoke.yaml", "08_release_notes/RN-7.2.0 Ledgerline Release Notes.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | SYS-API-14 |
| Name | Service Account Key Key Issue |
| Module | System > Service account |
| Access | IT-ADMIN, SYS-ADMIN |
| Services | api_key_issue, api_key_revoke, api_key_list |
| Status | current |

Screen SYS-API-14 is the Ledgerline administration interface used to issue, list, and revoke service account credentials for background integrations [^r2][^r3][^r8]. It replaces standard passwords for generic system logins, displaying the generated secret key only once upon issue [^r8][^r9]. Issued keys are valid for a maximum of 90 days and must be rotated prior to expiry in accordance with [[sop-it-002|SOP-IT-002]] [^r1].

## Fields

SYS-API-14 contains the following fields:

* **key_id**: Service account key identifier (mandatory) [^r2].
* **comment**: Optional operational remarks or description [^r2].
* **reason**: Optional business justification, also supplied when revoking a credential (optional) [^r2][^r7].
* **user_id**: Target user or account identifier (optional) [^r2].

User profile views display only active state, contact department, and an immediate revocation button [^r9]. Calling integration applications store credentials in secure operating system storage and provide the key in connection headers rather than prompting for passwords [^r11].

## Keys and services

Access to screen SYS-API-14 is restricted to roles IT-ADMIN and SYS-ADMIN under System > Service account [^r2].

The screen binds user actions to services in [[services-adm-api|services-adm-api]]:
* **Key Issue**: Invokes the write service `api_key_issue` via endpoint `POST /ll72/svc/api_key_issue` [^r3][^r4][^r5].
* **Key Revoke**: Invokes the write service `api_key_revoke` using `key_id` and optional `reason` [^r3][^r4][^r7]. If a key is lost or compromised, it cannot be retrieved; issuing a replacement immediately invalidates the superseded credential record [^r10].
* **Key List**: Invokes the read service `api_key_list` to retrieve service account keys [^r3][^r4][^r6].

## Messages

The screen raises the following error codes across its services [^r3][^r4]:
* `ERR-API-0001` [^r3][^r4]
* `ERR-API-0120` [^r3][^r4]

## See also

* [[services-adm-api|services-adm-api]]
* [[sop-it-002|sop-it-002]]

## References

[^r2]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 40, SYS-API-14 SERVICE ACCOUNT KEY KEY ISSUE
[^r3]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 40, SYS-API-14 SERVICE ACCOUNT KEY KEY ISSUE
[^r8]: 08_release_notes/RN-7.2.0 Ledgerline Release Notes.pdf, p. 4, Administration: Service account keys (SYS-API-14)
[^r9]: 08_release_notes/RN-7.2.0 Ledgerline Release Notes.pdf, p. 4, Administration: Service account keys (SYS-API-14)
[^r1]: 02_procedures/SOP-IT-002 Service Account Management v1.0.pdf, p. 3, §5. Procedure
[^r7]: 04_service_definitions/admin/api_key_revoke.yaml, screen
[^r11]: 08_release_notes/RN-7.2.0 Ledgerline Release Notes.pdf, p. 4, Administration: Service account keys (SYS-API-14)
[^r4]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 73, api_key_issue SERVICE ACCOUNT KEY KEY ISSUE
[^r5]: 04_service_definitions/admin/api_key_issue.yaml, screen
[^r10]: 08_release_notes/RN-7.2.0 Ledgerline Release Notes.pdf, p. 4, Administration: Service account keys (SYS-API-14)
[^r6]: 04_service_definitions/admin/api_key_list.yaml, screen
