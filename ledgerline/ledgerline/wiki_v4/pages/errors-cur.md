---
title: "ERR-CUR Error Codes"
type: "error-list"
slug: "errors-cur"
summary: "Error codes prefixed with ERR-CUR in Ledgerline Accounts Payable, covering currency lookup and exchange rate errors."
audience: "staff"
status: "current"
sources: ["04_service_definitions/accounts_payable/cur_get.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-CUR |
| Module | Accounts Payable |
| Domain | Currency Rates |
| Status | Current |

This catalogue lists all Ledgerline system error codes sharing the `ERR-CUR` prefix across Accounts Payable currency functions. These errors arise during currency retrieval and exchange rate validation tasks within currency services such as [[services-ap-cur|AP cur services]]. Operational users encountering these errors during transaction entry on [[screen-ap-cur-13|AP-CUR-13 Currency Rate]] can identify the raising service and error message here.

### ERR-CUR-0001

* **Message:** CURRENCY RATE NOT FOUND [^r1]
* **Cause:** The requested currency exchange rate record does not exist in the system for the specified currency or date parameters.
* **Remedy:** Verify that the exchange rate has been entered for the transaction date and currency code, or create the missing rate entry.
* **Raised by:** Service `cur_get` [^r1]
* **Detailed page:** [[err-cur-0001|ERR-CUR-0001 Currency Rate Action Failed]]

## See also

* [[err-cur-0001|ERR-CUR-0001 Currency Rate Action Failed]]
* [[screen-ap-cur-13|AP-CUR-13 Currency Rate]]
* [[services-ap-cur|AP cur services]]

## References

[^r1]: 04_service_definitions/accounts_payable/cur_get.yaml, errors
