---
title: "AP_invoices_2026"
type: "data-source"
slug: "data-ap-invoices-2026"
summary: "Accounts payable invoice register for 2026 recording 1,381 invoices, three-way match statuses, tax breakdowns, and payment run settlements."
audience: "staff"
status: "current"
sources: ["06_transactions/AP_invoices_2026.xlsx", "06_transactions/reports/Supplier Invoice Register Jan-Oct 2026 (printed).pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| File | 06_transactions/AP_invoices_2026.xlsx |
| Type | Transaction register |
| Primary key | ap_doc |
| Sheet count | 1 |
| Row count | 1,381 |
| Columns | 17 |
| Status | Current |

`AP_invoices_2026.xlsx` is the primary transactional register of Northbridge Cycles' supplier invoices logged during calendar year 2026 [^r1]. It tracks 1,381 invoice line records against purchase orders and goods receipt notes, capturing three-way matching verification, applicable VAT, and payment processing details [^r1][^r3][^r5]. As of 26 October 2026, 1,191 of these invoices have been settled across 74 payment runs, while matching exceptions remain flagged under quantity or price holds [^r5][^r7].

| Field | Detail |
|---|---|
| File | `06_transactions/AP_invoices_2026.xlsx` [^r1] |
| Report equivalent | AP-R010, Supplier Invoice Register 2026 (printed across 33 pages on 26 October 2026 at 05:40) [^r8] |
| Sheet name | `Invoices` [^r1] |
| Primary key | `ap_doc` [^r4] |
| Total records | 1,381 data rows [^r1] |
| Settlement status | 1,191 paid across 74 payment runs [^r7] |

## What it holds

The workbook logs incoming accounts payable invoices and monitors their path through invoice matching to final settlement [^r1][^r3][^r5][^r7]. Each row links an internal AP document record to a supplier code, purchase order, and goods receipt note [^r3]. It documents commercial pricing, line quantities, tax classifications, and payment scheduling [^r3]. 

Invoices are assigned one of three match status values: `MATCHED`, `HOLD-PRC`, or `HOLD-QTY` [^r5]. Invoices flagged with `HOLD-PRC` include AP/2026/00029, AP/2026/00051, AP/2026/00064, and AP/2026/00073 [^r10]. Quantity discrepancies such as `HOLD-QTY` include invoice AP/2026/00038 against purchase order PO/2026/00088 for supplier TF-TEL-0287, with a gross amount of 18,144.00 [^r11].

Tax classifications within the register use two codes: `VAT20-UK` and `VAT20-RC` [^r6]. Transactions classified under reverse charge carry the suffix `-RC` and feature zero supplier VAT [^r2].

The data corresponds to Ledgerline report AP-R010 (Supplier Invoice Register 2026), generated on 26 October 2026 at 05:40 covering 01-01-2026 to 26-10-2026 across 33 pages, which summarizes AP DOC, INV DT, SUP CD, PO NO, GROSS, TAX CD, MATCH, DUE, and PAID [^r8][^r9].

## Columns

The single sheet `Invoices` contains 17 columns [^r1][^r3]:

1. `ap_doc`: Internal AP document reference number [^r3][^r4].
2. `sup_inv_no`: External invoice identifier issued by the supplier [^r3].
3. `inv_dt`: Date of the supplier invoice [^r3].
4. `sup_cd`: Unique supplier account code [^r3].
5. `po_no`: Associated purchase order number [^r3].
6. `grn_no`: Linked goods receipt note number [^r3].
7. `itm_cd`: Item code billed on the invoice line [^r3].
8. `qty`: Invoiced item quantity [^r3].
9. `rate`: Unit price charged per item [^r3].
10. `basic`: Net base amount prior to tax calculation [^r3].
11. `tax_cd`: Tax rate code applied (`VAT20-UK` or `VAT20-RC`) [^r3][^r6].
12. `tax`: Billed VAT amount (zero on `-RC` reverse-charge entries) [^r2][^r3].
13. `gross`: Total payable invoice line amount [^r3].
14. `match_status`: Invoice reconciliation state (`MATCHED`, `HOLD-PRC`, or `HOLD-QTY`) [^r3][^r5].
15. `due_dt`: Scheduled due date for supplier payment [^r3].
16. `paid_on`: Date the settlement was executed [^r3].
17. `pay_run`: Batch code of the payment run executing the transfer [^r3].

## How to look up a row

Each entry is uniquely keyed by the internal AP document identifier `ap_doc` (for example, `AP/2026/00001`) [^r4]. To inspect an invoice line, search column A (`ap_doc`) in the `Invoices` sheet [^r1][^r3][^r4]. Related records can also be grouped by purchase order (`po_no`), supplier code (`sup_cd`), or payment batch (`pay_run`) [^r3].

## Size

The workbook contains one sheet named `Invoices` with 1,381 data rows across 17 columns [^r1][^r3]. As of 26 October 2026, 1,191 invoices have been paid across 74 distinct payment runs [^r7].

## See also

* [[data-tax-codes|Tax codes]]
* [[sop-ap-001|SOP-AP-001 Three-Way Invoice Matching]]
* [[sop-ap-003|SOP-AP-003 Supplier Payment Run]]
* [[sup-vc-ein-0042|Voltway Cells (VC-EIN-0042)]]

## References

[^r1]: 06_transactions/AP_invoices_2026.xlsx, sheet Invoices, SHEET Invoices
[^r3]: 06_transactions/AP_invoices_2026.xlsx, sheet Invoices, SHEET Invoices
[^r5]: 06_transactions/AP_invoices_2026.xlsx, sheet Invoices, SHEET Invoices
[^r7]: 06_transactions/AP_invoices_2026.xlsx, sheet Invoices, SHEET Invoices
[^r8]: 06_transactions/reports/Supplier Invoice Register Jan-Oct 2026 (printed).pdf, p. 1, AP-R010 SUPPLIER INVOICE REGISTER 2026
[^r4]: 06_transactions/AP_invoices_2026.xlsx, sheet Invoices, SHEET Invoices
[^r10]: 06_transactions/reports/Supplier Invoice Register Jan-Oct 2026 (printed).pdf, row AP/2026/00029, p. 1, AP-R010 SUPPLIER INVOICE REGISTER 2026
[^r11]: 06_transactions/reports/Supplier Invoice Register Jan-Oct 2026 (printed).pdf, row AP/2026/00038, p. 1, AP-R010 SUPPLIER INVOICE REGISTER 2026
[^r6]: 06_transactions/AP_invoices_2026.xlsx, sheet Invoices, SHEET Invoices
[^r2]: 06_transactions/AP_invoices_2026.xlsx, sheet Invoices, SHEET Invoices
[^r9]: 06_transactions/reports/Supplier Invoice Register Jan-Oct 2026 (printed).pdf, p. 1, AP-R010 SUPPLIER INVOICE REGISTER 2026
