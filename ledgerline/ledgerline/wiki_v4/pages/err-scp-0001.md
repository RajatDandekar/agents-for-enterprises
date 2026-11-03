---
title: "ERR-SCP-0001 Mandatory scrap header or line details missing"
type: "error"
slug: "err-scp-0001"
summary: "Error ERR-SCP-0001 indicates mandatory scrap header or line details such as work order number or item code are missing."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error Code | ERR-SCP-0001 |
| Message | Mandatory scrap header or line details missing |
| Module | PRD (Production) |
| Screen | PRD-SCP-12 |
| Services | scp_save, scp_post |

Error ERR-SCP-0001 is a production validation error raised when attempting to record scrap without necessary header or line data [^r1]. It halts execution during scrap transaction processing on screen [[screen-prd-scp-12|PRD-SCP-12]] [^r1]. Users must ensure key fields including work order number and item code are populated before resubmitting [^r1].

## Meaning
The error indicates that required header or line-level details are missing from the scrap transaction record [^r1].

## Cause
The error is triggered when required input fields such as WO NO or ITEM CD are omitted during scrap data entry [^r1].

## How to fix
Populate all mandatory header and line fields, specifically WO NO and ITEM CD, prior to saving or posting the scrap record on screen [[screen-prd-scp-12|PRD-SCP-12]] [^r1].

## Raised by
The message is raised during execution of the `scp_save` or `scp_post` services within [[services-prd-scp|PRD scp services]] on screen [[screen-prd-scp-12|PRD-SCP-12]] [^r1]. It is documented in [[man-prd-72|MAN-PRD-72]] [^r1].

## See also
* [[screen-prd-scp-12|PRD-SCP-12 Production Scrap Entry]]
* [[services-prd-scp|PRD scp services]]
* [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]]
* [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 56, Messages
