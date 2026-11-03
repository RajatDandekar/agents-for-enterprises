---
title: "SAL srl services"
type: "service-group"
slug: "services-sal-srl"
summary: "Ledgerline sales serial registration services group comprising srl_reg, srl_get, and srl_search exposed on screen SAL-SRL-16."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/sales/srl_get.yaml", "04_service_definitions/sales/srl_reg.yaml", "04_service_definitions/sales/srl_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| group | services-sal-srl |
| module | SAL |
| screen | SAL-SRL-16 |
| introduced | 7.2.0 |
| services | srl_reg, srl_get, srl_search |

The SAL srl service group provides serial registration, enquiry, and listing operations within the Ledgerline sales module [^r4][^r8][^r13][^r18]. Operating against screen [[screen-sal-srl-16|SAL-SRL-16]], these endpoints validate frame and unit serial identifiers against the stock ledger and track their sale statuses [^r1][^r4]. All services authenticate via standard session tokens and return structured envelopes with status codes, error codes, and messages [^r9][^r11][^r14][^r16][^r19][^r21].

## Services

### srl_reg

The `srl_reg` write service handles serial registration (SERIAL REGISTRATION REG) on screen [[screen-sal-srl-16|SAL-SRL-16]], calling stored procedure `sp_srl_reg` [^r1][^r4][^r5][^r13][^r17]. It validates that the item exists in the stock ledger, verifies that the serial identifier is not already registered, commits the registration, and updates the status to active sold [^r1].

* **Endpoint**: `POST /ll72/svc/srl_reg` [^r14]
* **Authentication**: Session token in header `X-LL-Session` with an authorized user role [^r14]
* **Version introduced**: Ledgerline 7.2.0 [^r13]
* **Required fields**:
  * `serial_no` (string, SERIAL NO) [^r5][^r15]
  * `itm_cd` (string, ITEM CD) [^r5][^r15]
* **Optional fields**:
  * `cust_cd` (string, CUST CD) [^r5][^r15]
  * `sold_dt` (date, SOLD DT) [^r5][^r15]
* **Response**: Envelope containing `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r16]
* **Errors**: [[err-itm-0011|ERR-ITM-0011]], `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r5][^r17]
* **Source file**: `04_service_definitions/sales/srl_reg.yaml` [^r13]

### srl_get

The `srl_get` read service retrieves stored serial registration records (SERIAL REGISTRATION GET) on screen [[screen-sal-srl-16|SAL-SRL-16]] (invoked via Get / F3) [^r2][^r4][^r6][^r8]. It fetches stored values for `ITEM CD`, `CUST CD`, `SOLD DT`, and `STATUS` for a given serial number [^r2].

* **Endpoint**: `POST /ll72/svc/srl_get` [^r9]
* **Authentication**: Session token in header `X-LL-Session` with an authorized user role [^r9]
* **Version introduced**: Ledgerline 7.2.0 [^r8]
* **Required fields**:
  * `serial_no` (string, serial number) [^r6][^r10]
* **Optional fields**: None [^r10]
* **Response**: Envelope containing `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r11]
* **Errors**: [[err-srl-0001|ERR-SRL-0001]] (raised when registration is not found), `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r6][^r11][^r12]
* **Source file**: `04_service_definitions/sales/srl_get.yaml` [^r8]

### srl_search

The `srl_search` read service searches and lists serial registration records (SERIAL REGISTRATION LIST) on screen [[screen-sal-srl-16|SAL-SRL-16]] (invoked via Search / F2/Enter) [^r3][^r4][^r7][^r18]. It retrieves matching frame identifiers, item codes, and dispatch dates based on account codes or partial serial numbers with wildcards [^r3].

* **Endpoint**: `POST /ll72/svc/srl_search` [^r18]
* **Authentication**: Session token in header `X-LL-Session` with an authorized user role [^r19]
* **Version introduced**: Ledgerline 7.2.0 [^r18]
* **Required fields**: None [^r20]
* **Optional fields**:
  * `serial_no` (string, SERIAL NO) [^r7][^r20]
  * `itm_cd` (string, ITEM CD) [^r7][^r20]
  * `cust_cd` (string, CUST CD) [^r7][^r20]
  * `status` (string, STATUS) [^r7][^r20]
* **Response**: Envelope containing `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r21]
* **Errors**: [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE), `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r7][^r22]
* **Source file**: `04_service_definitions/sales/srl_search.yaml` [^r18]

## See also

* [[screen-sal-srl-16|SAL-SRL-16 Serial Registration Reg]]
* [[err-srl-0001|ERR-SRL-0001 Serial Number Already Registered]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[services-sal-so|SAL so services]]
* [[services-sal-dlv|SAL dlv services]]

## References

[^r4]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 40, SAL-SRL-16 SERIAL REGISTRATION REG
[^r8]: 04_service_definitions/sales/srl_get.yaml, service: srl_get
[^r13]: 04_service_definitions/sales/srl_reg.yaml, service: srl_reg
[^r18]: 04_service_definitions/sales/srl_search.yaml, service
[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 64, Step by step
[^r9]: 04_service_definitions/sales/srl_get.yaml, service: srl_get
[^r11]: 04_service_definitions/sales/srl_get.yaml, response
[^r14]: 04_service_definitions/sales/srl_reg.yaml, auth
[^r16]: 04_service_definitions/sales/srl_reg.yaml, response.envelope
[^r19]: 04_service_definitions/sales/srl_search.yaml, auth
[^r21]: 04_service_definitions/sales/srl_search.yaml, response.envelope
[^r5]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 51, srl_reg SERIAL REGISTRATION REG
[^r17]: 04_service_definitions/sales/srl_reg.yaml, errors
[^r15]: 04_service_definitions/sales/srl_reg.yaml, request.fields
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 64, Step by step
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 51, srl_get SERIAL REGISTRATION GET
[^r10]: 04_service_definitions/sales/srl_get.yaml, request.fields
[^r12]: 04_service_definitions/sales/srl_get.yaml, common_errors
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 64, Step by step
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 51, srl_search SERIAL REGISTRATION LIST
[^r20]: 04_service_definitions/sales/srl_search.yaml, request.fields
[^r22]: 04_service_definitions/sales/srl_search.yaml, errors
