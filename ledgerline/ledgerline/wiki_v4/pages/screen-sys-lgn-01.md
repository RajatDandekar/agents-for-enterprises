---
title: "SYS-LGN-01 Sign In"
type: "screen"
slug: "screen-sys-lgn-01"
summary: "Ledgerline sign-in screen used by all roles to authenticate user ID, password, and operating unit code."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | SYS-LGN-01 |
| Module | SYS |
| Menu path | File > Sign in |
| Roles allowed | ALL |
| Triggered service | login |

Screen SYS-LGN-01 is the standard Ledgerline authentication screen accessible to all system roles via the File menu[^r1]. Users must provide their credentials alongside an operating unit code to authenticate their session[^r2]. Three consecutive incorrect password entries lock the user account and require IT assistance[^r2]. Every sign-in event is recorded in the live run log under the `usr_get` service action[^r4].

| Attribute | Value |
|---|---|
| Screen code | SYS-LGN-01 |
| Title | Sign In |
| Access path | File > Sign in |
| Available roles | ALL |
| Invoked service | login |

## Fields

* `user_id`: The alphanumeric user identifier required to authenticate[^r2].
* `password`: The user's account password; entering three incorrect passwords locks the account, requiring a call to IT on extension 2210[^r2].
* `ou_cd`: The organisation unit code for the session, such as `NBC-MAN-01` for Manchester[^r2].

## Keys and services

* **Sign in**: Submits the entered credentials and invokes the `login` service[^r3].
* **Shift+F8**: Mapped to Cancel to exit the sign-in window without authenticating[^r3].
* **Live run logging**: Each successful or attempted sign-in executes and logs under service `usr_get` under screen SYS-LGN-01[^r4].

## Messages

* `ERR-SEC-0007`: Raised when the supplied organisation unit code (`ou_cd`) does not match the user's authorised operating units[^r4].

## See also

* [[screen-sys-usr-01|SYS-USR-01 User]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 42, SYS-LGN-01 SIGN IN
[^r2]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 42, SYS-LGN-01 SIGN IN
[^r4]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 42, SYS-LGN-01 SIGN IN
[^r3]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 42, SYS-LGN-01 SIGN IN
