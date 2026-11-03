---
title: "Errors ACR"
type: "error-list"
slug: "errors-acr"
summary: "Reference catalogue of accounts payable goods received not invoiced accrual error codes raised by Ledgerline ACR services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/accounts_payable/acr_get.yaml", "04_service_definitions/accounts_payable/acr_reverse.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-ACR |
| Module | Accounts Payable |
| Subsystem | GRNI Accrual |
| Status | current |

Error catalogue for the `ERR-ACR-*` code family used in Ledgerline accounts payable processing as of 26 October 2026. These codes are returned during goods received not invoiced (GRNI) accrual lookups and reversals across [[services-ap-acr|AP acr services]]. Operational investigation and screen handling are documented under [[err-acr-0001|ERR-ACR-0001: Accrual execution or reversal failed]] and [[screen-ap-acr-10|AP-ACR-10 Grni Accrual]].

### ERR-ACR-0001

* **Message:** `GRNI ACCRUAL NOT FOUND` [^r1][^r2]
* **Cause:** The requested goods received not invoiced accrual record cannot be located during service execution [^r1][^r2].
* **Remedy:** Verify that the accrual reference exists and is available before querying or attempting reversal; refer to [[err-acr-0001|ERR-ACR-0001]] for narrative troubleshooting.
* **Raised by:** Service `acr_get` [^r1] and service `acr_reverse` [^r2].

## See also

* [[err-acr-0001|ERR-ACR-0001: Accrual execution or reversal failed]]
* [[screen-ap-acr-10|AP-ACR-10 Grni Accrual]]
* [[services-ap-acr|AP acr services]]
* [[user-jfletcher|Joanna Fletcher (JFLETCHER)]]

## References

[^r1]: 04_service_definitions/accounts_payable/acr_get.yaml, errors
[^r2]: 04_service_definitions/accounts_payable/acr_reverse.yaml, errors
