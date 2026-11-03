---
title: "System and framework error codes (ERR-SYS-*)"
type: "error-list"
slug: "errors-sys"
summary: "Reference list of Ledgerline system and framework error codes (ERR-SYS-*) raised across service definitions."
audience: "staff"
status: "current"
sources: ["04_service_definitions/accounts_payable/cur_save.yaml", "04_service_definitions/admin/usr_disable.yaml", "04_service_definitions/admin/usr_pwd_reset.yaml", "04_service_definitions/purchase/ntf_send.yaml", "04_service_definitions/purchase/usr_roles.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-SYS |
| Domain | System and framework |
| Module | Ledgerline core |
| Authority | Service definitions |
| Status | Current |

`ERR-SYS-*` error codes represent framework-level validation failures and platform availability issues in Ledgerline service calls [^r1][^r3]. These common errors are returned across administrative, accounts payable, and purchasing interfaces when payloads fail basic schema rules or the host system cannot process work [^r1][^r4][^r6]. As of 26 October 2026, they standardise system responses across service groups such as [[services-ap-cur|AP cur services]], [[services-adm-usr|ADM usr services]], [[services-pur-usr|PUR usr services]], and [[services-pur-ntf|PUR ntf services]] [^r1][^r4][^r6][^r7].

### ERR-SYS-0421
* **Message**: `<FIELD> MANDATORY` [^r1]
* **Cause**: A mandatory field was omitted from the service call payload [^r1].
* **Remedy**: Supply a valid value for the identified mandatory field and resubmit the request [^r1].
* **Raised by**: Ledgerline service calls including `cur_save` in [[services-ap-cur|AP cur services]], `usr_disable` and `usr_pwd_reset` in [[services-adm-usr|ADM usr services]], `usr_roles` in [[services-pur-usr|PUR usr services]], and `ntf_send` in [[services-pur-ntf|PUR ntf services]] [^r1][^r4][^r5][^r6][^r7].

### ERR-SYS-0422
* **Message**: `UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>` [^r2]
* **Cause**: An unrecognised field name or an invalid field value was supplied to the service [^r2].
* **Remedy**: Verify the service schema, correct the field name or format, and re-send the payload [^r2].
* **Raised by**: Ledgerline service calls including `cur_save`, `usr_disable`, `usr_pwd_reset`, `usr_roles`, and `ntf_send` [^r2][^r4][^r5][^r6][^r7].

### ERR-SYS-0503
* **Message**: `SERVER BUSY, TRY LATER` [^r3]
* **Cause**: The Ledgerline server is temporarily overloaded or unavailable [^r3].
* **Remedy**: Wait and retry the operation later [^r3].
* **Raised by**: Ledgerline framework across services including `cur_save`, `usr_disable`, `usr_pwd_reset`, `usr_roles`, and `ntf_send` [^r3][^r4][^r5][^r6][^r7].

## See also
* [[errors-sec|Security Error Codes (ERR-SEC)]]
* [[errors-usr|ERR-USR Error Codes]]
* [[screen-ap-cur-13|AP-CUR-13 Currency Rate]]
* [[screen-sys-usr-01|SYS-USR-01 User]]
* [[services-adm-usr|ADM usr services]]
* [[services-ap-cur|AP cur services]]
* [[services-pur-ntf|PUR ntf services]]
* [[services-pur-usr|PUR usr services]]
* [[user-jfletcher|Joanna Fletcher (JFLETCHER)]]

## References

[^r1]: 04_service_definitions/accounts_payable/cur_save.yaml, common_errors
[^r3]: 04_service_definitions/accounts_payable/cur_save.yaml, common_errors
[^r4]: 04_service_definitions/admin/usr_disable.yaml, common_errors
[^r6]: 04_service_definitions/purchase/ntf_send.yaml, common_errors
[^r7]: 04_service_definitions/purchase/usr_roles.yaml, common_errors
[^r5]: 04_service_definitions/admin/usr_pwd_reset.yaml, common_errors
[^r2]: 04_service_definitions/accounts_payable/cur_save.yaml, common_errors
