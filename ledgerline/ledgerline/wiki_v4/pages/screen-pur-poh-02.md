---
title: "PUR-POH-02 Order History By Item"
type: "screen"
slug: "screen-pur-poh-02"
summary: "Ledgerline screen PUR-POH-02 displays the last ten released purchase orders for an item for reference pricing."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/purchase/po_hist.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen | PUR-POH-02 |
| Name | Order History By Item |
| Module | Purchase |
| Menu path | Purchase > Order history |
| Access | ALL |
| Service | po_hist |
| Status | Current |

Screen PUR-POH-02 displays the last ten released purchase orders for an item in reverse chronological order, showing order quantity, rate, and date [^r1]. Accessible under the Ledgerline menu path Purchase > Order history to role ALL, it is intended strictly for reference enquiry [^r3][^r4]. Historical rates reflect past purchases, whereas active order entry in [[screen-pur-po-01|PUR-PO-01]] must take pricing from the current rate contract retrieved during Order Entry Fetch [^r2][^r4].

| Attribute | Value |
|---|---|
| Screen code | PUR-POH-02 [^r3] |
| Screen title | Order History By Item [^r3] |
| Module | Purchase [^r3] |
| Menu path | Purchase > Order history [^r3] |
| Role access | ALL [^r3] |
| Underlying service | po_hist [^r5][^r6] |

## Fields

* **ITEM CD (`itm_cd`)**: Mandatory item code used to query order history [^r5][^r6].
* **SUP CD (`sup_cd`)**: Optional supplier code used to filter order history results by a specific vendor [^r1][^r5][^r6].
* **History list**: Displays up to ten released orders in reverse chronological order, reporting order quantity, rate, and order date [^r1][^r4].

## Keys and services

* Screen queries are processed by the underlying service `po_hist` (PO HISTORY BY ITEM) documented in [[services-pur-po]] [^r5][^r6].
* Rates retrieved via this enquiry represent historical purchase prices, while live buying pricing is governed by the active rate contract fetched during order entry [^r2][^r4].

## Messages

The underlying `po_hist` service evaluates the mandatory `itm_cd` input and optional `sup_cd` filter to retrieve historical order records [^r5][^r6].

## See also

* [[man-pur-72|MAN-PUR-72 Ledgerline ERP 7.2 User Manual, Purchasing]]
* [[screen-pur-po-01|PUR-PO-01 Purchase Order Entry]]
* [[screen-pur-por-05|PUR-POR-05 Purchase Order Release]]
* [[screen-inv-itm-03|INV-ITM-03 Item Enquiry]]
* [[screen-pur-sup-03|PUR-SUP-03 Supplier Enquiry]]
* [[services-pur-po|PUR po services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 9, §15.1 Purpose
[^r3]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 28, PUR-POH-02 ORDER HISTORY BY ITEM
[^r4]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 28, PUR-POH-02 ORDER HISTORY BY ITEM
[^r2]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 9, §15.2 Using history
[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 28, PUR-POH-02 ORDER HISTORY BY ITEM
[^r6]: 04_service_definitions/purchase/po_hist.yaml, whole file
