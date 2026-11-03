---
title: "SAL crd services"
type: "service-group"
slug: "services-sal-crd"
summary: "Ledgerline credit control services managing credit hold evaluation, queue inspection, and account release via screen SAL-CRD-11."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/sales/crd_check.yaml", "04_service_definitions/sales/crd_hold_list.yaml", "04_service_definitions/sales/crd_release.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | SAL |
| Screen | SAL-CRD-11 |
| Services | crd_check, crd_hold_list, crd_release |
| Ledgerline Version | 7.0+ |
| Underlying Procedure | sp_crd_release |
| Authentication | X-LL-Session header |

The SAL crd service group manages credit control verification, hold review, and account releases in Ledgerline ERP 7.2 [^r4][^r8][^r13][^r18]. Operating primarily in connection with screen [[screen-sal-crd-11|SAL-CRD-11]], these services allow credit controllers to inspect customer exposure, review blocked orders across Manchester and Leeds, and clear credit flags [^r1][^r2][^r4]. All services run over HTTP POST under endpoint prefix `/ll72/svc/` and require role-authorised session tokens in the `X-LL-Session` header [^r8][^r9][^r14][^r19].

## Services

### crd_check
The `crd_check` read service checks credit control status for a customer account on screen [[screen-sal-crd-11|SAL-CRD-11]] [^r4][^r5][^r8]. It calculates total ledger debt, unallocated and unposted order values, agreed credit limits, and the age of the oldest unpaid invoice [^r2]. Available since Ledgerline version 7.0, it is invoked at endpoint `POST /ll72/svc/crd_check` and authenticates via an `X-LL-Session` header token [^r8][^r9].

* **Required fields**: `cust_cd` (string, CUST CD) [^r5][^r10].
* **Optional fields**: None [^r10].
* **Errors**: Specific error [[err-crd-0001|ERR-CRD-0001]] (CREDIT CONTROL NOT FOUND), and common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r5][^r12].
* **Response**: Returns an envelope with `rc` (`S`, `W`, or `E`), `err_cd` when `rc` is `E`, short uppercase `msg`, and `data` [^r11].
* **Source file**: `04_service_definitions/sales/crd_check.yaml` [^r8].

### crd_hold_list
The `crd_hold_list` read service retrieves all outstanding sales orders flagged with credit hold status across the Manchester and Leeds sites [^r1][^r6][^r13]. Introduced in Ledgerline version 7.0, it supports screen [[screen-sal-crd-11|SAL-CRD-11]] and is invoked via `POST /ll72/svc/crd_hold_list` with a session token in the `X-LL-Session` header [^r4][^r13][^r14].

* **Required fields**: None [^r15].
* **Optional fields**: `cust_cd` (string, CUST CD) [^r6][^r15].
* **Errors**: Specific error [[err-crd-0001|ERR-CRD-0001]] (CREDIT CONTROL NOT FOUND), alongside common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r6][^r17].
* **Response**: Returns an envelope containing `rc` (`S | W | E`), `err_cd`, short uppercase `msg`, and `data` [^r16].
* **Source file**: `04_service_definitions/sales/crd_hold_list.yaml` [^r13].

### crd_release
The `crd_release` write service removes credit hold flags on screen [[screen-sal-crd-11|SAL-CRD-11]] by executing database procedure `sp_crd_release` [^r4][^r7][^r18][^r21]. Available since version 7.0, it is called via `POST /ll72/svc/crd_release` with role authorization and session validation passed in header `X-LL-Session` [^r3][^r18][^r19].

* **Required fields**: `cust_cd` (string, CUST CD) [^r7][^r20].
* **Optional fields**: `comment` (string, COMMENT) [^r7][^r20].
* **Errors**: Specific errors [[err-crd-0001|ERR-CRD-0001]] (CREDIT CONTROL NOT FOUND) and `ERR-CRD-0007` (CREDIT CONTROL NOT IN DRAFT (<status>)), alongside common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r7][^r22][^r23].
* **Response**: Executes stored procedure `sp_crd_release` and returns an envelope with `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r21].
* **Source file**: `04_service_definitions/sales/crd_release.yaml` [^r18].

## Versions and conflicts

* **crd_release COMMENT requirement**: In the technical service definition and service catalogue, field `comment` is defined as optional in the request payload [^r7][^r20]. However, the sales user manual states that `crd_release` validates that the `COMMENT` field contains substantive explanatory text before removing the credit hold flag [^r3]. Sources: `04_service_definitions/sales/crd_release.yaml`, `MAN-SVC-72` (p. 48), and `MAN-SAL-72` (p. 46) (kind: `contradiction`).

## See also

* [[screen-sal-crd-11|SAL-CRD-11 Credit Control Check]]
* [[screen-sal-so-01|SAL-SO-01 Sales Order]]
* [[services-sal-so|SAL so services]]
* [[services-sal-cust|SAL cust services]]
* [[err-crd-0001|ERR-CRD-0001 Missing mandatory remarks for credit release]]

## References

[^r4]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 33, SAL-CRD-11 CREDIT CONTROL CHECK
[^r8]: 04_service_definitions/sales/crd_check.yaml, service: crd_check
[^r13]: 04_service_definitions/sales/crd_hold_list.yaml, service
[^r18]: 04_service_definitions/sales/crd_release.yaml, service: crd_release
[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 46, Reviewing the current hold queue
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 46, Checking an individual account status
[^r9]: 04_service_definitions/sales/crd_check.yaml, auth
[^r14]: 04_service_definitions/sales/crd_hold_list.yaml, endpoint
[^r19]: 04_service_definitions/sales/crd_release.yaml, auth
[^r5]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 48, crd_check CREDIT CONTROL CHECK
[^r10]: 04_service_definitions/sales/crd_check.yaml, request.fields
[^r12]: 04_service_definitions/sales/crd_check.yaml, errors
[^r11]: 04_service_definitions/sales/crd_check.yaml, response.envelope
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 48, crd_hold_list CREDIT CONTROL HOLD LIST
[^r15]: 04_service_definitions/sales/crd_hold_list.yaml, request.fields
[^r17]: 04_service_definitions/sales/crd_hold_list.yaml, errors
[^r16]: 04_service_definitions/sales/crd_hold_list.yaml, response.envelope
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 48, crd_release CREDIT CONTROL RELEASE
[^r21]: 04_service_definitions/sales/crd_release.yaml, response.envelope
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 46, Releasing an order from credit hold
[^r20]: 04_service_definitions/sales/crd_release.yaml, request.fields
[^r22]: 04_service_definitions/sales/crd_release.yaml, errors
[^r23]: 04_service_definitions/sales/crd_release.yaml, common_errors
