---
title: "ERR-DMO-0801 DEMO BIKE CLOSED (<status>)"
type: "error"
slug: "err-dmo-0801"
summary: "Ledgerline error ERR-DMO-0801 indicates a demo bike record state conflict when attempting to modify, close, or allocate an invalid loan record."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-DMO-0801 |
| Message | DEMO BIKE CLOSED (<status>) |
| Module | Sales (SAL) |
| Raised by | dmo_save, dmo_close |
| Status | Current |

ERR-DMO-0801 is a Ledgerline sales validation error triggered when demo bike transactions encounter conflicting record states [^r1][^r2]. It prevents users from updating archived or already terminated loan records, resolving race conditions across concurrent sessions [^r2]. As of 26 October 2026, the error is actively enforced by the demonstration service operations in [[man-sal-72|MAN-SAL-72]] [^r1][^r2].

## Meaning
In the Ledgerline message table, ERR-DMO-0801 displays the text `DEMO BIKE CLOSED (<status>)` [^r1]. It signals an invalid state transition on a demonstration bike record [^r2].

## Cause
The error occurs when a user or background process attempts to close an already closed demonstration loan [^r2]. It is also raised when modifying an archived record, when colliding with concurrent edit locks, or when attempting to allocate a serial number that is already tied to an open demonstration movement [^r2].

## How to fix
To resolve the error, inspect the status of the demonstration record to verify whether the loan has already been closed or archived [^r2]. Clear any concurrent edit locks or wait for parallel updates to complete [^r2]. If assigning a serial number, ensure the selected unit is not currently linked to an open demonstration movement before re-submitting [^r2].

## Raised by
The error is raised by the Ledgerline services [[services-sal-dmo|dmo_save]] and `dmo_close` [^r2]. Transactions in [[screen-sal-dmo-17|SAL-DMO-17]] invoke these routines during demonstration bike entry and status updates [^r2].

## See also
* [[man-sal-72|MAN-SAL-72 Ledgerline ERP 7.2 User Manual: Sales]]
* [[screen-sal-dmo-17|SAL-DMO-17 Demo Bike Entry]]
* [[services-sal-dmo|SAL dmo services]]
* [[screen-sal-srl-16|SAL-SRL-16 Serial Registration Reg]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 70, §21. Messages
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 70, Questions users ask
