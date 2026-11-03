---
title: "INV csg services"
type: "service-group"
slug: "services-inv-csg"
summary: "Ledgerline inventory services for registering, retrieving, querying, and settling vendor consignment stock records on screen INV-CSG-17."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/csg_get.yaml", "04_service_definitions/inventory/csg_save.yaml", "04_service_definitions/inventory/csg_search.yaml", "04_service_definitions/inventory/csg_settle.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | INV |
| Object | csg |
| Screen | INV-CSG-17 |
| Available since | Ledgerline 7.1 |
| Endpoint prefix | /ll72/svc/ |
| Status | current |

The `csg` service group manages vendor consignment inventory in Ledgerline's INV module on screen [[screen-inv-csg-17|INV-CSG-17 Consignment Stock Entry]][^r9][^r13]. Introduced in Ledgerline version 7.1, these services register on-site supplier parcels, retrieve parcel status, query active sessions, and execute financial settlements directly into purchase ledger accruals[^r1][^r4][^r13][^r18]. All endpoints require HTTP POST requests with a valid user session token passed in the `X-LL-Session` header and an authorised role[^r14][^r19][^r23][^r27].

| Property | Value |
|---|---|
| Module | INV[^r13] |
| Object | csg[^r13] |
| Screen | [[screen-inv-csg-17|INV-CSG-17]][^r9][^r13] |
| Endpoint base | `/ll72/svc/`[^r14][^r18] |
| Ledgerline version | Available since 7.1[^r13][^r18] |
| Status | current[^r1][^r13] |

## Services

### csg_save

Service `csg_save` (CONSIGNMENT STOCK SAVE) registers vendor consignment parcels, allocates a serial CSG NO, and sets the initial record status to active[^r1]. It executes write operations for screen [[screen-inv-csg-17|INV-CSG-17]] (invoked via function key F8) through backend stored procedure `sp_csg_save`[^r8][^r9][^r18].

* **Endpoint**: `POST /ll72/svc/csg_save`[^r18]
* **Authentication**: Session token in header `X-LL-Session` with an authorised user role[^r19]
* **Required fields**: `sup_cd` (SUP CD, string), `itm_cd` (ITEM CD, string), and `qty` (QTY, integer)[^r20]
* **Optional fields**: None[^r20]
* **Response**: Standard envelope returning return code `rc` (`S | W | E`), `err_cd`, `msg`, and data result fields[^r21]
* **Errors**: [[err-csg-0201|ERR-CSG-0201]], [[err-itm-0011|ERR-ITM-0011]], [[err-sup-0030|ERR-SUP-0030]], and common system errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503[^r8][^r9][^r21]
* **Source file**: `04_service_definitions/inventory/csg_save.yaml`[^r18]

### csg_get

Service `csg_get` (CONSIGNMENT STOCK GET) provides read access to consignment records on screen [[screen-inv-csg-17|INV-CSG-17]] (triggered by function key F3)[^r8][^r10][^r13]. It retrieves full record details for an assigned CSG NO from the host server, populating STATUS and parcel balance in QTY[^r2].

* **Endpoint**: `POST /ll72/svc/csg_get`[^r14]
* **Authentication**: Session token in header `X-LL-Session` with an authorised user role[^r14]
* **Required fields**: `csg_no` (CSG NO, string)[^r10][^r15]
* **Optional fields**: None[^r15]
* **Response**: Standard envelope returning `rc` (`S | W | E`), `err_cd`, `msg`, and data result fields[^r16]
* **Errors**: [[err-csg-0001|ERR-CSG-0001]] (CONSIGNMENT STOCK NOT FOUND), along with common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503[^r8][^r10][^r17]
* **Source file**: `04_service_definitions/inventory/csg_get.yaml`[^r13]

### csg_search

Service `csg_search` (CONSIGNMENT STOCK LIST) performs read-only queries against consignment inventory on screen [[screen-inv-csg-17|INV-CSG-17]] (invoked by F2 or Enter)[^r8][^r11][^r22]. It searches by SUP CD or ITEM CD and returns a matching list of active sessions, and can execute using SUP CD alone to locate all open consignment records for a vendor[^r3][^r7].

* **Endpoint**: `POST /ll72/svc/csg_search`[^r23]
* **Authentication**: Session token in header `X-LL-Session` with an authorised user role[^r23]
* **Required fields**: None[^r24]
* **Optional fields**: `sup_cd` (string), `itm_cd` (string), `qty` (integer), and `status` (string)[^r11][^r24]
* **Response**: Standard envelope returning `rc` (`S | W | E`), `err_cd`, `msg`, and data fields[^r25]
* **Errors**: [[err-csg-0201|ERR-CSG-0201]] and [[err-itm-0011|ERR-ITM-0011]][^r25]
* **Source file**: `04_service_definitions/inventory/csg_search.yaml`[^r22]

