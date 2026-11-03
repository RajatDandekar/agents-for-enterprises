---
title: "ERR-CRD-0001 Missing mandatory remarks for credit release"
type: "error"
slug: "err-crd-0001"
summary: "Validation error raised in Ledgerline when attempting a credit release with a blank or invalid COMMENT field."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-CRD-0001 |
| Module | SAL (Sales) |
| Service | crd_release |
| Screen | SAL-CRD-11 Credit Control Check |
| Trigger | Blank or invalid COMMENT field |
| Status | Current |

ERR-CRD-0001 is an application validation error raised during the credit release workflow in [[man-sal-72|Ledgerline ERP 7.2 Sales]][^r1]. It indicates that an operator attempted to execute a credit release without supplying the required justification in the mandatory remarks field[^r1]. Entering a valid comment is required before the credit hold can be overridden and released[^r1].

## Meaning
ERR-CRD-0001 indicates that mandatory remarks are missing or improperly formatted during a credit release action[^r1].

## Cause
The error occurs when a user triggers the `crd_release` action while leaving the `COMMENT` field completely blank or populated with invalid characters[^r1].

## How to fix
Provide a valid alphanumeric rationale in the `COMMENT` field on the credit release interface before executing the `crd_release` command[^r1].

## Raised by
The error is raised by the `crd_release` service, accessed via [[screen-sal-crd-11|SAL-CRD-11 Credit Control Check]] under [[services-sal-crd|SAL crd services]][^r1].

## See also
* [[screen-sal-crd-11|SAL-CRD-11 Credit Control Check]]
* [[services-sal-crd|SAL crd services]]
* [[man-sal-72|MAN-SAL-72 Ledgerline ERP 7.2 User Manual: Sales]]
* [[sop-sal-001|SOP-SAL-001 Sales Order to Despatch]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 46, Messages
