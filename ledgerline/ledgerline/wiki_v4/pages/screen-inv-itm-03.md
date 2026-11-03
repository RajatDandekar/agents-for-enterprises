---
title: "INV-ITM-03 Item Enquiry"
type: "screen"
slug: "screen-inv-itm-03"
summary: "Ledgerline item enquiry screen searching the item master by code or description, returning up to 20 rows with details and status indicators."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/purchase/itm_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | INV-ITM-03 |
| title | Item Enquiry |
| module | INV |
| service | itm_search |
| status | current |
| version | 7.2.3 |

`INV-ITM-03` is the item enquiry screen in Ledgerline ERP used to look up item master records by code or description.[^r1] The screen executes the read service `itm_search` and returns up to 20 matching items.[^r1][^r6] It displays critical item details such as active status, rework flags, category, reorder thresholds, and lithium-cell indicators, but does not carry over selected item codes to subsequent operational screens.[^r2][^r3][^r5]

## Fields

| Field | Type | Description |
|---|---|---|
| `q` | Search query (mandatory) | Search input matching item code or description, ignoring case and spaces, using `%` as a middle wildcard.[^r1][^r4] |
| `rows` | Grid (read-only) | Results table listing up to 20 matching records from the item master.[^r1][^r4] |
| `itm_cd` | Text (read-only) | Displays the item code.[^r4] |

Inactive items are displayed in grey in the results list and cannot be placed on new requests or purchase orders.[^r2] Item codes ending in `-R` denote rework items used by Quality.[^r2] Double-clicking an item row displays detailed attributes, including the item category, reorder level, average daily issue, and the lithium-cell flag maintained by Quality.[^r3] Selected item codes are not automatically shared with other screens and must be manually retyped on subsequent screens.[^r5]

## Keys and services

* **F2** or **Enter**: Executes search query field `q` by invoking the `itm_search` service.[^r4]
* **`itm_search`**: A read service in the PUR module accessed via endpoint `POST /ll72/svc/itm_search` to query the item master.[^r6]

## Messages

There are no dedicated message codes documented for this screen.[^r4]

## See also

* [[man-pur-72|MAN-PUR-72 Ledgerline ERP 7.2 User Manual, Purchasing]]
* [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]]
* [[screen-inv-stk-02|INV-STK-02 Stock Status Enquiry]]
* [[screen-pur-poh-02|PUR-POH-02 Order History By Item]]
* [[screen-pur-pr-01|PUR-PR-01 Purchase Request Entry]]
* [[screen-pur-po-01|PUR-PO-01 Purchase Order Entry]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 3, §3.2 Searching
[^r6]: 04_service_definitions/purchase/itm_search.yaml, service: itm_search
[^r2]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 3, §3.3 Reading the list
[^r3]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 4, §3.4 Item details
[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 15, INV-ITM-03 ITEM ENQUIRY
[^r4]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 15, INV-ITM-03 ITEM ENQUIRY
