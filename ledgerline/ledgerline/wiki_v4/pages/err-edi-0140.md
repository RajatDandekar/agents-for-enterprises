---
title: "ERR-EDI-0140 Unknown Buyer Item Code"
type: "error"
slug: "err-edi-0140"
summary: "Inbound EDI error raised when an incoming customer item code cannot be mapped to a Northbridge finished bicycle or frame part."
audience: "staff"
status: "current"
sources: ["12_integrations/EDI ORDERS interface spec v2.1.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-EDI-0140 |
| Message | Unknown Buyer Item Code |
| Interface | INT-EDI-001 |
| Module | Sales Order |
| Status | Current |

Error ERR-EDI-0140 occurs during EDI inbound order processing when an incoming buyer item code cannot be resolved to an internal part number [^r1]. It halts processing of the pending sales line until the translation is configured [^r1][^r2]. Inbound orders triggering this error remain pending until manual cross-reference remediation is completed by sales staff [^r2].

| Field | Value |
|---|---|
| Error Code | ERR-EDI-0140 |
| Interface | [[int-edi-001|INT-EDI-001]] |
| Severity | Error |
| Module | Sales Order |

## Meaning
The error indicates that an incoming EDI line item contains an unknown buyer item code that cannot be mapped via the customer cross-reference table to a valid Northbridge finished bicycle or frame part [^r1].

## Cause
The buyer has specified a product code in the EDI transmission that does not have an active translation entry pointing to an internal Northbridge item in the customer cross-reference table [^r1].

## How to fix
Sales staff must inspect the customer mapping table in the sales order module, add the missing item translation, and reprocess the pending order [^r2].

## Raised by
The error is raised by the inbound EDI order translation processing governed by [[int-edi-001|INT-EDI-001 EDI ORDERS Interface Specification]] when parsing incoming line item details [^r1].

## See also
* [[errors-edi|ERR-EDI error codes]]
* [[services-sal-edi|SAL edi services]]
* [[int-edi-001|INT-EDI-001 EDI ORDERS Interface Specification]]
* [[err-edi-0101|ERR-EDI-0101 Partner Not Set Up]]

## References

[^r1]: 12_integrations/EDI ORDERS interface spec v2.1.pdf, p. 3, §4. Errors
[^r2]: 12_integrations/EDI ORDERS interface spec v2.1.pdf, p. 3, §4. Errors
