---
title: "ERR-PCS-0001"
type: "error"
slug: "err-pcs-0001"
summary: "Validation error raised when mandatory petty cash fields OU CD, AMOUNT, PURPOSE, or CC CD are omitted."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-PCS-0001 |
| module | AP |
| raised_by | pcs_save, pcs_post |
| severity | Error |
| status | current |

ERR-PCS-0001 is an Accounts Payable validation error code in Ledgerline ERP 7.2 [^r1]. It indicates that one or more mandatory fields are missing during petty cash transaction processing [^r1]. Transactions cannot be saved or posted until all required header and distribution values are supplied [^r1].

## Meaning
The system rejects the transaction because at least one required petty cash field lacks a value [^r1].

## Cause
This error is triggered when `OU CD`, `AMOUNT`, `PURPOSE`, or `CC CD` is left blank on entry [^r1].

## How to fix
Populate all required fields—Operating Unit (`OU CD`), transaction amount (`AMOUNT`), business justification (`PURPOSE`), and Cost Centre (`CC CD`)—before attempting to save or post the record [^r1].

## Raised by
The message is returned by the `pcs_save` or `pcs_post` service operations [^r1].

## See also
* [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]]
* [[screen-ap-pcs-15|AP-PCS-15 Petty Cash Entry]]
* [[services-ap-pcs|AP pcs services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 57, Messages
