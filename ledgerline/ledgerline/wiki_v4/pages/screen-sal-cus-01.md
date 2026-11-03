---
title: "SAL-CUS-01 Customer Master Entry"
type: "screen"
slug: "screen-sal-cus-01"
summary: "Ledgerline screen for customer master maintenance, search, updates, trading blocks, and credit exposure checks under Sales > Customer master."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/sales/cust_block.yaml", "04_service_definitions/sales/cust_credit.yaml", "04_service_definitions/sales/cust_get.yaml", "04_service_definitions/sales/cust_save.yaml", "04_service_definitions/sales/cust_search.yaml", "04_service_definitions/sales/cust_update.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen Code | SAL-CUS-01 |
| Module | Sales |
| Menu Path | Sales > Customer master |
| Status | current |
| Services | cust_save, cust_get, cust_search, cust_update, cust_block, cust_credit |

SAL-CUS-01 (Customer Master Entry) is the Ledgerline ERP screen located at menu path Sales > Customer master used to maintain customer accounts [^r1]. It manages the creation of new debtor records, updates to trading details, application of account blocks, and inquiries into customer credit exposure [^r1][^r4][^r5]. The interface connects directly to the [[services-sal-cust|SAL cust services]] suite to validate account parameters and enforce trading controls across downstream order workflows [^r1][^r4].

| Field | Value |
|---|---|
| Screen Code | SAL-CUS-01 [^r1] |
| Module | Sales [^r1] |
| Menu Path | Sales > Customer master [^r1] |
| Primary Services | cust_save, cust_get, cust_search, cust_update, cust_block, cust_credit [^r1] |

## Fields

Screen SAL-CUS-01 contains both mandatory identification fields and optional account attributes [^r2]:

* **CUST CD** (`cust_cd`): Customer code, mandatory [^r2][^r16]. When creating a new customer, this field is left empty, and Ledgerline ERP automatically assigns the permanent customer reference upon successful execution of `cust_save` [^r3]. It is required when retrieving an existing account record [^r11].
* **CUST NAME** (`name`): Customer name, mandatory [^r2][^r7][^r14][^r16].
* **CITY** (`city`): City, mandatory [^r2][^r7][^r14][^r16].
* **COUNTRY CD (2)** (`country`): Two-character country code, mandatory [^r2][^r7][^r14][^r16].
* **VAT number** (`vat_no`): Optional tax registration number [^r2][^r7][^r14].
* **PAY TERM CD** (`pt_cd`): Optional payment terms code [^r2][^r7].
* **PRICE LIST** (`price_list`): Optional assigned price list [^r2][^r7].
* **STATUS** (`status`): Customer account status [^r2]. When trading restrictions are applied, `status` is set to blocked [^r4].
* **REASON** (`reason`): Free-text entry used to supply justification when restricting trading [^r2][^r4].

## Keys and services

SAL-CUS-01 provides keyboard shortcuts and service actions to execute debtor management operations [^r1][^r6]:

* **cust_search (F2/Enter)**: Executes read service `cust_search` via endpoint `POST /ll72/svc/cust_search` to find customer master records matching optional search criteria including customer name, city, two-character country code, and status [^r6][^r13].
* **cust_get (F3)**: Executes read service `cust_get` via endpoint `POST /ll72/svc/cust_get` using mandatory field `cust_cd` to retrieve account details [^r6][^r11].
* **cust_save (F8)**: Executes write service `cust_save` via endpoint `POST /ll72/svc/cust_save` (calling database procedure `sp_cust_save`) to register new customer records using mandatory name, city, and country code, alongside optional VAT number, payment term code, and price list [^r6][^r7][^r12].
* **cust_update**: Executes write service `cust_update` to update existing customer details such as customer name, city, country code, and VAT number [^r6][^r14].
* **cust_block**: Executes write service `cust_block` via endpoint `POST /ll72/svc/cust_block` using justification entered in `reason` to set the customer status to blocked, preventing selection on new [[screen-sal-so-01|sales orders]] or delivery notes [^r4][^r6][^r8][^r9].
* **cust_credit**: Executes read service `cust_credit` to interrogate sales ledger balances, committed bicycle orders, and unbilled dispatches to display current credit exposure [^r5][^r6][^r8][^r10].

## Messages

The following system messages and errors can be raised during customer maintenance operations on SAL-CUS-01:

* [[err-cus-0001|ERR-CUS-0001]]: Customer Master Not Found — raised during customer updates when the referenced customer master record does not exist [^r15].
* [[err-cus-0801|ERR-CUS-0801]]: Customer Master Closed (`<status>`) — raised during customer updates when the customer master record is closed [^r15].

## See also

* [[err-cus-0001|ERR-CUS-0001 Mandatory Field Missing or Invalid in Customer Master]]
* [[err-cus-0801|ERR-CUS-0801 Invalid or Duplicate VAT Number]]
* [[screen-sal-so-01|SAL-SO-01 Sales Order]]
* [[services-sal-cust|SAL cust services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 3, §3. Customer Master (SAL-CUS-01)
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 5, Step by step
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 5, Step by step
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 3, §3. Customer Master (SAL-CUS-01)
[^r16]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 34, SAL-CUS-01 CUSTOMER MASTER ENTRY
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 4, Step by step
[^r11]: 04_service_definitions/sales/cust_get.yaml, service: cust_get
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 38, §5. Sales services
[^r14]: 04_service_definitions/sales/cust_update.yaml, service
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 34, SAL-CUS-01 CUSTOMER MASTER ENTRY
[^r13]: 04_service_definitions/sales/cust_search.yaml, service: cust_search
[^r12]: 04_service_definitions/sales/cust_save.yaml, header
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 38, cust_block CUSTOMER MASTER BLOCK
[^r9]: 04_service_definitions/sales/cust_block.yaml, service: cust_block
[^r10]: 04_service_definitions/sales/cust_credit.yaml, service: cust_credit
[^r15]: 04_service_definitions/sales/cust_update.yaml, errors
