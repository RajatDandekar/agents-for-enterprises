---
title: "MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts"
type: "manual"
slug: "man-ap-72"
summary: "Ledgerline ERP 7.2 Accounts Payable user manual covering invoice processing, matching tolerances, debit and credit notes, payment runs, bank details, and advances."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | MAN-AP-72 |
| Title | Ledgerline ERP 7.2 User Manual: Accounts |
| Owner | Ledgerline Systems Documentation Group |
| Version | 7.2.3 |
| Effective date | 2025-01-15 |
| Status | current |
| Module | Accounts Payable |
| Target audience | Accounts payable clerks, purchase ledger supervisors, finance staff |

MAN-AP-72 is the operational user manual for the Accounts Payable module of Ledgerline ERP 7.2, issued by the Ledgerline Systems Documentation Group with an effective date of 15 January 2025 [^r1]. It provides operating procedures across Northbridge Cycles for accounts payable clerks, purchase ledger supervisors, and finance staff based at the Manchester factory and Leeds unit [^r2]. The manual defines standard screen workflows, key background services, matching tolerances, and validation rules governing supplier payments and adjustments [^r2][^r10]. As of 26 October 2026, version 7.2.3 remains the active reference documentation for purchase ledger processing [^r1].

| Field | Detail |
|---|---|
| Document Code | MAN-AP-72 |
| Version | 7.2.3 |
| Effective Date | 2025-01-15 |
| Author | Ledgerline Systems Documentation Group |
| Module | Accounts Payable |
| System Status | Idle sessions terminate after 20 minutes [^r3] |

## System integration and session rules

In Ledgerline ERP 7.2, a user session that remains idle for 20 minutes is closed automatically and unsaved work is lost [^r3]. The Accounts Payable module integrates in real time with Purchasing for open PO verification, Inventory for matching goods inward receipts across Manchester and Leeds, and Finance for direct postings to nominal ledger and control accounts [^r4]. Shipped three-way matching tolerances in Ledgerline ERP 7.2 are set at 2% and £50 per line via parameters AP.MATCH_TOL_PCT and AP.MATCH_TOL_ABS, where the smaller limit applies [^r10].

## Screens and workflows

### Screen AP-INV-01: Supplier invoice entry

On [[screen-ap-inv-01|AP-INV-01]], invoice reconciliation requires BASIC and TAX AMT to agree with GROSS, or the system displays [[errors-inv|ERR-INV-0001]] [^r5]. Invoking the `inv_save` routine from [[services-ap-inv|services-ap-inv]] generates a draft register entry, assigns the system document number to AP DOC, and sets STATUS to unposted [^r6]. If an invoice total exceeds received delivery value or invoiced quantities surpass goods received notes, clerks may hold the voucher using `inv_hold` and supply a note in REASON [^r7]. Once verified, clicking `inv_release` (if held) followed by `inv_post` changes STATUS to confirmed and generates immediate general ledger entries [^r8]. Posted invoices cannot be cancelled directly using `inv_cancel` due to validation ERR-INV-0801, requiring an offsetting credit note instead [^r9].

### Screen AP-DBN-04: Debit note entry

Screen [[screen-ap-dbn-04|AP-DBN-04]] allows accounts payable clerks to record, edit, view, and post debit notes against suppliers to adjust account balances [^r11]. Creating a draft debit note requires entering SUP CD, REF DOC, AMOUNT, REASON CD, and optional COMMENT; running `dbn_save` from [[services-ap-dbn|services-ap-dbn]] populates DBN NO and sets STATUS to draft without updating the supplier ledger [^r12]. Executing `dbn_post` runs the DEBIT NOTE POST routine, applies the balance to the supplier account ledger, updates STATUS to posted, and locks the record [^r13]. An unposted draft can be discarded using `dbn_cancel`, which updates STATUS to cancelled and clears commitments while retaining the record for audit [^r14].

### Screen AP-CRN-05: Supplier credit note

Screen [[screen-ap-crn-05|AP-CRN-05]] is accessed via Accounts payable > Supplier credit to record and post credit notes issued by suppliers across Manchester and Leeds, linking them to internal AP documents or nominal accounts [^r15][^r16]. The screen supports [[services-ap-crn|services-ap-crn]] routines `crn_save`, `crn_get`, `crn_search`, and `crn_post` [^r15]. Mandatory fields are SUP CD (`sup_cd`), SUP CRN NO (`sup_crn_no`), AMOUNT (`amount`), and CRN NO (`crn_no`), while AP DOC (`ap_doc`), STATUS (`status`), and COMMENT (`comment`) are optional [^r17]. Saving via `crn_save` sets an internal CRN NO reference and flags STATUS as draft [^r18]. Clicking `crn_post` commits the credit note to the purchase ledger, updating STATUS from draft to posted and locking all fields [^r18][^r19].

### Screen AP-PAY-03: Payment run

