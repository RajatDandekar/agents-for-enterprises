---
title: "Integration service account (SVC_AGENT)"
type: "person"
slug: "user-svc-agent"
summary: "Integration service profile holding SYS-ADMIN role and unbounded approval limits, frozen from new connections following audit finding ITS-2026-07."
audience: "staff"
status: "current"
sources: ["01_policies/POL-APR-002 Approval Matrix v3.0.pdf", "01_policies/POL-ITS-008 IT Security Policy v3.2.pdf", "04_service_definitions/README.md", "12_integrations/Integration inventory.xlsx", "12_integrations/SVC_AGENT integration account - design note.md", "09_email_archive/2026/2026-04-20_SVC_AGENT - audit finding ITS-2026-07.eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| User ID | SVC_AGENT |
| Name | Integration service account |
| Type | Service account |
| Role | SYS-ADMIN |
| Owner | None |
| Status | Active (frozen for new integrations) |

SVC_AGENT is a generic Ledgerline service account created in March 2024 for automated bot operations and integrations [^r6]. Audit finding ITS-2026-07 identified that the account holds the SYS-ADMIN role with access to every service and a nominal 1e12 approval limit [^r2][^r7][^r14]. Under policy and IT management instructions, no purchasing approval authority is recognised for this account, and no new integrations or routines may attach to it while permissions undergo restructuring [^r1][^r3][^r15].

| Field | Value |
|---|---|
| User ID | SVC_AGENT [^r1] |
| Account type | Integration / service account [^r1] |
| Assigned role | SYS-ADMIN [^r2] |
| Named owner | None [^r7] |
| Purchasing approval limit | 0 in policy (system configuration 1e12) [^r1][^r7] |
| Status | Restricted; frozen against new connections [^r3][^r15] |

## Account background and usage

SVC_AGENT was created in March 2024 for an initial bot pilot, configured with the SYS-ADMIN role to call every service temporarily while determining required access [^r6]. It currently connects the bi-directional Purchasing bot pilot interface INT-007 via HTTP services introduced in 2024 [^r5]. The profile is authorised to call all 38 services in the purchasing (PUR) module [^r4].

Because SVC_AGENT has no named owner, retains the SYS-ADMIN role, and connects across every automated service, unscheduled changes or failures can affect core manufacturing, warehouse, and accounting tables without clear accountability [^r7][^r8]. Audit trails log system modifications under the generic SVC_AGENT identifier rather than tracing the specific middleware routine, scheduled batch, or external endpoint [^r10].

## Operational and governance risks

SVC_AGENT has unrestricted read and write permissions across all operational modules, permitting background scripts to alter general ledger postings, stock valuations, and purchase orders without standard validation checks [^r9]. This configuration breaches internal audit standards and insurer segregation of duties requirements because automated feeds can post adjustments that normally require two-party authorisation [^r12].

In day-to-day operations, concurrent routines sharing SVC_AGENT session credentials increase the risk of system lockouts or hung background processes during peak shifts [^r11]. Furthermore, credentials for SVC_AGENT cannot be easily cycled without risking unannounced stoppages of production lines, shipping feeds, or invoice imports [^r13].

## Policy restrictions and audit finding ITS-2026-07

Internal audit finding ITS-2026-07 identified that SVC_AGENT held the SYS-ADMIN role, access to every service, and an approval limit of 1e12 because it was configured that way 'for the bot' [^r2][^r14]. Following this finding on 20 April 2026, IT Manager [[user-rpryce|Rhys Pryce]] instructed that no new integration may use the SVC_AGENT account until its excessive privileges are remediated [^r15].

Under clause 4.2 of [[pol-its-008|POL-ITS-008]], no new integration, script, or external routine may be attached to SVC_AGENT while its permission restructuring review remains open [^r3]. Furthermore, under [[pol-apr-002|POL-APR-002]], integration and service accounts such as SVC_AGENT possess no purchasing approval authority; any document approved by a service account is deemed unapproved and must be re-approved by a person or cancelled [^r1].

## Versions and conflicts

- Today's rule: SVC_AGENT possesses no purchasing approval authority, and any document approved by a service account is deemed unapproved and must be re-approved by a person or cancelled ([[pol-apr-002|POL-APR-002]], 2026-04-01) [^r1].
- System configuration: SVC_AGENT is configured with role SYS-ADMIN and a nominal approval limit of 1e12 (Design note, 2024; Audit finding ITS-2026-07, 2026-04-20) [^r2][^r7][^r14].
- Kind: `contradiction`

## See also

- [[pol-apr-002|POL-APR-002 Approval Matrix for Purchasing]]
- [[pol-its-008|POL-ITS-008 README ACCESS]]
- [[sop-it-002|SOP-IT-002 Service Account Management]]
- [[user-rpryce|Rhys Pryce (RPRYCE)]]
- [[data-integration-inventory|Integration inventory]]
- [[user-edi-gw|EDI gateway account (6.x) (EDI_GW)]]
- [[man-svc-72|MAN-SVC-72 Ledgerline ERP 7.2 Service Reference]]

## References

[^r6]: 12_integrations/SVC_AGENT integration account - design note.md, Design note: the SVC_AGENT integration account (2024)
[^r2]: 01_policies/POL-ITS-008 IT Security Policy v3.2.pdf, p. 4, §4. Service accounts
[^r7]: 12_integrations/SVC_AGENT integration account - design note.md, Design note: the SVC_AGENT integration account (2024)
[^r14]: 09_email_archive/2026/2026-04-20_SVC_AGENT - audit finding ITS-2026-07.eml, body
[^r1]: 01_policies/POL-APR-002 Approval Matrix v3.0.pdf, p. 2, §4. Who may not approve
[^r3]: 01_policies/POL-ITS-008 IT Security Policy v3.2.pdf, p. 4, §4. Service accounts
[^r15]: 09_email_archive/2026/2026-04-20_SVC_AGENT - audit finding ITS-2026-07.eml, body
[^r5]: 12_integrations/Integration inventory.xlsx, sheet Interfaces, row INT-007, SHEET Interfaces
[^r4]: 04_service_definitions/README.md, Ledgerline 7.2 service definitions
[^r8]: 12_integrations/SVC_AGENT integration account - design note.md, Design note
[^r10]: 12_integrations/SVC_AGENT integration account - design note.md, Design note
[^r9]: 12_integrations/SVC_AGENT integration account - design note.md, Design note
[^r12]: 12_integrations/SVC_AGENT integration account - design note.md, Design note
[^r11]: 12_integrations/SVC_AGENT integration account - design note.md, Design note
[^r13]: 12_integrations/SVC_AGENT integration account - design note.md, Design note
