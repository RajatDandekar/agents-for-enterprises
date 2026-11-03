---
title: "INV-WHS-01 Warehouse Master"
type: "screen"
slug: "screen-inv-whs-01"
summary: "Ledgerline screen to maintain and query storage locations across Northbridge Cycles, linking each store to an operating unit."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/whs_get.yaml", "04_service_definitions/inventory/whs_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen | INV-WHS-01 |
| Module | Inventory |
| Navigation | Inventory > Warehouse master |
| Roles | STORES, STORES-MGR, PUR-EXEC, SYS-ADMIN |
| Read service | whs_get |
| Write service | whs_save |

Screen INV-WHS-01 is used to register, maintain, and query storage locations across Northbridge Cycles, linking each store to an operating unit [^r1]. It opens in query mode to retrieve active warehouse lists or populate existing records into display mode, and commits new or amended definitions to the database [^r3][^r4][^r5]. The screen is accessed at Inventory > Warehouse master by roles STORES, STORES-MGR, PUR-EXEC, and SYS-ADMIN [^r8].

| Field | Value |
|---|---|
| Screen code | INV-WHS-01 |
| Title | Warehouse Master |
| Menu path | Inventory > Warehouse master |
| Allowed roles | STORES, STORES-MGR, PUR-EXEC, SYS-ADMIN |
| Primary services | [[services-inv-whs|whs_get]], [[services-inv-whs|whs_save]] |

## Fields

Screen INV-WHS-01 contains four data fields [^r2]:

* **WHS CD (`whs_cd`)**: Warehouse code; mandatory [^r2][^r8][^r14]. Used as the primary lookup key [^r11].
* **NAME (`name`)**: Warehouse name; mandatory [^r2][^r8][^r14].
* **OU CD (`ou_cd`)**: Operating unit code; mandatory [^r2][^r8][^r14]. Captures the Manchester operating unit identifier for the manufacturing site or the Leeds unit identifier for the secondary facility [^r6].
* **TYPE (`whs_type`)**: Warehouse classification; optional [^r2][^r8][^r14]. A single character indicating raw components, work in progress, or completed electric bicycles [^r6]. This classification field cannot be changed once stock movements have taken place against the location [^r7].

## Keys and services

The screen utilizes two services from the [[services-inv-whs|INV whs services]] group:

* **Get (F3: `whs_get`)**: Executes the read service `whs_get` via `POST /ll72/svc/whs_get` using mandatory field `whs_cd` [^r9][^r10][^r11]. Populates `NAME`, `OU CD`, and `TYPE` into display mode [^r3].
* **Save (F8: `whs_save`)**: Executes the write service `whs_save` via endpoint `POST /ll72/svc/whs_save` to commit new or updated warehouse master records to the database [^r4][^r9][^r10][^r13]. Requires `whs_cd`, `name`, and `ou_cd`, with `whs_type` submitted as optional [^r14].

## Messages

* [[err-whs-0001|ERR-WHS-0001]]: Warehouse Master Not Found [^r9]. Raised by `whs_get` when it fails to locate the warehouse code in the database [^r12].

## Versions and conflicts

* **Superseded manual version**: In the current Ledgerline v7.2.3 documentation, INV-WHS-01 defines mandatory fields `whs_cd`, `name`, `ou_cd` and optional `whs_type`, processed by services `whs_get` and `whs_save` [^r2][^r3][^r4][^r8][^r10]. The superseded v7.2.2 manual documented identical fields and services under the previous release [^r15][^r16] (kind: `superseded`).

## See also

* [[services-inv-whs|INV whs services]]
* [[err-whs-0001|ERR-WHS-0001]]
* [[screen-inv-bin-09|INV-BIN-09 Bin Master Entry]]
* [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]]
* [[screen-inv-stk-03|INV-STK-03 Stock Val]]
* [[screen-inv-trf-04|INV-TRF-04 Stock Transfer Entry]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 36, Purpose
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 37, Step by step
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 38, Step by step
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 39, Worked example
[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 21, INV-WHS-01 WAREHOUSE MASTER
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 36, §12. Warehouse Master (INV-WHS-01)
[^r14]: 04_service_definitions/inventory/whs_save.yaml, request.fields
[^r11]: 04_service_definitions/inventory/whs_get.yaml, service: whs_get
[^r6]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 39, Worked example
[^r7]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 40, Questions users ask
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 21, INV-WHS-01 WAREHOUSE MASTER
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 18, whs_save WAREHOUSE MASTER SAVE
[^r13]: 04_service_definitions/inventory/whs_save.yaml, service: whs_save
[^r12]: 04_service_definitions/inventory/whs_get.yaml, errors
[^r15]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 17, §12. Warehouse Master (INV-WHS-01)
[^r16]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 17, Step by step
