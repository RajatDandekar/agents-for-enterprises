---
title: "SAL-CRD-11 Credit Control Check"
type: "screen"
slug: "screen-sal-crd-11"
summary: "Ledgerline credit control check screen for querying account status, viewing hold lists, and releasing accounts under sales management authorisation."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/sales/crd_check.yaml", "04_service_definitions/sales/crd_hold_list.yaml", "04_service_definitions/sales/crd_release.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | SAL-CRD-11 |
| Module | Sales |
| Menu path | Sales > Credit control |
| Roles | SAL-EXEC, SAL-MGR, SYS-ADMIN |
| Read services | crd_check, crd_hold_list |
| Write service | crd_release |

Screen SAL-CRD-11 provides credit control enquiry, credit hold list reviews, and account release functions in Ledgerline [^r6]. It is accessed through the menu path Sales > Credit control by users assigned to roles SAL-EXEC, SAL-MGR, or SYS-ADMIN [^r1][^r6]. Before using the screen, morning bank receipt cash matching must be completed, manual receipts posted, and stop notices verified with finance [^r2]. Account releases executed from this screen require an audit note documenting authorisation and justification [^r3].

## Fields

| Field | Prompt | Requirement | Description |
|---|---|---|---|
| `cust_cd` | CUST CD | Mandatory for credit check; optional filter for hold list | Customer account code used to run credit checks and filter hold list records [^r1][^r7][^r9]. |
| `comment` | COMMENT | Optional on entry; required when releasing accounts | Explanatory note detailing approval identity and business reason for releasing a credit hold [^r1][^r3]. |

## Keys and services

* **Credit Check (`crd_check`)**: Read service invoked via endpoint `POST /ll72/svc/crd_check` using parameter `cust_cd` to retrieve account credit standing [^r6][^r7].
* **Hold List (`crd_hold_list`)**: Read service invoked via endpoint `POST /ll72/svc/crd_hold_list` to display credit control hold records, optionally filtered by `cust_cd` [^r6][^r8][^r9].
* **Account Release (`crd_release`)**: Write service executed via function key F9 and endpoint `POST /ll72/svc/crd_release`, running stored procedure `sp_crd_release` [^r6][^r10].

## Messages

* `ERR-CRD-0001`: Displayed when executing `crd_check` while the `cust_cd` (CUST CD) field is empty [^r4].
* `ERR-CRD-0007`: Displayed when executing `crd_release` while outstanding overdue balances exceed the agreed limit without an active override flag [^r5].

## See also

* [[err-crd-0001|ERR-CRD-0001]]
* [[services-sal-crd|SAL crd services]]
* [[screen-sal-so-01|SAL-SO-01 Sales Order]]
* [[screen-sal-cus-01|SAL-CUS-01 Customer Master Entry]]

## References

[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 33, SAL-CRD-11 CREDIT CONTROL CHECK
[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 45, §14. Credit Control (SAL-CRD-11)
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 45, Before you start
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 48, Worked example
[^r7]: 04_service_definitions/sales/crd_check.yaml, service: crd_check
[^r9]: 04_service_definitions/sales/crd_hold_list.yaml, request.fields
[^r8]: 04_service_definitions/sales/crd_hold_list.yaml, screen
[^r10]: 04_service_definitions/sales/crd_release.yaml, service: crd_release
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 48, Worked example
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 48, Worked example
