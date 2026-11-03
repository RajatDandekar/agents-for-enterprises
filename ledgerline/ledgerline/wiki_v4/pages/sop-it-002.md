---
title: "SOP-IT-002 Service Account Management"
type: "procedure"
slug: "sop-it-002"
summary: "SOP governing setup, key issuance, quarterly reviews, and security constraints for non-human Ledgerline ERP service accounts."
audience: "staff"
status: "current"
sources: ["01_policies/POL-ITS-008 IT Security Policy v3.2.pdf", "02_procedures/SOP-IT-002 Service Account Management v1.0.pdf", "03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf", "04_service_definitions/admin/api_key_issue.yaml", "08_release_notes/RN-7.2.0 Ledgerline Release Notes.pdf", "12_integrations/SVC_AGENT integration account - design note.md", "09_email_archive/2026/2026-04-20_SVC_AGENT - audit finding ITS-2026-07.eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | SOP-IT-002 |
| owner | Rhys Pryce |
| approver | Henrik Weber |
| version | 1.0 |
| effective | 2025-09-01 |
| classification | INTERNAL |

SOP-IT-002 defines the governance, security controls, and maintenance lifecycle for automated Ledgerline ERP service accounts [^r3][^r4]. It mandates that every non-human account have a designated permanent staff custodian, operate under least-privilege role assignments, and undergo quarterly audits [^r1][^r6][^r13]. Service accounts are strictly forbidden from approving workflow documents, and an operational freeze currently prevents new integrations from connecting through the legacy generic account [[user-svc-agent|SVC_AGENT]] [^r10][^r22][^r23].

| Field | Value |
|---|---|
| Code | SOP-IT-002 [^r3] |
| Owner | [[user-rpryce|Rhys Pryce]], IT Manager [^r3] |
| Approver | [[user-hweber|Henrik Weber]], Plant Head [^r3] |
| Effective date | 2025-09-01 [^r3] |
| Version | 1.0 [^r3] |
| Classification | INTERNAL [^r3] |

## Steps

### Account Provisioning and Setup
1. Establish a dedicated service credential configured strictly by operational task and location, avoiding shared credentials or generic multi-purpose profiles [^r14][^r18].
2. Designate a named primary custodian within the IT department, a permanent staff owner, and an operational sponsor from the user department [^r1][^r6][^r8][^r20].
3. Compile a written schedule of the exact services, database tables, and screens the account requires to execute its tasks [^r8][^r19].
4. Assign bespoke operational roles offering minimal access rights and appropriate ledger approval ceilings rather than duplicating administrative or standard departmental profiles [^r2][^r13].
5. Disable interactive login privileges as standard practice, ensuring regular staff accounts are never substituted for system jobs [^r5].
6. Generate a complex, non-expiring password and store emergency override credentials directly in the central IT administrative vault rather than on local spreadsheets [^r7][^r14].
7. Configure background interfaces to direct incoming transaction records into discrete staging tables rather than posting straight to live ledgers, ensuring automated validation can trap malformed entries [^r21].

### Key Issuance and Maintenance
1. Access screen [[screen-sys-api-14|SYS-API-14]] to generate API authentication keys under [[rn-7-2-0|Ledgerline ERP 7.2.0]] standards, verifying that the account possesses an assigned owner to prevent [[errors-api|ERR-API-0120]] during invocation of `api_key_issue` [^r15][^r16].
2. Track batch execution and interface audit trails against the distinct service identity rather than individual human credentials [^r17].
3. Enforce key rotation prior to the mandatory 90-day validity expiration date [^r9].

### Auditing and Incident Remediation
1. Run quarterly audit review batch job JOB-SYS-015 to evaluate all active service identities, requiring formal sign-off from the IT manager [^r1][^r11].
2. Verify that service accounts transferring ledger records operate within enforced profile limits and do not possess unrestricted authority across company ledgers [^r2].
3. Inspect document workflows to guarantee compliance with [[pol-apr-002|POL-APR-002]] §4.2, which prohibits any service identity from approving transactions [^r10].
4. Revoke the profile immediately from the approval chain if a service account appears on an authorisation record, promptly reassigning all pending documents to the appropriate managerial queue [^r12].

## Forms and screens

* [[screen-sys-api-14|SYS-API-14]] (Service Account Key Issue): Used to issue and manage 90-day rotated service account keys calling service `api_key_issue` and stored procedure `sp_api_key_issue` [^r9][^r15][^r16].
* JOB-SYS-015: Batch job executed quarterly to audit service account configurations, service scopes, and ownership for IT management sign-off [^r1][^r11].

## Versions and conflicts

* **SVC_AGENT usage freeze (email_overrides_sop)**: Today, a management freeze instituted on 2026-04-20 prohibits any new integration from utilising [[user-svc-agent|SVC_AGENT]] following audit finding ITS-2026-07, which identified that the account had SYS-ADMIN rights, universal service access, and a 1e12 approval limit [^r22][^r23]. Under standard SOP-IT-002 rules, service accounts may be provisioned provided they have a listed owner and defined services [^r8]. New integrations must instead be provisioned with dedicated, least-privilege credentials logging to staging tables [^r18][^r19][^r21].

## See also

* [[pol-apr-002|POL-APR-002 Approval Matrix for Purchasing]]
* [[screen-sys-api-14|SYS-API-14 Service Account Key Issue]]
* [[services-adm-api|ADM api services]]
* [[errors-api|ERR-API Error Codes]]
* [[rn-7-2-0|RN-7.2.0 Ledgerline ERP 7.2.0 Release Notes]]
* [[man-adm-72|MAN-ADM-72 Ledgerline ERP 7.2 System Administration]]
* [[user-svc-agent|Integration service account (SVC_AGENT)]]
* [[user-rpryce|Rhys Pryce (RPRYCE)]]
* [[user-hweber|Henrik Weber (HWEBER)]]

## References

[^r3]: 02_procedures/SOP-IT-002 Service Account Management v1.0.pdf, p. 1, Field
[^r4]: 02_procedures/SOP-IT-002 Service Account Management v1.0.pdf, p. 1, §1. Purpose
[^r1]: 01_policies/POL-ITS-008 IT Security Policy v3.2.pdf, p. 3, §4. Service accounts
[^r6]: 02_procedures/SOP-IT-002 Service Account Management v1.0.pdf, p. 2, §3. Responsibilities
[^r13]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 9, System behaviour and permissions
[^r10]: 02_procedures/SOP-IT-002 Service Account Management v1.0.pdf, p. 3, §5. Procedure
[^r22]: 09_email_archive/2026/2026-04-20_SVC_AGENT - audit finding ITS-2026-07.eml, body
[^r23]: 09_email_archive/2026/2026-04-20_SVC_AGENT - audit finding ITS-2026-07.eml, body
[^r14]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 10, Practical administration tips
[^r18]: 12_integrations/SVC_AGENT integration account - design note.md, Design note
[^r8]: 02_procedures/SOP-IT-002 Service Account Management v1.0.pdf, p. 3, §5. Procedure
[^r20]: 12_integrations/SVC_AGENT integration account - design note.md, Design note
[^r19]: 12_integrations/SVC_AGENT integration account - design note.md, Design note
[^r2]: 01_policies/POL-ITS-008 IT Security Policy v3.2.pdf, p. 3, §4. Service accounts
[^r5]: 02_procedures/SOP-IT-002 Service Account Management v1.0.pdf, p. 1, §1. Purpose
[^r7]: 02_procedures/SOP-IT-002 Service Account Management v1.0.pdf, p. 3, §3. Responsibilities
[^r21]: 12_integrations/SVC_AGENT integration account - design note.md, Design note
[^r15]: 04_service_definitions/admin/api_key_issue.yaml, procedures
[^r16]: 08_release_notes/RN-7.2.0 Ledgerline Release Notes.pdf, p. 4, Administration: Service account keys (SYS-API-14)
[^r17]: 08_release_notes/RN-7.2.0 Ledgerline Release Notes.pdf, p. 4, Administration: Service account keys (SYS-API-14)
[^r9]: 02_procedures/SOP-IT-002 Service Account Management v1.0.pdf, p. 3, §5. Procedure
[^r11]: 02_procedures/SOP-IT-002 Service Account Management v1.0.pdf, p. 3, §5. Procedure
[^r12]: 02_procedures/SOP-IT-002 Service Account Management v1.0.pdf, p. 4, §5. Procedure: notes and common mistakes
