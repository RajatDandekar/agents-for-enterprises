---
title: "INT-BNK-002 Supplier payment file: Standard 18 layout as used by Northbridge"
type: "procedure"
slug: "int-bnk-002"
summary: "Standard 18 payment transmission file layout and transmission procedure for domestic purchase ledger settlements in Ledgerline ERP."
audience: "staff"
status: "current"
sources: ["12_integrations/Bank payment file format STD18 v1.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | INT-BNK-002 |
| Title | Supplier payment file: Standard 18 layout as used by Northbridge |
| Version | 1.3 |
| Effective | 2024-06-01 |
| Status | current |
| Owner | Finance and IT |
| Classification | INTERNAL CURRENT |

INT-BNK-002 defines the Standard 18 bank payment file layout used by Northbridge Cycles to settle purchase ledger balances for domestic creditors, utilities, and recurring service charges across the Manchester factory and Leeds unit [^r1][^r2]. Generated directly from the Ledgerline ERP purchase ledger module, the file automates disbursements and replaces manual entry for UK suppliers [^r2][^r11]. Non-UK beneficiaries are excluded from the file transmission and require manual entry into the banking portal with dual authorisation [^r8][^r9].

## Steps

### Proposal generation and ledger verification
A finance clerk prepares a payment proposal within the Ledgerline purchase ledger module, checking proposed remittances against approved invoices and credit notes [^r11]. Supplier bank details must already be validated and saved in Ledgerline ERP ahead of the settlement run [^r4]. The export routine is run only after authorisation by the financial controller [^r11].

### File generation and storage handling
The Standard 18 transmission file generates from Ledgerline without manual intervention [^r2][^r11]. Staff must never open or edit the generated export file in spreadsheets or text editors before transmission, as manual edits alter character encodings and strip trailing spaces or leading zeroes [^r3]. Generated files must be kept strictly within the designated network directory without saving local working copies to desktops [^r13].

### Pre-upload control checks
Before uploading the file to the banking portal, the clerk confirms that the total payment sum and line count on the ERP batch summary balance with the header and trailer control totals [^r12].

### Portal upload, reconciliation, and release
Staff upload the export file to the banking portal and verify that the total value on the ledger summary report matches the control total shown in the portal [^r4]. A second authorised signatory reviews the control totals against the printed ledger control sheet before releasing the batch [^r12]. Immediately after release, bank portal confirmations must be reconciled against the ERP cash book posting report [^r13].

### Overseas supplier payments
Payments to suppliers outside the United Kingdom are excluded from the Standard 18 file [^r8]. The accounts payable manager keys overseas payments manually into the bank's portal using the foreign-payments list [^r8]. Staff must cross-check overseas beneficiary account details against the original signed purchase order or paper invoice rather than relying solely on screen displays [^r10]. Manually entered overseas settlements require a secondary release on the bank portal by an authorised signatory before the bank executes the transfer [^r9].

## Forms and screens

### Standard 18 record layout (one record per payment)
The transmission file formats one record per payment with the following fixed field positions:
* **Positions 1–6**: Destination sort code of the supplier (length 6) [^r5].
* **Positions 7–14**: Destination account number, zero-padded (length 8) [^r5].
* **Position 15**: Type indicator `'0'` (length 1) [^r5].
* **Positions 16–17**: Transaction code `'99'` for credit (length 2) [^r6].
* **Positions 18–23**: Originating sort code for Northbridge's main account (length 6) [^r6].
* **Positions 24–31**: Originating account number (length 8) [^r6].
* **Positions 36–46**: Payment amount in pence, zero-padded (length 11) [^r7].
* **Positions 47–64**: Originator name `'NORTHBRIDGE CYCLES'` (length 18) [^r7].
* **Positions 65–82**: AP run number reference (length 18) [^r7].
* **Positions 83–100**: Beneficiary name in uppercase (length 18) [^r7].

### Associated screens and reports
* **Ledgerline ERP Purchase Ledger**: Used to build proposals, review credit notes and invoices, and execute the payment export routine [^r11].
* **ERP Batch Summary and Printed Ledger Control Sheet**: Used to cross-check line counts, batch sums, and control totals against bank portal upload summaries [^r4][^r12].
* **ERP Cash Book Posting Report**: Used for immediate post-transmission reconciliation against bank portal confirmations [^r13].
* **Banking Portal**: Used to upload Standard 18 batch files, review control totals, manually enter foreign-payment lists, and execute secondary release approvals [^r4][^r8][^r9][^r12].

## See also
* [[sop-ap-003|SOP-AP-003 Supplier Payment Run]]
* [[data-integration-inventory|Integration inventory]]

## References

[^r1]: 12_integrations/Bank payment file format STD18 v1.3.pdf, p. 1, §1. Purpose
[^r2]: 12_integrations/Bank payment file format STD18 v1.3.pdf, p. 1, Operational practice
[^r11]: 12_integrations/Bank payment file format STD18 v1.3.pdf, p. 3, Practical operation at Northbridge
[^r8]: 12_integrations/Bank payment file format STD18 v1.3.pdf, p. 2, §3. Overseas suppliers
[^r9]: 12_integrations/Bank payment file format STD18 v1.3.pdf, p. 2, Operational procedure
[^r4]: 12_integrations/Bank payment file format STD18 v1.3.pdf, p. 1, Practical guidance
[^r3]: 12_integrations/Bank payment file format STD18 v1.3.pdf, p. 1, Practical guidance
[^r13]: 12_integrations/Bank payment file format STD18 v1.3.pdf, p. 3, Practical tips
[^r12]: 12_integrations/Bank payment file format STD18 v1.3.pdf, p. 3, Practical operation at Northbridge
[^r10]: 12_integrations/Bank payment file format STD18 v1.3.pdf, p. 2, Practical advice
[^r5]: 12_integrations/Bank payment file format STD18 v1.3.pdf, p. 1, §2. Record layout (one record per payment)
[^r6]: 12_integrations/Bank payment file format STD18 v1.3.pdf, p. 2, §2. Record layout (one record per payment)
[^r7]: 12_integrations/Bank payment file format STD18 v1.3.pdf, p. 2, §2. Record layout (one record per payment)
