---
title: "ERR-STK Error Codes"
type: "error-list"
slug: "errors-stk"
summary: "Reference list of ERR-STK inventory stock error codes raised across Ledgerline ERP stock services and transfer screens."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "04_service_definitions/inventory/stk_abc_run.yaml", "04_service_definitions/inventory/stk_age_query.yaml", "04_service_definitions/inventory/stk_move_query.yaml", "04_service_definitions/inventory/stk_snapshot.yaml", "04_service_definitions/inventory/stk_val_run.yaml", "04_service_definitions/purchase/stk_query.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-STK |
| Module | Inventory (INV) / Purchasing (PUR) |
| Applicable system | Ledgerline ERP 7.2 |
| Status | Current |

This page catalogues the `ERR-STK-*` error codes encountered across Ledgerline ERP inventory stock valuation, transfer, snapshot, and analysis operations. It documents standard message text, the underlying causes, and the services that raise each condition. Individual errors with extended operational documentation link directly to their dedicated error pages.

### ERR-STK-0001

* **Message:** STOCK NOT FOUND [^r2][^r3][^r4][^r5][^r6] / NO STOCK RECORD [^r7]
* **Cause:** The requested stock item record or valuation data cannot be located in the system during stock querying, analysis, or batch execution [^r2][^r3][^r4][^r5][^r6][^r7].
* **Remedy:** Verify that the item code and warehouse parameters exist in inventory and that relevant transactions have been posted. See [[err-stk-0001|ERR-STK-0001]] for detailed troubleshooting.
* **Raised by:** [[services-inv-stk|stk_abc_run]] [^r2], `stk_age_query` [^r3], `stk_move_query` [^r4], `stk_snapshot` [^r5], `stk_val_run` [^r6], and [[services-pur-stk|stk_query]] [^r7].

### ERR-STK-0102

* **Message:** Entered transfer quantity exceeds free physical balance [^r1].
* **Cause:** The quantity entered for a transfer exceeds the free physical stock balance available in the source warehouse [^r1].
* **Remedy:** Reduce the entered transfer quantity or check available warehouse stock on the relevant stock status or transfer entry screens before reattempting the transaction [^r1].
* **Raised by:** [[man-inv-72|MAN-INV-72]] inventory transfer validation [^r1].

## Versions and conflicts

* ERR-STK-0001 message wording: In inventory services (`stk_abc_run`, `stk_age_query`, `stk_move_query`, `stk_snapshot`, and `stk_val_run`), the code returns the message `STOCK NOT FOUND` [^r2][^r3][^r4][^r5][^r6]. In purchase stock query services (`stk_query`), the identical code returns `NO STOCK RECORD` [^r7] (contradiction).

## See also

* [[err-stk-0001|ERR-STK-0001]]
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]
* [[services-inv-stk|INV stk services]]
* [[services-pur-stk|PUR stk services]]
* [[screen-inv-stk-02|INV-STK-02 Stock Status Enquiry]]
* [[screen-inv-stk-03|INV-STK-03 Stock Val]]
* [[screen-inv-trf-04|INV-TRF-04 Stock Transfer Entry]]
* [[errors-itm|ERR-ITM error codes]]
* [[errors-txf|Stock Transfer Error Codes (ERR-TXF-*)]]

## References

[^r2]: 04_service_definitions/inventory/stk_abc_run.yaml, errors
[^r3]: 04_service_definitions/inventory/stk_age_query.yaml, errors
[^r4]: 04_service_definitions/inventory/stk_move_query.yaml, errors
[^r5]: 04_service_definitions/inventory/stk_snapshot.yaml, errors
[^r6]: 04_service_definitions/inventory/stk_val_run.yaml, errors
[^r7]: 04_service_definitions/purchase/stk_query.yaml, errors
[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 5, Messages
