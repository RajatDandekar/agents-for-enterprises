---
title: "Tax codes"
type: "data-source"
slug: "data-tax-codes"
summary: "Master reference of Ledgerline tax codes defining active UK domestic rates, overseas reverse-charge rates, and inactive legacy codes."
audience: "staff"
status: "mixed"
sources: ["05_master_data/Payment terms.csv", "05_master_data/Tax codes.xlsx", "07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf", "01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf", "01_policies/old/Purchase Policy v4.0.docx", "02_procedures/SOP-AP-001 Three-Way Invoice Matching v2.1.pdf", "02_procedures/SOP-PUR-002 PR to PO v1.3 (FINAL).pdf", "03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf", "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/old/LL6_purchasing_quickguide.docx", "03_ledgerline_manuals/old/Ledgerline 7.0 Purchasing Manual (2015).pdf", "04_service_definitions/purchase/tax_compute.yaml", "04_service_definitions/purchase/tax_list.yaml", "08_release_notes/LL6_release_history_2004-2012.txt", "11_training/New starter - Purchasing (2024) deck export.pdf", "11_training/QRC-02 Raising a purchase order - Fetch first.pdf", "11_training/QRC-03 ERR-PO-0412 quick fix.pdf", "06_transactions/AP_invoices_2026.xlsx", "99_scans/2011_VAT_rate_change_memo.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Source file | 05_master_data/Tax codes.xlsx |
| Worksheet | Tax codes |
| Total rows | 11 |
| Columns | 7 |
| Active codes | 8 |
| Legacy codes | 3 |
| Lookup key | tax_cd |

The Tax codes workbook is the master data reference for value added tax codes configured in Ledgerline ERP [^r3]. It defines the active domestic UK VAT rates and overseas reverse-charge codes, as well as closed historic rates that remain on historical orders and invoices [^r3][^r16][^r17][^r18][^r42]. Under [[pol-pur-001|POL-PUR-001]], orders and supplier invoices must use domestic `-UK` codes for UK vendors and reverse-charge `-RC` codes for overseas vendors [^r20][^r28]. Because the default line fetch on screens like [[screen-pur-po-01|PUR-PO-01]] populates `VAT20-UK`, buyers must manually switch to `-RC` codes for non-UK vendors to prevent [[err-po-0412|ERR-PO-0412]] and downstream payment blocks in accounts payable [^r29][^r35][^r36].

| Property | Value |
|---|---|
| Source file | `05_master_data/Tax codes.xlsx` [^r3] |
| Sheet | `Tax codes` [^r3] |
| Row count | 11 rows [^r3] |
| Column count | 7 columns [^r3] |
| Key column | `tax_cd` [^r30] |
| Classification kinds | `INTRA` (domestic UK), `INTER` (foreign reverse charge), `NA` (exempt or out of scope) [^r3][^r10][^r11][^r15] |

## What it holds

The workbook contains 11 tax codes defining VAT rates, validity date ranges, active status flags, and jurisdictional classification kinds [^r3]. Ledgerline classifies VAT into kind `INTRA` for suppliers located in the same country as Northbridge's operating unit (the UK), and kind `INTER` for overseas suppliers requiring reverse charge accounting [^r3][^r15].

Active codes in the register are:
* **UK domestic supplies (`INTRA`)**: `VAT20-UK` (standard rate of 20% / 0.20, valid from 2011-01-04), `VAT5-UK` (reduced rate of 5% / 0.05, valid from 2011-01-04), and `VAT0-ZR` (zero-rated at 0%, valid from 1998-04-01) [^r4][^r6][^r8][^r16].
* **Overseas reverse charge supplies (`INTER`)**: `VAT20-RC` (standard rate reverse charge of 20% / 0.20), `VAT5-RC` (reduced rate reverse charge of 5% / 0.05), and `VAT0-RC` (zero-rated reverse charge at 0%), all valid from 2011-01-04 [^r5][^r7][^r9][^r17]. Overseas invoices with `-RC` codes show zero VAT on the supplier document, and Ledgerline automatically accounts for the reverse charge without manual tax entry [^r21][^r38].
* **Special categories (`NA`)**: `VAT-EX` (exempt supplies at 0%) and `OUTSCOPE` (outside the scope of VAT at 0%), both valid from 1998-04-01 with active flag 1 [^r10][^r11][^r16].

The table also holds three inactive historical codes with active flag 0: `V175-UK` (legacy 17.5% UK VAT, valid 1998-04-01 to 2011-01-03), `V15-UK` (temporary 15% UK VAT, valid 2008-12-01 to 2009-12-31), and `V1` (Ledgerline 6.x legacy standard rate, valid 1998-04-01 to 2011-01-03) [^r12][^r13][^r14][^r18]. These legacy codes must not be used on new transactions [^r14][^r18].

## Columns

The `Tax codes` sheet is structured across 7 columns [^r3]:

1. **Tax code** (`tax_cd`): The unique alphanumeric code used in purchasing and accounts payable transactions [^r3][^r30].
2. **Description**: Narrative description of the tax rate and jurisdiction [^r3].
3. **Rate**: Decimal tax rate (e.g., `0.20` for standard, `0.05` for reduced, and `0` for zero/exempt) [^r3][^r4][^r6][^r8].
4. **Kind**: Territorial classification, holding `INTRA` (UK supplier), `INTER` (overseas reverse charge), or `NA` (exempt or outside scope) [^r3][^r10][^r11][^r15].
5. **Valid from**: Effective start date for the code [^r3].
6. **Valid to**: Expiration date (blank for current active codes; populated for legacy codes) [^r3][^r12][^r13][^r14].
7. **Active**: Binary flag where `1` indicates active and available for entry, and `0` marks retired legacy codes [^r3][^r4][^r12][^r18].

## How to look up a row

Individual rows are keyed by the tax code (`tax_cd`) [^r3][^r30]. In [[man-dd-72|MAN-DD-72]], the dictionary references `tax_cd` across purchasing and AP line records [^r19][^r43]. Programmatically, services query this data via [[services-pur-tax]]:
* The read service `tax_list` retrieves available codes via `POST /ll72/svc/tax_list` [^r31].
* The calculation service `tax_compute` executes stored procedure `sp_tax_compute` taking inputs `basic` and `tax_cd` to compute line VAT values [^r30].

Operational procedures in [[sop-ap-001|SOP-AP-001]] verify line tax codes against supplier country rules during three-way matching [^r20][^r21].

## Size

The workbook contains 11 total rows and 7 columns [^r3]. There are 8 active codes (active flag 1) and 3 inactive historic codes (active flag 0) [^r3][^r4][^r5][^r6][^r7][^r8][^r9][^r10][^r11][^r12][^r13][^r14][^r18].

## Versions and conflicts

* **Superseded UK Standard VAT Rates**: The current UK standard VAT code is `VAT20-UK` (rate 0.20, active flag 1), effective since 2011-01-04 [^r4][^r40][^r41]. Prior to 2011-01-04, UK standard VAT was 17.5% under code `V175-UK` (and Ledgerline 6.x code `V1`), which was closed on 2011-01-03 [^r12][^r14][^r39][^r41]. Between 2008-12-01 and 2009-12-31, a temporary 15% rate operated under code `V15-UK` [^r13][^r32]. Transactions posted prior to 2011-01-04 retain their historic rates and do not recalculate at 20% [^r42].

## See also

* [[data-payment-terms|Payment terms]]
* [[err-po-0412|ERR-PO-0412 TAX CODE DOES NOT MATCH SUPPLIER COUNTRY]]
* [[errors-po|ERR-PO Error Codes]]
* [[man-dd-72|MAN-DD-72 Ledgerline ERP 7.2 Data Dictionary, Purchasing]]
* [[pol-pur-001|POL-PUR-001 Purchase Policy]]
* [[screen-ap-inv-01|AP-INV-01 Supplier Invoice Entry]]
* [[screen-pur-po-01|PUR-PO-01 Purchase Order Entry]]
* [[services-pur-tax|PUR tax services]]
* [[sop-ap-001|SOP-AP-001 Three-Way Invoice Matching]]
* [[sop-pur-002|SOP-PUR-002 Purchase Request to Purchase Order]]

## References

[^r3]: 05_master_data/Tax codes.xlsx, sheet Tax codes, SHEET Tax codes
[^r16]: 05_master_data/Tax codes.xlsx, sheet Tax codes, row VAT20-UK, ALL 11 ROWS
[^r17]: 05_master_data/Tax codes.xlsx, sheet Tax codes, row VAT20-RC, ALL 11 ROWS
[^r18]: 05_master_data/Tax codes.xlsx, sheet Tax codes, row V1, ALL 11 ROWS
[^r42]: 99_scans/2011_VAT_rate_change_memo.pdf, p. 1, MEMO FINANCE DEPARTMENT
[^r20]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 2, §8. Tax
[^r28]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 18, ERR-PO-0412
[^r29]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 18, ERR-PO-0412
[^r35]: 11_training/QRC-02 Raising a purchase order - Fetch first.pdf, p. 1, Tips - Tax codes for overseas orders
[^r36]: 11_training/QRC-02 Raising a purchase order - Fetch first.pdf, p. 1, Tips - Tax codes for overseas orders
[^r30]: 04_service_definitions/purchase/tax_compute.yaml, whole file
[^r10]: 05_master_data/Tax codes.xlsx, sheet Tax codes, row VAT-EX, ALL 11 ROWS
[^r11]: 05_master_data/Tax codes.xlsx, sheet Tax codes, row OUTSCOPE, ALL 11 ROWS
[^r15]: 05_master_data/Tax codes.xlsx, sheet Tax codes, SHEET Tax codes
[^r4]: 05_master_data/Tax codes.xlsx, sheet Tax codes, row VAT20-UK, ALL 11 ROWS
[^r6]: 05_master_data/Tax codes.xlsx, sheet Tax codes, row VAT5-UK, ALL 11 ROWS
[^r8]: 05_master_data/Tax codes.xlsx, sheet Tax codes, row VAT0-ZR, ALL 11 ROWS
[^r5]: 05_master_data/Tax codes.xlsx, sheet Tax codes, row VAT20-RC, ALL 11 ROWS
[^r7]: 05_master_data/Tax codes.xlsx, sheet Tax codes, row VAT5-RC, ALL 11 ROWS
[^r9]: 05_master_data/Tax codes.xlsx, sheet Tax codes, row VAT0-RC, ALL 11 ROWS
[^r21]: 02_procedures/SOP-AP-001 Three-Way Invoice Matching v2.1.pdf, p. 3, §5. Procedure
[^r38]: 06_transactions/AP_invoices_2026.xlsx, sheet Invoices, SHEET Invoices
[^r12]: 05_master_data/Tax codes.xlsx, sheet Tax codes, row V175-UK, ALL 11 ROWS
[^r13]: 05_master_data/Tax codes.xlsx, sheet Tax codes, row V15-UK, ALL 11 ROWS
[^r14]: 05_master_data/Tax codes.xlsx, sheet Tax codes, row V1, ALL 11 ROWS
[^r19]: 07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf, p. 2, §7. Tax codes
[^r43]: 07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf, p. 2, §7. Tax codes
[^r31]: 04_service_definitions/purchase/tax_list.yaml, service: tax_list
[^r40]: 99_scans/2011_VAT_rate_change_memo.pdf, p. 1, MEMO FINANCE DEPARTMENT
[^r41]: 99_scans/2011_VAT_rate_change_memo.pdf, p. 1, MEMO FINANCE DEPARTMENT
[^r39]: 99_scans/2011_VAT_rate_change_memo.pdf, p. 1, MEMO FINANCE DEPARTMENT
[^r32]: 08_release_notes/LL6_release_history_2004-2012.txt, LEDGERLINE 6 RELEASE HISTORY (COPIED FROM THE OLD INTRANET)
