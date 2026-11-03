---
title: "Topic: Terminal and Session Management in Ledgerline"
type: "topic"
slug: "topic-terminal-and-session-management"
summary: "Operational guidelines and controls for managing Ledgerline terminal sessions, licence pool contention, background batch schedules, and abnormal session terminations across sites."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Area | System Administration & Operations |
| Application | Ledgerline ERP 7.2 |
| Primary Reference | [[man-adm-72|MAN-ADM-72]] |
| Key Focus | Session licence retention and process recovery |
| Target Sites | All sites including Leeds |

Terminal and session management governs how user logins, automated batch jobs, and remote connections consume concurrent Ledgerline ERP licence tokens. Proper session release is critical to prevent shop-floor terminal lockouts and prevent data corruption during network instability. System administrators manage active connections and clear hung processes to maintain transactional integrity across Northbridge sites.

## Session Licences and Exit Procedures

Users must log out using the standard exit command in the main menu to immediately return their session token to the licence pool [^r1]. Automated overnight reporting jobs must be scheduled to complete prior to early shift arrival to prevent session licence exhaustion on shop-floor terminals [^r2].

## Process Recovery and WAN Hazards

Orphaned processes resulting from abnormal session closures must be cleared via the process table to safely roll back uncommitted transactions [^r3]. Restarting remote terminal services during WAN slowdowns causes session drops that corrupt active frame stock adjustments and battery serial number allocations in Leeds [^r4].

## See also

* [[man-adm-72|MAN-ADM-72 Ledgerline ERP 7.2 System Administration]]
* [[man-bat-72|MAN-BAT-72 Ledgerline ERP 7.2 Batch Jobs: Northbridge]]
* [[sop-it-002|SOP-IT-002 Service Account Management]]
* [[screen-sys-job-06|SYS-JOB-06 Batch Job Submit]]

## References

[^r1]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 12, §11. Troubleshooting for administrators
[^r2]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 12, §11. Troubleshooting for administrators
[^r3]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 12, Day-to-day operation across sites
[^r4]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 13, Common errors and bad practice
