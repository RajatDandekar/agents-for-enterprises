---
title: "SOP-PUR-004 Rate Contract Maintenance"
type: "procedure"
slug: "sop-pur-004"
summary: "Standard operating procedure for setting up, reviewing, and amending supplier rate contracts in Ledgerline ERP across Manchester and Leeds sites."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-PUR-004 Rate Contract Maintenance v2.0.pdf", "09_email_archive/2019/2019-09-09_Rate contract review in March.eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | SOP-PUR-004 |
| Title | Rate Contract Maintenance |
| Version | v2.0 |
| Effective date | 2024-03-01 |
| Owner | Purchasing Manager |
| Status | current |
| Scope | Manchester works and Leeds unit |

SOP-PUR-004 governs the setup, ongoing review, and amendment of agreed supplier rate contracts in Ledgerline ERP across the Manchester works and Leeds unit [^r2]. Rate contracts ensure that standard components, frame materials, and sub-assemblies pull correct pricing directly into purchase orders without manual entry [^r1]. Under current procedure, existing rate contract lines must never be edited directly; instead, lines are closed and replaced under [[role-pur-mgr|role PUR-MGR]] to prevent overlapping validity and automated pricing errors [^r7][^r9][^r11].

| Field | Value |
|---|---|
| Code | SOP-PUR-004 |
| Version | v2.0 |
| Effective date | 2024-03-01 |
| Status | current |
| Document owner | Purchasing Manager |

## Responsibilities

* **Purchasing Manager:** Holds overall commercial responsibility for negotiating agreements, confirming annual price settlements, and authorising rate revisions on the system [^r3].
* **Buyers:** Enter agreed schedules, set validity windows, attach lead times, and update unit costs once signed agreements arrive from vendors [^r4]. Ahead of annual supplier negotiations, buyers verify unit rates in Ledgerline against signed paper agreements for both Manchester and Leeds [^r17]. When agreements are superseded, buyers archive the signed agreement, correspondence, and revised rate printout in the central procurement archive [^r14].
* **Purchase Ledger Clerks:** Monitor matching variances caused by rate discrepancies, route queries back to buyers, and ensure no disputed invoice is passed for payment until the master record is corrected or credit agreed [^r5].
* **Stores Personnel:** Hold no write access to rates at Manchester or Leeds, but book in receipts against the correct scheduled line so deliveries inherit prevailing contract terms [^r6].

## Steps

### 1. Pricing structure and preparation
* Separate fluctuating freight elements and carriage surcharges from the standard piece price so the ledger reflects true manufacturing costs [^r16].
* Verify that unit rates match physical signed contracts on file prior to entering or amending schedules [^r17]. Generating purchase orders with outdated rate cards causes matching holds on supplier invoices [^r15].

### 2. Contract creation and validity
* Access the Rate contracts tab on the supplier master using [[role-pur-mgr|role PUR-MGR]] in the purchase manager's office [^r7].
* Set the valid-from date for the new contract line [^r9]. Rate contracts run for at most 12 months, with most running from 1 April to 31 March, while contracts for [[items-bat|battery packs]] may run for six months [^r8].
* Ensure all relevant production components, frame hardware, electrical assemblies, or recurring workshop consumables are assigned to the schedule [^r2].

### 3. Rate revisions and amendments
* Terminate the previous contract line prior to creating replacement lines [^r11]. Staff must never change the rate on an existing contract line, but must end the line and add a new line [^r9].
* Do not allow overlapping validity windows, as Ledgerline ERP does not always block overlapping entries automatically, which causes unpredictable pricing on automated purchase orders [^r11].
* If an overlapping validity period or incorrect rate has already been saved and applied to live purchase orders, notify the purchase manager immediately [^r12]. Never delete the historical row, as deleting damages transaction logs [^r12].

### 4. Periodic review and reporting
* Review rate contracts bi-annually in March and September per [[pol-sup-003|POL-SUP-003]] §7.3 [^r10].
* Run the rate-contract expiry report (JOB-PUR-031) to identify all contracts ending within 45 days [^r10].

## Forms and screens

* **Supplier Master (Rate contracts tab):** Maintenance interface for entering schedules, validity windows, lead times, and unit rates under [[role-pur-mgr|role PUR-MGR]] [^r4][^r7].
* **JOB-PUR-031:** Batch report listing rate contracts due to expire within 45 days [^r10].
* **Records retention:** The buying team at Manchester holds the definitive master file for each supplier agreement, while the Leeds unit maintains local copies for parts called off directly into their assembly store [^r13]. Central archiving requires the signed agreement, vendor correspondence, and system printout of revised rates [^r14].

## See also

* [[pol-sup-003|POL-SUP-003 Supplier Policy]]
* [[role-pur-mgr|Role PUR-MGR]]
* [[items-bat|BAT-* items]]

## References

[^r2]: 02_procedures/SOP-PUR-004 Rate Contract Maintenance v2.0.pdf, p. 2, §2. Scope
[^r1]: 02_procedures/SOP-PUR-004 Rate Contract Maintenance v2.0.pdf, p. 1, §1. Purpose
[^r7]: 02_procedures/SOP-PUR-004 Rate Contract Maintenance v2.0.pdf, p. 3, §5. Procedure
[^r9]: 02_procedures/SOP-PUR-004 Rate Contract Maintenance v2.0.pdf, p. 3, §5. Procedure
[^r11]: 02_procedures/SOP-PUR-004 Rate Contract Maintenance v2.0.pdf, p. 3, §5. Procedure: notes and common mistakes
[^r3]: 02_procedures/SOP-PUR-004 Rate Contract Maintenance v2.0.pdf, p. 2, §3. Responsibilities
[^r4]: 02_procedures/SOP-PUR-004 Rate Contract Maintenance v2.0.pdf, p. 2, §3. Responsibilities
[^r17]: 09_email_archive/2019/2019-09-09_Rate contract review in March.eml, body
[^r14]: 02_procedures/SOP-PUR-004 Rate Contract Maintenance v2.0.pdf, p. 4, §6. Records
[^r5]: 02_procedures/SOP-PUR-004 Rate Contract Maintenance v2.0.pdf, p. 2, §3. Responsibilities
[^r6]: 02_procedures/SOP-PUR-004 Rate Contract Maintenance v2.0.pdf, p. 2, §3. Responsibilities
[^r16]: 09_email_archive/2019/2019-09-09_Rate contract review in March.eml, body
[^r15]: 09_email_archive/2019/2019-09-09_Rate contract review in March.eml, body
[^r8]: 02_procedures/SOP-PUR-004 Rate Contract Maintenance v2.0.pdf, p. 3, §5. Procedure
[^r12]: 02_procedures/SOP-PUR-004 Rate Contract Maintenance v2.0.pdf, p. 4, §5. Procedure: notes and common mistakes
[^r10]: 02_procedures/SOP-PUR-004 Rate Contract Maintenance v2.0.pdf, p. 3, §5. Procedure
[^r13]: 02_procedures/SOP-PUR-004 Rate Contract Maintenance v2.0.pdf, p. 4, §6. Records
