---
title: "INV-RES-12 Stock Reservation Entry"
type: "screen"
slug: "screen-inv-res-12"
summary: "Ledgerline screen for creating, retrieving, searching, and cancelling stock reservations against warehouse inventory and works orders."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/res_cancel.yaml", "04_service_definitions/inventory/res_get.yaml", "04_service_definitions/inventory/res_save.yaml", "04_service_definitions/inventory/res_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | INV-RES-12 |
| Title | Stock Reservation Entry |
| Module | Inventory |
| Menu path | Inventory > Stock reservation |
| Primary services | res_save, res_get, res_search, res_cancel |
| Status | current |

Screen INV-RES-12 (Stock Reservation Entry) is the Ledgerline interface used to manage stock reservations against warehouse inventory and works orders [^r1][^r3]. Accessed via the menu path Inventory > Stock reservation, the screen allows users to create new reservations, query existing records, and cancel allocations to return stock to free warehouse availability [^r1][^r6]. As of 26 October 2026, the screen operates against the core inventory reservation services [[services-inv-res|res_save, res_get, res_search, and res_cancel]] [^r1][^r3][^r9].

| Attribute | Value |
|---|---|
| Screen Code | INV-RES-12 [^r1] |
| Screen Title | STOCK RESERVATION ENTRY [^r7] |
| Menu Path | Inventory > Stock reservation [^r1] |
| Services | res_save, res_get, res_search, res_cancel [^r1][^r8] |

## Fields

Screen INV-RES-12 contains the following header and detail fields [^r2][^r7][^r9]:

| Field Label | Field Name | Requirement | Notes |
|---|---|---|---|
| RES NO | `res_no` | Mandatory [^r2][^r7] | Reservation reference number [^r2][^r9]. |
| ITEM CD | `itm_cd` | Mandatory [^r2][^r7] | Valid item code [^r2][^r15]. |
| WHS CD | `whs_cd` | Mandatory [^r2][^r7] | Warehouse code where stock is held [^r2][^r15]. |
| QTY | `qty` | Mandatory [^r2][^r7] | Quantity to reserve [^r2][^r15]. |
| REASON | `reason` | Mandatory [^r2][^r7] | Mandatory text reason for creation or cancellation [^r2][^r11]. |
| WO NO | `wo_no` | Optional [^r2][^r7] | Associated works order number [^r2][^r15]. |
| STATUS | `status` | Optional [^r2][^r7] | Left blank during creation; system assigns the initial state upon saving [^r4]. |

## Keys and services

INV-RES-12 links keyboard shortcuts and user actions directly to the [[services-inv-res|inventory reservation services]] [^r8][^r9]:

* **Save (F8)**: Calls write service `res_save` (endpoint `POST /ll72/svc/res_save`) to record the reservation using `itm_cd`, `whs_cd`, and `qty`, along with an optional `wo_no` [^r8][^r14][^r15].
* **Get (F3)**: Calls read service `res_get` (STOCK RESERVATION GET) via endpoint `POST /ll72/svc/res_get`, submitting mandatory key `res_no` to retrieve an existing record [^r8][^r12].
* **Search (F2 / Enter)**: Calls read service `res_search` to list matching reservations using partial search criteria such as `itm_cd`, `whs_cd`, or `wo_no`, returning records filtered by item code, warehouse code, quantity, and status [^r5][^r8][^r16].
* **Cancel (Shift+F8)**: Calls write service `res_cancel` at endpoint `POST /ll72/svc/res_cancel` with mandatory fields `res_no` and `reason`, cancelling the reservation and returning the reserved quantity to available free stock in the specified warehouse [^r6][^r8][^r10][^r11].

## Messages

The following system messages and errors can be raised on screen INV-RES-12 [^r8]:

* [[err-itm-0011|ERR-ITM-0011]]: ITEM NOT FOUND OR INACTIVE [^r8].
* [[err-res-0001|ERR-RES-0001]]: General reservation validation failure; raised when querying a reservation through `res_get` if the record is not found (STOCK RESERVATION NOT FOUND) [^r8][^r13].
* [[err-res-0201|ERR-RES-0201]]: Insufficient unreserved stock available [^r8].
* [[err-res-0801|ERR-RES-0801]]: Cancellation rejected [^r8].

## Versions and conflicts

* **Superseded reservation workflow details**: Today's specification is defined by Ledgerline v7.2.3 documentation and current service schemas [^r1][^r2][^r7][^r10][^r14]. In the superseded v7.2.2 manual (dated 2024-06-10), screen INV-RES-12 was specifically noted as enabling stores and production control staff at Manchester and Leeds to set aside stock for active works orders, generating `res_no` and setting `status` to confirmed upon invoking `res_save`, and calling STOCK RESERVATION CANCEL to return stock to available inventory [^r17][^r19][^r21].

## See also

* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[err-res-0001|ERR-RES-0001 General reservation validation failure]]
* [[err-res-0201|ERR-RES-0201 Insufficient unreserved stock available]]
* [[err-res-0801|ERR-RES-0801 Cancellation rejected]]
* [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]
* [[services-inv-res|INV res services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 33, §11. Stock Reservation (INV-RES-12)
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 34, Step by step
[^r6]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 34, Step by step
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 17, res_save STOCK RESERVATION SAVE
[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 18, INV-RES-12 STOCK RESERVATION ENTRY
[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 18, INV-RES-12 STOCK RESERVATION ENTRY
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 33, §11. Stock Reservation (INV-RES-12)
[^r15]: 04_service_definitions/inventory/res_save.yaml, request.fields
[^r11]: 04_service_definitions/inventory/res_cancel.yaml, request.fields
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 34, Step by step
[^r14]: 04_service_definitions/inventory/res_save.yaml, res_save
[^r12]: 04_service_definitions/inventory/res_get.yaml, service
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 34, Step by step
[^r16]: 04_service_definitions/inventory/res_search.yaml, service: res_search
[^r10]: 04_service_definitions/inventory/res_cancel.yaml, whole file
[^r13]: 04_service_definitions/inventory/res_get.yaml, errors
[^r17]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 15, Stock Reservation (INV-RES-12)
[^r19]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 16, Worked example
[^r21]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 16, Questions users ask
