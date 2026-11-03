---
title: "SAL-COM-15 Sales Commission"
type: "screen"
slug: "screen-sal-com-15"
summary: "Ledgerline screen SAL-COM-15 calculates and displays sales commission runs by period for sales representatives across assigned territories."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/sales/com_get.yaml", "04_service_definitions/sales/com_run.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | SAL-COM-15 |
| Title | Sales Commission |
| Menu | Sales > Sales commission |
| Module | Sales |
| Roles | SAL-EXEC, SAL-MGR, SYS-ADMIN |
| Services | com_run, com_get |
| Status | current |

SAL-COM-15 (Sales commission) calculates and retrieves sales representative commissions for a specified processing period in Ledgerline [^r1][^r10]. Located under the Sales menu, the screen requires fully posted invoices, credit notes, cash allocations, and confirmed territory assignments before execution [^r1][^r2][^r10]. Once batch runs are validated, figures are forwarded to payroll for disbursement in the standard payroll cycle [^r7].

| Key | Value |
|---|---|
| Screen code | SAL-COM-15 [^r1] |
| Menu path | Sales > Sales commission [^r1][^r10] |
| Permitted roles | SAL-EXEC, SAL-MGR, SYS-ADMIN [^r10] |
| Services | `com_run`, `com_get` [^r1][^r10] |

## Fields

* **PERIOD**: Mandatory field specifying the target accounting or sales commission period required to run or fetch commission data [^r1][^r4][^r10].
* **COMMENT**: Optional text field for recording notes or processing annotations against the run [^r1].

## Keys and services

* **com_run**: Executes the [[services-sal-com|SALES COMMISSION RUN]] write service [^r1][^r9]. It generates calculation batch status flags and calculates representative commission amounts from retailer deliveries, factoring in net turnover alongside qualifying deductions for discounts, credit notes, and returns [^r3]. Prior to executing `com_run`, sales invoices, customer cash allocations, bank postings, and approved credit notes must be completely posted, and territory assignments confirmed on the [[screen-sal-cus-01|customer master]] [^r2].
* **com_get**: Calls the [[services-sal-com|SALES COMMISSION GET]] read service to retrieve and present existing commission calculations broken down by territory and representative across the lower section of the screen [^r1][^r5][^r8][^r10].

Where manual credits raised outside the module require adjustments to commission totals, the accounts supervisor must be notified before signing off the register [^r6]. Finalised batch figures are forwarded to payroll for payment in the normal payroll cycle [^r7].

## Messages

* **[[err-com-0001|ERR-COM-0001]]**: Raised if commission calculation or retrieval fails because the PERIOD field is blank, invalid, non-existent, or locked against processing [^r4].

## See also

* [[err-com-0001|ERR-COM-0001 Period Not Open or Already Posted]]
* [[screen-sal-crn-09|SAL-CRN-09 Customer Credit Note Entry]]
* [[screen-sal-cus-01|SAL-CUS-01 Customer Master Entry]]
* [[screen-sal-inv-06|SAL-INV-06 Sales Invoice Entry]]
* [[services-sal-com|SAL com services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 59, §18. Sales Commission (SAL-COM-15)
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 33, SAL-COM-15 SALES COMMISSION
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 59, Before you start
[^r7]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 62, Questions users ask
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 61, Messages
[^r9]: 04_service_definitions/sales/com_run.yaml, service: com_run
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 60, Step by step
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 62, Questions users ask
[^r8]: 04_service_definitions/sales/com_get.yaml, whole file
[^r6]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 62, Questions users ask
