---
title: "PUR-POR-05 Purchase Order Release"
type: "screen"
slug: "screen-pur-por-05"
summary: "Ledgerline screen used by purchasing roles to transition approved purchase orders from AP to RL status and transmit them to suppliers."
audience: "staff"
status: "mixed"
sources: ["02_procedures/SOP-PUR-002 PR to PO v1.3 (FINAL).pdf", "02_procedures/SOP-PUR-002 PR to PO v1.4.pdf", "03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/purchase/po_release.yaml", "11_training/QRC-02 Raising a purchase order - Fetch first.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | PUR-POR-05 |
| Screen name | Purchase Order Release |
| Menu path | Purchase > Order release |
| Roles | PUR-EXEC, PUR-SR, PUR-MGR, SYS-ADMIN |
| Read-only fields | SUP CD, GROSS VALUE, CC CD, STATUS |
| Mandatory field | PO NO (po_no) |
| Keys | F3 (po_get), F9 (po_release) |

Screen PUR-POR-05 is the Ledgerline interface used to release approved purchase orders to external vendors [^r1][^r6]. Orders in approved (AP) status are held internally until executed on this screen, advancing their status to released (RL) so that vendor transmission, stock increments, and dispatch can proceed [^r1][^r2][^r3][^r12][^r13]. Staff must review the screen at the conclusion of every session to ensure approved orders do not remain stranded [^r14].

| Field | Value |
|---|---|
| Screen code | PUR-POR-05 [^r6] |
| Screen name | PURCHASE ORDER RELEASE [^r6] |
| Menu location | Purchase > Order release [^r6] |
| Authorised roles | PUR-EXEC, PUR-SR, PUR-MGR, SYS-ADMIN [^r6] |
| Mandatory input | PO NO (`po_no`) [^r7] |
| Primary services | `po_get`, `po_release` [^r8][^r9][^r10] |

## Fields

Screen PUR-POR-05 requires the mandatory input field PO NO (`po_no`) to locate the document [^r7]. The remaining header fields SUP CD, GROSS VALUE, CC CD, and STATUS are strictly read-only [^r7].

## Keys and services

PUR-POR-05 is accessible to users with roles PUR-EXEC, PUR-SR, PUR-MGR, and SYS-ADMIN under the menu path Purchase > Order release [^r6]. Pressing F3 invokes `po_get` to fetch the purchase order record into the screen [^r8].

Pressing F9 invokes the write service `po_release` to transition the order from AP to RL status [^r1][^r8][^r10]. This transaction records the release date, increments stock on order, and enqueues an e-mail transmission to the supplier via procedures `sp_po_status_set`, `sp_stk_onorder_upd`, and `sp_ntf_enqueue` [^r3][^r9]. The vendor transmission includes the order number, item, quantity, rate, need-by date, delivery warehouse, and printed remarks [^r5]. If the status code does not update to RL after pressing F9, the order file has not been produced and supplier picking and dispatch will not take place [^r2][^r13].

## Messages

The screen raises the following error messages during lookup and release operations:

* `ERR-PO-0001` (PO NOT FOUND): raised by `po_release` if the specified order number cannot be found in the system [^r11].
* `ERR-PO-0715` (DOCUMENT NOT IN RELEASABLE STATUS (<status>)): raised by `po_release` if an attempt is made to release an order that is not in AP status, such as a draft order, displaying the active status code in brackets [^r4][^r8][^r11].

## Versions and conflicts

Under current [[sop-pur-002|SOP-PUR-002]] v1.4 (effective 2025-02-01), approved purchase orders are released on PUR-POR-05 by pressing F9 to transition the status from AP to RL [^r1]. This reconfirms the process defined in superseded SOP-PUR-002 v1.3 (dated 2023-05-01), which previously specified the same F9 key release to status RL on PUR-POR-05 (`superseded`) [^r15].

## See also

* [[sop-pur-002|SOP-PUR-002 Purchase Request to Purchase Order]]
* [[screen-pur-po-01|PUR-PO-01 Purchase Order Entry]]
* [[screen-pur-poa-04|PUR-POA-04 Purchase Order Approval]]
* [[screen-pur-pom-06|PUR-POM-06 Purchase Order Amendment]]
* [[services-pur-po|PUR po services]]

## References

[^r1]: 02_procedures/SOP-PUR-002 PR to PO v1.4.pdf, p. 3, §5. Procedure
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 29, PUR-POR-05 PURCHASE ORDER RELEASE
[^r2]: 02_procedures/SOP-PUR-002 PR to PO v1.4.pdf, p. 4, What to check on the screen
[^r3]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 8, §13.2 Releasing
[^r12]: 11_training/QRC-02 Raising a purchase order - Fetch first.pdf, p. 1, Tips - Releasing approved orders
[^r13]: 11_training/QRC-02 Raising a purchase order - Fetch first.pdf, p. 1, Tips - Releasing approved orders
[^r14]: 11_training/QRC-02 Raising a purchase order - Fetch first.pdf, p. 1, Tips - Releasing approved orders
[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 29, PUR-POR-05 PURCHASE ORDER RELEASE
[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 29, PUR-POR-05 PURCHASE ORDER RELEASE
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 7, po_release PO RELEASE
[^r10]: 04_service_definitions/purchase/po_release.yaml, whole file
[^r5]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 9, §13.4 What the supplier receives
[^r11]: 04_service_definitions/purchase/po_release.yaml, errors
[^r4]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 9, §13.3 When release fails
[^r15]: 02_procedures/SOP-PUR-002 PR to PO v1.3 (FINAL).pdf, p. 3, §5. Procedure
