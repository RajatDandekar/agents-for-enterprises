---
title: "Integration inventory"
type: "data-source"
slug: "data-integration-inventory"
summary: "Register of Northbridge's seven system interfaces covering direction, transport method, service accounts, and business owners."
audience: "staff"
status: "current"
sources: ["11_training/intranet_export_2016/index.html", "12_integrations/Bank payment file format STD18 v1.3.pdf", "12_integrations/Carrier API notes - Moorland Logistics.md", "12_integrations/Integration inventory.xlsx", "12_integrations/edi_samples/ORDERS_4500091877.edi", "12_integrations/edi_samples/ORDERS_ORD-88213.edi", "12_integrations/edi_samples/ORDERS_ORD-88240.edi", "12_integrations/wsdl/LedgerlineGateway.wsdl"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | data-integration-inventory |
| file | 12_integrations/Integration inventory.xlsx |
| sheet | Interfaces |
| size | 7 rows |
| key_column | id |
| owner | IT / Integrations |
| status | current |

The Integration Inventory registers all automated system interfaces connecting Ledgerline ERP to external counterparties and internal boundary systems [^r11]. It catalogues seven active integrations covering inbound customer EDI, banking payment files, parcel freight bookings, battery test telemetry, payroll, business intelligence, and pilot purchasing automation [^r11][^r12][^r13][^r14][^r15][^r16][^r17][^r18]. As of 26 October 2026, it serves as the baseline register for identifying technical transport mechanisms, assigned service accounts, and operational ownership across Northbridge's digital boundary [^r11].

## What it holds

The file documents the electronic data exchanges across Northbridge Cycles, detailing data flow direction, underlying transport protocols, designated system credentials, and the responsible business lead [^r11]. Recorded flows include:

* Inbound retail orders transmitted via EDIFACT messages [^r12][^r19][^r21][^r23].
* Outbound corporate settlement files exported for bank clearing [^r2][^r13].
* Freight dispatch service calls routed to [[services-sal-frt|Moorland Logistics]] for parcel and pallet consignments [^r3][^r4][^r14][^r26].
* Telemetry imports ingesting battery pack quality control readings from shop-floor test rigs [^r15].
* Automated extracts serving periodic payroll processing and reporting datamarts [^r16][^r17].
* Pilot HTTP service integrations for experimental autonomous purchasing bots [^r18].

## Columns

The `Interfaces` sheet contains seven data columns [^r11]:

* `id`: The unique system interface identifier (e.g., `INT-001` through `INT-007`) [^r11].
* `interface`: A brief descriptive title of the integration [^r11].
* `direction`: Direction of data transmission relative to Ledgerline ERP (`in`, `out`, or bi-directional) [^r11][^r18].
* `transport`: The communication layer or protocol (such as SOAP gateway, file drop, database view, or HTTP services) [^r11][^r12][^r15][^r17][^r18].
* `account`: The batch username or service account executing the exchange [^r11].
* `owner`: The current business or technical owner responsible for the interface [^r11].
* `since`: The calendar year the interface went into operational service [^r11].

## How to look up a row

Lookups are indexed by interface identifier in the `id` column (`INT-001` to `INT-007`) on the `Interfaces` sheet [^r11]. For a specific interface:

1. Locate the interface code in the `id` column [^r11].
2. Identify the active technical transport and service credential (`account`) [^r11].
3. Route operational exceptions or change requests to the listed individual in the `owner` column [^r11].

For example, interface `INT-001` handles incoming retail EDI ORDERS via a SOAP gateway using account [[user-edi-gw|EDI_GW]] (disabled) -> SVC_EDI under [[user-imorgan|Isla Morgan]] since 2005 [^r12]. Interface `INT-002` manages the [[int-bnk-002|Standard 18]] bank payment file via an AP batch account under [[user-mkowalski|Marta Kowalski]] since 2007 [^r2][^r13]. Carrier bookings to Moorland Logistics under `INT-003` operate over a SOAP gateway via account SVC_CARRIER under [[user-cshaw|Callum Shaw]] since 2014 [^r4][^r14]. Battery test rig ingest under `INT-004` uses account SVC_RIG under [[user-pjansen|Pieter Jansen]] since 2023 [^r15]. The payroll file export under `INT-005` uses an HR batch account under [[user-slindqvist|Sofia Lindqvist]] since 2016 [^r16]. Outbound reporting extract `INT-006` runs over database views using account SVC_BI under [[user-gwhitaker|Grace Whitaker]] since 2020 [^r17]. Interface `INT-007` represents the bi-directional purchasing bot pilot operating over HTTP services using account [[user-svc-agent|SVC_AGENT]] without an assigned owner since 2024 [^r18].

## Size

The workbook contains one primary data sheet, `Interfaces`, comprising exactly 7 interface records [^r11].

## See also

* [[int-bnk-002|INT-BNK-002 Supplier payment file: Standard 18 layout as used by Northbridge]]
* [[services-sal-edi|SAL edi services]]
* [[services-sal-frt|SAL frt services]]
* [[services-ap-bnk|AP bnk services]]
* [[services-ap-pay|AP pay services]]
* [[sop-sal-001|SOP-SAL-001 Sales Order to Despatch]]
* [[sop-ap-003|SOP-AP-003 Supplier Payment Run]]
* [[sop-qua-001|SOP-QUA-001 Incoming Inspection]]
* [[pol-pur-001|POL-PUR-001 Purchase Policy]]
* [[user-imorgan|Isla Morgan (IMORGAN)]]
* [[user-mkowalski|Marta Kowalski (MKOWALSKI)]]
* [[user-cshaw|Callum Shaw (CSHAW)]]
* [[user-pjansen|Pieter Jansen (PJANSEN)]]
* [[user-slindqvist|Sofia Lindqvist (SLINDQVIST)]]
* [[user-gwhitaker|Grace Whitaker (GWHITAKER)]]
* [[user-svc-agent|Integration service account (SVC_AGENT)]]
* [[user-edi-gw|EDI gateway account (6.x) (EDI_GW)]]

## References

[^r11]: 12_integrations/Integration inventory.xlsx, sheet Interfaces, SHEET Interfaces
[^r12]: 12_integrations/Integration inventory.xlsx, sheet Interfaces, row INT-001, SHEET Interfaces
[^r13]: 12_integrations/Integration inventory.xlsx, sheet Interfaces, row INT-002, SHEET Interfaces
[^r14]: 12_integrations/Integration inventory.xlsx, sheet Interfaces, row INT-003, SHEET Interfaces
[^r15]: 12_integrations/Integration inventory.xlsx, sheet Interfaces, row INT-004, SHEET Interfaces
[^r16]: 12_integrations/Integration inventory.xlsx, sheet Interfaces, row INT-005, SHEET Interfaces
[^r17]: 12_integrations/Integration inventory.xlsx, sheet Interfaces, row INT-006, SHEET Interfaces
[^r18]: 12_integrations/Integration inventory.xlsx, sheet Interfaces, row INT-007, SHEET Interfaces
[^r19]: 12_integrations/edi_samples/ORDERS_4500091877.edi, whole file
[^r21]: 12_integrations/edi_samples/ORDERS_ORD-88213.edi, ORDERS_ORD-88213.edi
[^r23]: 12_integrations/edi_samples/ORDERS_ORD-88240.edi, whole file
[^r2]: 12_integrations/Bank payment file format STD18 v1.3.pdf, p. 1, §1. Purpose
[^r3]: 12_integrations/Carrier API notes - Moorland Logistics.md, Carrier API notes: Moorland Logistics
[^r4]: 12_integrations/Carrier API notes - Moorland Logistics.md, Booking
[^r26]: 12_integrations/Carrier API notes - Moorland Logistics.md, Services
