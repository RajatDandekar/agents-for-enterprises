---
title: "MTR-* items"
type: "item-family"
slug: "items-mtr"
summary: "Electric bike drive motors across hub, rear-hub, and mid-drive configurations in 250W, 350W, and 500W ratings used across assembly bills of materials."
audience: "staff"
status: "current"
sources: ["05_master_data/BOM_master_2026.xlsx", "05_master_data/Stock_on_hand_2026-10-26_0900.xlsx", "09_email_archive/2026/2026-09-02_Approving orders for lithium-cell parts - CERT OK in the approval comment.eml", "06_transactions/PO_extract_2026-01_to_2026-10.xlsx", "06_transactions/reports/Item master listing 2026-10 (printed).pdf", "06_transactions/reports/PO register 2026-07 (printed).pdf", "06_transactions/reports/Stock status listing 2026-10-26 (printed).pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| family | MTR |
| description | Electric bike motors (Hub, Rear Hub, Mid-Drive) |
| item_type | RAW |
| lifecycle_status | LC 1 (Active) |
| power_ratings | 250 W, 350 W, 500 W |
| primary_stores | WH-MAN-STR, WH-LDS-STR |

The `MTR-*` item family covers electric drive motors used in Northbridge Cycles' e-bike manufacturing lines, spanning front hub (`MTR-HUB-*`), rear hub (`MTR-RHB-*`), and mid-drive (`MTR-MID-*`) units across 250 W, 350 W, and 500 W power ratings.[^r1][^r13] All items are active raw materials classified as RAW with lifecycle code LC 1 in [[data-item-master|the item master]].[^r12][^r13] Orders for any motor items carrying the lithium-cell flag require compliance text and documentation references recorded in the purchase order approval comment prior to release.[^r18]

| Field | Value |
|---|---|
| Family code | MTR |
| Classification | RAW |
| Lifecycle code | LC 1 (Active) |
| Configurations | Front hub (HUB), Rear hub (RHB), Mid-drive (MID) |
| Power variants | 250 W, 350 W, 500 W |
| Primary stocking locations | WH-MAN-STR, WH-LDS-STR |

## Item definitions and bill of materials usage

The motor catalogue comprises nine core configurations across three power tiers: MTR-HUB-250, MTR-RHB-250, MTR-MID-250, MTR-HUB-350, MTR-RHB-350, MTR-MID-350, MTR-HUB-500, MTR-RHB-500, and MTR-MID-500.[^r13] Hub motor MTR-HUB-250 maps to legacy code NB104405, carrying an inventory reorder level (ROL) of 15,000 and an average daily issue (ADI) of 6,000.[^r12] 

In [[data-bom-master|BOM_master_2026]], MTR-HUB-250 is incorporated at line 30 of [[items-fg|finished e-bike]] bills of materials including FG-ANC-S-BLK and FG-ANC-M-BLK at a standard quantity of 1 NOS.[^r1]

## Stock on hand

Stock levels extracted from [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]] as of 26 October 2026 show motor inventory distributed across Manchester (WH-MAN-STR) and Leeds (WH-LDS-STR):

* **250 W motors:** WH-MAN-STR holds 48,000 units of MTR-HUB-250 on hand with zero allocated and zero on order against an ROL of 15,000 and ADI of 6,000.[^r2][^r16] WH-MAN-STR also stores 469 units on hand (13 allocated) of MTR-RHB-250, and 2,706 units on hand (134 allocated, 800 on order) of MTR-MID-250.[^r2]
* **350 W motors:** WH-MAN-STR maintains 124 units on hand (12 allocated) of MTR-HUB-350, 1,173 units on hand (192 allocated) of MTR-RHB-350, and 157 units on hand (10 allocated, 50 on order) of MTR-MID-350.[^r3] WH-LDS-STR holds an additional 35 units on hand of MTR-MID-350.[^r3]
* **500 W motors:** WH-MAN-STR holds 3,051 units on hand (89 allocated) of MTR-HUB-500, 1,815 units on hand (429 allocated, 2,500 on order) of MTR-RHB-500, and 10,610 units on hand (378 allocated) of MTR-MID-500 against an ROL of 9,000.[^r4][^r17] WH-LDS-STR holds an additional 6,919 units on hand of MTR-MID-500.[^r4][^r17]

## Procurement and ordering

Motor purchasing is tracked in [[data-po-extract-2026|PO_extract_2026-01_to_2026-10]] and related purchasing registers:

