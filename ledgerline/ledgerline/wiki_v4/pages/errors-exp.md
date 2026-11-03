---
title: "ERR-EXP error codes"
type: "error-list"
slug: "errors-exp"
summary: "Reference list of ERR-EXP error codes returned by Ledgerline accounts payable expense claim services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/accounts_payable/exp_approve.yaml", "04_service_definitions/accounts_payable/exp_get.yaml", "04_service_definitions/accounts_payable/exp_pay.yaml", "04_service_definitions/accounts_payable/exp_reject.yaml", "04_service_definitions/accounts_payable/exp_submit.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-EXP |
| Module | Accounts Payable |
| Domain | Expense Claims |
| Status | Current |

The `ERR-EXP` error code series covers validation and processing failures encountered during Ledgerline expense claim workflows. These codes are returned by accounts payable expense services when claims are missing, in an invalid status, out of date, or lacking required receipts.

### ERR-EXP-0001
* **Message:** `EXPENSE CLAIM NOT FOUND` [^r1]
* **Cause:** The requested expense claim record cannot be located in the system [^r1][^r4].
* **Remedy:** Verify the expense claim identifier and confirm the record exists before retrying the action.
* **Raised by:** `exp_approve` [^r1], `exp_get` [^r4], `exp_pay` [^r5], `exp_reject` [^r6], `exp_submit` [^r7]

### ERR-EXP-0007
* **Message:** `EXPENSE CLAIM NOT IN DRAFT (<status>)` [^r2]
* **Cause:** The operation requires the expense claim to be in draft state, but it is currently in another status [^r2][^r7].
* **Remedy:** Check the current claim status in the system and ensure the workflow action matches the permitted lifecycle state.
* **Raised by:** `exp_approve` [^r2], `exp_submit` [^r7]

### ERR-EXP-0230
* **Message:** `RECEIPT MISSING FOR LINE ABOVE LIMIT` [^r7]
* **Cause:** A line item on the expense claim exceeds the receipt threshold but does not have an attached receipt [^r7].
* **Remedy:** Attach the required receipt document to the specified line item before resubmitting.
* **Raised by:** `exp_submit` [^r7]

### ERR-EXP-0240
* **Message:** `CLAIM OLDER THAN 90 DAYS` [^r3]
* **Cause:** The expense claim submission or approval date exceeds the 90-day allowable window [^r3].
* **Remedy:** Review company expense filing limits or seek appropriate policy exception approvals for aged claims.
* **Raised by:** `exp_approve` [^r3]

## See also
* [[services-ap-exp|AP exp services]]
* [[screen-ap-exp-09|AP-EXP-09 Expense Claim Entry]]
* [[errors-apr|Errors APR]]

## References

[^r1]: 04_service_definitions/accounts_payable/exp_approve.yaml, errors
[^r4]: 04_service_definitions/accounts_payable/exp_get.yaml, errors
[^r5]: 04_service_definitions/accounts_payable/exp_pay.yaml, errors
[^r6]: 04_service_definitions/accounts_payable/exp_reject.yaml, errors
[^r7]: 04_service_definitions/accounts_payable/exp_submit.yaml, errors
[^r2]: 04_service_definitions/accounts_payable/exp_approve.yaml, errors
[^r3]: 04_service_definitions/accounts_payable/exp_approve.yaml, errors
