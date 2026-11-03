---
title: "Ledgerline ERP Backup Windows and Read-Only Mode"
type: "topic"
slug: "topic-backup-window"
summary: "Operational restrictions, read-only mode behaviour, and staff cut-off procedures during the scheduled Ledgerline ERP overnight backup window."
audience: "staff"
status: "current"
sources: ["09_email_archive/2026/2026-02-15_Ledgerline read-only during backup window.eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| System | Ledgerline ERP |
| Operating state | Read-only mode |
| Frequency | Overnight scheduled |
| Write access | Blocked |
| Read access | Permitted (search, view stock, account lookup) |

During the scheduled backup window, Ledgerline ERP operates in a restricted read-only state to safeguard data integrity while overnight maintenance runs [^r1]. Users can still view records and stock levels, but all transactional writes and record saves are completely blocked [^r1][^r2][^r3]. Staff must ensure all daily transactions, batch postings, and print requests are finalised and closed prior to the backup commencement [^r4][^r5][^r6].

## System behaviour during backup

During the scheduled backup window, Ledgerline is placed into read-only mode, permitting users to log in, search records, view stock levels, and look up customer accounts [^r1]. While Ledgerline is in read-only mode, users cannot save changes, raise purchase orders, post invoices, or update works orders [^r2]. Any attempt to write to the database or post transactions while the backup is running is blocked by the system, resulting in the loss of unsaved work [^r3]. Normal read and write access to Ledgerline is restored as soon as the overnight backup routine completes [^r7].

## Operating procedures and cut-offs

Staff working late must post all pending batches, save open records, and close active entry sessions before the scheduled backup begins [^r4]. Keeping open transaction screens during the backup window can hold locks on database tables and cause the backup routine to fail [^r5]. Dispatch staff must print all picking lists and dispatch notes needed for early morning collections prior to the backup cut-off [^r6].

## See also

## References

[^r1]: 09_email_archive/2026/2026-02-15_Ledgerline read-only during backup window.eml, body
[^r2]: 09_email_archive/2026/2026-02-15_Ledgerline read-only during backup window.eml, body
[^r3]: 09_email_archive/2026/2026-02-15_Ledgerline read-only during backup window.eml, body
[^r4]: 09_email_archive/2026/2026-02-15_Ledgerline read-only during backup window.eml, body
[^r5]: 09_email_archive/2026/2026-02-15_Ledgerline read-only during backup window.eml, body
[^r6]: 09_email_archive/2026/2026-02-15_Ledgerline read-only during backup window.eml, body
[^r7]: 09_email_archive/2026/2026-02-15_Ledgerline read-only during backup window.eml, body
