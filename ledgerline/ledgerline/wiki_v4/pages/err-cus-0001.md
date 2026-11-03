---
title: "ERR-CUS-0001 Mandatory Field Missing or Invalid in Customer Master"
type: "error"
slug: "err-cus-0001"
summary: "Ledgerline error raised when saving or updating a customer record with missing mandatory fields or invalid country or payment term codes."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-CUS-0001 |
| module | SAL |
| severity | Error |
| raised_by | cust_save, cust_update |
| screen | SAL-CUS-01 |
| status | current |

ERR-CUS-0001 is a Ledgerline validation error encountered during customer record creation or modification. It prevents saving or updating a customer profile when required core information is absent or fails standard data format rules [^r1]. Resolving it requires supplying all missing values and ensuring territory and payment term codes match system reference tables [^r2].

## Meaning

ERR-CUS-0001 indicates that a mandatory field is missing or fails basic formatting rules during a customer master save or update operation [^r1].

## Cause

The error is triggered when submitting customer data where `CUST NAME` is omitted, or where required codes such as `COUNTRY CD (2)` or `PAY TERM CD` are either missing or fail basic formatting validation checks [^r1].

## How to fix

To resolve ERR-CUS-0001:

1. Verify that the country identifier contains the exact required 2-character territory code [^r2].
2. Confirm that the specified payment term code exists in the active reference tables [^r2].
3. Re-enter any missing customer text fields, including customer name [^r1][^r2].
4. Re-submit the customer record using the `cust_save` or `cust_update` services on [[screen-sal-cus-01|SAL-CUS-01 Customer Master Entry]] [^r1][^r2].

## Raised by

This error is raised during `CUSTOMER MASTER SAVE` or `CUSTOMER MASTER UPDATE` execution by the [[services-sal-cust|SAL cust services]] (`cust_save` or `cust_update`), documented in [[man-sal-72|MAN-SAL-72]] [^r1][^r2].

## See also

* [[screen-sal-cus-01|SAL-CUS-01 Customer Master Entry]]
* [[services-sal-cust|SAL cust services]]
* [[man-sal-72|MAN-SAL-72 Ledgerline ERP 7.2 User Manual: Sales]]
* [[err-cus-0801|ERR-CUS-0801 Invalid or Duplicate VAT Number]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 5, Messages
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 5, Messages
