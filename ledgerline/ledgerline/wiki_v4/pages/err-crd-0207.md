---
title: "ERR-CRD-0207 Customer Credit Limit Exceeded"
type: "error"
slug: "err-crd-0207"
summary: "Error raised on screen SAL-SO-01 when confirming an order that exceeds the customer's credit limit."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-SAL-001 Sales Order to Despatch v2.2.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-CRD-0207 |
| Module | CRD (Credit / Sales) |
| Screen | SAL-SO-01 |
| Trigger | Confirming order exceeding credit limit |
| Action | Contact accounts to review ledger or adjust status |

`ERR-CRD-0207` is an error code in Ledgerline triggered when a user attempts to confirm a sales order that exceeds the assigned customer credit limit [^r1]. It blocks confirmation directly on screen [[screen-sal-so-01|SAL-SO-01]] [^r1]. To proceed, sales staff must coordinate with the accounts department to address the outstanding balance or update the customer's account status [^r2].

## Meaning
`ERR-CRD-0207` indicates that the order value pushes the customer account beyond its authorized credit ceiling [^r1].

## Cause
The error is generated when attempting to confirm an order on screen [[screen-sal-so-01|SAL-SO-01]] while the customer's credit limit is exceeded [^r1].

## How to fix
Staff must contact the accounts team to review the customer ledger, collect payment, or adjust the account status before re-attempting order confirmation on screen [[screen-sal-so-01|SAL-SO-01]] [^r2].

## Raised by
Confirmation process on screen [[screen-sal-so-01|SAL-SO-01]] under [[sop-sal-001|SOP-SAL-001]] [^r1].

## See also
* [[screen-sal-so-01|SAL-SO-01 Sales Order]]
* [[sop-sal-001|SOP-SAL-001 Sales Order to Despatch]]

## References

[^r1]: 02_procedures/SOP-SAL-001 Sales Order to Despatch v2.2.pdf, p. 3, §5. Procedure
[^r2]: 02_procedures/SOP-SAL-001 Sales Order to Despatch v2.2.pdf, p. 4, §5. Procedure: notes and common mistakes
