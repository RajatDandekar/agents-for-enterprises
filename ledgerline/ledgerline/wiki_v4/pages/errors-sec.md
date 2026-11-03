---
title: "Security Error Codes (ERR-SEC)"
type: "error-list"
slug: "errors-sec"
summary: "Ledgerline security error codes (ERR-SEC-*) covering access control, missing users, and password policy validation across services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/accounts_payable/cur_save.yaml", "04_service_definitions/admin/usr_disable.yaml", "04_service_definitions/admin/usr_pwd_reset.yaml", "04_service_definitions/purchase/ntf_send.yaml", "04_service_definitions/purchase/usr_get.yaml", "04_service_definitions/purchase/usr_roles.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-SEC |
| Category | Security and authentication |
| Domain | Ledgerline service layer |
| Status | Current |

Security error codes (`ERR-SEC-*`) are raised across Ledgerline service calls when authentication, role authorization, or user account validation fails [^r1][^r7]. They guard administration, accounts payable, and purchasing services against unauthorized execution or invalid credential operations [^r1][^r2][^r3][^r5].

## Error codes

### ERR-SEC-0001
* **Message:** `ACCESS DENIED` [^r1]
* **Cause:** The user's session token or assigned role does not permit access to the requested service [^r1][^r5]. It occurs when authentication or authorization fails during service execution [^r7].
* **Remedy:** Verify that the user has an active session and that their assigned user role grants permission for the specific operation [^r1][^r7][^r9].
* **Raised by:** [[services-ap-cur|cur_save]] [^r1], [[services-adm-usr|usr_disable]] [^r2], [[services-adm-usr|usr_pwd_reset]] [^r4], [[services-pur-ntf|ntf_send]] [^r5], [[services-pur-usr|usr_get]] [^r7], and [[services-pur-usr|usr_roles]] [^r9].

### ERR-SEC-0003
* **Message:** `NO SUCH USER` [^r6]
* **Cause:** The requested user record cannot be found in Ledgerline [^r6][^r8].
* **Remedy:** Confirm that the user identifier is correct and exists in the system before querying user details or roles [^r6][^r8].
* **Raised by:** [[services-pur-usr|usr_get]] [^r6] and [[services-pur-usr|usr_roles]] [^r8].

### ERR-SEC-0012
* **Message:** `PASSWORD DOES NOT MEET POLICY` [^r3]
* **Cause:** A submitted password does not satisfy Northbridge's configured password complexity or format rules [^r3].
* **Remedy:** Supply a password that complies with system password policy requirements [^r3].
* **Raised by:** [[services-adm-usr|usr_pwd_reset]] [^r3].

## See also

* [[errors-sys|System and framework error codes (ERR-SYS-*)]]
* [[errors-usr|ERR-USR Error Codes]]
* [[screen-sys-usr-01|SYS-USR-01 User]]
* [[screen-ap-cur-13|AP-CUR-13 Currency Rate]]
* [[services-adm-usr|ADM usr services]]
* [[services-ap-cur|AP cur services]]
* [[services-pur-ntf|PUR ntf services]]
* [[services-pur-usr|PUR usr services]]
* [[user-jfletcher|Joanna Fletcher (JFLETCHER)]]

## References

[^r1]: 04_service_definitions/accounts_payable/cur_save.yaml, common_errors
[^r7]: 04_service_definitions/purchase/usr_get.yaml, common_errors
[^r2]: 04_service_definitions/admin/usr_disable.yaml, common_errors
[^r3]: 04_service_definitions/admin/usr_pwd_reset.yaml, errors
[^r5]: 04_service_definitions/purchase/ntf_send.yaml, common_errors
[^r9]: 04_service_definitions/purchase/usr_roles.yaml, common_errors
[^r4]: 04_service_definitions/admin/usr_pwd_reset.yaml, common_errors
[^r6]: 04_service_definitions/purchase/usr_get.yaml, errors
[^r8]: 04_service_definitions/purchase/usr_roles.yaml, errors
