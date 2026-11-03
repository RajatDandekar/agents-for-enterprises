---
title: "AP sbal services"
type: "service-group"
slug: "services-ap-sbal"
summary: "Ledgerline read services for querying supplier balances, ageing analysis, and ledger statements on screen AP-SBL-08."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/accounts_payable/sbal_ageing.yaml", "04_service_definitions/accounts_payable/sbal_query.yaml", "04_service_definitions/accounts_payable/sbal_stmt.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | Accounts Payable |
| Screen | AP-SBL-08 |
| Services | sbal_query, sbal_ageing, sbal_stmt |
| Status | current |
| Version introduced | Ledgerline 7.0 |

The `services-ap-sbal` group consists of Ledgerline read services in the Accounts Payable module supporting screen [[screen-ap-sbl-08|AP-SBL-08]] [^r7][^r12][^r18]. Available since version 7.0, these services allow users to query aggregated supplier account balances, recalculate balance ageing across credit bands, and compile detailed ledger statements [^r1][^r2][^r3][^r7][^r12][^r18].

## Services

### sbal_query

Service `sbal_query` (SUPPLIER BALANCE QUERY) is an Accounts Payable read service backing screen [[screen-ap-sbl-08|AP-SBL-08]], present since Ledgerline 7.0 [^r4][^r12]. It aggregates all posted invoices, credit notes, and settlement entries up to the specified cut-off point and displays supplier name, address, currency, balance, and last transaction date [^r1]. Calls are submitted to endpoint `POST /ll72/svc/sbal_query` and require a valid session token in header `X-LL-Session` alongside an authorized user role [^r8][^r13]. The service returns standard envelope fields comprising return code `rc` ('S | W | E'), `err_cd`, `msg`, and `data` [^r15].

* **Required fields:** None [^r4][^r14].
* **Optional fields:** `sup_cd` (string, SUP CD), `as_on` (date, AS ON) [^r4][^r14].
* **Errors:** ERR-SBL-0001 (SUPPLIER BALANCE NOT FOUND), [[err-sup-0030|ERR-SUP-0030]] (SUPPLIER NOT FOUND), ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r4][^r16][^r17].
* **Source file:** `04_service_definitions/accounts_payable/sbal_query.yaml` [^r12].

### sbal_ageing

Service `sbal_ageing` (SUPPLIER BALANCE AGEING) is a read service linked to screen [[screen-ap-sbl-08|AP-SBL-08]] that recalculates open items across standard ageing bands strictly using invoice dates and supplier master credit terms [^r2][^r5][^r7]. It has been available since Ledgerline 7.0 and operates via endpoint `POST /ll72/svc/sbal_ageing`, requiring header `X-LL-Session` with an authorized user role [^r7][^r8].

* **Required fields:** `sup_cd` (string, SUP CD) [^r5][^r9].
* **Optional fields:** None [^r5][^r9].
* **Errors:** ERR-SBL-0001 (SUPPLIER BALANCE NOT FOUND), [[err-sup-0030|ERR-SUP-0030]] (SUPPLIER NOT FOUND), ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r5][^r10][^r11].
* **Source file:** `04_service_definitions/accounts_payable/sbal_ageing.yaml` [^r7].

### sbal_stmt

Service `sbal_stmt` (SUPPLIER BALANCE STMT) compiles a detailed ledger statement featuring opening balances, invoices, payments, credit notes, and closing balance, outputting directly to the print queue or document viewer [^r3][^r6][^r18]. It has been present since Ledgerline 7.0 for screen [[screen-ap-sbl-08|AP-SBL-08]] and uses endpoint `POST /ll72/svc/sbal_stmt` with session authentication in header `X-LL-Session` [^r18][^r19]. The service returns an envelope containing `rc`, `err_cd`, `msg`, and `data` [^r21].

* **Required fields:** `sup_cd` (string, SUP CD) [^r6][^r20].
* **Optional fields:** None [^r6][^r20].
* **Errors:** ERR-SBL-0001, [[err-sup-0030|ERR-SUP-0030]] [^r6][^r21].
* **Source file:** `04_service_definitions/accounts_payable/sbal_stmt.yaml` [^r18].

## See also

* [[screen-ap-sbl-08|AP-SBL-08 Supplier Balance]]
* [[services-ap-sup|AP sup services]]
* [[services-ap-inv|AP inv services]]
* [[services-ap-pay|AP pay services]]
* [[errors-sup|ERR-SUP Error Codes]]
* [[err-sup-0030|ERR-SUP-0030]]

## References

[^r7]: 04_service_definitions/accounts_payable/sbal_ageing.yaml, service: sbal_ageing
[^r12]: 04_service_definitions/accounts_payable/sbal_query.yaml, whole file
[^r18]: 04_service_definitions/accounts_payable/sbal_stmt.yaml, service: sbal_stmt
[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 30, Step by step
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 31, Tips
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 31, Step by step
[^r4]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 32, sbal_query SUPPLIER BALANCE QUERY
[^r8]: 04_service_definitions/accounts_payable/sbal_ageing.yaml, auth
[^r13]: 04_service_definitions/accounts_payable/sbal_query.yaml, whole file
[^r15]: 04_service_definitions/accounts_payable/sbal_query.yaml, response
[^r14]: 04_service_definitions/accounts_payable/sbal_query.yaml, request
[^r16]: 04_service_definitions/accounts_payable/sbal_query.yaml, errors
[^r17]: 04_service_definitions/accounts_payable/sbal_query.yaml, common_errors
[^r5]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 32, sbal_ageing SUPPLIER BALANCE AGEING
[^r9]: 04_service_definitions/accounts_payable/sbal_ageing.yaml, request.fields
[^r10]: 04_service_definitions/accounts_payable/sbal_ageing.yaml, errors
[^r11]: 04_service_definitions/accounts_payable/sbal_ageing.yaml, common_errors
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 32, sbal_stmt SUPPLIER BALANCE STMT
[^r19]: 04_service_definitions/accounts_payable/sbal_stmt.yaml, auth
[^r21]: 04_service_definitions/accounts_payable/sbal_stmt.yaml, response.envelope
[^r20]: 04_service_definitions/accounts_payable/sbal_stmt.yaml, request.fields
