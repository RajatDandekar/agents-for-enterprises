---
title: "AP acr services"
type: "service-group"
slug: "services-ap-acr"
summary: "Ledgerline AP acr services for executing, retrieving, and reversing goods received not invoiced (GRNI) accrual batches on screen AP-ACR-10."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/accounts_payable/acr_get.yaml", "04_service_definitions/accounts_payable/acr_reverse.yaml", "04_service_definitions/accounts_payable/acr_run.yaml", "04_service_definitions/service_index.csv"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | AP |
| Object | acr |
| Screen | screen-ap-acr-10 |
| Available since | 7.0 |
| Status | current |
| Services | acr_get, acr_reverse, acr_run |

The AP acr service group executes, retrieves, and reverses Goods Received Not Invoiced (GRNI) accruals in Ledgerline module AP [^r1][^r24]. Associated with screen [[screen-ap-acr-10|AP-ACR-10]], these services scan unmatched deliveries across Manchester and Leeds to post or reverse periodic accrual journal batches in the general ledger [^r1][^r2][^r3]. All three services were introduced in Ledgerline version 7.0 and authenticate calls via an `X-LL-Session` token header against authorized user roles [^r12][^r17][^r20][^r24].

## Services

### acr_run

Runs the GRNI accrual process to scan unmatched deliveries across Manchester and Leeds, assign an accrual batch, and post an unposted accrual journal to the general ledger [^r1][^r3]. It is a write service executing stored procedure `sp_acr_run` via endpoint `POST /ll72/svc/acr_run` on screen [[screen-ap-acr-10|AP-ACR-10]] [^r8][^r19][^r24].

* **Required fields:** `acr_no` (string) [^r8][^r21].
* **Optional fields:** `comment` (string) [^r8][^r21].
* **Errors:** [[err-acr-0001|ERR-ACR-0001]], `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, `ERR-SYS-0503` [^r6][^r23].
* **Source file:** `accounts_payable/acr_run.yaml` [^r24].

The response envelope returns `rc`, `err_cd`, `msg`, and `data` [^r22].

### acr_get

Retrieves saved GRNI accrual run details, including the processing status, initial comment, and accrued line items for a given run [^r4][^r9]. It is a read service invoked via endpoint `POST /ll72/svc/acr_get` (mapped to function key F3) on screen [[screen-ap-acr-10|AP-ACR-10]] [^r7][^r11][^r24].

* **Required fields:** `acr_no` (string) [^r7][^r9][^r13].
* **Optional fields:** None [^r13].
* **Errors:** [[err-acr-0001|ERR-ACR-0001]] (GRNI ACCRUAL NOT FOUND), `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, `ERR-SYS-0503` [^r7][^r9][^r15].
* **Source file:** `accounts_payable/acr_get.yaml` [^r24].

The response envelope returns `rc`, `err_cd`, `msg`, and `data` [^r14].

### acr_reverse

Reverses an active GRNI accrual run by posting a reversing journal to the general ledger and setting the accrual batch status to reversed at the beginning of a subsequent period [^r2][^r5]. It is a write service running stored procedure `sp_acr_reverse` via endpoint `POST /ll72/svc/acr_reverse` on screen [[screen-ap-acr-10|AP-ACR-10]] [^r10][^r16][^r17][^r24][^r25].

* **Required fields:** `acr_no` (string) [^r7][^r10][^r18].
* **Optional fields:** `reason` (string) [^r10][^r18].
* **Errors:** [[err-acr-0001|ERR-ACR-0001]], `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, `ERR-SYS-0503` [^r6][^r7][^r10][^r25].
* **Source file:** `accounts_payable/acr_reverse.yaml` [^r24].

## Versions and conflicts

* **Field requirements between service definition and user manual:** In the underlying service YAML definitions and reference manual MAN-SVC-72, `acr_run` requires `acr_no` while `comment` is optional, and `acr_reverse` requires `acr_no` while `reason` is optional [^r8][^r10][^r18][^r21]. User manual MAN-AP-72 states that `acr_run` assigns the ACR NO and requires the COMMENT field, and that `acr_reverse` validates that the REASON field is populated [^r3][^r5] (`contradiction`).

## See also

* [[screen-ap-acr-10|AP-ACR-10 Grni Accrual]]
* [[err-acr-0001|ERR-ACR-0001: Accrual execution or reversal failed]]
* [[services-ap-per|AP per services]]
* [[services-ap-gl|AP gl services]]
* [[services-ap-inv|AP inv services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 33, Purpose
[^r24]: 04_service_definitions/service_index.csv, sheet csv, row acr_get, SHEET csv
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 33, Purpose
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 34, Generating a new accrual run:
[^r12]: 04_service_definitions/accounts_payable/acr_get.yaml, auth
[^r17]: 04_service_definitions/accounts_payable/acr_reverse.yaml, auth
[^r20]: 04_service_definitions/accounts_payable/acr_run.yaml, auth
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 32, acr_run GRNI ACCRUAL RUN
[^r19]: 04_service_definitions/accounts_payable/acr_run.yaml, whole file
[^r21]: 04_service_definitions/accounts_payable/acr_run.yaml, request.fields
[^r6]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 35, Messages
[^r23]: 04_service_definitions/accounts_payable/acr_run.yaml, common_errors
[^r22]: 04_service_definitions/accounts_payable/acr_run.yaml, response.envelope
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 34, Retrieving an existing accrual record:
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 33, acr_get GRNI ACCRUAL GET
[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 4, p. 4
[^r11]: 04_service_definitions/accounts_payable/acr_get.yaml, service: acr_get
[^r13]: 04_service_definitions/accounts_payable/acr_get.yaml, request
[^r15]: 04_service_definitions/accounts_payable/acr_get.yaml, errors
[^r14]: 04_service_definitions/accounts_payable/acr_get.yaml, response
[^r5]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 34, Reversing an accrual run:
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 33, acr_reverse GRNI ACCRUAL REVERSE
[^r16]: 04_service_definitions/accounts_payable/acr_reverse.yaml, service: acr_reverse
[^r25]: 04_service_definitions/accounts_payable/acr_reverse.yaml, errors
[^r18]: 04_service_definitions/accounts_payable/acr_reverse.yaml, request.fields
