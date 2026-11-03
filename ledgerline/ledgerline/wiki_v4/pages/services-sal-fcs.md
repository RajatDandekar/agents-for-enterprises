---
title: "SAL fcs services"
type: "service-group"
slug: "services-sal-fcs"
summary: "Ledgerline sales forecasting services linked to screen SAL-FCS-14, providing single-line retrieval, creation, and bulk file uploads."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/sales/fcs_get.yaml", "04_service_definitions/sales/fcs_save.yaml", "04_service_definitions/sales/fcs_upload.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | SAL |
| Screen | SAL-FCS-14 |
| Services | fcs_get, fcs_save, fcs_upload |
| Since version | 7.0 |
| Protocol | POST |
| Endpoint prefix | /ll72/svc/ |
| Header | X-LL-Session |
| Status | current |

The `services-sal-fcs` group provides sales forecasting capabilities in Ledgerline ERP, operating against screen [[screen-sal-fcs-14|SAL-FCS-14]] [^r3][^r7]. Available since version 7.0, the group contains read and write endpoints to retrieve existing forecasts, commit individual forecast lines, and process bulk planning files [^r3][^r11][^r16][^r20]. All requests are exposed under `/ll72/svc/` and require session authentication via the `X-LL-Session` header with an authorised user role [^r11][^r12][^r17][^r21].

## Services

### fcs_get
Read service that interrogates sales tables to retrieve an existing sales forecast line onto screen [[screen-sal-fcs-14|SAL-FCS-14]] [^r2][^r9][^r11]. It was introduced in version 7.0 and is invoked at endpoint `POST /ll72/svc/fcs_get` with an `X-LL-Session` header [^r11][^r12]. On the screen interface, it maps to Get / F3 [^r7].

* **Required fields**: `fcs_id` (string) [^r9][^r13].
* **Optional fields**: none [^r13].
* **Response**: envelope returning `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r14].
* **Errors**: domain error `ERR-FCS-0001` (SALES FORECAST NOT FOUND), alongside common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r1][^r9][^r15].
* **Source file**: `04_service_definitions/sales/fcs_get.yaml` [^r11].

### fcs_save
Write service that validates input values, commits sales forecast records via stored procedure `sp_fcs_save`, and generates an `FCS ID` reference for new lines on screen [[screen-sal-fcs-14|SAL-FCS-14]] [^r4][^r8][^r16][^r18]. It was introduced in version 7.0, triggers from Save / F8 on screen, and is invoked at endpoint `POST /ll72/svc/fcs_save` with an `X-LL-Session` header [^r7][^r16][^r17].

* **Required fields**: `itm_cd` (string), `period` (string), and `qty` (integer) [^r8][^r18].
* **Optional fields**: none [^r18].
* **Response**: envelope returning `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r19].
* **Errors**: `ERR-FCS-0201` (QTY MUST BE > 0) and [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE), as well as standard system errors [^r1][^r8][^r19].
* **Source file**: `04_service_definitions/sales/fcs_save.yaml` [^r16].

### fcs_upload
Write service used to import bulk external forecast planning files into screen [[screen-sal-fcs-14|SAL-FCS-14]] using procedure `sp_fcs_upload` [^r5][^r8][^r10][^r24]. Available since version 7.0, it is triggered by the Upload function or via endpoint `POST /ll72/svc/fcs_upload` with an `X-LL-Session` header [^r7][^r20][^r21]. It validates uploaded lines sequentially against system requirements [^r5].

* **Required fields**: `itm_cd` (string), `period` (string), and `qty` (integer) [^r10][^r22].
* **Optional fields**: none [^r22].
* **Response**: envelope returning `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r23].
* **Errors**: `ERR-FCS-0201` (QTY MUST BE > 0) and [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE) alongside common system errors [^r1][^r10].
* **Source file**: `04_service_definitions/sales/fcs_upload.yaml` [^r20].

## Versions and conflicts

* **Lookup parameters for `fcs_get`**: In the service definition and reference catalogue, the `fcs_get` service accepts only `fcs_id` as a mandatory lookup parameter [^r9][^r13]. However, the sales manual states that records can be retrieved either by `FCS ID` or by the combination of `ITEM CD` and `PERIOD` [^r2][^r6] (`contradiction`).

## See also
* [[screen-sal-fcs-14|SAL-FCS-14 Sales Forecast Entry]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[services-sal-so|SAL so services]]
* [[services-sal-quo|SAL quo services]]

## References

[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 55, §17. Sales Forecast (SAL-FCS-14)
[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 36, SAL-FCS-14 SALES FORECAST ENTRY
[^r11]: 04_service_definitions/sales/fcs_get.yaml, whole file
[^r16]: 04_service_definitions/sales/fcs_save.yaml, service: fcs_save
[^r20]: 04_service_definitions/sales/fcs_upload.yaml, service: fcs_upload
[^r12]: 04_service_definitions/sales/fcs_get.yaml, auth
[^r17]: 04_service_definitions/sales/fcs_save.yaml, service: fcs_save
[^r21]: 04_service_definitions/sales/fcs_upload.yaml, endpoint
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 56, Retrieving an existing entry
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 50, fcs_get SALES FORECAST GET
[^r13]: 04_service_definitions/sales/fcs_get.yaml, request.fields
[^r14]: 04_service_definitions/sales/fcs_get.yaml, response.envelope
[^r1]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 10
[^r15]: 04_service_definitions/sales/fcs_get.yaml, errors
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 58, Worked example
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 50, fcs_save SALES FORECAST SAVE
[^r18]: 04_service_definitions/sales/fcs_save.yaml, request
[^r19]: 04_service_definitions/sales/fcs_save.yaml, response
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 59, Worked example
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 50, fcs_upload SALES FORECAST UPLOAD
[^r24]: 04_service_definitions/sales/fcs_upload.yaml, procedures
[^r22]: 04_service_definitions/sales/fcs_upload.yaml, request.fields
[^r23]: 04_service_definitions/sales/fcs_upload.yaml, response.envelope
[^r6]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 57, Loading bulk planning files
