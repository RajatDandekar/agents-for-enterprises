---
title: "ERR-SRL-0001 Serial Number Already Registered"
type: "error"
slug: "err-srl-0001"
summary: "Error ERR-SRL-0001 blocks serial registration in Ledgerline when a serial number already exists in the ledger to maintain strict uniqueness."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-SRL-0001 |
| message | SERIAL NO already present in the serial ledger |
| module | SAL |
| raised_by | srl_reg |
| status | current |

ERR-SRL-0001 is a Ledgerline error raised when an operator attempts to register a serial number that is already recorded in the serial ledger [^r1]. It halts the registration transaction immediately to guarantee strict uniqueness across all bicycle models and customer accounts [^r1]. Resolving it requires verifying physical frame numbers and paperwork, with escalation to quality control if duplicate numbering exists [^r2].

| Field | Value |
|---|---|
| Error code | ERR-SRL-0001 |
| Message | SERIAL NO already present in the serial ledger [^r1] |
| Module | SAL (Sales) [^r1] |
| Service | srl_reg [^r1] |
| Status | Current [^r1] |

## Meaning
The system halts the transaction because the entered `SERIAL NO` is already registered in the serial ledger, preventing duplicate serial records across all customers and models [^r1].

## Cause
The error occurs when the `srl_reg` service executes for a serial number that already exists in the database [^r1].

## How to fix
1. Inspect the physical bicycle frame and cross-check the serial number against the production paperwork [^r2].
2. Use the `srl_get` service (via [[services-sal-srl|SAL srl services]]) to review the existing record associated with that serial number [^r2].
3. If duplicate physical numbering on bicycle frames is suspected, notify the factory quality office immediately [^r2].

## Raised by
- Service: `srl_reg` within [[services-sal-srl|SAL srl services]] [^r1].
- Screen: [[screen-sal-srl-16|SAL-SRL-16 Serial Registration Reg]] [^r1].
- Reference: [[man-sal-72|MAN-SAL-72 Ledgerline ERP 7.2 User Manual: Sales]] [^r1].

## See also
- [[screen-sal-srl-16|SAL-SRL-16 Serial Registration Reg]]
- [[services-sal-srl|SAL srl services]]
- [[man-sal-72|MAN-SAL-72 Ledgerline ERP 7.2 User Manual: Sales]]
- [[sop-sal-001|SOP-SAL-001 Sales Order to Despatch]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 65, Messages
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 66, Questions users ask
