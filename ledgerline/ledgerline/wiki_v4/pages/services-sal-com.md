---
title: "SAL com services"
type: "service-group"
slug: "services-sal-com"
summary: "Ledgerline SAL commission services (com_get and com_run) calculating and retrieving sales commissions on screen SAL-COM-15."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/sales/com_get.yaml", "04_service_definitions/sales/com_run.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | SAL |
| Screen | SAL-COM-15 |
| Services | com_get, com_run |
| Introduced | Version 7.0 |
| Underlying procedures | sp_com_run |
| Status | Current |

The SAL com service group provides the backend commission processing and retrieval services for the sales ledger in Ledgerline [^r6][^r11]. These services back screen [[screen-sal-com-15|SAL-COM-15]] to compute payable commissions across representative territories and retrieve historic commission figures [^r1][^r2][^r3]. Both services have been available since version 7.0 and use standard session token authentication [^r6][^r7][^r12][^r13].

## Services

### com_get

Service `com_get` (SALES COMMISSION GET) is a read service in module SAL backing screen [[screen-sal-com-15|SAL-COM-15]] [^r5][^r6]. It queries and displays previously calculated sales commission figures, representative lines, and explanatory notes for a specified period [^r1][^r5]. The service is accessed via endpoint `POST /ll72/svc/com_get` and authenticates using a session token in header `X-LL-Session`, requiring an authorized user role [^r7].

* **Required fields**: `period` (string, PERIOD) [^r5][^r8].
* **Optional fields**: None [^r8].
* **Response**: Returns a standard envelope containing `rc` ('S | W | E'), `err_cd`, `msg`, and `data` [^r9].
* **Errors**: Raises [[err-com-0001|ERR-COM-0001]] if the commission run is not found [^r5][^r10]. Common errors include `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r10].
* **Source file**: `04_service_definitions/sales/com_get.yaml` [^r6].

### com_run

Service `com_run` (SALES COMMISSION RUN) is a write service in module SAL backing screen [[screen-sal-com-15|SAL-COM-15]] [^r4][^r11]. It evaluates posted sales ledger transactions, qualifying deliveries, credit deductions, and representative territories for a designated accounting period to calculate payable sales commission [^r2]. The service is accessed via endpoint `POST /ll72/svc/com_run` and authenticates using a session token in header `X-LL-Session` with an authorized user role [^r12][^r13]. Underlying database execution is handled by stored procedure `sp_com_run` [^r4][^r15][^r16].

* **Required fields**: `period` (string) [^r4][^r14].
* **Optional fields**: `comment` (string) [^r4][^r14].
* **Response**: Returns a standard envelope containing `rc` (S | W | E), `err_cd`, `msg`, and `data` [^r15].
* **Errors**: Returns common envelope error responses where `rc` is 'E' [^r15].
* **Source file**: `04_service_definitions/sales/com_run.yaml` [^r11].

## See also

* [[screen-sal-com-15|SAL-COM-15 Sales Commission]]
* [[err-com-0001|ERR-COM-0001 Period Not Open or Already Posted]]
* [[services-sal-so|SAL so services]]
* [[services-sal-sinv|SAL sinv services]]

## References

[^r6]: 04_service_definitions/sales/com_get.yaml, whole file
[^r11]: 04_service_definitions/sales/com_run.yaml, service: com_run
[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 60, Step by step
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 60, Step by step
[^r3]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 33, SAL-COM-15 SALES COMMISSION
[^r7]: 04_service_definitions/sales/com_get.yaml, whole file
[^r12]: 04_service_definitions/sales/com_run.yaml, service: com_run
[^r13]: 04_service_definitions/sales/com_run.yaml, auth
[^r5]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 51, com_get SALES COMMISSION GET
[^r8]: 04_service_definitions/sales/com_get.yaml, request
[^r9]: 04_service_definitions/sales/com_get.yaml, response
[^r10]: 04_service_definitions/sales/com_get.yaml, errors
[^r4]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 51, com_run SALES COMMISSION RUN
[^r15]: 04_service_definitions/sales/com_run.yaml, response.envelope
[^r16]: 04_service_definitions/sales/com_run.yaml, procedures
[^r14]: 04_service_definitions/sales/com_run.yaml, request.fields
