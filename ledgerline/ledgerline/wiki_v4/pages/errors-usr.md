---
title: "ERR-USR Error Codes"
type: "error-list"
slug: "errors-usr"
summary: "Reference catalogue of Ledgerline ERP ERR-USR user administration error codes, including causes, remedies, and originating administrative services."
audience: "staff"
status: "current"
sources: ["07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx", "04_service_definitions/admin/usr_create.yaml", "04_service_definitions/admin/usr_disable.yaml", "04_service_definitions/admin/usr_lock.yaml", "04_service_definitions/admin/usr_pwd_reset.yaml", "04_service_definitions/admin/usr_unlock.yaml", "04_service_definitions/admin/usr_update.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-USR |
| Domain | User Administration |
| System | Ledgerline ERP 7.2 |
| Status | current |
| Catalogued codes | 4 |
| Reference source | [[data-data-dictionary|Ledgerline_7.2_tables_and_fields]] |

The `ERR-USR` series comprises Ledgerline ERP 7.2 error codes returned during user administration and profile maintenance operations. These errors are raised by core administrative services when creating, modifying, locking, unlocking, or resetting passwords for system users. They ensure user uniqueness, enforce role-based approval limits, and guard closed accounts against unauthorized modification.

### ERR-USR-0001: USER NOT FOUND

* **Message:** `USER NOT FOUND` [^r1]
* **Cause:** The specified user record cannot be located in the database [^r1].
* **Remedy:** Verify that the supplied user ID exists and is entered correctly before attempting administrative actions.
* **Raised by:** [[services-adm-usr|usr_disable]] [^r7], `usr_lock` [^r8], `usr_pwd_reset` [^r9], `usr_unlock` [^r10], and `usr_update` [^r11].

### ERR-USR-0118: USER ID ALREADY EXISTS

* **Message:** `USER ID ALREADY EXISTS` [^r2]
* **Cause:** An attempt was made to register a user ID that already exists in the system [^r5].
* **Remedy:** Select a unique identifier or update the existing account using [[screen-sys-usr-01|SYS-USR-01 User]] rather than creating a duplicate.
* **Raised by:** `usr_create` [^r5].

### ERR-USR-0130: LIMIT ABOVE APPROVAL MATRIX FOR ROLE

* **Message:** `LIMIT ABOVE APPROVAL MATRIX FOR ROLE` [^r3]
* **Cause:** The requested `appr_limit` exceeds the ceiling allowed for the designated `role_cd` by the approval matrix [^r6].
* **Remedy:** Reduce the approval limit to conform with the role's maximum threshold, or assign a role with higher authorization limits.
* **Raised by:** `usr_create` [^r6].

### ERR-USR-0801: USER CLOSED (\<status\>)

* **Message:** `USER CLOSED (<status>)` [^r4]
* **Cause:** An update was attempted on a user account that has already been placed in a closed or inactive status [^r12].
* **Remedy:** Confirm the target account status in [[topic-status-codes|Document Status Codes]] and reactivate or reopen the account where authorized before submitting changes.
* **Raised by:** `usr_update` [^r12].

## See also

* [[data-data-dictionary]]
* [[man-dd-72-all]]
* [[screen-sys-usr-01]]
* [[services-adm-usr]]
* [[errors-sec]]
* [[errors-sys]]
* [[topic-status-codes]]

## References

[^r1]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-USR-0001, SHEET Error codes
[^r7]: 04_service_definitions/admin/usr_disable.yaml, errors
[^r8]: 04_service_definitions/admin/usr_lock.yaml, errors
[^r9]: 04_service_definitions/admin/usr_pwd_reset.yaml, errors
[^r10]: 04_service_definitions/admin/usr_unlock.yaml, errors
[^r11]: 04_service_definitions/admin/usr_update.yaml, errors
[^r2]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-USR-0118, SHEET Error codes
[^r5]: 04_service_definitions/admin/usr_create.yaml, errors
[^r3]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-USR-0130, SHEET Error codes
[^r6]: 04_service_definitions/admin/usr_create.yaml, errors
[^r4]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-USR-0801, SHEET Error codes
[^r12]: 04_service_definitions/admin/usr_update.yaml, errors
