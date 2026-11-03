---
title: "AP tax services"
type: "service-group"
slug: "services-ap-tax"
summary: "Ledgerline AP tax services tax_get and tax_save for managing tax code master records on screen AP-TAX-17."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/accounts_payable/tax_get.yaml", "04_service_definitions/accounts_payable/tax_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| service_group | services-ap-tax |
| module | Accounts Payable |
| screen | AP-TAX-17 |
| services | tax_get, tax_save |
| version_introduced | 7.0 |
| status | current |

The AP tax service group consists of the read service `tax_get` and write service `tax_save` supporting tax code administration in Ledgerline [^r5][^r6]. Operating against screen [[screen-ap-tax-17|AP-TAX-17]], these endpoints allow accounts payable staff to retrieve existing tax definitions and commit new or updated tax rates to the ledger [^r1][^r2]. Both services have been available since Ledgerline version 7.0 and communicate via HTTP POST requests requiring authenticated session tokens and role authorization [^r7][^r8][^r12][^r13].

## Services

### tax_get

The `tax_get` service (TAX CODE MASTER GET) is a read service introduced in Ledgerline 7.0 that retrieves tax code master details to populate the `DESCR`, `RATE`, and `INTRA/INTER` fields on screen [[screen-ap-tax-17|AP-TAX-17]] [^r1][^r5][^r7]. In the user interface, clicking the `tax_get` button on screen AP-TAX-17 invokes this underlying service [^r3]. The service is accessed at endpoint `POST /ll72/svc/tax_get` and requires an active session token in header `X-LL-Session` along with user role authorization [^r8].

* **Required fields**: `tax_cd` (string, TAX CD) [^r5][^r9].
* **Optional fields**: None [^r9].
* **Errors**: Raises [[err-tax-0001|ERR-TAX-0001]] (TAX CODE MASTER NOT FOUND) when the requested tax code does not exist [^r5][^r10]. Common errors include `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (`<FIELD> MANDATORY`), `ERR-SYS-0422` (`UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>`), and `ERR-SYS-0503` (`SERVER BUSY, TRY LATER`) [^r11]. The response envelope returns `rc`, `err_cd`, `msg`, and `data` [^r10].
* **Source file**: `04_service_definitions/accounts_payable/tax_get.yaml` [^r7].

### tax_save

The `tax_save` service (TAX CODE MASTER SAVE) is a write service introduced in Ledgerline 7.0 that validates tax code details against database rules and commits the record to the ledger catalogue and system tables via backend procedure `sp_tax_save` [^r2][^r6][^r12][^r15]. On screen [[screen-ap-tax-17|AP-TAX-17]], clicking the `tax_save` button triggers this service to commit modifications [^r4]. It is exposed at endpoint `POST /ll72/svc/tax_save` and requires session token authentication in the `X-LL-Session` header with appropriate role permissions [^r13].

* **Required fields**: `tax_cd` (string), `descr` (string), `rate` (float), and `kind` (string, representing `INTRA/INTER`) [^r6][^r14].
* **Optional fields**: None [^r14].
* **Errors**: Returns an envelope with `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r15]. Shared error codes include `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (`<FIELD> MANDATORY`), `ERR-SYS-0422` (`UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>`), and `ERR-SYS-0503` (`SERVER BUSY, TRY LATER`) [^r16].
* **Source file**: `04_service_definitions/accounts_payable/tax_save.yaml` [^r12].

## See also

* [[screen-ap-tax-17|AP-TAX-17 Tax Code Master]]
* [[err-tax-0001|ERR-TAX-0001 TAX CODE MASTER NOT FOUND]]
* [[services-ap-inv|AP inv services]]
* [[services-ap-vat|AP vat services]]

## References

[^r5]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 37, tax_get TAX CODE MASTER GET
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 38, tax_save TAX CODE MASTER SAVE
[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 63, Retrieving an existing record
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 63, Creating or modifying an entry
[^r7]: 04_service_definitions/accounts_payable/tax_get.yaml, service
[^r8]: 04_service_definitions/accounts_payable/tax_get.yaml, endpoint
[^r12]: 04_service_definitions/accounts_payable/tax_save.yaml, whole file
[^r13]: 04_service_definitions/accounts_payable/tax_save.yaml, auth
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 65, Worked example
[^r9]: 04_service_definitions/accounts_payable/tax_get.yaml, request
[^r10]: 04_service_definitions/accounts_payable/tax_get.yaml, response
[^r11]: 04_service_definitions/accounts_payable/tax_get.yaml, common_errors
[^r15]: 04_service_definitions/accounts_payable/tax_save.yaml, response.envelope
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 65, Worked example
[^r14]: 04_service_definitions/accounts_payable/tax_save.yaml, request.fields
[^r16]: 04_service_definitions/accounts_payable/tax_save.yaml, common_errors
