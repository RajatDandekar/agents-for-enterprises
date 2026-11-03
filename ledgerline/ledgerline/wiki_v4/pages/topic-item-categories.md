---
title: "Item Categories"
type: "topic"
slug: "topic-item-categories"
summary: "Definition of the seven valid item categories configured in Ledgerline ERP for inventory classification."
audience: "staff"
status: "current"
sources: ["05_master_data/ITEM_MASTER_2026-10-26.xlsx"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| System | Ledgerline ERP |
| Configured categories | 7 |
| Primary master | ITEM_MASTER_2026-10-26.xlsx |

Northbridge Cycles defines seven valid item categories within Ledgerline ERP for classifying inventory records [^r1]. These categories structure item setup across materials, components, maintenance items, and assemblies [^r1]. In particular, finished e-bikes map specifically to FINISHED, while battery packs are grouped under SPARES [^r2][^r3].

## Categories and usage

The system recognizes exactly seven item categories configured in the item master: RAW, COMPONENTS, SPARES, PACKING, MRO, CONSUMABLES, and FINISHED [^r1].

* **FINISHED**: Designated for finished e-bikes [^r3].
* **SPARES**: Defined as spares and battery packs [^r2].
* **RAW**: Raw materials [^r1].
* **COMPONENTS**: Component assemblies and parts [^r1].
* **PACKING**: Packaging supplies and materials [^r1].
* **MRO**: Maintenance, repair, and operating supplies [^r1].
* **CONSUMABLES**: General operational consumables [^r1].

## See also

* [[data-item-master|ITEM_MASTER_2026-10-26]]
* [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]]
* [[items-fg|FG-* items]]
* [[items-bat|BAT-* items]]
* [[items-spr|SPR-* items]]
* [[items-pkg|PKG-* items]]

## References

[^r1]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Categories, SHEET Categories
[^r2]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Categories, row SPARES, SHEET Categories
[^r3]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Categories, row FINISHED, SHEET Categories
