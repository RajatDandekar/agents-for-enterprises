---
title: "SPR-* items"
type: "item-family"
slug: "items-spr"
summary: "Spare parts and service kits family covering model-specific maintenance assemblies, stock levels across warehouses, and customer order fulfilment requirements."
audience: "staff"
status: "current"
sources: ["05_master_data/ITEM_MASTER_2026-10-26.xlsx", "05_master_data/Stock_on_hand_2026-10-26_0900.xlsx", "12_integrations/edi_samples/ORDERS_4500091877.edi", "12_integrations/edi_samples/ORDERS_ORD-88213.edi", "12_integrations/edi_samples/ORDERS_ORD-88240.edi"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code_prefix | SPR |
| category | SPARES |
| buyer | KMENSAH |
| default_uom | SET |
| inventory_sites | WH-MAN-STR, WH-LDS-STR |
| source_master | ITEM_MASTER_2026-10-26 |

The SPR item family designates replacement spare parts and model-specific service kits across Northbridge Cycles' product lines [^r1]. Standard purchasing and master attributes are assigned under buyer [[user-kmensah|Kwame Mensah (KMENSAH)]], with standard costing and lead times tracked in [[data-item-master|ITEM_MASTER_2026-10-26]] [^r1]. Inventory balances are held across the Manchester and Leeds warehouses, fulfilling ongoing workshop demand and external customer orders [^r2][^r32].

| Field | Value |
|---|---|
| Code prefix | SPR |
| Category | SPARES [^r1] |
| Default UOM | SET [^r1] |
| Buyer | [[user-kmensah|KMENSAH]] [^r1] |
| Primary Storage | WH-MAN-STR, WH-LDS-STR [^r2] |

## Master data and procurement

Items in this family represent complete replacement assemblies and service kits, such as mudguard and component repair kits [^r1]. In [[data-item-master|ITEM_MASTER_2026-10-26]], item SPR-ANC-07 is registered as an Ancoats city mudguard service kit within the SPARES category [^r1]. It carries a unit of measure of SET, a standard cost of 55.23, a reorder level of 0, a procurement lead time of 21 days, and is assigned to buyer [[user-kmensah|KMENSAH]] [^r1].

## Stock on hand

Inventory positions as of 26 October 2026 09:00 are recorded in [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]] across Manchester Stores (WH-MAN-STR) and Leeds Stores (WH-LDS-STR):

### Ancoats kits (SPR-ANC-*)
* SPR-ANC-01: 71 units on hand at WH-MAN-STR and 10 units at WH-LDS-STR [^r2].
* SPR-ANC-02: 66 units on hand and 50 on order at WH-MAN-STR [^r3].
* SPR-ANC-03: 10 units on hand at WH-MAN-STR [^r4].
* SPR-ANC-04: 28 units on hand and 50 on order at WH-MAN-STR [^r4].
* SPR-ANC-05: 141 units on hand and 50 on order at WH-MAN-STR [^r4].
* SPR-ANC-06: 6 units on hand at WH-MAN-STR and 6 units at WH-LDS-STR [^r5].
* SPR-ANC-07: 22 units on hand at WH-MAN-STR [^r6].
* SPR-ANC-08: 2 units on hand at WH-MAN-STR [^r6].
* SPR-ANC-09: 9 units on hand at WH-MAN-STR and 1 unit at WH-LDS-STR [^r7].
* SPR-ANC-10: 168 units on hand at WH-MAN-STR [^r8].
* SPR-ANC-11: 155 units on hand at WH-MAN-STR [^r8].
* SPR-ANC-12: 24 units on hand at WH-MAN-STR [^r8].
* SPR-ANC-13: 191 units on hand and 50 on order at WH-MAN-STR [^r9].
* SPR-ANC-14: 32 units on hand at WH-MAN-STR [^r9].
* SPR-ANC-15: 37 units on hand at WH-MAN-STR and 5 units at WH-LDS-STR [^r10].
* SPR-ANC-19: 24 units on hand and 50 on order at WH-MAN-STR [^r11].
* SPR-ANC-28: 184 units on hand, 0 allocated, and 50 on order at WH-MAN-STR [^r12].

### Deansgate kits (SPR-DEA-*)
* SPR-DEA-07: 7 units on hand at WH-MAN-STR and 9 units at WH-LDS-STR, with 0 allocated and 0 on order at both sites [^r13].
* SPR-DEA-30: 128 units on hand, 0 allocated, and 50 on order at WH-MAN-STR [^r14].

### Medlock kits (SPR-MED-*)
* SPR-MED-03: 21 units on hand at WH-MAN-STR and 2 units at WH-LDS-STR, with 0 on order at both locations [^r15].
* SPR-MED-10: 7 units on hand and 10 on order at WH-MAN-STR, and 4 units on hand at WH-LDS-STR [^r16].
* SPR-MED-15: 32 units on hand and 10 on order at WH-MAN-STR [^r17].
* SPR-MED-17: 23 units on hand and 10 on order at WH-MAN-STR [^r18].

