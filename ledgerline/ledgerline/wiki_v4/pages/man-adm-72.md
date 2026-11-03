---
title: "MAN-ADM-72 Ledgerline ERP 7.2 System Administration"
type: "manual"
slug: "man-adm-72"
summary: "System administration reference manual for Ledgerline ERP 7.2 covering security, parameters, sequences, batch processing, sessions, audit logging, and site operations across Manchester and Leeds."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf", "08_release_notes/RN-7.2.3-P2 Ledgerline Patch Notes.pdf", "11_training/intranet_export_2016/page_ledgerline_tips_and_tricks.html", "10_meeting_notes/2026-03-05 CAB minutes.docx", "09_email_archive/2022/2022-07-04_Ledgerline support contract renewal.eml", "09_email_archive/2026/2026-03-09_Ledgerline patch installed - sessions now time out after 15 minutes.eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | MAN-ADM-72 |
| Owner | IT |
| Version | 7.2.3 |
| Effective date | 2025-01-15 |
| Status | current |
| Target system | Ledgerline ERP 7.2 |

MAN-ADM-72 is the system administration manual for Ledgerline ERP 7.2 governing core infrastructure, user provisioning, batch execution, and system parameters across Northbridge Cycles' Manchester factory and Leeds distribution unit [^r1][^r21][^r38]. It defines operational controls for protecting ledger data integrity, managing database locks across WAN links, and enforcing concurrency limits across client terminals [^r14][^r19][^r21]. As of patch [[rn-7-2-3-p2|7.2.3-P2]], user inactivity timeouts operate at 15 minutes, and administrators must maintain operational procedures without relying on superseded documentation [^r31][^r36][^r41].

## Users, roles and delegation

Each user in Ledgerline ERP 7.2 is assigned exactly one role that controls access to screens, menus, and background services, while individual financial approval limits are recorded directly on the user record instead of the role [^r1]. Approval delegation configured on screen [[screen-sys-dlg-03|SYS-DLG-03]] temporarily redirects a delegator's approval inbox to another nominated user [^r2]. However, the system halts the save operation and raises [[err-dlg-0210|ERR-DLG-0210]] if the selected delegate holds a lower role than the delegator [^r2]. Under patch 7.2.3-P2, locked user accounts are excluded from the default operational user maintenance screen and are displayed in a dedicated locked users report [^r32].

Service accounts operate under the standard user framework, meaning each account is bound to a single role governing service calls and enforces its assigned approval limit [^r10]. If an automated service account attempts an adjustment or stock reallocation exceeding its configured approval ceiling, Ledgerline rejects the transaction immediately and places it into suspense without partial posting [^r11].

## System parameters and document sequences

IT administrators maintain system parameters on [[screen-sys-par-04|SYS-PAR-04]] using the administrative services par_get, par_set, par_list, and par_hist, with every modification captured in the permanent parameter history table [^r3].

Document sequence numbers follow the standard structure PR/<year>/<five digits>, PO/<year>/<five digits>, and GRN/<year>/<five digits> [^r4]. Batch job JOB-SYS-020 initialises each new year's numbering sequence at 00:05 on 1 January [^r4]. Requisitions reserve the next sequential identifier only upon formal submission for approval; draft entries do not consume document numbers [^r5].

## Batch processing and scheduled maintenance

Scheduled batch jobs are catalogued in [[man-bat-72|MAN-BAT-72]] and are submitted, monitored, and cancelled through screen [[screen-sys-job-06|SYS-JOB-06]] [^r6]. Administrators must never terminate running batch tasks via operating system commands, but must cancel them formally within SYS-JOB-06 so that partial postings can roll back cleanly [^r7]. Advancing the system date flag to clear failed overnight batches is prohibited because it bypasses periodic recalculations, standard cost rollovers, and reorder level evaluations, corrupting replenishment suggestions [^r29].

