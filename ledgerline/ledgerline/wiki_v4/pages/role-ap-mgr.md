---
title: "Role AP-MGR"
type: "role"
slug: "role-ap-mgr"
summary: "Ledgerline role required to perform three-way match overrides via the mat_override service."
audience: "staff"
status: "current"
sources: ["04_service_definitions/accounts_payable/mat_override.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Role code | AP-MGR |
| Module | Accounts Payable |
| Service authorization | mat_override |

The `AP-MGR` role is an Accounts Payable management role in Ledgerline that controls match discrepancy resolution. Users assigned this role hold the authorization required to execute three-way match overrides [^r1]. If a user without the role attempts to run the match override service, the system blocks the action and logs a permission error [^r1].

## Authorizations and services

The `AP-MGR` role is mandatory to execute the Accounts Payable three-way match override service `mat_override` in [[services-ap-mat|AP mat services]] [^r1]. When invoked without this role, the service fails and returns [[err-mat-0420|ERR-MAT-0420]] ('OVERRIDE NEEDS AP-MGR ROLE') [^r1].

## See also

* [[err-mat-0420|ERR-MAT-0420 Match override permission denied]]
* [[errors-mat|ERR-MAT message and error codes]]
* [[screen-ap-mat-02|AP-MAT-02 Three-Way Match]]
* [[services-ap-mat|AP mat services]]
* [[user-jfletcher|Joanna Fletcher (JFLETCHER)]]

## References

[^r1]: 04_service_definitions/accounts_payable/mat_override.yaml, errors
