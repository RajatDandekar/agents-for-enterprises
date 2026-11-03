---
title: "SOP-AP-003 Supplier Payment Run"
type: "procedure"
slug: "sop-ap-003"
summary: "Procedure for bi-weekly supplier payment runs in Ledgerline ERP, including proposal generation, dual approval, bank file export, and audit pack retention."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-AP-003 Supplier Payment Run v1.4.pdf", "03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf", "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "12_integrations/Bank payment file format STD18 v1.3.pdf", "12_integrations/bank_file_sample_2026-10-22.txt", "10_meeting_notes/2025-12-12 Finance and purchasing catch-up.md", "09_email_archive/2021/2021-05-27_Duplicate invoice caught.eml", "09_email_archive/2025/2025-01-08_Payment run approval cover.eml", "09_email_archive/2026/2026-02-15_Bank detail change requests.eml", "09_email_archive/2026/2026-03-05_Supplier asking for early payment.eml", "06_transactions/AP_invoices_2026.xlsx"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Document code | SOP-AP-003 |
| Version | v1.4 |
| Owner | Marta Kowalski (AP Manager) |
| Approver | Grace Whitaker (Financial Controller) |
| Effective date | 2024-06-01 |
| Status | current |

SOP-AP-003 governs the generation, approval, and bank release of supplier payments at Northbridge Cycles[^r1]. Bi-weekly payment proposals are automatically processed through Ledgerline ERP for verified UK domestic bank transfers, while overseas settlements require manual processing[^r2][^r10][^r11]. Enforcement of strict separation of duties, invoice matching validation, and independent verification of supplier bank details are mandatory before funds are transmitted[^r3][^r19][^r22].

| Field | Value |
|---|---|
| Document code | SOP-AP-003[^r1] |
| Version | v1.4[^r1] |
| Owner | [[user-mkowalski|Marta Kowalski]], AP Manager[^r1] |
| Approver | [[user-gwhitaker|Grace Whitaker]], Financial Controller[^r1] |
| Effective date | 2024-06-01[^r1] |
| Status | Current[^r1] |

## Steps

### 1. Proposal Generation
Supplier payment runs execute twice weekly on Tuesdays and Thursdays[^r2]. At 10:00, automated batch job JOB-AP-030 runs for bank account NBC-MAIN to generate payment proposals of due, matched invoices[^r2][^r7]. Invoices included in the schedule must be matched against purchase orders and warehouse delivery notes, and verified against supplier ledger entries, settlement terms, and VAT calculations[^r19].

The system automatically excludes suppliers lacking verified bank details under [[err-bnk-0101|ERR-BNK-0101]][^r5]. Suppliers with amended bank details that have not been fully checked and authorised via independent verbal verification must also not be included[^r22]. Invoices with incomplete goods received records, price variances, quality queries, or unapplied credits on supplier statements are held back from the proposal until resolved with purchasing[^r20][^r23]. If an order reference or matching value bypasses the initial posting check and creates a duplicate supplier invoice, Ledgerline ERP's proposal generation flags the matching values, requiring Accounts Payable to place a temporary hold on the duplicate entry and reverse the accrual[^r17][^r18]. Entering a proposal or search date prior to today raises error ERR-PAY-0105[^r9].

Before considering any payment release ahead of the standard schedule, Accounts Payable must check cash flow forecasts, confirm whether an early settlement discount applies, and verify on Ledgerline ERP that invoices are registered and approved with posted goods inwards notes and no inspection queries[^r23][^r24].

### 2. Proposal Review and Authorisation
An accounts payable clerk reviews the generated payment proposal on screen [[screen-ap-pay-03|AP-PAY-03]][^r3]. The accounts payable manager must approve the proposal, with separation of duties enforced so that the proposer cannot act as the approver; violating this constraint triggers [[err-pay-0430|ERR-PAY-0430]][^r3]. Attempting to approve or release a run that is not in Draft or pending status raises ERR-PAY-0007[^r8].

Payment proposals in Ledgerline ERP also require formal authorisation by the financial controller before file export[^r12][^r21].

### 3. Bank File Generation and Release
Following authorisation, batch job JOB-AP-031 generates the payment file in fixed-width Standard 18 (STD18) format at 14:30[^r4][^r7][^r10]. The domestic STD18 settlement file handles UK bank transfers, requiring transaction code 99 and originator name 'NORTHBRIDGE CYCLES'[^r10]. Invoices processed in the run receive an assigned payment run identifier prefixed with 'PR-' along with a paid_on date, and the exported BACS text file references this PR-YYYYMMDD code alongside Northbridge Cycles and the beneficiary name[^r13][^r14].

Control totals must be validated against ERP batch summaries before an authorised signatory performs secondary release on the bank portal[^r12]. The file must be released to the bank by 14:30 for same-day processing[^r4]. Upon formal approval, accounts payable posts the batch, issues payment remittance advices, and releases instructions to the bank[^r21].

### 4. Overseas Supplier Payments
Payments to vendors outside the United Kingdom are excluded from the automated domestic STD18 bank file[^r11]. The AP manager must manually key these foreign payments into the banking portal using the foreign-payments list[^r11]. Advance bank payments and pro-forma deposits for overseas vendors must be cross-referenced against open foreign purchase orders before month-end to clear suspense account balances[^r15]. Supplier credit hold notifications received from purchasing must be forwarded directly to the joint finance mailbox[^r16].

