---
title: "Errors SIN (ERR-SIN-*)"
type: "error-list"
slug: "errors-sin"
summary: "Error codes for sales invoicing (ERR-SIN-*) covering delivery references, period locks, draft validation, and invoice cancellation in Ledgerline Sales."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "04_service_definitions/sales/sinv_cancel.yaml", "04_service_definitions/sales/sinv_get.yaml", "04_service_definitions/sales/sinv_post.yaml", "04_service_definitions/sales/sinv_print.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-SIN-* |
| Module | Sales Invoicing (SAL) |
| Document reference | [[man-sal-72|MAN-SAL-72]] |
| Service group | [[services-sal-sinv|SAL sinv services]] |
| Primary screen | [[screen-sal-inv-06|SAL-INV-06]] |
| Status | current |

Sales invoicing error codes (ERR-SIN-*) are raised during sales invoice maintenance, posting, printing, and cancellation across Ledgerline ERP Sales and related backend services [^r1][^r4][^r7][^r9]. They alert users to invalid delivery references, missing invoice records, non-draft posting attempts, accounting period restrictions, and improper cancellation requests [^r1][^r2][^r3][^r8]. Understanding these codes ensures billing can proceed through [[screen-sal-inv-06|SAL-INV-06 Sales Invoice Entry]] without blocking order completion [^r1][^r2].

### ERR-SIN-0001
* **Message**: `SALES INVOICE NOT FOUND` [^r4][^r6][^r7][^r9]
* **Cause**: In backend processing, the requested sales invoice record cannot be located [^r4][^r6][^r7][^r9]. During invoice entry in [[man-sal-72|MAN-SAL-72]], the delivery reference entered in `DLV NO` does not exist in distribution tables, has not reached completed dispatch status, or has already been invoiced [^r1].
* **Remedy**: Verify that the delivery reference exists, that dispatch has reached completed status, that the delivery has not already been billed, or confirm that the targeted sales invoice number exists in the database [^r1][^r4][^r6][^r7][^r9].
* **Raised by**: Services `sinv_cancel` [^r4], `sinv_get` [^r6], `sinv_post` [^r7], and `sinv_print` [^r9]; screen [[screen-sal-inv-06|SAL-INV-06]] validation described in [[man-sal-72|MAN-SAL-72]] [^r1].

### ERR-SIN-0007
* **Message**: `SALES INVOICE NOT IN DRAFT (<status>)` [^r8]
* **Cause**: Raised by backend service `sinv_post` when an operator attempts to post a sales invoice that is not in draft status [^r8]. According to [[man-sal-72|MAN-SAL-72]], the code also indicates that the sales invoice record is locked because the financial period matching `INV DT` is closed, the customer account has a hard lock, or posting lacks a nominal distribution code or linked tax category [^r2].
* **Remedy**: Ensure the invoice remains in draft status prior to posting [^r8]. Check that the financial period for `INV DT` is open, resolve any customer account locks, and verify that nominal distribution codes and linked tax categories are properly assigned [^r2].
* **Raised by**: Service `sinv_post` [^r8]; [[screen-sal-inv-06|SAL-INV-06]] posting routines in [[man-sal-72|MAN-SAL-72]] [^r2].

### ERR-SIN-0801
* **Message**: `SALES INVOICE CLOSED (<status>)` [^r5]
* **Cause**: Raised by service `sinv_cancel` when an action is invoked against a closed invoice status [^r5]. It also occurs when `sinv_cancel` is called without filling `REASON`, when attempting to cancel an invoice that has already been cleared by cash allocation, or when attempting to post while the sales ledger accounting period is closed [^r3].
* **Remedy**: Provide a cancellation reason in `REASON`, verify that the sales ledger accounting period is open, and ensure the target invoice is not closed or already cleared by cash allocation [^r3][^r5].
* **Raised by**: Service `sinv_cancel` [^r3][^r5]; sales invoice cancellation processes in [[man-sal-72|MAN-SAL-72]] [^r3].

## Versions and conflicts
* **ERR-SIN-0001 definition**: Today's backend services return the message `SALES INVOICE NOT FOUND` across `sinv_cancel`, `sinv_get`, `sinv_post`, and `sinv_print` [^r4][^r6][^r7][^r9]. In contrast, user manual [[man-sal-72|MAN-SAL-72]] (v7.2.3, 2025-01-15, p. 27) documents ERR-SIN-0001 as occurring when a delivery reference entered in `DLV NO` does not exist in distribution tables, has not reached completed dispatch status, or has already been invoiced (`contradiction`) [^r1].
* **ERR-SIN-0007 definition**: The service definition for `sinv_post` defines ERR-SIN-0007 as `SALES INVOICE NOT IN DRAFT (<status>)` [^r8]. Manual [[man-sal-72|MAN-SAL-72]] (p. 28) describes ERR-SIN-0007 as an invoice lock triggered by a closed financial period for `INV DT`, a customer account hard lock, or posting lacking a nominal distribution code or linked tax category (`contradiction`) [^r2].
* **ERR-SIN-0801 definition**: Service `sinv_cancel` explicitly assigns ERR-SIN-0801 the message `SALES INVOICE CLOSED (<status>)` [^r5]. Manual [[man-sal-72|MAN-SAL-72]] (p. 28) describes ERR-SIN-0801 as occurring when calling `sinv_cancel` without `REASON`, when attempting to cancel an invoice cleared by cash allocation, or when posting while the sales ledger period is closed (`contradiction`) [^r3].

## See also
* [[screen-sal-inv-06|SAL-INV-06 Sales Invoice Entry]]
* [[services-sal-sinv|SAL sinv services]]
* [[man-sal-72|MAN-SAL-72 Ledgerline ERP 7.2 User Manual: Sales and Distribution]]
* [[errors-so|Errors SO (Sales Order)]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 27, Messages
[^r4]: 04_service_definitions/sales/sinv_cancel.yaml, errors
[^r7]: 04_service_definitions/sales/sinv_post.yaml, errors
[^r9]: 04_service_definitions/sales/sinv_print.yaml, errors
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 28, Messages
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 28, Messages
[^r8]: 04_service_definitions/sales/sinv_post.yaml, errors
[^r6]: 04_service_definitions/sales/sinv_get.yaml, errors
[^r5]: 04_service_definitions/sales/sinv_cancel.yaml, errors
