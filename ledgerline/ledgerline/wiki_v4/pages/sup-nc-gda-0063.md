---
title: "Nordic Cell Co. (NC-GDA-0063)"
type: "supplier"
slug: "sup-nc-gda-0063"
summary: "Active battery supplier NC-GDA-0063 with a 2026-27 BAT-500 rate contract, currently under an order hold due to an expired UN 38.3 test report."
audience: "staff"
status: "mixed"
sources: ["05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx", "05_master_data/SUPPLIER_MASTER.xlsx", "05_master_data/supplier_master_EXPORT_2024.csv", "10_meeting_notes/2026-10-19 Weekly purchasing meeting.md", "09_email_archive/2026/2026-09-29_UN 38.3 report renewal.eml", "09_email_archive/2026/2026-10-01_CERT EXPIRED - DO NOT ORDER_ Nordic Cell Co. (NC-GDA-0063).eml", "06_transactions/PO_extract_2026-01_to_2026-10.xlsx", "06_transactions/reports/Certificate expiry report 2026-10-01.pdf", "06_transactions/reports/PO register 2026-05 (printed).pdf", "06_transactions/reports/PO register 2026-06 (printed).pdf", "06_transactions/reports/Supplier listing 2026-10 (printed).pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Supplier code | NC-GDA-0063 |
| Name | Nordic Cell Co. |
| Status | ACTIVE (purchasing frozen for regulated items) |
| Location | Gdańsk, Poland |
| VAT number | PL5842736190 |
| Payment terms | N45 |
| Contact | Agnieszka Nowak (orders@nc-gda-0063.example) |

Nordic Cell Co. (NC-GDA-0063) is an active battery supplier based in Gdańsk, Poland, holding an active rate contract for battery pack [[items-bat|BAT-500]] [^r1][^r3]. Although the vendor remains marked as active in Ledgerline, purchasing activities for lithium cells are under an immediate hold because its [[topic-un-38-3-certificates|UN 38.3]] transport certificate expired on 30 September 2026 [^r12][^r13][^r16][^r17]. Replacement test documentation is delayed by the testing laboratory until late November 2026, and no purchase orders may be placed until verified compliance documentation is recorded [^r13][^r14][^r17].

## Record

Nordic Cell Co. is registered under supplier code NC-GDA-0063 in Gdańsk, Poland, with status ACTIVE, VAT number PL5842736190, and payment terms N45 [^r3][^r11]. The primary contact is Agnieszka Nowak at orders@nc-gda-0063.example [^r3]. In Ledgerline purchase order history, purchase order PO/2026/00590 was placed on 4 May 2026 for 1,200 units of BAT-500 at £111.00 each (£133,200.00 basic value, £159,840.00 gross under VAT20-RC) allocated to cost centre [[cc-prd-04|PRD-04]] [^r5][^r9]. Purchase order PO/2026/00805 was placed on 16 June 2026 by [[user-lmoreno|Luis Moreno]] for 1,800 units of BAT-500 at £111.00 each (£199,800.00 basic value, £239,760.00 gross under VAT20-RC) for cost centre [[cc-prd-05|PRD-05]] with status CL [^r6][^r10]. Recorded order spend with the vendor totaled £159,840 in May 2026 and £239,760 in June 2026, with zero spend across all other months between January and October 2026 [^r7].

## Certificates

Nordic Cell Co. held UN 38.3 certificate reference UN38.3-TR/NC/2025/090, issued on 26 September 2025 and uploaded by Luis Moreno on 1 October 2025, which expired on 30 September 2026 [^r4][^r8][^r16]. The expiration of this quality certificate triggered an immediate freeze on purchasing activities for regulated items under [[sop-pur-001|SOP-PUR-001]] [^r12]. While Agnieszka Nowak requested that Northbridge Cycles continue placing orders during the interim delay, no purchase orders for lithium cells are permitted until renewed compliance documentation is approved and uploaded [^r13][^r15][^r17].

## Rate contracts

For the 2026-27 contract year, Nordic Cell Co. holds a contracted rate of £111.00 per unit for BAT-500, valid from 1 April 2026 to 31 March 2027 [^r1][^r17]. Under the prior 2025-26 contract period, the vendor held a rate contract for BAT-500 at £108.00 per unit, valid from 1 April 2025 to 31 March 2026 [^r2].

## Notes

Nordic Cell's updated UN 38.3 test report was delayed by the testing laboratory and is expected in late November 2026 [^r14]. Formal purchasing instructions issued on 1 October 2026 confirmed that despite the vendor's active master status and current rate contract, no lithium-cell orders may be placed until the replacement report is uploaded and verified [^r17].

## Versions and conflicts

- Today's rule: Nordic Cell Co. holds an active rate contract for BAT-500 at £111.00 per unit for 2026-27 (valid 2026-04-01 to 2027-03-31) [^r1]. In 2025-26, the contracted rate was £108.00 per unit (valid 2025-04-01 to 2026-03-31) [^r2]. Kind: superseded.
- Today's rule: Nordic Cell Co.'s active master record is maintained in [[data-supplier-master|SUPPLIER_MASTER.xlsx]] [^r3]. The older supplier export file supplier_master_EXPORT_2024.csv listed the same core details (code NC-GDA-0063, Gdańsk, PL, VAT PL5842736190, ACTIVE, N45) but is superseded [^r18]. Kind: superseded.

## See also

- [[data-supplier-master|SUPPLIER_MASTER]]
- [[data-rate-contracts|Rate Contracts 2025-26 and 2026-27]]
- [[data-po-extract-2026|PO_extract_2026-01_to_2026-10]]
- [[data-certificate-expiry-report-2026-10-01|Certificate Expiry Report 2026-10-01 (PUR-R022)]]
- [[topic-un-38-3-certificates|UN 38.3 Certificates]]
- [[sop-pur-001|SOP-PUR-001 Supplier Onboarding]]
- [[sop-pur-005|SOP-PUR-005 Certificate Renewal (UN 38.3)]]
- [[decision-2026-10-01-nordic-cell-order-hold|Decision 2026-10-01 Order Hold on Nordic Cell Co. (NC-GDA-0063)]]
- [[items-bat|BAT-* items]]
- [[cc-prd-04|PRD-04 Medlock trekking line]]
- [[cc-prd-05|PRD-05 City e-bike line, regular production]]
- [[user-lmoreno|Luis Moreno (LMORENO)]]
- [[screen-pur-sup-03|PUR-SUP-03 Supplier Enquiry]]

## References

[^r1]: 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx, sheet 2026-27, row NC-GDA-0063/BAT-500/2026-04-01, SHEET 2026-27
[^r3]: 05_master_data/SUPPLIER_MASTER.xlsx, sheet Suppliers, row NC-GDA-0063, SHEET Suppliers
[^r12]: 10_meeting_notes/2026-10-19 Weekly purchasing meeting.md, Discussion
[^r13]: 10_meeting_notes/2026-10-19 Weekly purchasing meeting.md, Discussion
[^r16]: 09_email_archive/2026/2026-10-01_CERT EXPIRED - DO NOT ORDER_ Nordic Cell Co. (NC-GDA-0063).eml, body
[^r17]: 09_email_archive/2026/2026-10-01_CERT EXPIRED - DO NOT ORDER_ Nordic Cell Co. (NC-GDA-0063).eml, body
[^r14]: 09_email_archive/2026/2026-09-29_UN 38.3 report renewal.eml, body
[^r11]: 06_transactions/reports/Supplier listing 2026-10 (printed).pdf, row NC-GDA-0063, p. 1, PUR-R003
[^r5]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-05, row PO/2026/00590, SHEET 2026-05
[^r9]: 06_transactions/reports/PO register 2026-05 (printed).pdf, row PO/2026/00590, p. 1, PUR-R010 PURCHASE ORDER REGISTER
[^r6]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-06, row PO/2026/00805, SHEET 2026-06
[^r10]: 06_transactions/reports/PO register 2026-06 (printed).pdf, row PO/2026/00805, p. 3, PURCHASE ORDER REGISTER
[^r7]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet Spend by supplier, row NC-GDA-0063, Spend by supplier
[^r4]: 05_master_data/SUPPLIER_MASTER.xlsx, sheet Certificates, row NC-GDA-0063/UN38.3/UN38.3-TR/NC/2025/090, SHEET Certificates
[^r8]: 06_transactions/reports/Certificate expiry report 2026-10-01.pdf, row NC-GDA-0063, p. 3, PUR-R022 CERTIFICATE EXPIRY DAYS=90
[^r15]: 09_email_archive/2026/2026-09-29_UN 38.3 report renewal.eml, body
[^r2]: 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx, sheet 2025-26, row NC-GDA-0063/BAT-500/2025-04-01, SHEET 2025-26
[^r18]: 05_master_data/supplier_master_EXPORT_2024.csv, sheet csv, row NC-GDA-0063, SHEET csv
