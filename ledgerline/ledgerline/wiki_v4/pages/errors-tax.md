---
title: "ERR-TAX Error Codes"
type: "error-list"
slug: "errors-tax"
summary: "Catalogue of Ledgerline ERP 7.2 tax error codes including tax code lookup failures and invalid tax codes."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "04_service_definitions/accounts_payable/tax_get.yaml", "04_service_definitions/purchase/tax_compute.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code_prefix | ERR-TAX |
| module | Accounts Payable / Purchase |
| system | Ledgerline ERP 7.2 |
| status | current |

This page catalogues the tax error codes defined under the ERR-TAX prefix in [[man-ap-72|Ledgerline ERP 7.2 User Manual: Accounts]][^r1]. These messages handle missing tax master records and invalid tax specifications across accounts payable and purchasing operations[^r1][^r2][^r3].

### ERR-TAX-0001

* **Message:** TAX CODE MASTER NOT FOUND[^r1][^r2]
* **Cause:** The requested tax code cannot be found in the tax master record[^r2].
* **Remedy:** Ensure the referenced tax code exists and is correctly defined in the master records[^r1][^r2].
* **Raised by:** Service `tax_get` (documented under [[services-ap-tax|AP tax services]])[^r2].
* **Detailed page:** [[err-tax-0001]]

### ERR-TAX-0101

* **Message:** INVALID TAX CODE[^r1][^r3]
* **Cause:** The tax code supplied is invalid during calculation[^r3].
* **Remedy:** Verify and enter an active, valid tax code[^r1][^r3].
* **Raised by:** Service `tax_compute` (documented under [[services-pur-tax|PUR tax services]])[^r3].

## See also

* [[data-tax-codes|Tax codes]]
* [[err-tax-0001|ERR-TAX-0001 TAX CODE MASTER NOT FOUND]]
* [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]]
* [[screen-ap-tax-17|AP-TAX-17 Tax Code Master]]
* [[services-ap-tax|AP tax services]]
* [[services-pur-tax|PUR tax services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 66, §20. Messages
[^r2]: 04_service_definitions/accounts_payable/tax_get.yaml, errors
[^r3]: 04_service_definitions/purchase/tax_compute.yaml, errors
