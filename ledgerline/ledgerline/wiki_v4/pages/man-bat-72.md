---
title: "MAN-BAT-72 Ledgerline ERP 7.2 Batch Jobs: Northbridge"
type: "manual"
slug: "man-bat-72"
summary: "Technical reference and operating schedule for Ledgerline ERP 7.2 scheduled batch jobs across procurement, inventory, finance, production, and system administration."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf", "03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf", "03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf", "06_transactions/reports/Draft orders report 2026-10-26.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | MAN-BAT-72 |
| Version | 7.2.3-NBC4 |
| Effective | 2026-09-14 |
| Status | Current |
| Owner | Joanna Fletcher (IT) |

MAN-BAT-72 defines the technical configuration, scheduling, and ownership of automated batch jobs running in Ledgerline ERP 7.2 at Northbridge Cycles [^r4]. As of 26 October 2026, it governs routines across procurement, inventory, accounts payable, sales, manufacturing, and system administration [^r4][^r5][^r11][^r15][^r20][^r24][^r27]. The reference documents operational parameters, service triggers, report mappings, and administrative diagnostic rules for interrupted queues [^r4][^r11][^r33][^r34].

## Scheduled jobs

### Procurement

* **JOB-PUR-014 (Draft orders report)**: Runs daily at 07:00 with parameter `OU=ALL` under owner [[user-dokafor|DOKAFOR]], executing report PUR-R014 ("Draft Orders (Status DR)") to list purchase orders in draft status `DR` along with warning codes before reaching suppliers [^r5][^r34].
* **JOB-PUR-022 (Certificate expiry report)**: Runs monthly on the first working day at 06:00 with parameters `DAYS=90;CERT=UN38.3` under owner [[user-lmoreno|LMORENO]] to report supplier certificates—including [[topic-un-38-3-certificates|UN 38.3 certificates]] under [[sop-pur-005|SOP-PUR-005]]—expiring within a 90-day window [^r1][^r6].
* **JOB-PUR-031 (Rate contract expiry report)**: Runs weekly on Monday at 06:30 with parameter `DAYS=45` under owner DOKAFOR, reporting rate contracts expiring within 45 days [^r7].
* **JOB-PUR-033 (Orders pending approval reminder)**: Runs daily at 08:00 and 14:00 with parameter `AGE_DAYS=2` under owner DOKAFOR, emailing approvers about purchase documents waiting longer than 2 days [^r8].
* **JOB-PUR-040 (Price variance report)**: Runs monthly on the third working day with parameter `TOL_PCT=2` under owner DOKAFOR, extracting released orders where the purchase rate exceeds the contract rate by more than 2 percent [^r9].
* **JOB-PUR-051 (Open orders by supplier)**: Runs weekly on Friday at 16:00 under owner LMORENO, tracking purchase orders in status `AP` or `RL` that are not fully received [^r10].

### Inventory

* **JOB-INV-040 (Items below reorder level)**: Runs daily at 06:15 with parameter `WHS=WH-MAN-STR,WH-LDS-STR` under owner CSHAW, executing the equivalent of service `stk_reorder_list` and dispatching email notifications to buyers [^r11].
* **JOB-INV-044 (Cycle count list)**: Runs daily at 05:45 with parameter `PLAN=CCP-A` under owner CSHAW, extracting warehouse bins due for counting under cycle count plan A [^r12].
* **JOB-INV-050 (Stock valuation)**: Runs monthly on the last calendar day at 23:00 with parameter `METHOD=STD` under owner GWHITAKER to value inventory at standard cost across all warehouses [^r13].
* **JOB-INV-052 (Quality hold ageing)**: Runs daily at 07:30 with parameter `DAYS=3` under owner PJANSEN, reporting inspection receipts held in quality quarantine locations `WH-MAN-QC` or `WH-LDS-QC` longer than 3 days [^r14].

### Accounts payable

* **JOB-AP-010 (Three-way match)**: Runs every 30 minutes from 06:00 to 20:00 with parameters `TOL_PCT=2;TOL_ABS=50` under owner MKOWALSKI, performing matching between posted invoices, purchase orders, and goods receipts [^r15].
* **JOB-AP-030 (Payment proposal)**: Runs Tuesday and Thursday at 10:00 with parameter `BANK=NBC-MAIN` under owner MKOWALSKI to prepare due, matched invoices for the payment run under [[sop-ap-003|SOP-AP-003]] [^r16].
* **JOB-AP-031 (Payment file)**: Runs Tuesday and Thursday at 14:30 with parameter `FORMAT=STD18` under owner MKOWALSKI to generate electronic bank payment output files from approved proposals [^r17].
* **JOB-AP-040 (GRNI accrual)**: Runs monthly on working day 1 at 21:00 under owner GWHITAKER to calculate goods received not invoiced balances [^r18].
* **JOB-AP-045 (VAT reverse-charge listing)**: Runs monthly on working day 2 under owner GWHITAKER, extracting invoices posted to `-RC` tax codes for VAT reporting [^r19].

### Sales and despatch