The nightly backup job JOB-SYS-001 runs at 01:30, placing Ledgerline into a read-only state from 01:30 to 01:50 [^r12]. During this window, night shift personnel may query bin locations, assembly lists, and dispatch records, but posting goods receipts, issuing raw materials, or printing dispatch notes is blocked [^r13]. Overnight automated reporting extracts must complete before the early morning shift begins to avoid licence contention with incoming shop-floor users [^r18]. Pending print jobs left in workstation spool queues lock batch processes and slow down overnight production reporting [^r33].

## Audit trail and archiving

Every service call is logged in the audit trail with its timestamp, user id, service name, payload, return code, and error code [^r8]. Audit records older than 84 months are transferred to the archive schema by batch job JOB-SYS-012 [^r8]. Archived records remain intact and retrievable, requiring systems administrators to mount the archive schema in read-only mode to satisfy auditor queries [^r9].

## Session management and multi-site operations

Northbridge Cycles hosts its primary database and application environment in Manchester, while the Leeds distribution facility connects via remote terminal sessions over a wide area network [^r21]. Ledgerline software licences are allocated from a concurrent shared pool where every active client connection, including read-only enquiry sessions, consumes a token [^r14]. Users must log out using the standard main menu exit command to return their session token to the pool [^r15]. Idle sessions must never be left logged in during shift changes or rest breaks, especially on shared terminals in assembly and stores [^r16]. Running multiple enquiry sessions and stock lookups concurrently alongside purchase ledger screens consumes server memory and risks system freezes during large receipting batches [^r34].

When connection limits are reached, administrators must inspect the active session table rather than permitting operators to force entry repeatedly [^r17]. Following patch 7.2.3-P2 and [[decision-2026-03-05-cab-cr-2026-007|CAB decision CR-2026-007]] implemented on 8 March 2026, the SYS.SESSION_TIMEOUT parameter drops idle sessions after 15 minutes of inactivity, safely rolling back uncommitted entries without data corruption [^r31][^r36][^r37][^r41]. Restarting terminal services to address slow screen refreshes in Leeds is prohibited because it terminates all active Leeds sessions, corrupting unfinished frame stock adjustments and battery serial number allocations [^r28].

Northbridge's standard support contract provides routine telephone support, technical desk access for Manchester and Leeds, current release patch updates, and response levels for critical overnight processing failures [^r38][^r40]. In July 2022, Manchester reported batch posting delays and Leeds noted occasional session drops when printing dispatch notes [^r39].

## Concurrency, record locking and troubleshooting

During system outages or degradation, the administrator's operational priority is to protect ledger integrity first, clear physical congestion in despatch and shop-floor areas second, and restore general user access third [^r19]. Administrators must never bypass standard record validation routines to expedite keying [^r20]. Before intervening in reported terminal lockups, administrators must verify whether a lock is genuine or whether a large reporting query is running in the background [^r30]. Users encountering a record lock while editing an order should verify status with Goods Inward or Accounts before logging an IT support call [^r35].

Concurrent bulk goods receipts for frame consignments or motor assemblies run alongside purchase ledger matching routines trigger exclusive locks on supplier ledger partitions [^r22]. When investigating lock contention, administrators must inspect active user sessions from the central console and speak directly with the locking user if active data entry is underway [^r23]. If a locking session has terminated abnormally or been abandoned, administrators clear the orphaned entry from the process table to initiate a clean rollback of deferred updates [^r24]. Arbitrary termination of sessions during batch journal commits leaves ledger tables out of balance and requires sequential transaction log audits [^r26]. Furthermore, clearing locks prematurely on sales orders or despatch notes during picking document generation causes duplicate consignments to be picked and shipped to bike shops [^r27].

On network drops, Ledgerline stops the affected print spooler entirely rather than retrying [^r25]. Administrators must inspect the print queue, purge half-written files, and restart the spooler service manually [^r25].

## Versions and conflicts

- **Inactivity timeout threshold**: Today, idle sessions time out after 15 minutes under parameter SYS.SESSION_TIMEOUT, rolling back uncommitted entries cleanly [^r31][^r36][^r37][^r41]. Under the original text of MAN-ADM-72 v7.2.3 (January 2025), the default idle threshold was 20 minutes [^r31][^r36]. The timeout was reduced to 15 minutes on the evening of 8 March 2026 following [[decision-2026-03-05-cab-cr-2026-007|CAB approval]] and the deployment of patch [[rn-7-2-3-p2|RN-7.2.3-P2]]; vendor manuals were not reissued to reflect this patch update (`superseded`) [^r31][^r36][^r41].

