---
title: "ERR-DLG Error Codes"
type: "error-list"
slug: "errors-dlg"
summary: "Error codes prefixed with ERR-DLG raised by Ledgerline administration services handling approval delegations."
audience: "staff"
status: "current"
sources: ["04_service_definitions/admin/dlg_cancel.yaml", "04_service_definitions/admin/dlg_get.yaml", "04_service_definitions/admin/dlg_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-DLG |
| Domain | Administration / Approval Delegations |
| Module | ADM |
| Services | dlg_get, dlg_save, dlg_cancel |

The ERR-DLG error code prefix covers validation and state errors raised during approval delegation processing in Ledgerline [^r1][^r2][^r3][^r4]. These errors occur when retrieving, creating, modifying, or cancelling delegation records across the [[services-adm-dlg|ADM dlg services]] [^r1][^r3][^r4].

### ERR-DLG-0001
* **Message:** APPROVAL DELEGATION NOT FOUND [^r1][^r3]
* **Cause:** The requested approval delegation record does not exist when attempting to access, fetch, or cancel it [^r1][^r3].
* **Remedy:** Verify the delegation identifier before attempting retrieval or cancellation [^r1][^r3].
* **Raised by:** `dlg_get` [^r3], `dlg_cancel` [^r1]

### ERR-DLG-0210
* **Message:** DELEGATE ROLE LOWER THAN DELEGATOR [^r4]
* **Cause:** The designated delegate holds a role lower than that of the delegator [^r4].
* **Remedy:** Select a delegate who holds a role equal to or higher than the delegator [^r4].
* **Raised by:** `dlg_save` [^r4]
* **Page:** [[err-dlg-0210|ERR-DLG-0210 Delegate role lower than delegator]]

### ERR-DLG-0801
* **Message:** APPROVAL DELEGATION CLOSED (<status>) [^r2]
* **Cause:** An attempt was made to cancel an approval delegation that is already closed [^r2].
* **Remedy:** Do not attempt cancellation on a delegation record that has already concluded [^r2].
* **Raised by:** `dlg_cancel` [^r2]

## See also
* [[err-dlg-0210|ERR-DLG-0210 Delegate role lower than delegator]]
* [[screen-sys-dlg-03|SYS-DLG-03 Approval Delegation Entry]]
* [[services-adm-dlg|ADM dlg services]]

## References

[^r1]: 04_service_definitions/admin/dlg_cancel.yaml, errors
[^r2]: 04_service_definitions/admin/dlg_cancel.yaml, errors
[^r3]: 04_service_definitions/admin/dlg_get.yaml, errors
[^r4]: 04_service_definitions/admin/dlg_save.yaml, errors