* **JOB-SAL-010 (EDI inbound orders)**: Runs every 10 minutes with parameter `PARTNER=ALL` under owner IMORGAN to ingest inbound `ORDERS` messages from the EDI mailbox [^r20].
* **JOB-SAL-012 (EDI outbound despatch advice)**: Runs every 10 minutes under owner IMORGAN, generating and transmitting outbound `DESADV` messages for posted despatches [^r21].
* **JOB-SAL-020 (Credit hold report)**: Runs daily at 07:00 under owner IMORGAN, detailing sales orders flagged on credit hold [^r22].
* **JOB-SAL-031 (Carrier manifest)**: Runs daily at 16:45 with parameter `CARRIER=MOORLAND` under owner CSHAW, finalising parcel consignments with Moorland [^r23].

### Manufacturing and quality

* **JOB-PRD-010 (MRP run)**: Runs nightly at 02:00 with parameter `HORIZON=120` under owner SBERG, computing net material requirements and planned manufacturing orders across a 120-day horizon [^r24].
* **JOB-PRD-015 (Backflush)**: Runs hourly under owner SBERG, posting standard component stock issues against completed work orders [^r25].
* **JOB-PRD-022 (Battery end-of-line test upload)**: Runs every 15 minutes with parameter `RIG=BTR-01,BTR-02` under owner PJANSEN, importing automated test rig readings directly into [[screen-qa-btt-03|QA-BTT-03]] [^r26].

### System administration

* **JOB-SYS-001 (Nightly backup)**: Runs daily at 01:30 under owner RPRYCE, executing a database backup that places Ledgerline into a read-only state between 01:30 and 01:50 [^r3][^r27].
* **JOB-SYS-004 (Session clean-up)**: Runs every 5 minutes under owner JFLETCHER to disconnect idle terminals according to the `SYS.SESSION_TIMEOUT` configuration [^r28].
* **JOB-SYS-009 (Notification sender)**: Runs every minute under owner JFLETCHER, processing queued outbound emails and SMS alerts [^r29].
* **JOB-SYS-012 (Audit trail archive)**: Runs monthly on the 1st at 03:00 with parameter `KEEP_MONTHS=84` under owner RPRYCE, migrating audit trail records older than 84 months to the archive schema [^r2][^r30].
* **JOB-SYS-015 (Service account review report)**: Runs quarterly on the first Monday under owner RPRYCE, producing access and utilisation audits for system service accounts in accordance with [[pol-its-008|POL-ITS-008]] [^r31].
* **JOB-SYS-020 (Year-end sequence reset)**: Runs annually on 1 January at 00:05 with parameter `DOC=PR,PO,GRN` under owner JFLETCHER, reinitialising numbering counters for purchase requisitions, orders, and goods receipt notes [^r32].

## Operational handling and diagnostics

When a scheduled batch routine halts or fails, system administrators must open the central job management interface and locate the aborted execution record within queue history [^r33]. The aborted entry must not be cleared or purged from the queue, as the active queue entry preserves the internal execution state and pointer references to diagnostic spool files required for troubleshooting [^r33].

## See also

* [[man-adm-72|MAN-ADM-72 Ledgerline ERP 7.2 System Administration]]
* [[pol-its-008|POL-ITS-008 README ACCESS]]
* [[screen-qa-btt-03|QA-BTT-03 Battery End-Of-Line Test Entry]]
* [[sop-ap-003|SOP-AP-003 Supplier Payment Run]]
* [[sop-pur-005|SOP-PUR-005 Certificate Renewal (UN 38.3)]]
* [[topic-un-38-3-certificates|UN 38.3 Certificates]]

## References

[^r4]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 1, Field
[^r5]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 2, §2. Job details
[^r11]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 3, §2. Job details
[^r15]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 3, §2. Job details
[^r20]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 4, §2. Job details
[^r24]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 4, §2. Job details
[^r27]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 4, §2. Job details
[^r33]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 7, Initial notification and locating the job
[^r34]: 06_transactions/reports/Draft orders report 2026-10-26.pdf, p. 1, LEDGERLINE ERP 7.2 REPORT PUR-R014 DRAFT ORDERS (STATUS DR)
[^r1]: 02_procedures/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf, p. 3, §5. Procedure
[^r6]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 3, §2. Job details
[^r7]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 3, §2. Job details
[^r8]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 3, §2. Job details
[^r9]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 3, §2. Job details
[^r10]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 3, §2. Job details
[^r12]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 3, §2. Job details
[^r13]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 3, §2. Job details
[^r14]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 3, §2. Job details
[^r16]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 3, §2. Job details
[^r17]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 3, §2. Job details
[^r18]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 3, §2. Job details
[^r19]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 4, §2. Job details
[^r21]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 4, §2. Job details
[^r22]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 4, §2. Job details
[^r23]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 4, §2. Job details
[^r25]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 4, §2. Job details
[^r26]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 4, §2. Job details
[^r3]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 10, §9. Backups and maintenance windows
[^r28]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 4, §2. Job details
[^r29]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 4, §2. Job details
[^r2]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 8, Practical operation at Northbridge
[^r30]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 4, §2. Job details
[^r31]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 4, §2. Job details
[^r32]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 5, §2. Job details
