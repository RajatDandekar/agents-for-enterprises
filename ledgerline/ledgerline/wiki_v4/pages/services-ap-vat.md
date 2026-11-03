---
title: "AP vat services"
type: "service-group"
slug: "services-ap-vat"
summary: "Ledgerline Accounts Payable services supporting VAT return calculation, retrieval, and reverse charge transaction extraction on screen AP-VAT-12."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/accounts_payable/vat_get.yaml", "04_service_definitions/accounts_payable/vat_rc_list.yaml", "04_service_definitions/accounts_payable/vat_run.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| service_group | services-ap-vat |
| module | Accounts Payable (AP) |
| screen | AP-VAT-12 |
| introduced | Ledgerline 7.0 |
| endpoints | /ll72/svc/vat_run, /ll72/svc/vat_get, /ll72/svc/vat_rc_list |
| status | current |

The `services-ap-vat` service group provides backend services for the calculation, retrieval, and analysis of Value Added Tax returns in Ledgerline Accounts Payable [^r8][^r18]. Operating through [[screen-ap-vat-12|AP-VAT-12]], these services compute preliminary input tax and reverse charge liabilities, fetch compiled summary figures, and itemise individual reverse charge transactions for a reporting interval [^r1][^r2][^r3]. All three endpoints require an active session token in the `X-LL-Session` header and an authorised user role [^r9][^r14][^r19].

## Services

### vat_run

* **Title**: VAT RETURN RUN [^r5][^r18]
* **Type**: Write service [^r18]
* **Endpoint**: `POST /ll72/svc/vat_run` [^r19]
* **Linked screen**: [[screen-ap-vat-12|AP-VAT-12]] [^r5][^r18]
* **Source file**: `04_service_definitions/accounts_payable/vat_run.yaml` [^r18]
* **Description**: Scans posted tax lines across the specified interval, builds temporary calculation tables, and calculates preliminary totals for input tax and reverse charges [^r1]. It executes stored procedure `sp_vat_run` [^r5][^r21].
* **Required fields**: `period` (`str`) [^r5][^r20]
* **Optional fields**: `comment` (`str`) [^r5][^r20]
* **Errors**: Halts with `ERR-VAT-0001` if invalid parameters, closed periods without transactions, or unposted batches are encountered [^r4]. Common errors include `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (`<FIELD>` MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD `<FIELD>` / BAD VALUE FOR `<FIELD>`), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r22].

### vat_get

* **Title**: VAT RETURN GET [^r6][^r8]
* **Type**: Read service [^r8]
* **Endpoint**: `POST /ll72/svc/vat_get` [^r9]
* **Linked screen**: [[screen-ap-vat-12|AP-VAT-12]] [^r6]
* **Source file**: `04_service_definitions/accounts_payable/vat_get.yaml` [^r8]
* **Description**: Retrieves compiled tax return data from temporary tables and populates summary fields and grid totals on screen [[screen-ap-vat-12|AP-VAT-12]] [^r2]. Returns an envelope containing `rc`, `err_cd`, `msg`, and `data` [^r10].
* **Required fields**: `period` (`str`) [^r6][^r10]
* **Optional fields**: None [^r10]
* **Errors**: Specific error `ERR-VAT-0001` (VAT RETURN NOT FOUND) if the return is not found [^r6][^r11]. Common errors include `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (`<FIELD>` MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD `<FIELD>` / BAD VALUE FOR `<FIELD>`), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r12].

### vat_rc_list

* **Title**: VAT RETURN RC LIST [^r7]
* **Type**: Read service [^r13]
* **Endpoint**: `POST /ll72/svc/vat_rc_list` [^r13]
* **Linked screen**: [[screen-ap-vat-12|AP-VAT-12]] [^r7][^r13]
* **Source file**: `04_service_definitions/accounts_payable/vat_rc_list.yaml` [^r13]
* **Description**: Extracts all transactions flagged for reverse charge treatment for the specified period, presenting supplier details, net expenditure, and calculated tax liability [^r3][^r7]. Returns a response envelope with `rc` (values `'S'`, `'W'`, or `'E'`), `err_cd`, `msg`, and `data` [^r16].
* **Required fields**: `period` (`str`) [^r7][^r15]
* **Optional fields**: None [^r15]
* **Errors**: Specific error `ERR-VAT-0001` (VAT RETURN NOT FOUND) if the return is not found [^r7][^r16]. Common errors include `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (`<FIELD>` MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD `<FIELD>` / BAD VALUE FOR `<FIELD>`), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r17].

## See also

* [[screen-ap-vat-12|AP-VAT-12 Vat Return]]
* [[screen-ap-tax-17|AP-TAX-17 Tax Code Master]]
* [[services-ap-tax|AP tax services]]
* [[screen-ap-per-11|AP-PER-11 Ap Period]]
* [[services-ap-per|AP per services]]
* [[services-ap-gl|AP gl services]]

## References

[^r8]: 04_service_definitions/accounts_payable/vat_get.yaml, service: vat_get
[^r18]: 04_service_definitions/accounts_payable/vat_run.yaml, service: vat_run
[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 41, Screen layout and fields
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 41, Screen layout and fields
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 41, Screen layout and fields
[^r9]: 04_service_definitions/accounts_payable/vat_get.yaml, endpoint
[^r14]: 04_service_definitions/accounts_payable/vat_rc_list.yaml, auth
[^r19]: 04_service_definitions/accounts_payable/vat_run.yaml, endpoint
[^r5]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 34, vat_run VAT RETURN RUN
[^r21]: 04_service_definitions/accounts_payable/vat_run.yaml, procedures
[^r20]: 04_service_definitions/accounts_payable/vat_run.yaml, request.fields
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 42, Messages
[^r22]: 04_service_definitions/accounts_payable/vat_run.yaml, common_errors
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 34, vat_get VAT RETURN GET
[^r10]: 04_service_definitions/accounts_payable/vat_get.yaml, request
[^r11]: 04_service_definitions/accounts_payable/vat_get.yaml, errors
[^r12]: 04_service_definitions/accounts_payable/vat_get.yaml, common_errors
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 34, vat_rc_list VAT RETURN RC LIST
[^r13]: 04_service_definitions/accounts_payable/vat_rc_list.yaml, service: vat_rc_list
[^r16]: 04_service_definitions/accounts_payable/vat_rc_list.yaml, response
[^r15]: 04_service_definitions/accounts_payable/vat_rc_list.yaml, request
[^r17]: 04_service_definitions/accounts_payable/vat_rc_list.yaml, common_errors
