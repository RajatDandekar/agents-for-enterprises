---
title: "ERR-SUP-0118 VAT number already registered"
type: "error"
slug: "err-sup-0118"
summary: "Ledgerline error ERR-SUP-0118 prevents creating a duplicate supplier record when the specified VAT number is already registered."
audience: "staff"
status: "mixed"
sources: ["01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf", "01_policies/POL-SUP-003 Supplier Policy v2.3.pdf", "01_policies/old/Supplier_Policy_v2.2.docx", "04_service_definitions/purchase/sup_create.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error Code | ERR-SUP-0118 |
| Message | VAT NO ALREADY REGISTERED |
| Raised By | sup_create |
| Module | Purchase / Supplier Master |
| Severity | Error (blocks creation) |

ERR-SUP-0118 is a Ledgerline validation error that blocks the creation of a new supplier record when the entered VAT registration number already exists in the supplier master [^r1][^r2]. Under [[pol-sup-003|POL-SUP-003]], duplicate prevention during supplier creation relies on this validation [^r1][^r3]. As of 26 October 2026, it ensures that distinct supplier codes are not assigned to an entity sharing an existing VAT registration [^r1].

| Field | Value |
|---|---|
| Error Code | ERR-SUP-0118 |
| Message | VAT NO ALREADY REGISTERED |
| Raised By | `sup_create` |
| Module | Purchase / Supplier Master |
| Severity | Error (blocks creation) |

## Meaning
The error message `VAT NO ALREADY REGISTERED` indicates that the submitted VAT registration number is already assigned to an existing supplier in the master database [^r1][^r2]. Ledgerline halts the onboarding transaction and refuses to create a second supplier record [^r1][^r4].

## Cause
This error is triggered when a user or interface attempts to register a supplier profile with a VAT number that matches a record already stored in the system [^r1][^r2]. In the `sup_create` service, duplicate prevention is enforced exclusively through ERR-SUP-0118 whenever a VAT registration number is provided in the payload [^r3].

## How to fix
Users encountering this error must not attempt to duplicate the supplier profile in Ledgerline [^r1][^r4]. To resolve it:
1. Search the existing supplier master via the supplier search facilities to identify the supplier record currently using the VAT number [^r1].
2. Verify whether the vendor is already registered and active under an existing supplier code [^r1].
3. If an existing supplier record matches the entity, utilize the existing code rather than creating a new record [^r1].

## Raised by
The error is raised by the `sup_create` service in [[services-pur-sup|PUR sup services]] when processing new supplier registrations [^r2][^r3].

## Versions and conflicts
- **Current rule (effective 2026-04-01):** [[pol-sup-003|POL-SUP-003]] v2.3 specifies that Ledgerline generates ERR-SUP-0118 and refuses supplier creation when a VAT registration number is already registered in the master [^r1].
- **Older rule:** Superseded policy POL-SUP-003 v2.2 (referenced in [[pol-pur-001|POL-PUR-001]]) similarly issued ERR-SUP-0118 and refused record creation when attempting to register a supplier with an existing VAT number [^r5].
- **Conflict type:** `superseded` [^r1][^r5].

## See also
- [[errors-sup|ERR-SUP Error Codes]]
- [[pol-sup-003|POL-SUP-003 Supplier Policy]]
- [[services-pur-sup|PUR sup services]]
- [[sop-pur-001|SOP-PUR-001 Supplier Onboarding]]
- [[screen-pur-sup-01|PUR-SUP-01 Supplier Master Create]]

## References

[^r1]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 2, §6. Duplicate suppliers
[^r2]: 04_service_definitions/purchase/sup_create.yaml, errors
[^r3]: 04_service_definitions/purchase/sup_create.yaml, notes
[^r4]: 01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf, p. 2, §6. Duplicate suppliers
[^r5]: 01_policies/old/Supplier_Policy_v2.2.docx, §6. Duplicate suppliers
