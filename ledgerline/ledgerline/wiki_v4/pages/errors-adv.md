---
title: "Errors ADV"
type: "error-list"
slug: "errors-adv"
summary: "Catalogue of ERR-ADV advance payment error codes raised by Ledgerline accounts payable advance services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/accounts_payable/adv_adjust.yaml", "04_service_definitions/accounts_payable/adv_approve.yaml", "04_service_definitions/accounts_payable/adv_get.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| prefix | ERR-ADV |
| module | Accounts Payable |
| subsystem | Advance Payments |
| status | current |

The ERR-ADV error code prefix identifies exceptions raised by Ledgerline's accounts payable advance payment services. These codes signal validation failures during advance retrieval, adjustment, and approval workflows. As of 26 October 2026, the catalogue covers missing records and invalid advance payment lifecycle states encountered across [[services-ap-adv|AP adv services]].

### ERR-ADV-0001
* **Message:** ADVANCE PAYMENT NOT FOUND [^r1][^r2][^r4]
* **Cause:** The system cannot locate the specified advance payment number in the database [^r2].
* **Remedy:** Verify the advance payment reference number and ensure it exists before attempting retrieval, adjustment, or approval.
* **Raised by:** Service `adv_adjust` [^r1], service `adv_approve` [^r2], and service `adv_get` [^r4].
* **Detailed page:** [[err-adv-0001]]

### ERR-ADV-0007
* **Message:** ADVANCE PAYMENT NOT IN DRAFT (<status>) [^r3]
* **Cause:** The service `adv_approve` attempted to approve an advance payment that is not currently in DRAFT status [^r3].
* **Remedy:** Check the current lifecycle status of the advance payment record before submitting an approval request.
* **Raised by:** Service `adv_approve` [^r3].
* **Detailed page:** [[err-adv-0007]]

## See also
* [[services-ap-adv|AP adv services]]
* [[screen-ap-adv-07|AP-ADV-07 Advance Payment Entry]]
* [[err-adv-0001]]
* [[err-adv-0007]]
* [[errors-apr|Errors APR]]
* [[errors-sup|ERR-SUP Error Codes]]

## References

[^r1]: 04_service_definitions/accounts_payable/adv_adjust.yaml, errors
[^r2]: 04_service_definitions/accounts_payable/adv_approve.yaml, errors
[^r4]: 04_service_definitions/accounts_payable/adv_get.yaml, errors
[^r3]: 04_service_definitions/accounts_payable/adv_approve.yaml, errors
