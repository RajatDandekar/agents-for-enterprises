---
title: "SOP-FIN-001 Cost Centre Open and Close"
type: "procedure"
slug: "sop-fin-001"
summary: "Procedure for opening and retiring Ledgerline cost centres, requiring zero balances, buyer notification, and document settlement."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-FIN-001 Cost Centre Open and Close v1.1.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | SOP-FIN-001 |
| owner | Grace Whitaker |
| version | 1.1 |
| effective | 2025-01-01 |
| approved_by | Henrik Weber |
| status | current |

SOP-FIN-001 governs the opening and closing of cost centres in Ledgerline ERP at the start and end of production programmes [^r1][^r4]. All financial postings in Ledgerline ERP require an active, validated cost centre before any transactions can proceed [^r2]. Finance cannot mark a cost centre inactive until all associated purchase orders, subcontracts, and timesheets are settled to a zero balance, and buyers are given advance notice [^r3][^r5].

## Steps

Finance opens or retires cost centre records at the start or conclusion of each production programme [^r4]. 

When closing a cost centre, Finance must notify buyers 10 working days prior to initiating the closure [^r5]. The cost centre manager must certify that all purchase orders, subcontract charges, and timesheet allocations are fully settled [^r3]. Finance then verifies that the ending balance of the cost centre is exactly zero before marking the record inactive [^r3]. 

If any open documents remain assigned to the cost centre, Ledgerline ERP blocks the closure and returns error [[err-cc-0310|ERR-CC-0310]], requiring open items to be cancelled or reassigned before proceeding [^r7]. Closing a cost centre does not automatically update user profiles; cost centre owners must submit an access amendment request to IT under [[sop-it-001|SOP-IT-001]] to reassign default cost centres [^r6].

Once a cost centre is retired, staff must attach the final balance listing and the closure sign-off sheet to the original opening document, file them alphabetically by department name, and preserve them indefinitely in the finance archive at the Manchester plant, with a digital scan saved to the shared network drive [^r8].

## Forms and screens

* Screen [[screen-fin-cc-01|FIN-CC-01]]: used by Finance to open and close cost centre records [^r4].
* Closure sign-off sheet: completed alongside the final balance listing and attached to the original opening document [^r8].

## See also

* [[screen-fin-cc-01|FIN-CC-01 Cost Centre Entry]]
* [[sop-it-001|SOP-IT-001 User Access Request]]
* [[err-cc-0310|ERR-CC-0310 Cost centre has open documents]]
* [[errors-cc|Cost Centre Error Codes (ERR-CC-*)]]
* [[user-gwhitaker|Grace Whitaker]]
* [[user-hweber|Henrik Weber]]

## References

[^r1]: 02_procedures/SOP-FIN-001 Cost Centre Open and Close v1.1.pdf, p. 1, Cost Centre Open and Close
[^r4]: 02_procedures/SOP-FIN-001 Cost Centre Open and Close v1.1.pdf, p. 3, §5. Procedure
[^r2]: 02_procedures/SOP-FIN-001 Cost Centre Open and Close v1.1.pdf, p. 2, §2. Scope
[^r3]: 02_procedures/SOP-FIN-001 Cost Centre Open and Close v1.1.pdf, p. 2, §3. Responsibilities
[^r5]: 02_procedures/SOP-FIN-001 Cost Centre Open and Close v1.1.pdf, p. 3, §5. Procedure
[^r7]: 02_procedures/SOP-FIN-001 Cost Centre Open and Close v1.1.pdf, p. 3, §5. Procedure
[^r6]: 02_procedures/SOP-FIN-001 Cost Centre Open and Close v1.1.pdf, p. 3, §5. Procedure
[^r8]: 02_procedures/SOP-FIN-001 Cost Centre Open and Close v1.1.pdf, p. 4, §6. Records
