---
title: "Errors SO (Sales Order)"
type: "error-list"
slug: "errors-so"
summary: "Error code catalogue for Ledgerline Sales Order processing, listing causes, remedies, services, and discrepancies between UI manual and service definitions."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "04_service_definitions/sales/so_amend.yaml", "04_service_definitions/sales/so_cancel.yaml", "04_service_definitions/sales/so_confirm.yaml", "04_service_definitions/sales/so_fetch.yaml", "04_service_definitions/sales/so_get.yaml", "04_service_definitions/sales/so_hold.yaml", "04_service_definitions/sales/so_release.yaml", "04_service_definitions/sales/so_save.yaml", "04_service_definitions/sales/so_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-SO |
| Module | Sales Order (SAL) |
| Document code | MAN-SAL-72 |
| System | Ledgerline ERP 7.2 |
| Status | current |

This page catalogues the `ERR-SO-*` error codes raised during sales order processing in Ledgerline ERP 7.2. It covers validation and state failures encountered on [[screen-sal-so-01|SAL-SO-01 Sales Order]] and via backend [[services-sal-so|SAL so services]]. Discrepancies exist between user manual [[man-sal-72|MAN-SAL-72]] and raw backend service definitions regarding error meanings and messages.

### ERR-SO-0001

* **Message:** `SALES ORDER NOT FOUND` [^r6] (Backend service definition) / Mandatory field missing [^r1] (User manual).
* **Cause:** The sales order cannot be located during service operations [^r6], or mandatory header/line fields are blank on UI entry [^r1].
* **Remedy:** Ensure valid order identification when querying or amending [^r6], or populate `CUST CD`, `ITEM CD`, `QTY`, and `REQ DT` before saving [^r1].
* **Raised by:** Services `so_amend` [^r6], `so_cancel` [^r9], `so_confirm` [^r11], `so_fetch` [^r13], `so_get` [^r16], `so_hold` [^r17], and `so_release` [^r18]; UI order entry [^r1].

### ERR-SO-0007

* **Message:** `SALES ORDER NOT IN DRAFT (<status>)` [^r12] (Backend service definition) / Invalid status transition [^r2] (User manual).
* **Cause:** An operation expected the order to be in draft state [^r12], or an illegal status progression was attempted such as confirming a cancelled order or amending an invoiced order [^r2].
* **Remedy:** Verify current order status before invoking confirmation or release workflows [^r2][^r12].
* **Raised by:** Services `so_confirm` [^r12] and `so_release` [^r19]; UI order state transitions [^r2].

### ERR-SO-0105

* **Message:** `DATE IN PAST` [^r15] (Backend service definition) / Insufficient physical stock [^r3] (User manual).
* **Cause:** An entered date is prior to the current business date during fetch or save operations [^r15][^r21], or stock is unavailable for immediate allocation at the designated unit [^r3].
* **Remedy:** Ensure required dates are set forward [^r15][^r21], or initiate forward backordering or inter-site stock transfer between Manchester and Leeds [^r3].
* **Raised by:** Services `so_fetch` [^r15] and `so_save` [^r21]; UI allocation entry [^r3].

### ERR-SO-0201

* **Message:** `QTY MUST BE > 0` [^r8] (Backend service definition) / Duplicate customer PO reference [^r4] (User manual).
* **Cause:** An order quantity was submitted as zero or negative [^r8][^r20], or the reference in `CUST PO REF` has already been used on an existing order for that customer [^r4].
* **Remedy:** Enter a positive quantity value [^r8][^r20], or provide a distinct customer purchase order reference [^r4].
* **Raised by:** Services `so_amend` [^r8], `so_fetch` [^r14], `so_save` [^r20], and `so_search` [^r22]; UI order saving [^r4].

### ERR-SO-0801

* **Message:** `SALES ORDER CLOSED (<status>)` [^r7] (Backend service definition) / Record locked [^r5] (User manual).
* **Cause:** The order is already in a closed status when attempting amendment or cancellation [^r7][^r10], or the sales order record is locked by another terminal session [^r5].
* **Remedy:** Do not execute update services on closed orders [^r7][^r10], or wait for the concurrent user terminal session to release the record lock [^r5].
* **Raised by:** Services `so_amend` [^r7] and `so_cancel` [^r10]; UI record retrieval [^r5].

