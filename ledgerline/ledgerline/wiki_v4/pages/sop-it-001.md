---
title: "SOP-IT-001 User Access Request"
type: "procedure"
slug: "sop-it-001"
summary: "Standard operating procedure governing Ledgerline ERP user access provisioning, role assignments, default cost centres, and periodic manager access reviews."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-FIN-001 Cost Centre Open and Close v1.1.pdf", "02_procedures/SOP-IT-001 User Access Request v1.6.pdf", "09_email_archive/2019/2019-08-07_New starters in purchasing.eml", "09_email_archive/2026/2026-04-23_Password change reminder.eml", "09_email_archive/2026/2026-07-15_User access review.eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Document code | SOP-IT-001 |
| Title | User Access Request |
| Owner | [[user-rpryce|Rhys Pryce]] |
| Approver | [[user-hweber|Henrik Weber]] |
| Effective date | 2025-09-01 |
| Status | current |
| Version | 1.6 |

SOP-IT-001 defines the procedure for provisioning, updating, and reviewing Ledgerline ERP user accounts across Northbridge Cycles [^r2][^r3]. It enforces single-role assignments aligned with business functions, controls authorization limits, and mandates explicit department head confirmation for sensitive transactional capabilities [^r4][^r7]. The procedure also sets out requirements for updating closed cost centres and executing mandatory six-monthly manager access reviews across sites [^r5][^r6][^r16].

| Field | Value |
|---|---|
| Document code | SOP-IT-001 |
| Title | User Access Request |
| Owner | [[user-rpryce|Rhys Pryce]] |
| Approver | [[user-hweber|Henrik Weber]] |
| Effective date | 2025-09-01 |
| Status | current |
| Version | 1.6 |

## Steps

### Requesting and provisioning access
Staff must request Ledgerline ERP access using form NBC-F-031, signed by their line manager [^r3]. Access to financial postings, purchase order approval, and inventory adjustments requires explicit confirmation from the relevant department head before credentials are issued [^r7]. IT assigns exactly one role per user to match their job responsibilities, with approval limits configured according to [[pol-apr-002|POL-APR-002]] [^r4]. Standard buyer user setup in Ledgerline ERP is provisioned by cloning an existing buyer template profile and adding the account to the purchasing user group [^r9]. Purchasing workstations require mapping to the purchasing template directory and access configured to the shared supplier correspondence mailbox [^r10].

### Default cost centre maintenance
Default cost centres are configured in Ledgerline ERP by IT and do not update automatically when Finance closes a cost centre [^r1][^r5]. In accordance with [[sop-fin-001|SOP-FIN-001]], cost centre owners must submit an amendment request on form NBC-F-031 to IT to update user default cost centres following a closure [^r1][^r5].

### Credential security and workstation usage
Users must choose password phrases that have not been used previously, are not obvious, and are not shared across personal accounts [^r11]. Staff must not write login credentials down on pads by terminals, leave notes under keyboards, or disclose credentials to colleagues or shop floor visitors under any circumstances [^r12]. Staff sharing designated workstations on assembly lines and packing benches must log out completely at shift end or when stepping away for tea breaks to prevent stock booking and shop floor progress discrepancies [^r13]. Team leaders must not log in under their own names on behalf of other staff, as every transaction against an order or purchase line must trace back to the individual performing the work [^r15]. Users locked out after multiple attempts must contact the internal systems office for a temporary reset issued in person upon identity verification [^r14].

### Periodic access reviews
Each manager must review user access rights every six months [^r6]. Routine reviews of user accounts on the system cover both the Manchester works and the unit in Leeds to confirm active profile access rights match current duties [^r16]. Departmental user access reviews require managers to check whether leavers or staff who transferred between the workshop, stores, or office retain unneeded permissions, and to ensure supervisory posting rights are restricted to current sign-off holders [^r17]. Managers submit account removals, suspensions, or modifications either by marking the active profile printout sheets or by returning adjustments via email before master records are updated [^r18]. Regular verification evidence from the user access review must be completed and retained for external auditors [^r19].

## Forms and screens

### Forms
* **NBC-F-031 (User Access Request Form)**: Paper form signed by the line manager to request new Ledgerline user accounts, role amendments, and updates to default cost centres [^r3][^r5]. Completed access request paper forms are filed in the central filing cabinet in the server room, electronic copies are saved in a secure network administration folder, and administrators log a cross-reference on the user profile [^r8].
* **Active Profile Printout Sheets**: Profile printout lists distributed during periodic departmental access reviews for managers to mark account adjustments, suspensions, or removals [^r18].

### Screens
* IT administrators manage user profiles, role assignments, and default cost centre settings directly within Ledgerline ERP administration [^r4][^r5][^r8].

## Versions and conflicts

* **Manager access review adjustment submission**: Today, managers may submit account removals, suspensions, or modifications during routine user access reviews either by marking the active profile printout sheets or by returning adjustments via email before master records are updated (email from 2026-07-15) [^r18]. SOP-IT-001 v1.6 (§5, effective 2025-09-01) specifies that access requests and default cost centre amendments must be submitted via signed form NBC-F-031 (`email_overrides_sop`) [^r3][^r5].

## See also

* [[pol-apr-002|POL-APR-002 Approval Matrix for Purchasing]]
* [[sop-fin-001|SOP-FIN-001 Cost Centre Open and Close]]
* [[user-rpryce|Rhys Pryce]]
* [[user-hweber|Henrik Weber]]

## References

[^r2]: 02_procedures/SOP-IT-001 User Access Request v1.6.pdf, p. 1, Field Value
[^r3]: 02_procedures/SOP-IT-001 User Access Request v1.6.pdf, p. 3, §5. Procedure
[^r4]: 02_procedures/SOP-IT-001 User Access Request v1.6.pdf, p. 3, §5. Procedure
[^r7]: 02_procedures/SOP-IT-001 User Access Request v1.6.pdf, p. 1, §1. Purpose
[^r5]: 02_procedures/SOP-IT-001 User Access Request v1.6.pdf, p. 3, §5. Procedure
[^r6]: 02_procedures/SOP-IT-001 User Access Request v1.6.pdf, p. 3, §5. Procedure
[^r16]: 09_email_archive/2026/2026-07-15_User access review.eml, body
[^r9]: 09_email_archive/2019/2019-08-07_New starters in purchasing.eml, body
[^r10]: 09_email_archive/2019/2019-08-07_New starters in purchasing.eml, body
[^r1]: 02_procedures/SOP-FIN-001 Cost Centre Open and Close v1.1.pdf, p. 4, What to do when something does not look right
[^r11]: 09_email_archive/2026/2026-04-23_Password change reminder.eml, body
[^r12]: 09_email_archive/2026/2026-04-23_Password change reminder.eml, body
[^r13]: 09_email_archive/2026/2026-04-23_Password change reminder.eml, body
[^r15]: 09_email_archive/2026/2026-04-23_Password change reminder.eml, body
[^r14]: 09_email_archive/2026/2026-04-23_Password change reminder.eml, body
[^r17]: 09_email_archive/2026/2026-07-15_User access review.eml, body
[^r18]: 09_email_archive/2026/2026-07-15_User access review.eml, body
[^r19]: 09_email_archive/2026/2026-07-15_User access review.eml, body
[^r8]: 02_procedures/SOP-IT-001 User Access Request v1.6.pdf, p. 4, §6. Records
