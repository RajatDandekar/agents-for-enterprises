---
title: "AP-CUR-13 Currency Rate"
type: "screen"
slug: "screen-ap-cur-13"
summary: "Ledgerline screen for retrieving, listing, and maintaining foreign currency conversion rates to GBP."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/accounts_payable/cur_get.yaml", "04_service_definitions/accounts_payable/cur_list.yaml", "04_service_definitions/accounts_payable/cur_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | AP-CUR-13 |
| Menu path | Accounts payable > Currency rate |
| Module | Accounts Payable |
| Roles | AP-CLERK, AP-MGR, FIN-CTRL, SYS-ADMIN |
| Read services | cur_get, cur_list |
| Write service | cur_save |
| Status | Current |

Screen AP-CUR-13 maintains foreign currency exchange rates against GBP in Ledgerline Accounts Payable [^r1][^r13]. Accessed via Accounts payable > Currency rate, it allows authorised roles to look up, record, and list conversion factors for specified effective dates [^r1][^r8]. All exchange rates recorded in this screen must originate from authorised finance office exchange sheets rather than public feeds [^r4].

## Fields

The screen requires three mandatory fields to define an exchange rate entry [^r1]:

| Field | Parameter | Type | Description |
|---|---|---|---|
| CUR CD | `cur_cd` | string | Foreign currency identifier [^r1][^r5][^r9]. |
| RATE DT | `rate_dt` | date | Effective date of the conversion rate [^r1][^r5][^r9]. |
| RATE TO GBP | `rate` | float | Conversion factor to GBP [^r1][^r5][^r9]. |

## Keys and services

Access is restricted to roles AP-CLERK, AP-MGR, FIN-CTRL, and SYS-ADMIN [^r8]. Screen operations are supported by [[services-ap-cur|AP cur services]] [^r9][^r11][^r12][^r13]:

* **Get (F3)**: Executes `cur_get` (CURRENCY RATE GET via `POST /ll72/svc/cur_get`) using CUR CD and RATE DT to verify or retrieve an existing conversion rate lodged for that currency and date, populating RATE TO GBP [^r2][^r6][^r9][^r11].
* **Save (F8)**: Invokes `cur_save` (`POST /ll72/svc/cur_save`) using `cur_cd`, `rate_dt`, and `rate` to commit exchange rates to GBP [^r9][^r13].
* **List**: Calls `cur_list` (CURRENCY RATE LIST via `POST /ll72/svc/cur_list`) to display historical recorded entries for the selected currency in reverse chronological order without clearing the active screen record [^r3][^r7][^r9][^r12].

## Messages

The screen reports error [[err-cur-0001|ERR-CUR-0001]] (Currency Rate Not Found) when a queried currency rate cannot be retrieved [^r10].

## See also

* [[services-ap-cur|AP cur services]]
* [[err-cur-0001|ERR-CUR-0001 Currency Rate Action Failed]]
* [[screen-ap-inv-01|AP-INV-01 Supplier Invoice Entry]]
* [[screen-ap-pay-03|AP-PAY-03 Payment Run]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 47, §15. Currency Rate (AP-CUR-13)
[^r13]: 04_service_definitions/accounts_payable/cur_save.yaml, screen
[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 5, AP-CUR-13 CURRENCY RATE
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 48, Before you start
[^r5]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 49, Messages
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 5, AP-CUR-13 CURRENCY RATE
[^r11]: 04_service_definitions/accounts_payable/cur_get.yaml, service: cur_get
[^r12]: 04_service_definitions/accounts_payable/cur_list.yaml, service: cur_list
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 48, Step by step
[^r6]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 50, Worked example
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 48, Step by step
[^r7]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 51, Questions users ask
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 5, AP-CUR-13 CURRENCY RATE
