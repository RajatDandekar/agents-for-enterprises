---
title: "ERR-SCN-0007 Customer credit note posting validation failure"
type: "error"
slug: "err-scn-0007"
summary: "Validation failure raised during sales credit note posting if the financial period is closed, document already posted, invoice settled, or amount excessive."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | ERR-SCN-0007 |
| Type | Error |
| Module | Sales (SAL) |
| Object | Customer Credit Note (SCN) |
| Raised by service | scn_post |
| Source manual | MAN-SAL-72 |

`ERR-SCN-0007` is a validation error raised by Ledgerline ERP during customer credit note posting[^r1]. It blocks posting when pre-conditions regarding the accounting period, document state, invoice status, or unsettled balance are violated[^r1]. Credit notes triggering this error cannot update the sales ledger until the underlying condition is resolved[^r1].

## Meaning

The error indicates that the credit note failed pre-posting validation checks during execution of the credit note posting service[^r1].

## Cause

The error is triggered during `scn_post` if any of the following conditions are met[^r1]:
* The financial posting period is closed[^r1].
* The document has already been posted[^r1].
* The targeted sales invoice is locked or fully settled[^r1].
* The credit note `AMOUNT` exceeds the remaining unsettled balance on the invoice[^r1].

## How to fix

To resolve the error, review the credit note and related invoice details[^r1]:
* Verify that the posting date falls within an open financial posting period[^r1].
* Confirm whether the credit note document already holds a posted status before attempting to re-post[^r1].
* Check the status of the related invoice on [[screen-sal-inv-06|Sales Invoice Entry]] to ensure it is not locked or already settled[^r1].
* Adjust the credit note `AMOUNT` on [[screen-sal-crn-09|Customer Credit Note Entry]] so that it does not exceed the unsettled invoice balance[^r1].

## Raised by

Raised by the `scn_post` service within [[services-sal-scn|SAL scn services]], documented in [[man-sal-72|MAN-SAL-72]][^r1].

## See also

* [[screen-sal-crn-09|SAL-CRN-09 Customer Credit Note Entry]]
* [[services-sal-scn|SAL scn services]]
* [[screen-sal-inv-06|SAL-INV-06 Sales Invoice Entry]]
* [[man-sal-72|MAN-SAL-72 Ledgerline ERP 7.2 User Manual: Sales and Distribution]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 43, Messages
