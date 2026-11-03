---
title: "PUR tax services"
type: "service-group"
slug: "services-pur-tax"
summary: "Ledgerline purchasing module tax engine and tax code list services used for tax calculations and code retrieval."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/purchase/tax_compute.yaml", "04_service_definitions/purchase/tax_list.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | PUR |
| Object | tax |
| Available since | Ledgerline 7.0 |
| Protocol | POST |
| Authentication | Header X-LL-Session |
| Status | current |

The `services-pur-tax` group provides read-only tax calculation and reference services within Ledgerline's purchasing module [^r3][^r8]. It contains the `tax_compute` calculation engine and the `tax_list` query service, both active since Ledgerline 7.0 [^r1][^r3][^r8]. Both endpoints accept POST requests and require user role authorisation validated through the `X-LL-Session` session token header [^r4][^r9].

## Services

### tax_compute

The `tax_compute` service is a read-only purchasing engine titled TAX ENGINE, available at endpoint `POST /ll72/svc/tax_compute` and backed by database procedure `sp_tax_compute` [^r2][^r3].

* **Required fields:** `basic` (float, basic value) and `tax_cd` (string, tax code) [^r2][^r5].
* **Optional fields:** None [^r5].
* **Errors:** Raises service-specific error `ERR-TAX-0101` (INVALID TAX CODE) if the provided tax code is invalid [^r2][^r7]. It also raises common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r7].
* **Response envelope:** Returns return code `rc` (`S | W | E`), error code `err_cd`, message `msg`, and data result `data` [^r6].
* **Source file:** `04_service_definitions/purchase/tax_compute.yaml` [^r3].

### tax_list

The `tax_list` service is a read-only query service titled TAX CODE LIST in the PUR module, exposed at endpoint `POST /ll72/svc/tax_list` [^r8][^r9].

* **Required fields:** None; the service takes no request parameters [^r1][^r10].
* **Optional fields:** None [^r10].
* **Errors:** Specifies no service-specific errors or warnings, but returns common errors `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (`<FIELD>` MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD `<FIELD>` / BAD VALUE FOR `<FIELD>`), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r11].
* **Response envelope:** Returns an envelope containing `rc` (`S | W | E`), `err_cd` (error code when `rc` is `E`), `msg` (short message in capitals), and `data` (result) [^r10].
* **Source file:** `04_service_definitions/purchase/tax_list.yaml` [^r8].

## See also

* [[data-tax-codes|Tax codes]]
* [[screen-ap-tax-17|AP-TAX-17 Tax Code Master]]
* [[services-pur-po|PUR po services]]

## References

[^r3]: 04_service_definitions/purchase/tax_compute.yaml, whole file
[^r8]: 04_service_definitions/purchase/tax_list.yaml, service: tax_list
[^r1]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 3, §2. Purchase services
[^r4]: 04_service_definitions/purchase/tax_compute.yaml, auth
[^r9]: 04_service_definitions/purchase/tax_list.yaml, endpoint
[^r2]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 8, tax_compute TAX ENGINE
[^r5]: 04_service_definitions/purchase/tax_compute.yaml, request.fields
[^r7]: 04_service_definitions/purchase/tax_compute.yaml, errors
[^r6]: 04_service_definitions/purchase/tax_compute.yaml, response.envelope
[^r10]: 04_service_definitions/purchase/tax_list.yaml, request
[^r11]: 04_service_definitions/purchase/tax_list.yaml, common_errors
