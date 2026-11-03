---
title: "QRC-08 Stock enquiry and days of cover"
type: "procedure"
slug: "qrc-08"
summary: "Quick reference guide covering stock status enquiries on INV-STK-02 and the calculation of days of cover across sites."
audience: "staff"
status: "current"
sources: ["11_training/QRC-08 Stock enquiry and days of cover.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Document code | QRC-08 |
| Title | Stock enquiry and days of cover |
| Owner | Purchasing key users |
| Version | 2026.1 |
| Effective date | 2026-01-12 |
| Classification | INTERNAL |
| Status | current |

QRC-08 provides operational guidance on checking inventory balances and calculating days of cover across Northbridge Cycles' facilities [^r1][^r4]. It instructs staff on using standard inventory screens to assess stock availability before placing purchase orders or scheduling inter-site transfers [^r2][^r4]. As of 26 October 2026, version 2026.1 is in force [^r1].

## Steps

1. Navigate to screen [[screen-inv-stk-02|INV-STK-02]] to enquire on stock status [^r2].
2. Input an item code and warehouse [^r2]. Leaving the warehouse field blank displays combined inventory across both the Manchester plant and the Leeds unit, which must be verified before creating purchase orders or scheduling inter-site transfers [^r2][^r4].
3. Review the inventory status quantities [^r2][^r5]:
   - Free stock represents usable inventory for works orders and customer despatches, excluding stock on order until purchase receipts pass incoming inspection and Ledgerline ERP registers them as on hand [^r5].
   - Allocated inventory includes parts committed to active assembly shop orders as well as sales despatches awaiting collection [^r6].
   - Quantities displayed as on order represent open purchase order lines acknowledged by suppliers [^r7].
4. Calculate days of cover by dividing free stock (on hand minus allocated) by the average daily issue [^r3].

## Forms and screens

* [[screen-inv-stk-02|INV-STK-02]] (Stock Status Enquiry): Used to view on-hand, allocated, and on-order quantities by item and warehouse, or across all sites [^r2][^r4].

## See also

* [[screen-inv-stk-02]]

## References

[^r1]: 11_training/QRC-08 Stock enquiry and days of cover.pdf, p. 1, Quick reference: Stock enquiry and days of cover
[^r4]: 11_training/QRC-08 Stock enquiry and days of cover.pdf, p. 1, Tips / Reviewing cross-site balances
[^r2]: 11_training/QRC-08 Stock enquiry and days of cover.pdf, p. 1, Steps
[^r5]: 11_training/QRC-08 Stock enquiry and days of cover.pdf, p. 1, Tips / Calculating free stock
[^r6]: 11_training/QRC-08 Stock enquiry and days of cover.pdf, p. 1, Tips / Stock allocated to production
[^r7]: 11_training/QRC-08 Stock enquiry and days of cover.pdf, p. 1, Tips / Purchase orders in transit
[^r3]: 11_training/QRC-08 Stock enquiry and days of cover.pdf, p. 1, Steps
