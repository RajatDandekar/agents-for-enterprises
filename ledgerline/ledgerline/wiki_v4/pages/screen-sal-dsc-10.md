---
title: "SAL-DSC-10 Discount"
type: "screen"
slug: "screen-sal-dsc-10"
summary: "SAL-DSC-10 records and maintains customer trade discount schedules via services dsc_get, dsc_save, and dsc_search."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/sales/dsc_get.yaml", "04_service_definitions/sales/dsc_save.yaml", "04_service_definitions/sales/dsc_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen | SAL-DSC-10 |
| Menu path | Sales > Discount |
| Roles | SAL-EXEC, SAL-MGR, SYS-ADMIN |
| Read services | dsc_get, dsc_search |
| Write service | dsc_save |
| Error codes | ERR-DSC-0001 |

Screen SAL-DSC-10 records and maintains commercial discount terms with individual trade accounts in Ledgerline [^r1]. It is accessed via the menu path Sales > Discount by users assigned to the SAL-EXEC, SAL-MGR, or SYS-ADMIN roles [^r1][^r7]. The screen interacts directly with the [[services-sal-dsc|SAL dsc services]] dsc_get, dsc_save, and dsc_search to query, validate, and store customer discounts [^r1][^r7].

## Fields

The screen layout contains five fields used to establish customer discount parameters [^r2]:

| Field | Description | Mandatory / Optional |
|---|---|---|
| DSC CD | Discount schedule identifier (`dsc_cd`) [^r2][^r7] | Mandatory [^r2][^r7] |
| CUST CD | Customer account identifier (`cust_cd`) [^r2][^r7] | Mandatory [^r2][^r7] |
| DISC % | Percentage deduction (`dsc_pct`) [^r2][^r7] | Mandatory [^r2][^r7] |
| VALID TO | Validity end date (`valid_to`) [^r2][^r7] | Optional [^r2][^r7] |
| STATUS | Operational state (`status`) [^r2][^r7] | Optional [^r2][^r7] |

## Keys and services

SAL-DSC-10 links standard function keys to background sales discount services [^r8]:

* **Search (`F2`/`Enter`)**: Calls the read service `dsc_search` (DISCOUNT LIST) to open an inquiry window displaying existing discount schedules and associated customer references [^r3][^r8][^r11]. Results can be filtered optionally by CUST CD, DISC %, VALID TO, and STATUS [^r11].
* **Get (`F3`)**: Invokes the read service `dsc_get` (DISCOUNT GET) using the parameter `dsc_cd` to populate stored record values into CUST CD, DISC %, VALID TO, and STATUS [^r4][^r8][^r9].
* **Save (`F8`)**: Triggers the write service `dsc_save` (DISCOUNT SAVE) using fields `cust_cd`, `dsc_pct`, and optional `valid_to` to validate entries against the customer ledger and commit terms to core tables [^r5][^r8][^r10].

## Messages

The screen raises validation errors when account verification fails [^r6][^r8]:

* [[err-dsc-0001|ERR-DSC-0001]]: Displayed when customer account rules fail or if the targeted customer account is marked on stop, halting the transaction [^r6][^r8].

## See also

* [[err-dsc-0001]]
* [[services-sal-dsc]]
* [[screen-sal-cus-01]]
* [[screen-sal-crd-11]]
* [[screen-sal-so-01]]
* [[screen-sal-prc-08]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 37, §12. Discount (SAL-DSC-10)
[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 35, SAL-DSC-10 DISCOUNT
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 38, Screen layout and fields
[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 35, SAL-DSC-10 DISCOUNT
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 38, Step by step: Searching for an existing discount record
[^r11]: 04_service_definitions/sales/dsc_search.yaml, service: dsc_search
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 39, Step by step: Retrieving and viewing a discount record
[^r9]: 04_service_definitions/sales/dsc_get.yaml, whole file
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 38, Available buttons and services
[^r10]: 04_service_definitions/sales/dsc_save.yaml, screen: SAL-DSC-10
[^r6]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 40, Worked example
