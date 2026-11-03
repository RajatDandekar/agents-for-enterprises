---
title: "ERR-DSC-0001"
type: "error"
slug: "err-dsc-0001"
summary: "Error raised when a discount operation fails validation, lacks a matching discount record, or encounters an invalid customer account."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | ERR-DSC-0001 |
| Module | Sales (SAL) |
| Source | MAN-SAL-72 |
| Status | current |

Error ERR-DSC-0001 is a Ledgerline sales pricing error that indicates a discount operation has failed validation or lookup requirements [^r1]. When triggered, the system rejects the discount transaction entirely and commits no changes to underlying pricing tables [^r2]. The active interface remains in its prior state, requiring correction of customer status or entry parameters before retrying [^r2].

## Meaning

The error signifies that the requested discount cannot be processed because the discount record could not be found, the associated customer account does not exist or carries an administrative stop or hold, or the supplied values breach structural validation or category deduction limits [^r1].

## Cause

ERR-DSC-0001 is caused by:
* Attempting to apply or retrieve a discount record that does not exist in the database [^r1].
* Referencing a customer account that is missing or currently subject to an administrative hold or stop [^r1].
* Submitting values that fail structural validation criteria [^r1].
* Submitting discount parameters that exceed permitted category deduction limits [^r1].

## How to fix

To resolve ERR-DSC-0001:
* Confirm that the target discount record is configured and active via [[screen-sal-dsc-10|SAL-DSC-10 Discount]] and associated [[services-sal-dsc|SAL dsc services]] [^r1].
* Check [[screen-sal-cus-01|SAL-CUS-01 Customer Master Entry]] to verify that the customer account exists and does not carry an administrative stop or hold [^r1].
* Verify that all input fields meet structural formatting rules and that the requested deduction values do not exceed category limits [^r1].
* Re-enter the transaction once customer and discount parameters comply with system limits, as no partial updates are committed to pricing tables [^r2].

## Raised by

* [[man-sal-72|MAN-SAL-72 Ledgerline ERP 7.2 User Manual: Sales and]] message catalogue [^r1].
* [[screen-sal-dsc-10|SAL-DSC-10 Discount]] and discount processing under [[services-sal-dsc|SAL dsc services]] [^r1][^r2].

## See also

* [[man-sal-72|MAN-SAL-72 Ledgerline ERP 7.2 User Manual: Sales and]]
* [[screen-sal-dsc-10|SAL-DSC-10 Discount]]
* [[services-sal-dsc|SAL dsc services]]
* [[screen-sal-cus-01|SAL-CUS-01 Customer Master Entry]]
* [[screen-sal-crd-11|SAL-CRD-11 Credit Control Check]]
* [[screen-sal-prc-08|SAL-PRC-08 Price List]]
* [[err-cus-0001|ERR-CUS-0001 Mandatory Field Missing or Invalid in Customer Master]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 40, Messages
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 40, Messages
