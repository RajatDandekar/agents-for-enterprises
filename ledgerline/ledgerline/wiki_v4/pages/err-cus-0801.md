---
title: "ERR-CUS-0801 Invalid or Duplicate VAT Number"
type: "error"
slug: "err-cus-0801"
summary: "Ledgerline error when customer VAT registration format fails validation or duplicates an active trading account."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-CUS-0801 |
| Module | Sales (SAL) |
| Screen | SAL-CUS-01 Customer Master Entry |
| Service | cust_search / cust services |
| Severity | Fatal / Validation Block |
| Status | Current |

ERR-CUS-0801 is a customer maintenance validation error in Ledgerline ERP 7.2 [^r1]. It blocks saving when a VAT registration number fails syntax rules or duplicates an existing record, preventing incorrect tax treatment and split credit records [^r1]. Resolving it requires verifying formatting or coordinating with credit control before creating duplicate accounts [^r2].

| Field | Value |
|---|---|
| Error code | ERR-CUS-0801 |
| Module | Sales (SAL) |
| Standard screen | [[screen-sal-cus-01|SAL-CUS-01 Customer Master Entry]] |
| Related services | [[services-sal-cust|SAL cust services]] |

## Meaning
ERR-CUS-0801 signifies that an entered VAT number fails tax format checks or matches an existing active account trading under the identical registration [^r1].

## Cause
The error is triggered during customer record creation or update on [[screen-sal-cus-01|SAL-CUS-01 Customer Master Entry]] [^r1]. It occurs either when the input string does not conform to expected regional tax format rules, or when the database detects another active customer account already registered under the exact same VAT number [^r1].

## How to fix
Inspect the entered VAT registration string for typographical errors or unintended spaces [^r2]. Use the `cust_search` service within [[services-sal-cust|SAL cust services]] to verify whether existing branch accounts are already operating under that number [^r2]. Consult credit control prior to saving the record [^r2].

## Raised by
The error is raised by customer record validation routines in [[man-sal-72|MAN-SAL-72 Ledgerline ERP 7.2 User Manual: Sales]] during customer maintenance actions [^r1].

## See also
* [[screen-sal-cus-01|SAL-CUS-01 Customer Master Entry]]
* [[services-sal-cust|SAL cust services]]
* [[screen-sal-crd-11|SAL-CRD-11 Credit Control Check]]
* [[err-cus-0001|ERR-CUS-0001 Mandatory Field Missing or Invalid in Customer Master]]
* [[man-sal-72|MAN-SAL-72 Ledgerline ERP 7.2 User Manual: Sales]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 5, Messages
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 5, Messages
