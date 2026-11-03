---
title: "ERR-PO-0801 Order in CN, RJ or CL status cannot be amended"
type: "error"
slug: "err-po-0801"
summary: "Error raised when attempting to amend a purchase order that is in cancelled (CN), rejected (RJ), or closed (CL) status."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-PUR-003 PO Amendment and Cancellation v1.2.pdf", "04_service_definitions/purchase/po_amend.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-PO-0801 |
| type | error |
| module | purchase |
| service | po_amend |
| message | PO CLOSED (<status>) |
| status | current |

ERR-PO-0801 is a purchase order error raised when a user attempts to amend an order that is already in CN (cancelled), RJ (rejected), or CL (closed) status [^r1]. The system displays the message 'PO CLOSED (<status>)' to block modification of finalised orders [^r3]. If the purchasing requirement persists, staff must check the historical log and initiate a replacement order instead of modifying the closed record [^r2].

## Meaning
The error indicates that an amendment was attempted on an order that is already closed, rejected, or cancelled [^r1][^r3]. The system displays the message 'PO CLOSED (<status>)' [^r3].

## Cause
The error is triggered when an amendment is attempted on a purchase order whose status is CN (cancelled), RJ (rejected), or CL (closed) [^r1][^r3].

## How to fix
Users encountering this error must check the historical log to identify who closed or cancelled the record [^r2]. If the procurement requirement persists, a fresh replacement order must be raised [^r2].

## Raised by
The error is raised by the service `po_amend` within [[services-pur-po]] [^r3].

## See also
* [[sop-pur-003|SOP-PUR-003 Purchase Order Amendment and Cancellation]]
* [[errors-po|ERR-PO Error Codes]]
* [[screen-pur-pom-06|PUR-POM-06 Purchase Order Amendment]]

## References

[^r1]: 02_procedures/SOP-PUR-003 PO Amendment and Cancellation v1.2.pdf, p. 3, §5. Procedure
[^r3]: 04_service_definitions/purchase/po_amend.yaml, errors
[^r2]: 02_procedures/SOP-PUR-003 PO Amendment and Cancellation v1.2.pdf, p. 4, §5. Procedure: notes and common mistakes
