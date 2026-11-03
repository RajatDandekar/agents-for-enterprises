---
title: "ERR-EDI-0101 Partner Not Set Up"
type: "error"
slug: "err-edi-0101"
summary: "Error raised when an incoming EDI transmission sender trading partner identifier is not linked to an active sales ledger account."
audience: "staff"
status: "current"
sources: ["12_integrations/EDI ORDERS interface spec v2.1.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-EDI-0101 |
| type | error |
| module | EDI / Sales |
| source_interface | INT-EDI-001 |
| severity | Error |

Error ERR-EDI-0101 is an inbound interface error triggered when an EDI transmission originates from an unmapped trading partner [^r1]. It indicates that the incoming sender trading partner identifier cannot be matched to any active customer account in the sales ledger [^r1]. Transactions triggering this code halt processing until sales administration establishes the partner mapping [^r2].

| Field | Value |
|---|---|
| Error Code | ERR-EDI-0101 |
| Message | Partner Not Set Up |
| Document | [[int-edi-001|INT-EDI-001]] |
| Functional Area | EDI / Sales Ledger |

## Meaning
ERR-EDI-0101 indicates that an incoming EDI transmission contains a sender trading partner identifier that is not linked to an active sales ledger account [^r1].

## Cause
The error occurs when an inbound EDI transmission arrives with a trading partner identifier that lacks an active association to an approved sales ledger account [^r1].

## How to fix
To clear ERR-EDI-0101, sales administrators must verify that the retailer has an open, approved credit account [^r2]. Once verified, administrators must enable electronic trading flags and associate the partner identifier with the account [^r2].

## Raised by
The error is defined in the [[int-edi-001|INT-EDI-001]] interface specification and is raised during inbound transmission validation [^r1].

## See also
* [[errors-edi|ERR-EDI error codes]]
* [[int-edi-001|INT-EDI-001 EDI ORDERS Interface Specification]]
* [[services-sal-edi|SAL edi services]]
* [[err-edi-0140|ERR-EDI-0140 Unknown Buyer Item Code]]

## References

[^r1]: 12_integrations/EDI ORDERS interface spec v2.1.pdf, p. 3, §4. Errors
[^r2]: 12_integrations/EDI ORDERS interface spec v2.1.pdf, p. 3, §4. Errors
