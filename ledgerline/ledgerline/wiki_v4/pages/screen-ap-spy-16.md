---
title: "AP-SPY-16 Supplier Payment Hold Hold"
type: "screen"
slug: "screen-ap-spy-16"
summary: "Ledgerline screen to apply and release supplier payment holds across Manchester and Leeds using services sup_pay_hold and sup_pay_release."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/accounts_payable/sup_pay_hold.yaml", "04_service_definitions/accounts_payable/sup_pay_release.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen | AP-SPY-16 |
| Module | Accounts Payable |
| Menu path | Accounts payable > Supplier payment |
| Write services | sup_pay_hold, sup_pay_release |
| Status | current |

Screen AP-SPY-16 manages the application and release of supplier payment holds across Northbridge Cycles' Manchester and Leeds operations [^r3]. Accessed via the Accounts payable > Supplier payment menu path, it allows accounts payable staff to place vendor disbursements on hold or restore them to normal processing [^r2][^r3]. The screen interacts directly with backend services `sup_pay_hold` and `sup_pay_release` [^r2].

| Field | Value |
|---|---|
| Screen code | AP-SPY-16 [^r1] |
| Title | Supplier Payment Hold Hold [^r7] |
| Navigation | Accounts payable > Supplier payment [^r2] |
| Services | sup_pay_hold, sup_pay_release [^r2] |
| Status | current [^r1] |

## Fields

Screen AP-SPY-16 contains three primary fields [^r1][^r7]:

* **SUP CD (`sup_cd`)**: Mandatory string field identifying the vendor code [^r1][^r7][^r12].
* **REASON (`reason`)**: Optional string field used to enter or select an authorised dispute reason code when placing a hold [^r1][^r4][^r7][^r12]. When releasing a hold, this field is cleared or updated [^r5].
* **COMMENT (`comment`)**: Optional string field used to provide notes regarding the hold or its release [^r1][^r5][^r7]. Standard practice at Northbridge Cycles requires users placing a hold to log the internal delivery reference, affected stock location, and purchasing clerk initials in this field [^r6].

## Keys and services

Screen AP-SPY-16 triggers two underlying write services [^r2][^r11][^r13]:

* **Apply hold**: The user inputs the vendor in SUP CD, enters an authorised dispute reason in REASON, adds comments in COMMENT, and triggers the `sup_pay_hold` service [^r4]. This executes `sp_sup_pay_hold` via write endpoint `POST /ll72/svc/sup_pay_hold`, passing mandatory `sup_cd` and optional `reason` [^r9][^r11][^r12].
* **Release hold**: The user enters the vendor in SUP CD, clears or amends REASON, records a release note in COMMENT, and invokes the `sup_pay_release` service [^r5][^r13]. This executes backend procedure `sp_sup_pay_release` requiring `sup_cd` alongside an optional `comment` parameter [^r10].

## Messages

The screen displays the following validation and processing errors:

* **ERR-SPY-0001**: Supplier Payment Hold Not Found [^r8][^r9][^r10].
* **ERR-SPY-0007**: Supplier Payment Hold Not In Draft (<Status>) [^r8][^r10].
* **[[err-sup-0030|ERR-SUP-0030]]**: Supplier Not Found [^r8][^r9][^r10].

## See also

* [[screen-ap-pay-03|AP-PAY-03 Payment Run]]
* [[screen-ap-sbl-08|AP-SBL-08 Supplier Balance]]
* [[services-ap-pay|AP pay services]]
* [[services-ap-sup|AP sup services]]
* [[err-sup-0030|ERR-SUP-0030]]

## References

[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 59, Step by step
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 58, §18. Supplier Payment Hold (AP-SPY-16)
[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 58, §18. Supplier Payment Hold (AP-SPY-16)
[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 10, AP-SPY-16 SUPPLIER PAYMENT HOLD HOLD
[^r12]: 04_service_definitions/accounts_payable/sup_pay_hold.yaml, request.fields
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 59, Step by step
[^r5]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 60, Step by step
[^r6]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 61, Worked example
[^r11]: 04_service_definitions/accounts_payable/sup_pay_hold.yaml, service: sup_pay_hold
[^r13]: 04_service_definitions/accounts_payable/sup_pay_release.yaml, service
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 37, sup_pay_hold SUPPLIER PAYMENT HOLD HOLD
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 37, sup_pay_release SUPPLIER PAYMENT HOLD RELEASE
[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 10, AP-SPY-16 SUPPLIER PAYMENT HOLD HOLD