* **HDM-TAI-0162:** On 2026-01-29, order PO/2026/00122 secured 1,600 units of MTR-RHB-350 at £208.59 each (£333,744 basic value).[^r5] On 2026-03-05, PO/2026/00271 placed another 1,600 units of MTR-RHB-350 at £208.59 each (£400,492.80 gross) on advance payment terms, and PO/2026/00294 ordered 800 units of MTR-MID-250 at £217.85 each.[^r8][^r9]
* **Ondina Motores (ODM-POR-0170):** In February 2026, PO/2026/00135 procured 2,500 units of MTR-RHB-500 at £192.31 each (£480,775.00 basic value) for Leeds assembly cost centre [[cc-lds-prd-01|LDS-PRD-01]], while PO/2026/00185 ordered 1,200 units of MTR-HUB-500 at £154.50 each (£222,480.00 gross value) for cost centre [[cc-prd-02|PRD-02]].[^r6][^r7] In March 2026, PO/2026/00323 covered 150 units of MTR-HUB-350 at £226.65 each, and PO/2026/00325 procured 7,500 units of MTR-RHB-500 at £192.31 each.[^r10][^r11] In July 2026, PO/2026/00889 ordered 800 units of MTR-HUB-500 at £161.31 each (£154,857.60 gross, VAT20-RC) for [[cc-prd-03|PRD-03]].[^r14] An additional July order, PO/2026/00999 for 50 units of MTR-MID-350 at £154.03 each (£9,241.80 gross) for [[cc-prd-02|PRD-02]], was subsequently cancelled.[^r15]

For any motor orders flagged for lithium cells, approval rules mandate that approvers include "CERT OK" along with the document reference of the certificate in the approval comment field.[^r18]

## See also

* [[data-item-master|ITEM_MASTER_2026-10-26]]
* [[data-bom-master|BOM_master_2026]]
* [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]
* [[data-po-extract-2026|PO_extract_2026-01_to_2026-10]]
* [[items-bat|BAT-* items]]
* [[items-ctl|CTL-* items]]
* [[items-dsp|DSP-* items]]
* [[items-fg|FG-* items]]
* [[cc-lds-prd-01|LDS-PRD-01 Leeds assembly]]
* [[cc-prd-02|PRD-02 Deansgate step-through line]]
* [[cc-prd-03|PRD-03 Cargo e-bike line]]

## References

[^r1]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-S-BLK, SHEET BOM
[^r13]: 06_transactions/reports/Item master listing 2026-10 (printed).pdf, row MTR-RHB-250, p. 1, LEDGERLINE ERP 7.2 REPORT INV-R001 ITEM MASTER LISTING
[^r12]: 06_transactions/reports/Item master listing 2026-10 (printed).pdf, row MTR-HUB-250, p. 1, LEDGERLINE ERP 7.2 REPORT INV-R001 ITEM MASTER LISTING
[^r18]: 09_email_archive/2026/2026-09-02_Approving orders for lithium-cell parts - CERT OK in the approval comment.eml, body
[^r2]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row MTR-HUB-250@WH-MAN-STR, SHEET Stock
[^r16]: 06_transactions/reports/Stock status listing 2026-10-26 (printed).pdf, row MTR-HUB-250, p. 1, Stock listing
[^r3]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row MTR-RHB-350@WH-MAN-STR, SHEET Stock
[^r4]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row MTR-MID-500@WH-MAN-STR, SHEET Stock
[^r17]: 06_transactions/reports/Stock status listing 2026-10-26 (printed).pdf, row MTR-MID-500, p. 1, Stock listing
[^r5]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-01, row PO/2026/00122, SHEET 2026-01
[^r8]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-03, row PO/2026/00271, SHEET 2026-03
[^r9]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-03, row PO/2026/00294, SHEET 2026-03
[^r6]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-02, row PO/2026/00135, SHEET 2026-02
[^r7]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-02, row PO/2026/00185, SHEET 2026-02
[^r10]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-03, row PO/2026/00323, SHEET 2026-03
[^r11]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-03, row PO/2026/00325, SHEET 2026-03
[^r14]: 06_transactions/reports/PO register 2026-07 (printed).pdf, row PO/2026/00889, p. 1, PUR-R010 PURCHASE ORDER REGISTER
[^r15]: 06_transactions/reports/PO register 2026-07 (printed).pdf, row PO/2026/00999, p. 3, PUR-R010 PURCHASE ORDER REGISTER