## See also

- [[decision-2026-03-05-cab-cr-2026-007|Decision 2026-03-05 CAB CR-2026-007 Install 7.2.3-P2 and Session Timeout]]
- [[err-dlg-0210|ERR-DLG-0210 Delegate role lower than delegator]]
- [[man-bat-72|MAN-BAT-72 Ledgerline ERP 7.2 Batch Jobs: Northbridge]]
- [[rn-7-2-3-p2|RN-7.2.3-P2 Ledgerline ERP 7.2.3-P2 Patch Notes]]
- [[screen-sys-dlg-03|SYS-DLG-03 Approval Delegation Entry]]
- [[screen-sys-job-06|SYS-JOB-06 Batch Job Submit]]
- [[screen-sys-par-04|SYS-PAR-04 System Parameter]]
- [[services-adm-par|ADM par services]]
- [[sop-it-002|SOP-IT-002 Service Account Management]]
- [[topic-terminal-and-session-management|Topic: Terminal and Session Management in Ledgerline]]

## References

[^r1]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 2, §2. Users and roles
[^r21]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 12, Day-to-day operation across sites
[^r38]: 09_email_archive/2022/2022-07-04_Ledgerline support contract renewal.eml, body
[^r14]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 11, Common Misconceptions
[^r19]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 12, Purpose and scope
[^r31]: 08_release_notes/RN-7.2.3-P2 Ledgerline Patch Notes.pdf, p. 2, §2. Changes
[^r36]: 10_meeting_notes/2026-03-05 CAB minutes.docx, Discussion
[^r41]: 09_email_archive/2026/2026-03-09_Ledgerline patch installed - sessions now time out after 15 minutes.eml, body
[^r2]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 4, §3. Approval delegation
[^r32]: 08_release_notes/RN-7.2.3-P2 Ledgerline Patch Notes.pdf, p. 2, §3. Details
[^r10]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 9, §8. Service accounts
[^r11]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 10, System behaviour and permissions
[^r3]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 5, §4. System parameters
[^r4]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 6, §5. Document sequences
[^r5]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 6, §5. Document sequences
[^r6]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 7, §6. The batch scheduler
[^r7]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 8, Practical guidance
[^r29]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 13, Common errors and bad practice
[^r12]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 10, §9. Backups and maintenance windows
[^r13]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 10, Routine operation across sites
[^r18]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 12, §11. Troubleshooting for administrators
[^r33]: 11_training/intranet_export_2016/page_ledgerline_tips_and_tricks.html, System performance and day-to-day use
[^r8]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 8, §7. The audit trail
[^r9]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 9, Common misunderstandings
[^r15]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 12, §11. Troubleshooting for administrators
[^r16]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 12, §11. Troubleshooting for administrators
[^r34]: 11_training/intranet_export_2016/page_ledgerline_tips_and_tricks.html, System performance and day-to-day use
[^r17]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 12, §11. Troubleshooting for administrators
[^r37]: 10_meeting_notes/2026-03-05 CAB minutes.docx, Discussion
[^r28]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 13, Common errors and bad practice
[^r40]: 09_email_archive/2022/2022-07-04_Ledgerline support contract renewal.eml, body
[^r39]: 09_email_archive/2022/2022-07-04_Ledgerline support contract renewal.eml, body
[^r20]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 12, Purpose and scope
[^r30]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 13, Practical administrator tips
[^r35]: 11_training/intranet_export_2016/page_ledgerline_tips_and_tricks.html, System performance and day-to-day use
[^r22]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 12, Day-to-day operation across sites
[^r23]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 12, Day-to-day operation across sites
[^r24]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 12, Day-to-day operation across sites
[^r26]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 12, Common errors and bad practice
[^r27]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 13, Common errors and bad practice
[^r25]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 12, Day-to-day operation across sites
