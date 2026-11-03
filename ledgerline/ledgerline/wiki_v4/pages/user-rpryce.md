---
title: "Rhys Pryce (RPRYCE)"
type: "person"
slug: "user-rpryce"
summary: "IT Manager responsible for systems security, IT policies and SOPs, change approvals, service account governance, and network infrastructure at Northbridge Cycles."
audience: "staff"
status: "current"
sources: ["01_policies/POL-ITS-008 IT Security Policy v3.2.pdf", "02_procedures/SOP-IT-001 User Access Request v1.6.pdf", "02_procedures/SOP-IT-002 Service Account Management v1.0.pdf", "08_release_notes/NBC_customisations_and_patch_log.xlsx", "10_meeting_notes/2022-03-03 Production planning meeting.docx", "10_meeting_notes/2022-10-16 Weekly purchasing meeting.docx", "10_meeting_notes/2024-05-08 Leeds unit update.docx", "10_meeting_notes/2026-03-05 CAB minutes.docx", "10_meeting_notes/2026-06-10 Health and safety committee.docx", "09_email_archive/2019/2019-01-16_Planned network outage.eml", "09_email_archive/2019/2019-05-02_Phishing e-mails pretending to be suppliers.eml", "09_email_archive/2026/2026-01-18_Old 6.x gateway still in use.eml", "09_email_archive/2026/2026-04-20_SVC_AGENT - audit finding ITS-2026-07.eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| User ID | RPRYCE |
| Name | Rhys Pryce |
| Role | IT Manager |
| Status | Active |
| Department | IT |
| Document owner | POL-ITS-008, SOP-IT-001, SOP-IT-002 |

Rhys Pryce is the IT Manager at Northbridge Cycles, responsible for internal IT infrastructure, access management, and systems governance [^r1][^r2]. He is the author and document owner of IT policies and operating procedures, including user onboarding and service account controls [^r1][^r2][^r3]. Pryce also oversees Change Advisory Board (CAB) releases and security compliance across Manchester and Leeds operations [^r4][^r8][^r14][^r15].

## Responsibilities and policy ownership

Pryce authored and approved [[pol-its-008|POL-ITS-008]] (version 3.2) on 1 September 2025 [^r1]. He is the designated document owner of [[sop-it-001|SOP-IT-001]] User Access Request [^r2]. Under [[sop-it-002|SOP-IT-002]], he owns the procedure and holds responsibility for signing off quarterly service account reviews (JOB-SYS-015) [^r3].

## Systems governance and Change Advisory Board

Pryce acts as an owner on change management decisions, including the 5 March 2026 [[decision-2026-03-05-cab-cr-2026-007|CAB decision CR-2026-007]] which approved installing [[rn-7-2-3-p2|7.2.3-P2]] and shortening the system session timeout to 15 minutes [^r8]. On 7 October 2026, he logged CAB CR-2026-031 in the [[data-nbc-change-log|NBC_customisations_and_patch_log.xlsx]] master log, confirming that PUR.CERT_CHK was not enabled, with its review scheduled for January 2027 [^r4].

On 18 January 2026, Pryce flagged that automated polling for dispatch notes between Leeds and Manchester remained active on the legacy 6.x gateway and instructed [[user-jfletcher|Joanna Fletcher]] to plan its decommissioning [^r14]. On 20 April 2026, following internal audit finding ITS-2026-07 regarding [[user-svc-agent|SVC_AGENT]] holding the SYS-ADMIN role, full service access, and an approval limit of 1e12, Pryce alerted [[user-hweber|Henrik Weber]] and Fletcher, directing that no new integration may use the SVC_AGENT account until the audit finding is resolved [^r15][^r16].

## Meeting attendance and communications

Pryce regularly represents IT in cross-functional operations and safety governance:
* On 3 March 2022, he was recorded as present and listed as the owner of the production planning meeting [^r5].
* On 16 October 2022, he attended and was listed as the owner of the [[decision-2022-10-16-purchasing-meeting|weekly purchasing meeting]] [^r6].
* On 8 May 2024, he attended the [[decision-2024-05-08-leeds-unit-update|Leeds unit update meeting]] [^r7].
* On 10 June 2026, he attended the Health and Safety Committee meeting [^r9].

In staff-wide IT operational directives, Pryce notified Manchester staff on 16 January 2019 regarding scheduled switch maintenance suspending network access across the factory floor and offices, instructing personnel to save work, close sessions, and power down workstations to prevent locked records upon reconnection [^r10][^r11]. On 2 May 2019, he issued a security notice concerning phishing emails impersonating suppliers, directing staff to forward suspicious messages as attachments to the systems desk, delete them, and purge their deleted items folders [^r12][^r13].

## See also

* [[data-nbc-change-log|NBC_customisations_and_patch_log]]
* [[pol-its-008|POL-ITS-008 README ACCESS]]
* [[sop-it-001|SOP-IT-001 User Access Request]]
* [[sop-it-002|SOP-IT-002 Service Account Management]]
* [[decision-2026-03-05-cab-cr-2026-007|Decision 2026-03-05 CAB CR-2026-007 Install 7.2.3-P2 and Session Timeout]]
* [[rn-7-2-3-p2|RN-7.2.3-P2 Ledgerline ERP 7.2.3-P2 Patch Notes]]
* [[topic-leeds-manchester-gateway|Leeds to Manchester Data Transfer Gateway]]
* [[user-jfletcher|Joanna Fletcher]]
* [[user-hweber|Henrik Weber]]
* [[user-svc-agent|Integration service account (SVC_AGENT)]]

## References

[^r1]: 01_policies/POL-ITS-008 IT Security Policy v3.2.pdf, p. 1, §1. Scope
[^r2]: 02_procedures/SOP-IT-001 User Access Request v1.6.pdf, p. 1, Field Value
[^r3]: 02_procedures/SOP-IT-002 Service Account Management v1.0.pdf, p. 3, §5. Procedure
[^r4]: 08_release_notes/NBC_customisations_and_patch_log.xlsx, sheet Log, row NBC-2026-021, SHEET Log
[^r8]: 10_meeting_notes/2026-03-05 CAB minutes.docx, Discussion
[^r14]: 09_email_archive/2026/2026-01-18_Old 6.x gateway still in use.eml, Subject: Old 6.x gateway still in use
[^r15]: 09_email_archive/2026/2026-04-20_SVC_AGENT - audit finding ITS-2026-07.eml, body
[^r16]: 09_email_archive/2026/2026-04-20_SVC_AGENT - audit finding ITS-2026-07.eml, body
[^r5]: 10_meeting_notes/2022-03-03 Production planning meeting.docx, Production planning meeting
[^r6]: 10_meeting_notes/2022-10-16 Weekly purchasing meeting.docx, Weekly purchasing meeting
[^r7]: 10_meeting_notes/2024-05-08 Leeds unit update.docx, Leeds unit update
[^r9]: 10_meeting_notes/2026-06-10 Health and safety committee.docx, Health and safety committee
[^r10]: 09_email_archive/2019/2019-01-16_Planned network outage.eml, Planned network outage
[^r11]: 09_email_archive/2019/2019-01-16_Planned network outage.eml, Planned network outage
[^r12]: 09_email_archive/2019/2019-05-02_Phishing e-mails pretending to be suppliers.eml, Subject: Phishing e-mails pretending to be suppliers
[^r13]: 09_email_archive/2019/2019-05-02_Phishing e-mails pretending to be suppliers.eml, Subject: Phishing e-mails pretending to be suppliers