Accessed under Accounts payable > Payment run, screen [[screen-ap-pay-03|AP-PAY-03]] manages payment processing through [[services-ap-pay|services-ap-pay]] routines `pay_propose`, `pay_get`, `pay_approve`, `pay_release`, `pay_file`, `pay_cancel`, and `pay_search` [^r20]. Screen fields are structured as follows:
* Mandatory: RUN DT (`run_dt`), BANK CD (`bank_cd`), DUE UPTO (`due_upto`), RUN NO (`run_no`), and REASON (`reason`) [^r21].
* Optional: SUP CD (`sup_cd`), COMMENT (`comment`), and STATUS (`status`) [^r21].

### Screen AP-BNK-06: Supplier bank details

Located at Accounts payable > Supplier bank, screen [[screen-ap-bnk-06|AP-BNK-06]] operates via [[services-ap-bnk|services-ap-bnk]] routines `bnk_save`, `bnk_get`, `bnk_verify`, `bnk_block`, and `bnk_search`, requiring SUP CD and ACCT NAME [^r22]. Before modifying bank data, staff must obtain formal written confirmation on signed company letterhead, verify numbers via independent telephone contact using existing records, and confirm all pending ledger payment runs are complete [^r23]. Executing `bnk_save` marks the record as requiring verification [^r24]. Under dual-control procedures, `bnk_verify` requires a second authorised finance user to inspect source documentation before approving bank records for automated payment selection [^r24]. Applying `bnk_block` flags the account as blocked and prevents inclusion in automated runs [^r25].

### Screen AP-ADV-07: Advance payment entry

Screen [[screen-ap-adv-07|AP-ADV-07]] manages prepayments against approved purchase orders prior to invoice or receipt for Manchester and Leeds operations [^r26]. Mandatory fields are SUP CD (`sup_cd`), PO NO (`po_no`), AMOUNT (`amount`), and ADV NO (`adv_no`), supported by [[services-ap-adv|services-ap-adv]] routines `adv_save`, `adv_get`, `adv_search`, `adv_approve`, and `adv_adjust` [^r27]. Clerks enter advance payments for Manchester production parts against existing purchase orders, leaving ADV NO blank for automatic assignment [^r28]. Entering an invalid, held, or unverified supplier returns [[err-sup-0030|ERR-SUP-0030]] [^r29]. Supplying a PO reference that cannot be found or is closed triggers [[err-adv-0001|ERR-ADV-0001]] [^r30].

## See also

* [[screen-ap-inv-01|AP-INV-01 Supplier Invoice Entry]]
* [[screen-ap-mat-02|AP-MAT-02 Three-Way Match]]
* [[screen-ap-pay-03|AP-PAY-03 Payment Run]]
* [[screen-ap-dbn-04|AP-DBN-04 Debit Note Entry]]
* [[screen-ap-crn-05|AP-CRN-05 Supplier Credit Note Entry]]
* [[screen-ap-bnk-06|AP-BNK-06 Supplier Bank Details Entry]]
* [[screen-ap-adv-07|AP-ADV-07 Advance Payment Entry]]
* [[screen-ap-sbl-08|AP-SBL-08 Supplier Balance]]
* [[sop-ap-004|SOP-AP-004 Supplier Bank Detail Changes]]
* [[err-adv-0001|ERR-ADV-0001 Missing or invalid advance payment fields]]
* [[err-sup-0030|ERR-SUP-0030]]
* [[errors-inv|Errors INV (ERR-INV-*)]]
* [[services-ap-inv|AP inv services]]
* [[services-ap-dbn|AP dbn services]]
* [[services-ap-crn|AP crn services]]
* [[services-ap-pay|AP pay services]]
* [[services-ap-bnk|AP bnk services]]
* [[services-ap-adv|AP adv services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 1, Version history
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 2, Intended Audience
[^r10]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 10, Questions users ask
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 2, §2. Signing in and sessions
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 2, Module Integration
[^r5]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 7, Questions users ask
[^r6]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 7, Questions users ask
[^r7]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 7, Questions users ask
[^r8]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 7, Questions users ask
[^r9]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 7, Questions users ask
[^r11]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 11, Purpose
[^r12]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 12, To create and save a new draft debit note:
[^r13]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 12, To post the debit note:
[^r14]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 12, To cancel an unposted debit note:
[^r15]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 14, §6. Supplier Credit Note (AP-CRN-05)
[^r16]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 15, Purpose
[^r17]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 14, §6. Supplier Credit Note (AP-CRN-05)
[^r18]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 16, Entering a new credit note:
[^r19]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 18, Worked example: Supplier Credit Note
[^r20]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 18, §7. Payment Run (AP-PAY-03)
[^r21]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 18, §7. Payment Run (AP-PAY-03)
[^r22]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 22, §8. Supplier Bank Details (AP-BNK-06)
[^r23]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 23, Screen layout and fields
[^r24]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 24, Step by step
[^r25]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 24, Step by step
[^r26]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 26, Advance Payment (AP-ADV-07)
[^r27]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 26, §9. Advance Payment (AP-ADV-07)
[^r28]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 29, Advance Payment (AP-ADV-07)
[^r29]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 29, Advance Payment (AP-ADV-07)
[^r30]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 29, Advance Payment (AP-ADV-07)
