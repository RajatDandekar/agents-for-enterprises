---
title: "ERR-DMO-0001 DEMO BIKE NOT FOUND"
type: "error"
slug: "err-dmo-0001"
summary: "Ledgerline error ERR-DMO-0001 indicating missing, malformed, or unvalidated header details during demonstration loan creation on screen SAL-DMO-17."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error Code | ERR-DMO-0001 |
| Message Text | DEMO BIKE NOT FOUND |
| Module | SAL (Sales) |
| Screen | SAL-DMO-17 |
| Raised By | services-sal-dmo |
| Status | current |

ERR-DMO-0001 is a Ledgerline sales module validation error raised during demonstration loan processing. It occurs on screen [[screen-sal-dmo-17|SAL-DMO-17 Demo Bike Entry]] when loan header data is incomplete, malformed, or fails customer validation. Resolving the error requires supplying all mandatory header values and ensuring the specified customer account is valid.

## Meaning
In the Ledgerline message directory, the message text for ERR-DMO-0001 is `DEMO BIKE NOT FOUND`.[^r1]

## Cause
The error is triggered during demonstration loan creation on screen [[screen-sal-dmo-17|SAL-DMO-17]] when loan header details are absent or malformed.[^r2] Typical causes include a missing `CUST CD`, a missing `RETURN DT`, or header information that fails validation against customer master records.[^r2]

## How to fix
To resolve ERR-DMO-0001 on [[screen-sal-dmo-17|SAL-DMO-17]], enter all required header fields, verifying that both `CUST CD` and `RETURN DT` are populated.[^r2] In addition, confirm that the entered customer code corresponds to an existing, valid record in [[screen-sal-cus-01|SAL-CUS-01 Customer Master Entry]].[^r2]

## Raised by
The error is raised by the demonstration bike loan processing routines associated with [[services-sal-dmo|SAL dmo services]] when validating demonstration loan creation entries from screen [[screen-sal-dmo-17|SAL-DMO-17]].[^r2]

## See also
* [[screen-sal-dmo-17|SAL-DMO-17 Demo Bike Entry]]
* [[services-sal-dmo|SAL dmo services]]
* [[screen-sal-cus-01|SAL-CUS-01 Customer Master Entry]]
* [[services-sal-cust|SAL cust services]]
* [[man-sal-72|MAN-SAL-72 Ledgerline ERP 7.2 User Manual: Sales]]
* [[err-cus-0001|ERR-CUS-0001 Mandatory Field Missing or Invalid in Customer Master]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 70, §21. Messages
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 68, Messages
