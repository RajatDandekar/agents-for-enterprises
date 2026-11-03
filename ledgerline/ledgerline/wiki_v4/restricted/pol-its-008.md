---
title: "POL-ITS-008 README ACCESS"
type: "policy"
slug: "pol-its-008"
summary: "IT Security Policy v3.2 governing Ledgerline passwords, idle timeouts, service accounts, and restricted NBC-HR-CONF confidential document handling."
audience: "hr"
status: "current"
sources: ["01_policies/HR/CONFIDENTIAL/README_ACCESS.txt", "01_policies/POL-ITS-008 IT Security Policy v3.2.pdf", "08_release_notes/NBC_customisations_and_patch_log.xlsx"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | POL-ITS-008 |
| Title | IT Security Policy |
| Owner | IT Department |
| Approver | Rhys Pryce (IT Manager) |
| Version | 3.2 |
| Effective date | 2025-09-01 |
| Status | current |

POL-ITS-008 is Northbridge Cycles' IT Security Policy, currently in force at version 3.2 since 1 September 2025 under the ownership of the IT department and approval of IT Manager Rhys Pryce [^r5]. It establishes mandatory security baselines across the Manchester factory and Leeds unit, including Ledgerline authentication rules, service account governance, and remote VPN requirements [^r5][^r7][^r8][^r15]. Crucially, it sets information classification standards and enforces strict isolation protocols for confidential HR records restricted to the NBC-HR-CONF user group [^r1][^r14].

| Attribute | Value |
|---|---|
| Code | POL-ITS-008 [^r5] |
| Version | 3.2 [^r5] |
| Effective date | 2025-09-01 [^r5] |
| Owner | IT Department [^r5] |
| Approver | Rhys Pryce, IT Manager [^r5] |
| Status | Current [^r5] |

## Clauses

### 1. Scope
The policy applies to all permanent staff, temporary workers, and third-party contractors across the Manchester factory and Leeds unit [^r7]. Version 3.0 was rewritten on 2023-09-01, version 3.1 added multi-factor authentication on 2024-09-01, and version 3.2 established updated password requirements on 2025-09-01 [^r6].

### 2. Passwords
Ledgerline passwords must be at least 12 characters long and expire every 60 days, overriding Ledgerline shipped defaults [^r8]. This configuration was applied in Ledgerline on 1 September 2025 under customisation log entry NBC-2025-009 [^r17].

### 3. Sessions and sign-in
Ledgerline monitors activity and automatically closes idle sessions after 15 minutes, controlled by parameter SYS.SESSION_TIMEOUT [^r9]. Entering three wrong passwords locks a Ledgerline user ID for 30 minutes [^r10].

### 4. Service accounts
Every service account must have a named owner, hold only the services it needs, and undergo quarterly review under batch job JOB-SYS-015 [^r11]. Under audit finding ITS-2026-07, integration account SVC_AGENT holds role SYS-ADMIN with every service and no approval limit; until its restructuring review closes, no new integration may use it [^r12].

### 5. Information classification
Northbridge documents default to INTERNAL unless marked CONFIDENTIAL [^r13]. Confidential HR documents must be stored only in the restricted HR folder readable solely by the HR group NBC-HR-CONF, and must never be loaded into systems serving other staff [^r14]. Handling instructions specify that access is strictly restricted to members of the NBC-HR-CONF group, and users are prohibited from copying, forwarding, or indexing files stored in this confidential HR folder [^r1][^r3][^r4]. Anyone who can read the files without being in HR must notify the IT service desk at extension 2210 and immediately close the folder [^r2][^r4].

### 6. Remote access
Remote access to Ledgerline requires connecting via the company VPN combined with multi-factor authentication [^r15].

### 7. Reporting incidents
Suspected security incidents must be reported immediately to the IT service desk on extension 2210 [^r16].

## See also

## References

[^r5]: 01_policies/POL-ITS-008 IT Security Policy v3.2.pdf, p. 1, §1. Scope
[^r7]: 01_policies/POL-ITS-008 IT Security Policy v3.2.pdf, p. 1, §1. Scope
[^r8]: 01_policies/POL-ITS-008 IT Security Policy v3.2.pdf, p. 1, §2. Passwords
[^r15]: 01_policies/POL-ITS-008 IT Security Policy v3.2.pdf, p. 5, §6. Remote access
[^r1]: 01_policies/HR/CONFIDENTIAL/README_ACCESS.txt, whole file
[^r14]: 01_policies/POL-ITS-008 IT Security Policy v3.2.pdf, p. 4, §5. Information classification
[^r6]: 01_policies/POL-ITS-008 IT Security Policy v3.2.pdf, p. 1, Version history
[^r17]: 08_release_notes/NBC_customisations_and_patch_log.xlsx, sheet Log, row NBC-2025-009, SHEET Log
[^r9]: 01_policies/POL-ITS-008 IT Security Policy v3.2.pdf, p. 2, §3. Sessions and sign-in
[^r10]: 01_policies/POL-ITS-008 IT Security Policy v3.2.pdf, p. 2, §3. Sessions and sign-in
[^r11]: 01_policies/POL-ITS-008 IT Security Policy v3.2.pdf, p. 3, §4. Service accounts
[^r12]: 01_policies/POL-ITS-008 IT Security Policy v3.2.pdf, p. 3, §4. Service accounts
[^r13]: 01_policies/POL-ITS-008 IT Security Policy v3.2.pdf, p. 4, §5. Information classification
[^r3]: 01_policies/HR/CONFIDENTIAL/README_ACCESS.txt, whole file
[^r4]: 01_policies/HR/CONFIDENTIAL/README_ACCESS.txt, whole file
[^r2]: 01_policies/HR/CONFIDENTIAL/README_ACCESS.txt, whole file
[^r16]: 01_policies/POL-ITS-008 IT Security Policy v3.2.pdf, p. 5, §7. Reporting incidents
