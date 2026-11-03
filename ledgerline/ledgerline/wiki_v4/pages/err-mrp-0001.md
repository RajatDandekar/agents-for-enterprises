---
title: "ERR-MRP-0001"
type: "error"
slug: "err-mrp-0001"
summary: "Fatal MRP run execution error halting order generation due to invalid parameters, missing calendars, pending transactions, or circular BOM references."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error Code | ERR-MRP-0001 |
| Module | Production (PRD) |
| Service | mrp_run |
| Severity | Fatal |
| Status | current |

Error `ERR-MRP-0001` is a fatal system message raised during the material requirements planning calculation in [[man-prd-72|MAN-PRD-72]]. When triggered, the planning engine terminates immediately without generating planned orders and marks the run as aborted [^r2]. Resolving the error requires clearing configuration faults, posting uncommitted inventory movements, or removing circular references from the bill of materials [^r3].

## Meaning

`ERR-MRP-0001` signals that the MRP engine encountered an unrecoverable condition during processing [^r1]. The MRP calculation halts immediately, no planned orders are created, and the corresponding RUN ID status is marked as aborted [^r2].

## Cause

The error occurs during the execution of `mrp_run` when the engine encounters one of the following root causes [^r1]:
* An invalid parameter entry, such as an invalid planning horizon [^r1][^r3].
* Missing planning calendar data across active sites [^r1][^r3].
* Incomplete or unposted transaction logs in inventory movements [^r1][^r3].
* An unresolvable circular reference within an active bill of materials [^r1][^r3].

## How to fix

To resolve `ERR-MRP-0001`, complete the following diagnostic checks prior to relaunching the process [^r3]:
1. Verify that the `HORIZON` parameter contains a valid entry [^r3].
2. Confirm that factory calendars for Manchester and Leeds are defined and open across the entire planning window [^r3].
3. Ensure that all pending inventory movements and transaction logs are posted [^r3].
4. Inspect assembly structures on [[screen-prd-bom-02|PRD-BOM-02]] to ensure no sub-assembly lists itself as a parent component, resolving any circular loops [^r3].

## Raised by

This error is raised by the `mrp_run` service within [[services-prd-mrp|PRD mrp services]] during execution from [[screen-prd-mrp-09|PRD-MRP-09 Mrp Run]] [^r1].

## See also

* [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]]
* [[screen-prd-mrp-09|PRD-MRP-09 Mrp Run]]
* [[services-prd-mrp|PRD mrp services]]
* [[screen-prd-bom-02|PRD-BOM-02 Bill Of Materials]]
* [[services-prd-bom|PRD bom services]]
* [[err-bom-0001|ERR-BOM-0001 Parent assembly not found on bill of materials master]]

## References

[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 24, Messages
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 24, Messages
[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 24, Messages