### Irk kits (SPR-IRK-*)
* SPR-IRK-07: 32 units on hand and 20 on order at WH-MAN-STR [^r19].
* SPR-IRK-13: 9 units on hand and 10 on order at WH-MAN-STR [^r20].
* SPR-IRK-20: 19 units on hand and 10 on order at WH-MAN-STR [^r21].
* SPR-IRK-22: 38 units on hand, 0 allocated, and 10 on order at WH-MAN-STR; 3 units on hand, 0 allocated, and 0 on order at WH-LDS-STR [^r22].
* SPR-IRK-23: 56 units on hand, 0 allocated, and 50 on order at WH-MAN-STR [^r23].
* SPR-IRK-26: 130 units on hand, 0 allocated, and 50 on order at WH-MAN-STR [^r24].
* SPR-IRK-28: 190 units on hand, 0 allocated, and 50 on order at WH-MAN-STR [^r25].

### Tame kits (SPR-TAM-*)
* SPR-TAM-15: 124 units on hand, 0 allocated, and 0 on order at WH-MAN-STR [^r26].
* SPR-TAM-23: 104 units on hand, 0 allocated, and 50 on order at WH-MAN-STR; 33 units on hand, 0 allocated, and 0 on order at WH-LDS-STR [^r27].
* SPR-TAM-25: 197 units on hand, 0 allocated, and 0 on order at WH-MAN-STR; 28 units on hand, 0 allocated, and 0 on order at WH-LDS-STR [^r28].

### Rochdale kits (SPR-ROC-*)
* SPR-ROC-04: 177 units on hand, 0 allocated, and 0 on order at WH-MAN-STR [^r29].
* SPR-ROC-08: 29 units on hand at WH-MAN-STR [^r30].
* SPR-ROC-09: 18 units across WH-MAN-STR and WH-LDS-STR, with 20 on order [^r30].
* SPR-ROC-10: 140 units across both WH-MAN-STR and WH-LDS-STR [^r30].

### General spare kits (SPR-SPR-*)
* SPR-SPR-05: 156 units on hand and 50 on order at WH-MAN-STR [^r31].
* SPR-SPR-06: 154 units on hand at WH-MAN-STR [^r31].
* SPR-SPR-07: 170 units on hand at WH-MAN-STR [^r31].

## Customer orders

Customer EDI transmissions reference line items from this family for replacement fulfilment:
* EDI order 4500091877 requests line 2 item SPR-ANC-07 with an order quantity of 5 units [^r32].
* Customer C01012 ordered 5 units of spare part SPR-ANC-07 on order ORD-88213 [^r33].
* Inbound EDI order ORD-88240 orders a quantity of 5 units of spare part SPR-ANC-07 [^r34].

## See also

* [[data-item-master|ITEM_MASTER_2026-10-26]]
* [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]
* [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]]
* [[services-pur-stk|PUR stk services]]
* [[user-kmensah|Kwame Mensah (KMENSAH)]]
* [[items-fg|FG-* items]]

## References

[^r1]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Items, row SPR-ANC-07, first 5 rows, then the 10 rows whose key appears in the narrative documents
[^r2]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-ANC-01@WH-MAN-STR, SHEET Stock
[^r32]: 12_integrations/edi_samples/ORDERS_4500091877.edi, whole file
[^r3]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-ANC-02@WH-MAN-STR, SHEET Stock
[^r4]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-ANC-05@WH-MAN-STR, SHEET Stock
[^r5]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-ANC-06@WH-MAN-STR, SHEET Stock
[^r6]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-ANC-07@WH-MAN-STR, SHEET Stock
[^r7]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-ANC-09@WH-MAN-STR, SHEET Stock
[^r8]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-ANC-10@WH-MAN-STR, SHEET Stock
[^r9]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-ANC-13@WH-MAN-STR, SHEET Stock
[^r10]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-ANC-15@WH-MAN-STR, SHEET Stock
[^r11]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-ANC-19@WH-MAN-STR
[^r12]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-ANC-28@WH-MAN-STR
[^r13]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-DEA-07@WH-MAN-STR
[^r14]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-DEA-30@WH-MAN-STR
[^r15]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-MED-03@WH-MAN-STR
[^r16]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-MED-10@WH-MAN-STR, SHEET Stock
[^r17]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-MED-15@WH-MAN-STR, SHEET Stock
[^r18]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-MED-17@WH-MAN-STR, SHEET Stock
[^r19]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-IRK-07@WH-MAN-STR, SHEET Stock
[^r20]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-IRK-13@WH-MAN-STR, SHEET Stock
[^r21]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-IRK-20@WH-MAN-STR, SHEET Stock
[^r22]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-IRK-22@WH-MAN-STR, Stock
[^r23]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-IRK-23@WH-MAN-STR, Stock
[^r24]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-IRK-26@WH-MAN-STR, Stock
[^r25]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-IRK-28@WH-MAN-STR, Stock
[^r26]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-TAM-15@WH-MAN-STR, Stock
[^r27]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-TAM-23@WH-MAN-STR, Stock
[^r28]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-TAM-25@WH-MAN-STR, Stock
[^r29]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-ROC-04@WH-MAN-STR, Stock
[^r30]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-ROC-08@WH-MAN-STR
[^r31]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row SPR-SPR-05@WH-MAN-STR
[^r33]: 12_integrations/edi_samples/ORDERS_ORD-88213.edi, ORDERS_ORD-88213.edi
[^r34]: 12_integrations/edi_samples/ORDERS_ORD-88240.edi, whole file
