---
title: "ERR-PO-0610 Direct order exceeds maximum allowed value"
type: "error"
slug: "err-po-0610"
summary: "Ledgerline error code raised when a direct purchase order exceeds the maximum allowed monetary threshold."
audience: "staff"
status: "mixed"
sources: ["01_policies/AMD-PUR-2026-03_Amendment3_PurchasePolicy_DIRlimit.pdf", "11_training/intranet_export_2016/error_messages.html"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | ERR-PO-0610 |
| Message | DIRECT PO LIMIT EXCEEDED |
| Module | Purchasing |
| Current threshold | £30,000 |
| Future threshold | £25,000 gross including VAT (effective 2026-12-01) |
| Status | current |

`ERR-PO-0610` is a Ledgerline error message indicating that a direct purchase order exceeds the maximum allowed value [^r1]. Today, the system permits direct purchase orders up to a limit of £30,000 only [^r1]. From 1 December 2026, this threshold will decrease to £25,000 gross including VAT under [[amd-pur-2026-03|AMD-PUR-2026-03]] [^r2].

## Meaning

The error produces the message `DIRECT PO LIMIT EXCEEDED` [^r1]. It indicates that the value of a direct order has breached the ceiling established for direct procurement [^r1].

## Cause

The total value entered for a direct purchase order exceeds the system threshold of £30,000 [^r1].

## How to fix

Reduce the order value to £30,000 or below to proceed with a direct order [^r1]. If the required purchase exceeds this limit, process it through the standard non-direct purchasing route governed by [[pol-pur-001|POL-PUR-001]].

## Raised by

Raised by Ledgerline during purchase order entry or validation [^r1][^r2].

## Versions and conflicts

* **Today's rule:** Direct purchase orders are permitted up to £30,000 only [^r1].
* **Future rule:** Effective 1 December 2026, Ledgerline will raise `ERR-PO-0610` whenever a direct purchase order exceeds £25,000 gross including VAT pursuant to [[amd-pur-2026-03|AMD-PUR-2026-03]] [^r2].
* **Sources and dates:** 11_training/intranet_export_2016/error_messages.html (current) [^r1] versus [[amd-pur-2026-03|AMD-PUR-2026-03]] v1.0 (effective 2026-12-01) [^r2].
* **Kind:** `future_dated`.

## See also

* [[amd-pur-2026-03|AMD-PUR-2026-03 Amendment 3 to the Purchase Policy]]
* [[pol-pur-001|POL-PUR-001 Purchase Policy]]
* [[man-pur-72|MAN-PUR-72 Ledgerline ERP 7.2 User Manual, Purchasing]]
* [[err-po-0412|ERR-PO-0412 TAX CODE DOES NOT MATCH SUPPLIER COUNTRY]]

## References

[^r1]: 11_training/intranet_export_2016/error_messages.html, Error messages
[^r2]: 01_policies/AMD-PUR-2026-03_Amendment3_PurchasePolicy_DIRlimit.pdf, p. 1, §3. What changes in Ledgerline
