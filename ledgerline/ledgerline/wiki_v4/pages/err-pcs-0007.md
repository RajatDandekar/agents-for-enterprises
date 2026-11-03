---
title: "ERR-PCS-0007"
type: "error"
slug: "err-pcs-0007"
summary: "Ledgerline Accounts Payable error raised when saving or posting a locked or already posted petty cash voucher, or during period-end reconciliation lock."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-PCS-0007 |
| Module | Accounts Payable (AP) |
| Component | Petty Cash |
| Severity | Error |
| Related service | pcs_save, pcs_post |
| Source manual | MAN-AP-72 |

ERR-PCS-0007 is an Accounts Payable error in Ledgerline ERP that blocks modifications or posting of petty cash transactions [^r1]. It indicates that the targeted petty cash voucher is immutable or that the petty cash book is currently locked for period-end reconciliation [^r1]. Users encountering this message cannot save or post changes until the voucher or reconciliation lock condition is resolved [^r1].

| Field | Value |
|---|---|
| Error Code | ERR-PCS-0007 |
| Module | Accounts Payable (AP) |
| Services | pcs_save, pcs_post |
| Relevant Manual | [[man-ap-72|MAN-AP-72]] |

## Meaning
Message ERR-PCS-0007 indicates that an operation was rejected because the petty cash record or book is locked against updates or postings [^r1].

## Cause
The error occurs when a user attempts to execute `pcs_save` or `pcs_post` on a voucher that has already been posted or locked [^r1]. It is also triggered when the entire petty cash book is locked for period-end reconciliation [^r1].

## How to fix
Verify whether the selected petty cash voucher has already been posted or marked as locked [^r1]. If the petty cash book is locked for period-end reconciliation, postpone changes until reconciliation is complete and the book is reopened [^r1].

## Raised by
This error is raised by the [[services-ap-pcs|AP pcs services]] `pcs_save` and `pcs_post`, commonly accessed through [[screen-ap-pcs-15|AP-PCS-15 Petty Cash Entry]] [^r1].

## See also
* [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]]
* [[screen-ap-pcs-15|AP-PCS-15 Petty Cash Entry]]
* [[services-ap-pcs|AP pcs services]]
* [[screen-ap-per-11|AP-PER-11 Ap Period]]
* [[errors-per|ERR-PER Error Codes]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 57, Messages
