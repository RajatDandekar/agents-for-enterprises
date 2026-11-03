---
title: "ERR-BNK-0118 Modulus check or clearing code validation failed"
type: "error"
slug: "err-bnk-0118"
summary: "Ledgerline error when bank sort code, account number, or IBAN fails domestic modulus or format validation checks."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | ERR-BNK-0118 |
| Severity | Error |
| Module | Accounts Payable (AP) |
| Manual | [[man-ap-72|MAN-AP-72]] |

Error code ERR-BNK-0118 is a bank validation error in Ledgerline Accounts Payable. It prevents saving invalid banking information when account numbers, clearing codes, or international account identifiers fail standard format or mathematical checks. This ensures payments processed via AP cannot be directed to malformed bank account details.

| Field | Value |
|---|---|
| Error code | ERR-BNK-0118 |
| Message | Modulus check or clearing code validation failed |
| Module | Accounts Payable |
| Reference | [[man-ap-72|MAN-AP-72]] |

## Meaning

Error ERR-BNK-0118 indicates that SORT CD or ACCT NO failed domestic clearing modulus algorithm checks, or that IBAN failed standard format validation rules [^r1].

## Cause

The error is triggered when entered domestic bank account numbers and sort codes do not pass the modulus validation algorithm prescribed by the domestic clearing system, or when an IBAN does not conform to standard format rules [^r1].

## How to fix

Verify the entered bank account details against the supplier's verified documentation, re-enter the correct sort code and account number or standard IBAN format, and ensure all digits conform to domestic clearing modulus requirements [^r1]. Bank detail adjustments must follow standard procedures under [[sop-ap-004|SOP-AP-004]].

## Raised by

This error is raised during bank account validation operations in the Accounts Payable module, such as entries made on [[screen-ap-bnk-06|AP-BNK-06]] or processed by [[services-ap-bnk|AP bnk services]] [^r1].

## See also

* [[errors-bnk|Errors BNK]]
* [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]]
* [[screen-ap-bnk-06|AP-BNK-06 Supplier Bank Details Entry]]
* [[services-ap-bnk|AP bnk services]]
* [[sop-ap-004|SOP-AP-004 Supplier Bank Detail Changes]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 24, Messages
