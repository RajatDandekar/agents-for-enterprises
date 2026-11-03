---
title: "SOP-AP-001 Three-Way Invoice Matching"
type: "procedure"
slug: "sop-ap-001"
summary: "Standard operating procedure governing automated three-way matching of supplier purchase invoices against orders and delivery records before payment release."
audience: "staff"
status: "current"
sources: ["07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx", "02_procedures/SOP-AP-001 Three-Way Invoice Matching v2.1.pdf", "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "08_release_notes/RN-7.2.2 Ledgerline Release Notes.pdf", "08_release_notes/RN-7.2.3-P3 Ledgerline Patch Notes.pdf", "08_release_notes/RN-7.2.3-P5 Ledgerline Patch Notes.pdf", "11_training/intranet_export_2016/page_glossary_of_ledgerline_terms.html", "11_training/intranet_export_2016/page_how_we_work_with_finance.html", "11_training/intranet_export_2016/page_suppliers_in_europe.html", "10_meeting_notes/2025-07-24 Supplier review.docx", "10_meeting_notes/2025-12-12 Finance and purchasing catch-up.md", "09_email_archive/2021/2021-02-24_Supplier statement does not match.eml", "09_email_archive/2021/2021-05-27_Duplicate invoice caught.eml", "09_email_archive/2025/2025-05-18_Invoices on hold for price differences.eml", "09_email_archive/2026/2026-05-14_Voltway freight.eml", "09_email_archive/2026/2026-07-23_Partial delivery of brake pads.eml", "06_transactions/AP_invoices_2026.xlsx"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | SOP-AP-001 |
| Title | Three-Way Invoice Matching |
| Version | 2.1 |
| Effective | 2025-04-01 |
| Owner | Marta Kowalski (Accounts Payable Manager) |
| Approver | Grace Whitaker (Financial Controller) |
| Status | current |
| Classification | Internal |

SOP-AP-001 governs the verification of trade supplier purchase invoices for goods and carriage against purchase orders and goods receipt notes across the Manchester works and the Leeds unit prior to payment release [^r5][^r6]. Automated three-way matching in Ledgerline compares prices and quantities against configured tolerance thresholds, placing mismatched items on administrative hold [^r7][^r15][^r20]. Reconciled invoices proceed to the payment run, whereas disputed or out-of-tolerance documents require formal buyer intervention or managerial override [^r10][^r21][^r39].

| Field | Detail |
|---|---|
| Document Code | SOP-AP-001 [^r5] |
| Version | 2.1 [^r5] |
| Effective Date | 2025-04-01 [^r5] |
| Document Owner | [[user-mkowalski|Marta Kowalski]] (Accounts Payable Manager) [^r5] |
| Approved By | [[user-gwhitaker|Grace Whitaker]] (Financial Controller) [^r5] |
| Classification | Current Internal [^r5] |
| System Job | JOB-AP-010 [^r7] |

## Steps

### 1. Invoice Registration and Pre-Validation
Accounts payable staff enter incoming trade invoices against their purchase order reference on [[screen-ap-inv-01|AP-INV-01]] [^r7][^r28]. Ledgerline strictly checks supplier invoice references per vendor account and blocks registration with [[err-inv-0118|ERR-INV-0118]] if an identical reference already exists [^r4][^r17]. If a single supplier invoice covers multiple deliveries or separate order parts, staff and vendors must establish unique reference or sub-reference numbers before posting to prevent reference rejection [^r18]. Duplicate reference incidents must be recorded in system supplier account notes to maintain departmental visibility, guarding against variations across electronic and postal submissions [^r37][^r38]. Invoices from overseas vendors on `-RC` tax codes ([[data-tax-codes|Tax codes]]) carry no supplier VAT, and Ledgerline automatically accounts for the reverse charge [^r11]. Invoices from [[sup-vc-ein-0042|Voltway Cells]] that include freight charges must be rejected and returned immediately because rates are contracted delivered DAP Manchester [^r42].

### 2. Automated Three-Way Matching Run
Three-way matching job JOB-AP-010 compares each entered invoice with its corresponding purchase order and goods received records for quantity and price alignment [^r7][^r20]. Each matched accounts payable document is linked directly to a unique Goods Receipt Note (`grn_no`) and Purchase Order (`po_no`) [^r31]. Match tolerances are governed by system configuration parameters `AP.MATCH_TOL_PCT` and `AP.MATCH_TOL_ABS` [^r15]. If an invoice line differs from the order rate by more than 2% or by more than £50 (whichever limit is smaller), or exceeds either parameter threshold, automated matching halts, the entry is blocked from the payment run, and the line is placed on hold with status `HOLD-PRC` [^r8][^r16][^r30][^r39]. When the invoiced quantity exceeds the received quantity, the line fails matching and is placed on hold with status `HOLD-QTY` [^r9][^r30]. When all line values and quantities match within tolerance, the document receives status `MATCHED` and is passed for payment [^r21][^r30].

### 3. Discrepancy Investigation and Dispute Management
Discrepancies on price variance require manual intervention from purchase ledger staff, temporarily delaying invoice clearing across both Manchester and Leeds [^r40]. Matching failure causes include unrecorded shortages or damages on warehouse delivery notes, unposted plant goods receipts, unnotified freight surcharges, unapplied credit notes, or raw material rate adjustments [^r22][^r32][^r35][^r36]. Over-deliveries must not be accepted without prior commercial agreement, and invoices covering partial deliveries must not be cleared for full settlement until outstanding balances are physically received and booked in [^r23][^r43]. Buyers must provide advance written notification of agreed price changes and regularly review unmatched receipts and accrued delivery lists provided by finance [^r33][^r34]. To release an invoice held for price, the purchasing buyer must provide written sign-off instructing accounts payable whether to demand an official supplier credit note or re-approve an amended purchase order via [[sop-pur-003|SOP-PUR-003]] [^r24][^r25][^r29][^r41]. Historical order values must never be altered directly, and disputed invoices cannot be authorised for payment without formal finance office agreement [^r25][^r27]. Returned defective components must be supported by official return documentation to match corresponding incoming credit notes under [[sop-inv-002|SOP-INV-002]] [^r26].

### 4. Match Overrides
Only the Accounts Payable Manager possesses permission to execute a system override on a failed three-way match using Ledgerline service group [[services-ap-mat|services-ap-mat]] (`mat_override`) [^r10][^r14]. Attempting to override a match failure without the mandatory `AP-MGR` role triggers system error [[err-mat-0420|ERR-MAT-0420]] [^r14]. Whenever an override is authorised, a formal explanation must be recorded in the system override comment field [^r10].

### 5. Document Archiving and Physical Records
Following reconciliation, matched paper documentation is retained in the accounts payable archive [^r12]. System electronic entries cross-reference physical batch storage locations and carrier delivery sheets [^r12]. Physical receipt dockets originating from the Leeds unit must be transferred promptly to the Manchester accounts office for consolidation [^r12]. Approved and reconciled invoices proceed to [[sop-ap-003|SOP-AP-003]] for payment processing [^r21][^r39].

## Forms and screens

* [[screen-ap-inv-01|AP-INV-01]]: Supplier invoice entry screen for registering invoices against purchase orders [^r7].
* JOB-AP-010: Automated three-way matching batch job [^r7].
* System error `ERR-INV-0118`: Raised on duplicate supplier invoice reference entries during registration [^r4][^r17].
* System error `ERR-MAT-0410`: Match failure raised when invoice price exceeds purchase order tolerance [^r1][^r13].
* System error `ERR-MAT-0411`: Match failure raised when invoiced quantity exceeds received quantity [^r2][^r13].
* System error `ERR-MAT-0412`: Match failure raised when matching is attempted but no GRN exists for the specified PO line [^r3][^r13].
* System error [[err-mat-0420|ERR-MAT-0420]]: Match override permission failure raised if an override is attempted without the `AP-MGR` role [^r14].
* Known system issue: Under Ledgerline 7.2.3-P5, matching an invoice against a completed GRN may display an advisory spurious rounding prompt despite identical net totals; accounts payable staff bypass this prompt by manually confirming the line items [^r19].

## See also

* [[screen-ap-inv-01|AP-INV-01 Supplier Invoice Entry]]
* [[err-mat-0420|ERR-MAT-0420 Match override permission denied]]
* [[err-inv-0118|ERR-INV-0118 Duplicate supplier invoice number]]
* [[sop-ap-002|SOP-AP-002 Accounts Payable Period Close]]
* [[sop-ap-003|SOP-AP-003 Supplier Payment Run]]
* [[sop-pur-002|SOP-PUR-002 Purchase Request to Purchase Order]]
* [[sop-pur-003|SOP-PUR-003 Purchase Order Amendment]]
* [[sop-inv-002|SOP-INV-002 Returns to Vendor (RTV)]]
* [[services-ap-mat|services-ap-mat]]
* [[data-tax-codes|Tax codes]]
* [[sup-vc-ein-0042|Voltway Cells (VC-EIN-0042)]]
* [[user-mkowalski|Marta Kowalski (MKOWALSKI)]]
* [[user-gwhitaker|Grace Whitaker (GWHITAKER)]]

## References

[^r5]: 02_procedures/SOP-AP-001 Three-Way Invoice Matching v2.1.pdf, p. 1, Field
[^r6]: 02_procedures/SOP-AP-001 Three-Way Invoice Matching v2.1.pdf, p. 2, Scope
[^r7]: 02_procedures/SOP-AP-001 Three-Way Invoice Matching v2.1.pdf, p. 3, §5. Procedure
[^r15]: 08_release_notes/RN-7.2.2 Ledgerline Release Notes.pdf, p. 3, §3. Details
[^r20]: 11_training/intranet_export_2016/page_glossary_of_ledgerline_terms.html, Receipt and matching
[^r10]: 02_procedures/SOP-AP-001 Three-Way Invoice Matching v2.1.pdf, p. 3, §5. Procedure
[^r21]: 11_training/intranet_export_2016/page_how_we_work_with_finance.html, Deliveries and matching
[^r39]: 09_email_archive/2025/2025-05-18_Invoices on hold for price differences.eml, Invoices on hold for price differences
[^r28]: 11_training/intranet_export_2016/page_suppliers_in_europe.html, Invoicing and Payment Processing
[^r4]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-INV-0118, SHEET Error codes
[^r17]: 08_release_notes/RN-7.2.3-P3 Ledgerline Patch Notes.pdf, p. 2, §3. Details
[^r18]: 08_release_notes/RN-7.2.3-P3 Ledgerline Patch Notes.pdf, p. 1, Upgrade Notes for Key Users
[^r37]: 09_email_archive/2021/2021-05-27_Duplicate invoice caught.eml, body
[^r38]: 09_email_archive/2021/2021-05-27_Duplicate invoice caught.eml, body
[^r11]: 02_procedures/SOP-AP-001 Three-Way Invoice Matching v2.1.pdf, p. 3, §5. Procedure
[^r42]: 09_email_archive/2026/2026-05-14_Voltway freight.eml, body
[^r31]: 06_transactions/AP_invoices_2026.xlsx, sheet Invoices, SHEET Invoices
[^r8]: 02_procedures/SOP-AP-001 Three-Way Invoice Matching v2.1.pdf, p. 3, §5. Procedure
[^r16]: 08_release_notes/RN-7.2.2 Ledgerline Release Notes.pdf, p. 3, §3. Details
[^r30]: 06_transactions/AP_invoices_2026.xlsx, sheet Invoices, SHEET Invoices
[^r9]: 02_procedures/SOP-AP-001 Three-Way Invoice Matching v2.1.pdf, p. 3, §5. Procedure
[^r40]: 09_email_archive/2025/2025-05-18_Invoices on hold for price differences.eml, Invoices on hold for price differences
[^r22]: 11_training/intranet_export_2016/page_how_we_work_with_finance.html, Deliveries and matching
[^r32]: 10_meeting_notes/2025-07-24 Supplier review.docx, # Discussion
[^r35]: 09_email_archive/2021/2021-02-24_Supplier statement does not match.eml, body
[^r36]: 09_email_archive/2021/2021-02-24_Supplier statement does not match.eml, body
[^r23]: 11_training/intranet_export_2016/page_how_we_work_with_finance.html, Deliveries and matching
[^r43]: 09_email_archive/2026/2026-07-23_Partial delivery of brake pads.eml, body
[^r33]: 10_meeting_notes/2025-12-12 Finance and purchasing catch-up.md, Discussion
[^r34]: 10_meeting_notes/2025-12-12 Finance and purchasing catch-up.md, Discussion
[^r24]: 11_training/intranet_export_2016/page_how_we_work_with_finance.html, Queries and credit notes
[^r25]: 11_training/intranet_export_2016/page_how_we_work_with_finance.html, Queries and credit notes
[^r29]: 11_training/intranet_export_2016/page_suppliers_in_europe.html, Invoicing and Payment Processing
[^r41]: 09_email_archive/2025/2025-05-18_Invoices on hold for price differences.eml, Invoices on hold for price differences
[^r27]: 11_training/intranet_export_2016/page_how_we_work_with_finance.html, Queries and credit notes
[^r26]: 11_training/intranet_export_2016/page_how_we_work_with_finance.html, Queries and credit notes
[^r14]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 13, ERR-MAT-0420 OVERRIDE NEEDS AP-MGR ROLE
[^r12]: 02_procedures/SOP-AP-001 Three-Way Invoice Matching v2.1.pdf, p. 4, §6. Records
[^r1]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-MAT-0410, SHEET Error codes
[^r13]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 13, ERR-MAT-0410 MATCH FAILED: PRICE OUTSIDE TOLERANCE
[^r2]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-MAT-0411, SHEET Error codes
[^r3]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-MAT-0412, SHEET Error codes
[^r19]: 08_release_notes/RN-7.2.3-P5 Ledgerline Patch Notes.pdf, p. 3, §4. Known issues
