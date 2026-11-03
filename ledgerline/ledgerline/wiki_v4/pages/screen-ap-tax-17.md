---
title: "AP-TAX-17 Tax Code Master"
type: "screen"
slug: "screen-ap-tax-17"
summary: "Ledgerline screen AP-TAX-17 defines and maintains tax code master records, rates, and territory flags for accounts payable."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/accounts_payable/tax_get.yaml", "04_service_definitions/accounts_payable/tax_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen | AP-TAX-17 |
| Title | Tax Code Master |
| Module | Accounts payable |
| Menu path | Accounts payable > Tax code |
| Roles | AP-CLERK, AP-MGR, FIN-CTRL, SYS-ADMIN |
| Services | tax_get, tax_save |

Screen AP-TAX-17 defines and maintains the tax codes used across Ledgerline accounts payable processing [^r1][^r9]. Located under Accounts payable > Tax code, it is accessible to roles AP-CLERK, AP-MGR, FIN-CTRL, and SYS-ADMIN [^r9]. Users must possess master file security clearance, ensure no daybook updates or payment runs are active, and have written instructions from the finance manager on the effective ledger period before updating records [^r4]. It provides creation and retrieval functions but cannot be used to delete tax code records [^r8].

| Field | Description |
|---|---|
| Screen | AP-TAX-17 |
| Module | Accounts payable |
| Path | Accounts payable > Tax code |
| Roles | AP-CLERK, AP-MGR, FIN-CTRL, SYS-ADMIN |
| Services | tax_get, tax_save |

## Fields

Four fields are mandatory on screen AP-TAX-17 [^r1][^r15]:

* **TAX CD (`tax_cd`)**: Mandatory character code identifying the tax record [^r1][^r2][^r11].
* **DESCR (`descr`)**: Mandatory text description of the tax code [^r1][^r3][^r15]. The text entered here appears on purchase ledger audit reports, daybook printouts, and balance sheets produced for external accountants [^r6].
* **RATE (`rate`)**: Mandatory numeric tax rate [^r1][^r3][^r15].
* **INTRA/INTER (`kind`)**: Mandatory classification flag [^r1][^r3][^r12][^r15]. This flag determines whether Ledgerline treats purchases bearing the tax code as domestic transactions or as movements between operating regions and outside territories [^r7].

## Keys and services

The screen interacts with the backend database using two dedicated [[services-ap-tax|AP tax services]] [^r8][^r11][^r12]:

* **`tax_get`**: Retrieves an existing record using the character code entered in `TAX CD` [^r2][^r11][^r13]. Executed when the operator presses the tax_get button [^r2].
* **`tax_save`**: Saves new or modified tax code records via backend stored procedure `sp_tax_save` [^r3][^r12][^r14]. Executed when the operator enters all required fields and clicks the tax_save button [^r3].

The screen cannot be used to delete records directly [^r8].

## Messages

* **[[err-tax-0001|ERR-TAX-0001]]**: Tax Code Master Not Found [^r10]. Displayed when pressing `tax_get` if the entered `TAX CD` does not exist in the database [^r5][^r11]. It is also raised when pressing `tax_save` if a required field is blank, contains invalid characters, or violates table constraints [^r5].

## See also

* [[err-tax-0001|ERR-TAX-0001 TAX CODE MASTER NOT FOUND]]
* [[services-ap-tax|AP tax services]]
* [[screen-ap-inv-01|AP-INV-01 Supplier Invoice Entry]]
* [[screen-ap-pay-03|AP-PAY-03 Payment Run]]
* [[screen-ap-per-11|AP-PER-11 Ap Period]]
* [[screen-ap-vat-12|AP-VAT-12 Vat Return]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 62, §19. Tax Code Master (AP-TAX-17)
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 10, AP-TAX-17 TAX CODE MASTER
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 62, Before you start
[^r8]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 65, Questions users ask
[^r15]: 04_service_definitions/accounts_payable/tax_save.yaml, request.fields
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 63, Retrieving an existing record
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 37, tax_get TAX CODE MASTER GET
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 63, Creating or modifying an entry
[^r6]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 64, Tips
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 38, tax_save TAX CODE MASTER SAVE
[^r7]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 65, Questions users ask
[^r13]: 04_service_definitions/accounts_payable/tax_get.yaml, screen
[^r14]: 04_service_definitions/accounts_payable/tax_save.yaml, whole file
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 10, AP-TAX-17 TAX CODE MASTER
[^r5]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 64, Messages
