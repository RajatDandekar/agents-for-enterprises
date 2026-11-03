---
title: "sales_orders_2026"
type: "data-source"
slug: "data-sales-orders-2026"
summary: "Register of 2026 sales order transactions covering order lines, customer details, pricing, statuses, and assigned sales representatives."
audience: "staff"
status: "current"
sources: ["06_transactions/sales_orders_2026.csv"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| File | 06_transactions/sales_orders_2026.csv |
| Type | Transaction register |
| Format | CSV |
| Row count | 4,188 |
| Key column | so_no |

The `sales_orders_2026.csv` dataset is the transaction register recording Northbridge Cycles' sales orders across the 2026 operating year [^r1]. It tracks customer order details, item lines, pricing tiers, and delivery progress across key domestic and European markets [^r2][^r4][^r5]. As of 26 October 2026, it serves as the operational reference for monitoring order fulfilment status and sales representative portfolio allocations [^r3][^r7].

## What it holds

The file holds transactional records for Northbridge Cycles sales orders, encompassing 140 distinct [[items-fg|finished goods]] items ordered in discrete quantities such as 1, 2, 3, 4, 6, and 10 [^r1][^r6]. The register reflects order activity across seven countries, including BE, DE, DK, FR, GB, and IE [^r4]. Every order line is assigned to one of three price lists—PL-EU-RTL, PL-KEY, or PL-UK-RTL—and tracked through one of five order statuses: ALLOCATED, CANCELLED, INVOICED, OPEN, or SHIPPED [^r3][^r5]. Transactions are attributed to sales representatives [[user-echen|Ethan Chen]] (`ECHEN`) or [[user-imorgan|Isla Morgan]] (`IMORGAN`) [^r7].

## Columns

The dataset contains 11 columns [^r1]:

| Column | Description |
|---|---|
| `so_no` | Sales order number identifier [^r2] |
| `order_dt` | Date the sales order was placed [^r2] |
| `cust_cd` | Customer account code [^r2] |
| `cust_name` | Registered customer name [^r2] |
| `country` | Destination or billing country code (e.g. BE, DE, DK, FR, GB, IE) [^r2][^r4] |
| `itm_cd` | Item code for the ordered product [^r2] |
| `qty` | Order quantity [^r2] |
| `unit_price` | Price charged per unit [^r2] |
| `price_list` | Price list applied (`PL-EU-RTL`, `PL-KEY`, or `PL-UK-RTL`) [^r2][^r5] |
| `status` | Fulfilment status (`ALLOCATED`, `CANCELLED`, `INVOICED`, `OPEN`, `SHIPPED`) [^r2][^r3] |
| `rep` | Assigned sales representative (`ECHEN` or `IMORGAN`) [^r2][^r7] |

## How to look up a row

Look up records by sales order number in the `so_no` column [^r2]. Where an order contains multiple line items, lookups filter by `so_no` combined with the finished goods code in `itm_cd` [^r2][^r6].

## Size

The file consists of 4,188 data rows across 11 columns in `csv` format [^r1][^r2].

## See also

* [[items-fg]]
* [[user-echen]]
* [[user-imorgan]]

## References

[^r1]: 06_transactions/sales_orders_2026.csv, sheet csv, SHEET csv
[^r2]: 06_transactions/sales_orders_2026.csv, sheet csv, SHEET csv
[^r4]: 06_transactions/sales_orders_2026.csv, sheet csv, SHEET csv
[^r5]: 06_transactions/sales_orders_2026.csv, sheet csv, SHEET csv
[^r3]: 06_transactions/sales_orders_2026.csv, sheet csv, SHEET csv
[^r7]: 06_transactions/sales_orders_2026.csv, sheet csv, SHEET csv
[^r6]: 06_transactions/sales_orders_2026.csv, sheet csv, SHEET csv
