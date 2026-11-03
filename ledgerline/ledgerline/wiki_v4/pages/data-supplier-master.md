---
title: "SUPPLIER_MASTER"
type: "data-source"
slug: "data-supplier-master"
summary: "Supplier master workbook containing supplier entity records and compliance certificates exported from Ledgerline ERP 7.2."
audience: "staff"
status: "mixed"
sources: ["05_master_data/SUPPLIER_MASTER.xlsx", "05_master_data/supplier_master_EXPORT_2024.csv", "08_release_notes/RN-7.1.2 Ledgerline Release Notes.pdf", "06_transactions/reports/Supplier listing 2026-10 (printed).pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| File | SUPPLIER_MASTER.xlsx |
| Path | 05_master_data/SUPPLIER_MASTER.xlsx |
| Export report | PUR-SUP-03 |
| System | Ledgerline ERP 7.2 |
| Rows | 430 suppliers, 326 certificates |
| Sheets | Suppliers, Certificates |
| Audience | staff |
| Status | current |

`05_master_data/SUPPLIER_MASTER.xlsx` is the central supplier master data export PUR-SUP-03 from Ledgerline ERP 7.2 [^r1][^r33]. It maintains the registered details of 430 supplier accounts along with their associated compliance certificates [^r1][^r3]. As of 26 October 2026, it serves as the reference dataset for procurement status, payment terms, and vendor qualification records [^r1][^r5].

## What it holds

The workbook comprises two main sheets: `Suppliers` and `Certificates` (sup_cert) [^r1][^r3].

The `Suppliers` sheet holds account profiles, contact details, and core trading terms for all suppliers [^r1]. Migrated records originating from Ledgerline 6.x retain their original code structure and display `MIGRATION` in the creator field rather than an individual user identifier [^r31]. In Ledgerline 7.1.2 and later, migrated supplier codes cannot be edited manually, but operational fields including address, payment terms, and remittance details can be updated [^r32]. System report PUR-R003 generates a printed listing covering both active and blocked supplier records with each supplier's code, name, city, country, status, payment terms code, and VAT number [^r33][^r34].

The `Certificates` sheet (sup_cert) records regulatory and compliance documentation across 282 suppliers [^r3][^r5]. It tracks five distinct certificate types: ISO-14001, ISO-9001, REACH-DECL, ROHS-DECL, and UN38.3 [^r5]. Because Ledgerline 7.2 does not natively store certificate issue dates, the `issued_on` value is populated directly from the underlying test report [^r4][^r6]. Uploads in this sheet are tracked by staff members including [[user-lmoreno|Luis Moreno]], [[user-pjansen|Pieter Jansen]], and [[user-eclarke|Emma Clarke]] [^r7][^r8][^r9].

## Columns

The `Suppliers` sheet contains 13 columns [^r1]:
* `sup_cd`: Unique supplier code [^r1]
* `name`: Registered supplier trading name [^r1]
* `vat_no`: Supplier VAT registration number [^r1]
* `state`: Country identifier preserving its 1998 system column name but containing two-letter country codes across 13 distinct values [^r1][^r2]
* `city`: City location [^r1]
* `status`: Supplier account status [^r1]
* `pt_cd`: Payment terms code [^r1]
* `supply_category`: Supply classification category [^r1]
* `creator`: User identity or migration tag that created the record [^r1][^r31]
* `creation_date`: Date the record was created [^r1]
* `contact`: Named primary contact person [^r1]
* `email`: Primary contact email address [^r1]
* `notes`: Operational and historical notes [^r1]

The `Certificates` sheet contains 8 columns [^r3][^r6]:
* `line`: Sequential certificate line number [^r3][^r6]
* `sup_cd`: Associated supplier code [^r3][^r6]
* `cert_type`: Type of compliance certificate (ISO-14001, ISO-9001, REACH-DECL, ROHS-DECL, UN38.3) [^r3][^r5]
* `doc_ref`: Document reference or certificate number [^r3][^r6]
* `issued_on`: Certificate issuance date taken from the test report [^r3][^r4]
* `valid_to`: Expiration or validity limit date [^r3][^r6]
* `uploaded_by`: User who uploaded the certificate [^r3][^r6]
* `uploaded_on`: Date the certificate record was added [^r3][^r6]

## How to look up a row

To locate a supplier's core master record, look up the unique supplier code (`sup_cd`) in the `Suppliers` sheet [^r1]. To inspect compliance documents, filter the `Certificates` sheet by `sup_cd` or document reference (`doc_ref`) [^r3][^r6]. Individual supplier accounts and listings correspond to the [[screen-pur-sup-03|PUR-SUP-03 Supplier Enquiry]] screen and report PUR-R003 in Ledgerline [^r1][^r33][^r34].

## Size

* `Suppliers` sheet: 430 data rows across 13 columns [^r1].
* `Certificates` sheet: 326 data rows across 8 columns covering 282 distinct suppliers [^r3][^r5].

## Versions and conflicts

* **Superseded export format and record count**: Today's active supplier master is `05_master_data/SUPPLIER_MASTER.xlsx`, containing 430 supplier rows across 13 columns and a dedicated 326-row `Certificates` sheet [^r1][^r3]. The older file `05_master_data/supplier_master_EXPORT_2024.csv` is superseded; it contained only 380 supplier records across 7 columns (`sup_cd`, `name`, `vat_no`, `state`, `city`, `status`, `pt_cd`) with status restricted to `ACTIVE` or `BLOCKED` and payment terms limited to 6 codes (`ADV`, `EOM30`, `N15`, `N30`, `N45`, `N60`), lacking the certificate register and extended metadata [^r35][^r36]. Kind: `superseded`.

## See also

* [[screen-pur-sup-03|PUR-SUP-03 Supplier Enquiry]]
* [[rn-7-1-2|RN-7.1.2 Ledgerline ERP 7.1.2 Release Notes]]
* [[topic-un-38-3-certificates|UN 38.3 Certificates]]
* [[user-eclarke|Emma Clarke]]
* [[user-lmoreno|Luis Moreno]]
* [[user-pjansen|Pieter Jansen]]

## References

[^r1]: 05_master_data/SUPPLIER_MASTER.xlsx, sheet Suppliers, SHEET Suppliers
[^r33]: 06_transactions/reports/Supplier listing 2026-10 (printed).pdf, p. 1, PUR-R003
[^r3]: 05_master_data/SUPPLIER_MASTER.xlsx, sheet Certificates, SHEET Certificates
[^r5]: 05_master_data/SUPPLIER_MASTER.xlsx, sheet Certificates, SHEET Certificates
[^r31]: 08_release_notes/RN-7.1.2 Ledgerline Release Notes.pdf, p. 1, Core Changes and Migration Behaviour
[^r32]: 08_release_notes/RN-7.1.2 Ledgerline Release Notes.pdf, p. 2, §3. Details
[^r34]: 06_transactions/reports/Supplier listing 2026-10 (printed).pdf, p. 1, PUR-R003
[^r4]: 05_master_data/SUPPLIER_MASTER.xlsx, sheet Certificates, SHEET Certificates
[^r6]: 05_master_data/SUPPLIER_MASTER.xlsx, sheet Certificates, SHEET Certificates
[^r7]: 05_master_data/SUPPLIER_MASTER.xlsx, sheet Certificates, row WC-NAN-0318/ISO-9001/ISO9001/44328, SHEET Certificates
[^r8]: 05_master_data/SUPPLIER_MASTER.xlsx, sheet Certificates, row CC-WAR-0321/ISO-9001/ISO9001/91474, SHEET Certificates
[^r9]: 05_master_data/SUPPLIER_MASTER.xlsx, sheet Certificates, row PF-HUL-0325/ISO-9001/ISO9001/20724, SHEET Certificates
[^r2]: 05_master_data/SUPPLIER_MASTER.xlsx, sheet Suppliers, SHEET Suppliers
[^r35]: 05_master_data/supplier_master_EXPORT_2024.csv, sheet csv, SHEET csv
[^r36]: 05_master_data/supplier_master_EXPORT_2024.csv, sheet csv, SHEET csv
