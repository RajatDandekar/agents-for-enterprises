---
title: "AP-SBL-08 Supplier Balance"
type: "screen"
slug: "screen-ap-sbl-08"
summary: "AP-SBL-08 Supplier Balance provides ledger balance enquiries, ageing analysis, and chronological statements for accounts payable suppliers."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/accounts_payable/sbal_ageing.yaml", "04_service_definitions/accounts_payable/sbal_query.yaml", "04_service_definitions/accounts_payable/sbal_stmt.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | AP-SBL-08 |
| Name | Supplier Balance |
| Module | Accounts payable |
| Menu path | Accounts payable > Supplier balance |
| Allowed roles | AP-CLERK, AP-MGR, FIN-CTRL, SYS-ADMIN |

Screen AP-SBL-08 (Supplier Balance) is the Accounts payable inquiry interface used to view supplier ledger balances, debt ageing, and transaction statements [^r1][^r3][^r5]. It is accessible to users assigned the AP-CLERK, AP-MGR, FIN-CTRL, and SYS-ADMIN roles [^r5]. The interface connects directly to the underlying [[services-ap-sbal|sbal]] read services to retrieve financial summaries and chronological account details in pounds [^r3][^r7][^r8][^r10].

## Fields

| Field label | Technical name | Description |
|---|---|---|
| SUP CD | `sup_cd` | Supplier code to identify the account record [^r1]. |
| AS ON | `as_on` | Cut-off date for calculating balances and ageing [^r1]. |

In the user interface, `sup_cd` and `as_on` appear as non-mandatory input fields, but procedural validation requires both fields to be populated prior to initiating a query [^r1][^r2].

## Keys and services

Screen AP-SBL-08 connects to three backend read endpoints provided by the [[services-ap-sbal|AP sbal services]] group:

* **sbal_query**: Executed via button `sbal_query` using service `POST /ll72/svc/sbal_query` to display the supplier balance and breakdown in pounds using parameters `sup_cd` and `as_on` [^r3][^r8][^r9].
* **sbal_ageing**: Executed via button `sbal_ageing` to retrieve debt ageing buckets using parameter `sup_cd` [^r3][^r7].
* **sbal_stmt**: Executed via button `sbal_stmt` using read service endpoint `POST /ll72/svc/sbal_stmt` to produce a detailed chronological ledger statement using parameter `sup_cd` [^r3][^r10].

## Messages

The following error messages are displayed on the screen:

* `ERR-SBL-0001`: Raised as "Supplier Balance Not Found" or when the `as_on` cut-off date parameter is missing or invalid [^r2][^r4][^r6].
* [[err-sup-0030|ERR-SUP-0030]]: Raised as "Supplier Not Found" when the entered `sup_cd` is invalid or has been purged from the system [^r4][^r6].

## Versions and conflicts

* **Input parameter requirements**: In procedural manual MAN-AP-72, the step-by-step instructions state that both `sup_cd` and `as_on` must be populated before clicking `sbal_query`, and leaving `as_on` blank halts execution with `ERR-SBL-0001` [^r2]. However, the backend service schema `sbal_query.yaml` defines both `sup_cd` and `as_on` as optional request parameters [^r9]. (`contradiction`)

## See also

* [[services-ap-sbal|AP sbal services]]
* [[errors-sup|ERR-SUP Error Codes]]
* [[err-sup-0030|ERR-SUP-0030]]
* [[screen-pur-sup-03|PUR-SUP-03 Supplier Enquiry]]
* [[screen-ap-inv-01|AP-INV-01 Supplier Invoice Entry]]
* [[screen-ap-pay-03|AP-PAY-03 Payment Run]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 30, Supplier Balance (AP-SBL-08)
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 31, Step by step
[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 9, AP-SBL-08 SUPPLIER BALANCE
[^r7]: 04_service_definitions/accounts_payable/sbal_ageing.yaml, service: sbal_ageing
[^r8]: 04_service_definitions/accounts_payable/sbal_query.yaml, whole file
[^r10]: 04_service_definitions/accounts_payable/sbal_stmt.yaml, screen: AP-SBL-08
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 30, Step by step
[^r9]: 04_service_definitions/accounts_payable/sbal_query.yaml, request
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 31, Messages
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 10, AP-SBL-08 SUPPLIER BALANCE
