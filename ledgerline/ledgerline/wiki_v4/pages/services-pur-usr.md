---
title: "PUR usr services"
type: "service-group"
slug: "services-pur-usr"
summary: "Read services in the purchase module for retrieving user profiles and assigned roles by user ID."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/purchase/usr_get.yaml", "04_service_definitions/purchase/usr_roles.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | PUR |
| Object | usr |
| Service count | 2 |
| Protocol | HTTP POST |
| Base path | /ll72/svc/ |
| Status | current |

The PUR usr service group provides read access to user profile data and assigned role allocations within Ledgerline ERP 7.2 [^r2][^r3][^r9]. It consists of `usr_get` and `usr_roles`, both introduced in version 7.0 to retrieve user details based on a mandatory user identifier [^r2][^r3][^r9]. Live user logins via [[screen-sys-lgn-01|SYS-LGN-01 Sign In]] trigger `usr_get` to record session initialization [^r1].

## Services

### usr_get

`usr_get` (USER GET) is a read service in the PUR module that retrieves user information for a specified user identifier [^r2][^r3]. It operates at endpoint `POST /ll72/svc/usr_get` and has no dedicated screen [^r3]. Every user sign-in through screen [[screen-sys-lgn-01|SYS-LGN-01]] is recorded in the live run as service `usr_get` [^r1].

* **Authentication:** Requires a valid session token supplied in header `X-LL-Session`, and the user's role must allow execution of the service [^r4].
* **Required fields:** `user_id` (string, USER ID) [^r2][^r5].
* **Optional fields:** None [^r5].
* **Response envelope:** Returns `rc` (`S | W | E`), `err_cd` (error code when `rc` is `E`), `msg` (short message in capitals), and `data` (result) [^r6].
* **Errors:** Returns `ERR-SEC-0003` (NO SUCH USER) if the user is not found [^r2][^r7]. Common errors include `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (`<FIELD>` MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD `<FIELD>` / BAD VALUE FOR `<FIELD>`), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r8].
* **Source file:** `04_service_definitions/purchase/usr_get.yaml` [^r3].

### usr_roles

`usr_roles` is a read service in the PUR module that retrieves the role assignments associated with a given user identifier [^r2][^r9]. It operates at endpoint `POST /ll72/svc/usr_roles` and has been available since version 7.0 [^r9].

* **Authentication:** Requires a valid session token in header `X-LL-Session`, and the user's role must permit access to the service [^r10].
* **Required fields:** `user_id` (string, USER ID) [^r2][^r11].
* **Optional fields:** None [^r11].
* **Response envelope:** Returns `rc` (`S | W | E`), `err_cd` (error code when `rc` is `E`), `msg` (short message in capitals), and `data` (result) [^r12].
* **Errors:** Returns `ERR-SEC-0003` (`NO SUCH USER`) when the requested user does not exist [^r2][^r13]. Common errors include `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (`<FIELD>` MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD `<FIELD>` / BAD VALUE FOR `<FIELD>`), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r14].
* **Source file:** `04_service_definitions/purchase/usr_roles.yaml` [^r9].

## See also

* [[screen-sys-lgn-01|SYS-LGN-01 Sign In]]
* [[services-pur-po|PUR po services]]
* [[services-pur-pr|PUR pr services]]

## References

[^r2]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 4, §2. Purchase services
[^r3]: 04_service_definitions/purchase/usr_get.yaml, whole file
[^r9]: 04_service_definitions/purchase/usr_roles.yaml, service: usr_roles
[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 42, SYS-LGN-01 SIGN IN
[^r4]: 04_service_definitions/purchase/usr_get.yaml, auth
[^r5]: 04_service_definitions/purchase/usr_get.yaml, request.fields
[^r6]: 04_service_definitions/purchase/usr_get.yaml, response.envelope
[^r7]: 04_service_definitions/purchase/usr_get.yaml, errors
[^r8]: 04_service_definitions/purchase/usr_get.yaml, common_errors
[^r10]: 04_service_definitions/purchase/usr_roles.yaml, auth
[^r11]: 04_service_definitions/purchase/usr_roles.yaml, request.fields
[^r12]: 04_service_definitions/purchase/usr_roles.yaml, response.envelope
[^r13]: 04_service_definitions/purchase/usr_roles.yaml, errors
[^r14]: 04_service_definitions/purchase/usr_roles.yaml, common_errors
