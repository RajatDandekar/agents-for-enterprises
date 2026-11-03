---
title: "ERR-INV-0118 Duplicate supplier invoice number"
type: "error"
slug: "err-inv-0118"
summary: "Error raised by Ledgerline ERP when a supplier invoice reference already exists for the vendor account."
audience: "staff"
status: "current"
sources: ["08_release_notes/RN-7.2.3-P3 Ledgerline Patch Notes.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | ERR-INV-0118 |
| Severity | Error |
| Module | AP (Accounts Payable) |
| Trigger | Duplicate invoice reference entry |
| First introduced | Ledgerline 7.2.3-P3 |

ERR-INV-0118 is a Ledgerline ERP transaction validation error triggered when an entered invoice reference already exists for the specified vendor account [^r1]. As of 26 October 2026, the error halts document processing to prevent duplicate liability postings across both interactive entry and automated integration channels [^r1][^r2]. In interactive entry, the system leaves the document unposted and retains the input focus on the reference field until resolved [^r2].

## Meaning
The system has identified an existing ledger record under the same vendor account that shares the exact invoice reference entered by the user or import interface [^r1].

## Cause
The error occurs when a user or an inbound interface submits an invoice reference that matches a previously recorded invoice on that vendor's account [^r1].

## How to fix
For interactive invoice entry, verify the supplier invoice document to correct any typographical errors in the reference field, or cancel the entry if the invoice has already been registered on the ledger [^r1][^r2]. Automated import interfaces encountering the error must log the transaction in the interface error queue and send a notification to the finance systems administrator, allowing the remainder of the batch transfer run to continue [^r3].

## Raised by
Ledgerline ERP transaction processing during manual supplier invoice entry or inbound batch invoice integration [^r1][^r2][^r3]. When raised interactively, Ledgerline halts transaction processing, leaves the document unposted without incrementing batch totals, and places the cursor back in the reference field until corrected or cancelled [^r2].

## See also
* [[sop-ap-001|SOP-AP-001 Three-Way Invoice Matching]]
* [[rn-7-2-3-p3|RN-7.2.3-P3 Ledgerline ERP 7.2.3-P3 Patch Notes]]

## References

[^r1]: 08_release_notes/RN-7.2.3-P3 Ledgerline Patch Notes.pdf, p. 2, §3. Details
[^r2]: 08_release_notes/RN-7.2.3-P3 Ledgerline Patch Notes.pdf, p. 2, §3. Details
[^r3]: 08_release_notes/RN-7.2.3-P3 Ledgerline Patch Notes.pdf, p. 3, §3. Details
