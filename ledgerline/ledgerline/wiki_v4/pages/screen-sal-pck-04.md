---
title: "SAL-PCK-04 Pick List Entry"
type: "screen"
slug: "screen-sal-pck-04"
summary: "Ledgerline screen SAL-PCK-04 produces and confirms warehouse pick lists against confirmed sales orders for Manchester or Leeds."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/sales/pck_confirm.yaml", "04_service_definitions/sales/pck_get.yaml", "04_service_definitions/sales/pck_save.yaml", "04_service_definitions/sales/pck_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | SAL-PCK-04 |
| Title | Pick List Entry |
| Module | Sales > Pick list |
| Roles | SAL-EXEC, SAL-MGR, SYS-ADMIN |
| Services | pck_save, pck_get, pck_search, pck_confirm |
| Status | Current |

SAL-PCK-04 (Pick List Entry) generates unique pick lists against confirmed sales orders for Manchester or Leeds warehouses [^r1]. Operating under Sales > Pick list, it is accessible to roles SAL-EXEC, SAL-MGR, and SYS-ADMIN [^r5]. The screen allows users to allocate inventory, retrieve existing pick lists, search records, and execute confirmations [^r1][^r2][^r6].

## Fields

SAL-PCK-04 features header and control fields including SO NO, WHS CD, PCK NO, STATUS, and COMMENT [^r1]. Screen field requirements define so_no, whs_cd, and pck_no as mandatory, alongside optional status and comment fields [^r5]. In practice, when creating a new pick list, the user leaves PCK NO blank, enters SO NO, WHS CD, and an optional COMMENT, and saves to allocate stock and auto-generate the pick list number [^r2].

## Keys and services

SAL-PCK-04 maps standard function keys to underlying Ledgerline services:
* **Search (F2/Enter)**: Executes the read service `pck_search` to list pick lists, filtering optionally by so_no, whs_cd, and status [^r6][^r10].
* **Get (F3)**: Calls the read service `pck_get` (endpoint `POST /ll72/svc/pck_get`), passing mandatory field pck_no to retrieve pick list details [^r6][^r8].
* **Save (F8)**: Invokes the write service `pck_save` (endpoint `POST /ll72/svc/pck_save`) specifying mandatory fields so_no and whs_cd to allocate inventory and generate a pick list number [^r2][^r6][^r9].
* **Confirm (F9)**: Uses the write service `pck_confirm` (endpoint `POST /ll72/svc/pck_confirm`) to confirm pick lists [^r6][^r7].

All four operations are detailed in [[services-sal-pck]].

## Messages

The screen raises two primary error codes:
* **ERR-PCK-0001**: Displayed when mandatory header information is missing or unrecognized, or when the sales order cannot be located, is locked, or is on credit or technical hold [^r3][^r6].
* **ERR-PCK-0007**: Returned when stock cannot be allocated from the specified WHS CD due to insufficient balances, warehouse mismatch against the order header, or altered inventory balances during confirmation [^r4][^r6].

## Versions and conflicts

* **Contradiction**: MAN-SCR-72 lists `pck_no` as a mandatory input field on SAL-PCK-04 [^r5], whereas the operational procedure in MAN-SAL-72 specifies leaving PCK NO blank during creation so that `pck_save` can auto-generate the number [^r2]. In service definitions, `pck_save` requires only `so_no` and `whs_cd` [^r9], while `pck_get` requires `pck_no` [^r8].

## See also

* [[screen-sal-so-01|SAL-SO-01 Sales Order]]
* [[screen-sal-alc-03|SAL-ALC-03 Allocation]]
* [[screen-sal-dlv-05|SAL-DLV-05 Despatch Entry]]
* [[services-sal-pck|SAL pck services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 18, Purpose
[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 37, SAL-PCK-04 PICK LIST ENTRY
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 19, Creating a new pick list
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 37, SAL-PCK-04 PICK LIST ENTRY
[^r10]: 04_service_definitions/sales/pck_search.yaml, screen
[^r8]: 04_service_definitions/sales/pck_get.yaml, screen
[^r9]: 04_service_definitions/sales/pck_save.yaml, service: pck_save
[^r7]: 04_service_definitions/sales/pck_confirm.yaml, service: pck_confirm
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 20, Messages
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 20, Messages