### 5. Audit Pack Retention
Staff must assemble and retain both a physical and electronic audit pack for every run[^r6]. The pack contains the signed authorisation sheet, preliminary and final payment summaries, and the bank transmission confirmation, filed chronologically by payment date[^r6].

## Forms and screens
* [[screen-ap-pay-03|AP-PAY-03]] (Payment Run): Used by the AP clerk to review and adjust payment proposals[^r3].
* JOB-AP-030: Automated batch job executing at 10:00 on Tuesdays and Thursdays to generate proposals for account NBC-MAIN[^r2][^r7].
* JOB-AP-031: Automated batch job executing at 14:30 on Tuesdays and Thursdays to create the STD18 bank payment file[^r4][^r7].
* Banking portal: External interface used for secondary authorisation of the STD18 file release and manual keying of overseas payments[^r11][^r12].

## Versions and conflicts
* **Payment run frequency**: Today's rule dictates that payment runs take place twice weekly on Tuesdays and Thursdays (JOB-AP-030 running at 10:00 and JOB-AP-031 at 14:30), as established in SOP-AP-003 v1.4 (effective 2024-06-01) and [[man-bat-72|MAN-BAT-72]][^r2][^r7]. An e-mail regarding early supplier payments dated 2026-03-05 mentions that Northbridge Cycles operates a weekly payment schedule (`contradiction`)[^r24].

## See also
* [[screen-ap-pay-03|AP-PAY-03 Payment Run]]
* [[err-pay-0430|ERR-PAY-0430 Payment proposal approver cannot be proposer]]
* [[err-bnk-0101|ERR-BNK-0101 Supplier bank details unverified]]
* [[sop-ap-001|SOP-AP-001 Three-Way Invoice Matching]]
* [[sop-ap-004|SOP-AP-004 Supplier Bank Detail Changes]]
* [[man-bat-72|MAN-BAT-72 Ledgerline ERP 7.2 Batch Jobs: Northbridge]]
* [[man-err-72|MAN-ERR-72 Ledgerline ERP 7.2 Message and Error Code]]
* [[services-ap-pay|services-ap-pay]]
* [[services-ap-bnk|services-ap-bnk]]
* [[user-mkowalski|Marta Kowalski]]
* [[user-gwhitaker|Grace Whitaker]]

## References

[^r1]: 02_procedures/SOP-AP-003 Supplier Payment Run v1.4.pdf, p. 1, Supplier Payment Run
[^r2]: 02_procedures/SOP-AP-003 Supplier Payment Run v1.4.pdf, p. 3, §5. Procedure
[^r10]: 12_integrations/Bank payment file format STD18 v1.3.pdf, p. 2, §2. Record layout (one record per payment)
[^r11]: 12_integrations/Bank payment file format STD18 v1.3.pdf, p. 2, §3. Overseas suppliers
[^r3]: 02_procedures/SOP-AP-003 Supplier Payment Run v1.4.pdf, p. 3, §5. Procedure
[^r19]: 09_email_archive/2025/2025-01-08_Payment run approval cover.eml, body
[^r22]: 09_email_archive/2026/2026-02-15_Bank detail change requests.eml, Bank detail change requests
[^r7]: 03_ledgerline_manuals/MAN-BAT-72 Batch Jobs and Scheduler Reference (NBC schedule).pdf, p. 3, §2. Job details
[^r5]: 02_procedures/SOP-AP-003 Supplier Payment Run v1.4.pdf, p. 3, §5. Procedure
[^r20]: 09_email_archive/2025/2025-01-08_Payment run approval cover.eml, body
[^r23]: 09_email_archive/2026/2026-03-05_Supplier asking for early payment.eml, body
[^r17]: 09_email_archive/2021/2021-05-27_Duplicate invoice caught.eml, body
[^r18]: 09_email_archive/2021/2021-05-27_Duplicate invoice caught.eml, body
[^r9]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 15, ERR-PAY-0105 DATE IN PAST
[^r24]: 09_email_archive/2026/2026-03-05_Supplier asking for early payment.eml, body
[^r8]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 15, ERR-PAY-0007 PAYMENT RUN NOT IN DRAFT (<status>)
[^r12]: 12_integrations/Bank payment file format STD18 v1.3.pdf, p. 3, Practical operation at Northbridge
[^r21]: 09_email_archive/2025/2025-01-08_Payment run approval cover.eml, body
[^r4]: 02_procedures/SOP-AP-003 Supplier Payment Run v1.4.pdf, p. 3, §5. Procedure
[^r13]: 12_integrations/bank_file_sample_2026-10-22.txt, whole file
[^r14]: 06_transactions/AP_invoices_2026.xlsx, sheet Invoices, SHEET Invoices
[^r15]: 10_meeting_notes/2025-12-12 Finance and purchasing catch-up.md, Discussion
[^r16]: 10_meeting_notes/2025-12-12 Finance and purchasing catch-up.md, Discussion
[^r6]: 02_procedures/SOP-AP-003 Supplier Payment Run v1.4.pdf, p. 4, §6. Records