## Versions and conflicts

* **ERR-SO-0001 meaning:** In backend service definitions, ERR-SO-0001 indicates `SALES ORDER NOT FOUND` [^r6][^r9][^r11][^r13][^r16][^r17][^r18]. In [[man-sal-72|MAN-SAL-72]] v7.2.3 (2025-01-15), it indicates a mandatory field missing on UI entry (`CUST CD`, `ITEM CD`, `QTY`, `REQ DT`) [^r1]. Kind: `contradiction`.
* **ERR-SO-0007 meaning:** In backend service definitions, ERR-SO-0007 indicates `SALES ORDER NOT IN DRAFT (<status>)` [^r12][^r19]. In [[man-sal-72|MAN-SAL-72]] v7.2.3 (2025-01-15), it indicates an invalid status transition like confirming a cancelled order or amending an invoiced order [^r2]. Kind: `contradiction`.
* **ERR-SO-0105 meaning:** In backend service definitions, ERR-SO-0105 indicates `DATE IN PAST` [^r15][^r21]. In [[man-sal-72|MAN-SAL-72]] v7.2.3 (2025-01-15), it indicates insufficient physical stock for immediate allocation requiring backordering or transfer [^r3]. Kind: `contradiction`.
* **ERR-SO-0201 meaning:** In backend service definitions, ERR-SO-0201 indicates `QTY MUST BE > 0` [^r8][^r14][^r20][^r22]. In [[man-sal-72|MAN-SAL-72]] v7.2.3 (2025-01-15), it indicates duplicate use of `CUST PO REF` for that customer [^r4]. Kind: `contradiction`.
* **ERR-SO-0801 meaning:** In backend service definitions, ERR-SO-0801 indicates `SALES ORDER CLOSED (<status>)` [^r7][^r10]. In [[man-sal-72|MAN-SAL-72]] v7.2.3 (2025-01-15), it indicates that the order record is locked by another terminal session [^r5]. Kind: `contradiction`.

## See also

* [[man-sal-72|MAN-SAL-72 Ledgerline ERP 7.2 User Manual: Sales and]]
* [[screen-sal-so-01|SAL-SO-01 Sales Order]]
* [[services-sal-so|SAL so services]]
* [[sop-sal-001|SOP-SAL-001 Sales Order to Despatch]]
* [[errors-po|ERR-PO Error Codes]]
* [[errors-itm|ERR-ITM error codes]]
* [[errors-rma|ERR-RMA Error Codes]]

## References

[^r6]: 04_service_definitions/sales/so_amend.yaml, errors
[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 9, Messages
[^r9]: 04_service_definitions/sales/so_cancel.yaml, errors
[^r11]: 04_service_definitions/sales/so_confirm.yaml, errors
[^r13]: 04_service_definitions/sales/so_fetch.yaml, errors
[^r16]: 04_service_definitions/sales/so_get.yaml, errors
[^r17]: 04_service_definitions/sales/so_hold.yaml, errors
[^r18]: 04_service_definitions/sales/so_release.yaml, errors
[^r12]: 04_service_definitions/sales/so_confirm.yaml, errors
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 9, Messages
[^r19]: 04_service_definitions/sales/so_release.yaml, errors
[^r15]: 04_service_definitions/sales/so_fetch.yaml, errors
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 9, Messages
[^r21]: 04_service_definitions/sales/so_save.yaml, errors
[^r8]: 04_service_definitions/sales/so_amend.yaml, errors
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 9, Messages
[^r20]: 04_service_definitions/sales/so_save.yaml, errors
[^r14]: 04_service_definitions/sales/so_fetch.yaml, errors
[^r22]: 04_service_definitions/sales/so_search.yaml, errors
[^r7]: 04_service_definitions/sales/so_amend.yaml, errors
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 9, Messages
[^r10]: 04_service_definitions/sales/so_cancel.yaml, errors