### csg_settle

Service `csg_settle` (CONSIGNMENT STOCK SETTLE) initiates financial settlement of absorbed consignment goods, transferring liability directly to purchase ledger accruals without duplicate manual goods received notes[^r4][^r12][^r26]. It adjusts stock balances, sets records to settled or partially settled condition, and writes valuation entries to accounts ledger background tables via backend procedure `sp_csg_settle`[^r5][^r12][^r29]. Executing `csg_settle` against a record that is fully settled, cancelled, frozen, or exceeding remaining balance returns [[err-csg-0201|ERR-CSG-0201]][^r6].

* **Endpoint**: `POST /ll72/svc/csg_settle`[^r27]
* **Authentication**: Session token in header `X-LL-Session` with an authorised user role[^r27]
* **Required fields**: `csg_no` (string)[^r12][^r28]
* **Optional fields**: `sup_cd` (string), `itm_cd` (string), and `qty` (integer)[^r12][^r28]
* **Response**: Standard envelope returning `rc`, `err_cd`, `msg`, and data fields[^r29]
* **Errors**: [[err-csg-0001|ERR-CSG-0001]], [[err-csg-0201|ERR-CSG-0201]], [[err-itm-0011|ERR-ITM-0011]], and [[err-sup-0030|ERR-SUP-0030]][^r8][^r12][^r29]
* **Source file**: `04_service_definitions/inventory/csg_settle.yaml`[^r26]

## Versions and conflicts

* **Settlement workflow and record creation**: Under current v7.2.3 documentation, `csg_save` allocates a serial CSG NO and marks status active, and `csg_settle` transfers financial liability directly to purchase ledger accruals without duplicate manual goods received notes[^r1][^r4]. In superseded manual MAN-INV-72 v7.2.2 (dated 2024-06-10), `csg_save` was described generally as creating CSG NO and recording stock held on site, while `csg_settle` transferred stock liability and ownership to Northbridge Cycles (`superseded`)[^r30].

## See also

* [[screen-inv-csg-17|INV-CSG-17 Consignment Stock Entry]]
* [[err-csg-0001|ERR-CSG-0001 CONSIGNMENT STOCK NOT FOUND]]
* [[err-csg-0201|ERR-CSG-0201 QTY MUST BE > 0 / Invalid Consignment Status]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[err-sup-0030|ERR-SUP-0030]]
* [[services-inv-rtv|INV rtv services]]
* [[services-inv-stk|INV stk services]]

## References

[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 24, csg_save CONSIGNMENT STOCK SAVE
[^r13]: 04_service_definitions/inventory/csg_get.yaml, service: csg_get
[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 65, To record newly delivered consignment stock:
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 64, Purpose
[^r18]: 04_service_definitions/inventory/csg_save.yaml, service: csg_save
[^r14]: 04_service_definitions/inventory/csg_get.yaml, service: csg_get
[^r19]: 04_service_definitions/inventory/csg_save.yaml, auth
[^r23]: 04_service_definitions/inventory/csg_search.yaml, endpoint
[^r27]: 04_service_definitions/inventory/csg_settle.yaml, endpoint
[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 14, Label
[^r20]: 04_service_definitions/inventory/csg_save.yaml, request.fields
[^r21]: 04_service_definitions/inventory/csg_save.yaml, errors
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 24, csg_get CONSIGNMENT STOCK GET
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 65, To retrieve an existing consignment record:
[^r15]: 04_service_definitions/inventory/csg_get.yaml, request.fields
[^r16]: 04_service_definitions/inventory/csg_get.yaml, response.envelope
[^r17]: 04_service_definitions/inventory/csg_get.yaml, errors
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 24, csg_search CONSIGNMENT STOCK LIST
[^r22]: 04_service_definitions/inventory/csg_search.yaml, service: csg_search
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 65, To retrieve an existing consignment record:
[^r7]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 66, Tips
[^r24]: 04_service_definitions/inventory/csg_search.yaml, request.fields
[^r25]: 04_service_definitions/inventory/csg_search.yaml, response
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 24, csg_settle CONSIGNMENT STOCK SETTLE
[^r26]: 04_service_definitions/inventory/csg_settle.yaml, service: csg_settle
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 66, Messages
[^r29]: 04_service_definitions/inventory/csg_settle.yaml, errors
[^r6]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 67, Questions users ask
[^r28]: 04_service_definitions/inventory/csg_settle.yaml, request
[^r30]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 28, Step by step
