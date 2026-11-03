---
title: "SOP-INV-002 Returns to Vendor (RTV)"
type: "procedure"
slug: "sop-inv-002"
summary: "SOP for returning non-conforming, surplus, or damaged goods and warranty cores to suppliers from Manchester and Leeds using screen INV-RTV-07."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-INV-002 Returns to Vendor (RTV) v1.3.pdf", "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "11_training/intranet_export_2016/page_year_end_stock_count__2016.html", "10_meeting_notes/2026-01-17 Warranty review.docx"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | SOP-INV-002 |
| Version | 1.3 |
| Owner | Callum Shaw |
| Approver | Henrik Weber |
| Effective | 2025-01-01 |
| Status | current |

SOP-INV-002 governs returning non-conforming, surplus, or damaged goods and recalled parts from the Manchester factory and Leeds satellite unit [^r1][^r9]. It is owned by stores manager [[user-cshaw|Callum Shaw]], was approved by plant head [[user-hweber|Henrik Weber]], and has been effective since 2025-01-01 [^r1]. Faulty warranty cores, including water-damaged display switches and wiring harnesses, are also returned through Ledgerline ERP return-to-vendor workflows to maintain stock accuracy and secure supplier credits [^r12].

| Field | Value |
|---|---|
| Document Code | SOP-INV-002 |
| Version | 1.3 |
| Owner | Callum Shaw |
| Approver | Henrik Weber |
| Effective Date | 2025-01-01 |
| Status | Current |

## Steps

1. **Pre-return verification**: Stores staff must locate the original goods receipt note (GRN NO), confirm quality sign-off on the NCR NO when applicable, coordinate collection scheduling with purchasing and the haulier, and record the supplier's formal returns authorisation in REMARKS [^r10].
2. **System entry**: Raise the Return to Vendor (RTV) transaction on screen [[screen-inv-rtv-07|INV-RTV-07]] against the GRN within 30 days of receipt pursuant to [[pol-ret-006|POL-RET-006]] §2.1 [^r2]. The RTV quantity must not exceed the quantity received on the GRN, or Ledgerline enforces validation error ERR-RTV-0204 [^r7].
3. **Invoice check**: If the GRN has already been matched to an invoice in accounts payable, `rtv_save` blocks the transaction with error [[err-rtv-0230|ERR-RTV-0230]]; stores staff must instead request a debit note from accounts payable [^r4][^r8].
4. **Physical segregation and staging**: Immediately move the goods to warehouse WH-MAN-RTV and label them with the assigned RTV number [^r3]. Delivery documentation for items sent for rework or credit must be fully registered prior to year-end counts to prevent rejected stock from appearing on count sheets [^r11].
5. **Dangerous goods handling**: Return [[items-bat|traction battery packs]] exclusively via the haulier's dangerous-goods service in approved crates bearing an exterior UN3480 label [^r5].
6. **Documentation and carrier dispatch**: Obtain the carrier driver's signature on the Northbridge dispatch note at handover [^r6]. The signed original must be delivered to purchase ledger in finance, one copy filed in stores, and a third copy packed in the consignment envelope [^r6]. RTV processing generates haulier paperwork and posts credit note expectations directly to Accounts Payable [^r9].

## Forms and screens

* [[screen-inv-rtv-07|INV-RTV-07 Return To Vendor Entry]]: Screen used by stores staff to enter returns against original GRN records and capture return authorisations [^r2][^r10].
* Services: Back-end processing is handled by [[services-inv-rtv|INV rtv services]] including `rtv_save` [^r8].
* Error handling: [[man-err-72|MAN-ERR-72]] documents ERR-RTV-0204 (excess quantity) and [[err-rtv-0230|ERR-RTV-0230]] (matched receipt requiring an AP debit note) [^r7][^r8].

## See also

* [[err-rtv-0230|ERR-RTV-0230 Invoice already posted against receipt]]
* [[items-bat|BAT-* items]]
* [[pol-ret-006|POL-RET-006 Returns Policy]]
* [[screen-inv-rtv-07|INV-RTV-07 Return To Vendor Entry]]
* [[services-inv-rtv|INV rtv services]]
* [[sop-ap-001|SOP-AP-001 Three-Way Invoice Matching]]
* [[sop-inv-003|SOP-INV-003 Stock Count (cycle and annual)]]
* [[sop-sal-002|SOP-SAL-002 Warranty Claims from Bike Shops]]
* [[user-cshaw|Callum Shaw (CSHAW)]]
* [[user-hweber|Henrik Weber (HWEBER)]]

## References

[^r1]: 02_procedures/SOP-INV-002 Returns to Vendor (RTV) v1.3.pdf, p. 1, Returns to Vendor (RTV)
[^r9]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 15, Purpose
[^r12]: 10_meeting_notes/2026-01-17 Warranty review.docx, Discussion
[^r10]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 17, Tips
[^r2]: 02_procedures/SOP-INV-002 Returns to Vendor (RTV) v1.3.pdf, p. 3, §5. Procedure
[^r7]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 21
[^r4]: 02_procedures/SOP-INV-002 Returns to Vendor (RTV) v1.3.pdf, p. 3, §5. Procedure
[^r8]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 21
[^r3]: 02_procedures/SOP-INV-002 Returns to Vendor (RTV) v1.3.pdf, p. 3, §5. Procedure
[^r11]: 11_training/intranet_export_2016/page_year_end_stock_count__2016.html, Goods received and invoice matching
[^r5]: 02_procedures/SOP-INV-002 Returns to Vendor (RTV) v1.3.pdf, p. 3, §5. Procedure
[^r6]: 02_procedures/SOP-INV-002 Returns to Vendor (RTV) v1.3.pdf, p. 4, §6. Records
