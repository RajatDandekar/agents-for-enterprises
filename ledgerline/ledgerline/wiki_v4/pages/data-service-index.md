---
title: "service_index"
type: "data-source"
slug: "data-service-index"
summary: "Index and metadata catalogue of 400 Ledgerline 7.2 read and write services across six functional modules exported on 26 October 2026."
audience: "staff"
status: "current"
sources: ["04_service_definitions/README.md", "04_service_definitions/purchase/sup_cert_upload.yaml", "04_service_definitions/service_index.csv"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Source file | 04_service_definitions/service_index.csv |
| Modules | ADM, AP, INV, PRD, PUR, SAL |
| Total services | 400 |
| Associated screens | 101 distinct screens across 376 services |
| Export date | 2026-10-26 |
| Format | CSV |

The service index dataset catalogues the service definitions exported from the Ledgerline 7.2 service registry (SYS-SVC) on 26 October 2026 [^r1]. It covers 400 distinct read and write services distributed across six functional modules [^r8][^r9]. The catalogue provides cross-references to corresponding Ledgerline screens and defines compatibility formats for both current YAML specifications and legacy SOAP gateway endpoints [^r1][^r2][^r10].

## What it holds
The dataset indexes all 400 distinct services operating in Ledgerline 7.2 across six modules: 38 purchasing (PUR), 84 inventory (INV), 71 accounts payable (AP), 79 sales (SAL), 67 production (PRD), and 61 administration (ADM) [^r3][^r8]. Every service accepts a flat payload limited to at most 12 fields named after legacy column names and returns a legacy envelope containing fields `rc`, `err_cd`, `msg`, and `data` [^r4]. The envelope return code `rc` produces `'S'` for success, `'W'` for success with a warning, or `'E'` for error [^r5]. Ledgerline 7 services are documented in individual YAML files, while legacy SOAP gateway services for EDI, bank payments, and carrier booking remain active through the compatibility listener and are formatted in WSDL-style XML [^r1][^r2]. For example, definition `sup_cert_upload` in module PUR was exported by JFLETCHER on 26 October 2026 [^r7].

## Columns
Services in the index are classified by functional module, service kind (read or write), and version origin ranging across 6.2, 7.0, 7.1, 7.2.0, and 7.2.3 [^r8][^r9][^r10]. For 376 of the entries, the dataset specifies associated screen codes linking back to 101 distinct Ledgerline screens [^r10].

## How to look up a row
To look up a service, find the row in `service_index.csv` using the service name or its associated screen code [^r8][^r10]. Specific payload structures, parameters, and error responses can then be inspected in the individual definition file exported under `04_service_definitions/` [^r1][^r7].

## Size
The index contains 400 distinct service records spanning six modules (38 PUR, 84 INV, 71 AP, 79 SAL, 67 PRD, and 61 ADM), mapping to 101 distinct screens across 376 of those services [^r3][^r8][^r10].

## Versions and conflicts
Ledgerline 7.2 services currently execute via active registry exports or compatibility listeners, whereas three Ledgerline 6 service definitions kept under `_legacy_6x/` for reference following the 2015 upgrade no longer exist on the server [^r1][^r2][^r6].

## See also
* [[man-svc-72|MAN-SVC-72 Ledgerline ERP 7.2 Service Reference]]
* [[services-pur-sup|PUR sup services]]
* [[services-ap-acr|AP acr services]]
* [[services-inv-adj|INV adj services]]
* [[screen-ap-acr-10|AP-ACR-10 Grni Accrual]]
* [[screen-inv-adj-05|INV-ADJ-05 Stock Adjustment Entry]]
* [[errors-sup|ERR-SUP Error Codes]]
* [[user-svc-agent|Integration service account (SVC_AGENT)]]

## References

[^r1]: 04_service_definitions/README.md, Ledgerline 7.2 service definitions
[^r8]: 04_service_definitions/service_index.csv, sheet csv, SHEET csv
[^r9]: 04_service_definitions/service_index.csv, sheet csv, SHEET csv
[^r2]: 04_service_definitions/README.md, Ledgerline 7.2 service definitions
[^r10]: 04_service_definitions/service_index.csv, sheet csv, SHEET csv
[^r3]: 04_service_definitions/README.md, Ledgerline 7.2 service definitions
[^r4]: 04_service_definitions/README.md, Ledgerline 7.2 service definitions
[^r5]: 04_service_definitions/README.md, Ledgerline 7.2 service definitions
[^r7]: 04_service_definitions/purchase/sup_cert_upload.yaml, whole file
[^r6]: 04_service_definitions/README.md, Ledgerline 7.2 service definitions
