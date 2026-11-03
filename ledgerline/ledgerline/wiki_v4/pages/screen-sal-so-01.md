---
title: "SAL-SO-01 Sales Order"
type: "screen"
slug: "screen-sal-so-01"
summary: "Sales order entry and processing screen for commercial bike shop and retail trade orders at Manchester and Leeds."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-SAL-001 Sales Order to Despatch v2.2.pdf", "03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/sales/so_amend.yaml", "04_service_definitions/sales/so_cancel.yaml", "04_service_definitions/sales/so_confirm.yaml", "04_service_definitions/sales/so_fetch.yaml", "04_service_definitions/sales/so_get.yaml", "04_service_definitions/sales/so_hold.yaml", "04_service_definitions/sales/so_release.yaml", "04_service_definitions/sales/so_save.yaml", "04_service_definitions/sales/so_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | SAL-SO-01 |
| Menu path | Sales > Sales order |
| Roles | SAL-EXEC, SAL-MGR, SYS-ADMIN |
| Primary services | so_fetch, so_save, so_confirm, so_get, so_search, so_cancel, so_amend, so_hold, so_release |

SAL-SO-01 is the Ledgerline ERP screen used by staff at the Manchester plant and Leeds unit to record trade orders for electric bicycles, spare parts, and accessories from bike shops, independent retailers, and commercial accounts [^r5]. Accessible via Sales > Sales order, it handles the end-to-end sales order lifecycle from initial entry and pricing calculation through confirmation, amendment, hold, and cancellation [^r3][^r5]. Confirmation on this screen runs automated inventory and credit limit checks, routing confirmed demand directly to warehouse dispatch queues [^r1][^r8].

## Fields

| Field label | Technical name | Mandatory / Optional | Notes |
|---|---|---|---|
| SO NO | `so_no` | Mandatory | System sales order number generated on save [^r4][^r7][^r13][^r21]. |
| CUST CD | `cust_cd` | Mandatory | Customer account code [^r4][^r13][^r20]. |
| ITEM CD | `itm_cd` | Mandatory | Item identifier [^r4][^r13][^r20]. |
| QTY | `qty` | Mandatory | Order line quantity [^r4][^r13][^r20]. |
| REQ DT | `req_dt` | Mandatory | Customer requested delivery date [^r4][^r13][^r20]. |
| REASON | `reason` | Mandatory | Justification code or text, required for hold and administrative operations [^r4][^r10][^r13]. |
| PRICE | `price` | Optional | Line price, populated by list or contract pricing on fetch [^r4][^r6][^r13]. |
| CUST PO REF | `cust_ref` | Optional | Customer purchase order reference [^r4][^r13]. |
| STATUS | `status` | Optional | Lifecycle status including draft, confirmed, held, or cancelled [^r4][^r7][^r8][^r10][^r12][^r13]. |
| COMMENT | `comment` | Optional | Free-text order notes [^r4][^r13]. |

## Keys and services

SAL-SO-01 is authorised for user roles SAL-EXEC, SAL-MGR, and SYS-ADMIN [^r13]. Key bindings and backend services include:

* **Fetch (F3)** invokes read service `so_fetch` to retrieve order line descriptions, verify stock balances at the default shipping site, and populate list or contract pricing [^r6][^r14][^r16][^r20].
* **Save (F8)** calls write service `so_save` (`POST /ll72/svc/so_save`), generating an `SO NO`, calculating line extensions and VAT, and setting status to draft [^r7][^r14][^r16][^r24].
* **Get (F3)** triggers `so_get` (`POST /ll72/svc/so_get`) using mandatory parameter `so_no` to retrieve existing orders [^r14][^r16][^r21].
* **Search (F2/Enter)** invokes `so_search` to query order lists with optional filters such as `cust_cd`, `itm_cd`, `qty`, and `status` [^r14][^r16][^r25].
* **Confirm (F9)** runs write service `so_confirm` (`POST /ll72/svc/so_confirm`), which verifies credit standing and inventory, transitions status to confirmed, and queues demand to the warehouse [^r8][^r14][^r16][^r19].
* **Hold** calls `so_hold` using a mandatory `REASON`, updating status to held and blocking picking tickets and dispatch [^r10][^r14][^r16][^r22].
* **Release (F9)** calls write service `so_release` (`POST /ll72/svc/so_release`) to restore held orders to confirmed status for dispatch scheduling [^r11][^r14][^r16][^r23].
* **Amend** invokes write service `so_amend` (`POST /ll72/svc/so_amend`); it is restricted from altering orders that are already fully picked or invoiced [^r9][^r14][^r16][^r17].
* **Cancel (Shift+F8)** executes write service `so_cancel` (`POST /ll72/svc/so_cancel`), unallocating reserved stock across Manchester and Leeds facilities and setting status to cancelled [^r12][^r14][^r16][^r18].

## Messages

The screen can return the following validation, master data, and processing errors [^r15]:

* `ERR-SO-0001` [^r15]
* `ERR-SO-0201` [^r15]
* [[err-itm-0011|ERR-ITM-0011]] [^r15]
* `ERR-SO-0105` [^r15]
* `ERR-CUS-0031` [^r15]
* [[err-prc-0001|ERR-PRC-0001]] [^r15]
* `ERR-SO-0007` [^r15]
* [[err-crd-0207|ERR-CRD-0207]]: raised during confirmation if a bike shop or customer account exceeds its authorised credit limit, leaving the sales order in an unconfirmed state [^r1][^r2][^r15].
* `ERR-SO-0801` [^r15]

## See also

* [[sop-sal-001|SOP-SAL-001 Sales Order to Despatch]]
* [[services-sal-so|SAL so services]]
* [[errors-so|Errors SO (Sales Order)]]
* [[screen-sal-cus-01|SAL-CUS-01 Customer Master Entry]]
* [[screen-sal-quo-02|SAL-QUO-02 Quotation Entry]]

## References

[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 7, Purpose
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 7, §4. Sales Order (SAL-SO-01)
[^r1]: 02_procedures/SOP-SAL-001 Sales Order to Despatch v2.2.pdf, p. 3, §5. Procedure
[^r8]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 8, Step by step
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 7, §4. Sales Order (SAL-SO-01)
[^r7]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 8, Step by step
[^r13]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 39, SAL-SO-01 SALES ORDER
[^r21]: 04_service_definitions/sales/so_get.yaml, screen
[^r20]: 04_service_definitions/sales/so_fetch.yaml, service: so_fetch
[^r10]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 9, Step by step
[^r6]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 8, Step by step
[^r12]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 9, Step by step
[^r14]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 39, SAL-SO-01 SALES ORDER
[^r16]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 39, so_fetch SALES ORDER FETCH
[^r24]: 04_service_definitions/sales/so_save.yaml, service: so_save
[^r25]: 04_service_definitions/sales/so_search.yaml, screen
[^r19]: 04_service_definitions/sales/so_confirm.yaml, screen
[^r22]: 04_service_definitions/sales/so_hold.yaml, whole file
[^r11]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 9, Step by step
[^r23]: 04_service_definitions/sales/so_release.yaml, service: so_release
[^r9]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 8, Step by step
[^r17]: 04_service_definitions/sales/so_amend.yaml, whole file
[^r18]: 04_service_definitions/sales/so_cancel.yaml, whole file
[^r15]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 39, SAL-SO-01 SALES ORDER
[^r2]: 02_procedures/SOP-SAL-001 Sales Order to Despatch v2.2.pdf, p. 4, §5. Procedure: notes and common mistakes
