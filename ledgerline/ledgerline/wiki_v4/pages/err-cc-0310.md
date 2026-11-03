---
title: "ERR-CC-0310 Cost centre has open documents"
type: "error"
slug: "err-cc-0310"
summary: "Ledgerline error blocking cost centre closure when open purchase requisitions, incomplete purchase orders, or unposted goods receipts remain attached."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-FIN-001 Cost Centre Open and Close v1.1.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-CC-0310 |
| Message | Cost centre has open documents |
| Type | error |
| Module | Finance (CC) |
| Source | [[sop-fin-001|SOP-FIN-001]] |

Error ERR-CC-0310 is a Ledgerline ERP validation message that prevents users from closing an active cost centre.[^r1] The block occurs whenever open commitments or unfinished documents remain assigned to the cost centre code.[^r1] As of 26 October 2026, closing the cost centre requires identifying and clearing all associated open items before the closure can proceed under [[sop-fin-001|SOP-FIN-001]].[^r1][^r3]

## Meaning

The error indicates that an attempt was made in Ledgerline ERP to close a cost centre that still carries open documents or unfinished commitments.[^r1]

## Cause

The condition is triggered by unfinished documents assigned to the cost centre, including open purchase requisitions, incomplete purchase orders, and unposted goods receipts.[^r2]

## How to fix

To resolve the error during cost centre closure, run the commitment enquiry to identify every open document tied to the cost centre.[^r3] Contact originators to either cancel redundant orders or transfer remaining commitments to a replacement cost centre.[^r3]

## Raised by

The error is raised by Ledgerline ERP during the cost centre closure procedure.[^r1]

## See also

* [[sop-fin-001|SOP-FIN-001 Cost Centre Open and Close]]
* [[screen-fin-cc-01|FIN-CC-01 Cost Centre Entry]]
* [[errors-cc|Cost Centre Error Codes (ERR-CC-*)]]

## References

[^r1]: 02_procedures/SOP-FIN-001 Cost Centre Open and Close v1.1.pdf, p. 3, §5. Procedure
[^r3]: 02_procedures/SOP-FIN-001 Cost Centre Open and Close v1.1.pdf, p. 4, What to do when something does not look right
[^r2]: 02_procedures/SOP-FIN-001 Cost Centre Open and Close v1.1.pdf, p. 3, Common mistakes
