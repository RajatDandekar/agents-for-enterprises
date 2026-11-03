---
title: "ERR-MAT-0420 Match override permission denied"
type: "error"
slug: "err-mat-0420"
summary: "Error raised when an unauthorized user attempts to override an invoice match, requiring AP manager review."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-AP-001 Three-Way Invoice Matching v2.1.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | ERR-MAT-0420 |
| Module | AP |
| Type | Error |
| Raised by | Three-way matching override |
| Resolution | AP manager review required |

Error ERR-MAT-0420 is an authorization error in Ledgerline accounts payable processing that prevents non-managerial staff from bypassing invoice discrepancies [^r1]. As of 26 October 2026, the error stops any user other than the AP manager from forcing an invoice match [^r1]. Invoices encountering this error cannot be processed further by standard entry staff and must remain on hold pending managerial review [^r2].

| Field | Value |
|---|---|
| Error code | ERR-MAT-0420 |
| Description | Match override permission denied |
| Procedure | [[sop-ap-001|SOP-AP-001]] |
| Required role | AP Manager |

## Meaning
ERR-MAT-0420 indicates that the user attempting to override a three-way invoice match lacks the necessary system permission [^r2].

## Cause
The error is raised when any user other than the AP manager attempts to execute a match override in the system [^r1].

## How to fix
Repeated override attempts by unauthorized users will not clear the match failure [^r2]. Affected invoices must remain on hold until the AP manager reviews the file directly and resolves the discrepancy [^r2].

## Raised by
The error is triggered during the invoice matching procedure when an unauthorized override action is submitted [^r1].

## See also
* [[sop-ap-001|SOP-AP-001 Three-Way Invoice Matching]]
* [[screen-ap-inv-01|AP-INV-01 Supplier Invoice Entry]]

## References

[^r1]: 02_procedures/SOP-AP-001 Three-Way Invoice Matching v2.1.pdf, p. 3, §5. Procedure
[^r2]: 02_procedures/SOP-AP-001 Three-Way Invoice Matching v2.1.pdf, p. 4, Common mistakes when entering invoices
