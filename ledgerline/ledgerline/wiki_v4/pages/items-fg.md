---
title: "FG-* items"
type: "item-family"
slug: "items-fg"
summary: "Finished goods e-bikes across model series, structured under standard single-level bills of materials and sales channels."
audience: "staff"
status: "current"
sources: ["05_master_data/BOM_master_2026.xlsx", "05_master_data/ITEM_MASTER_2026-10-26.xlsx", "05_master_data/Price list PL-UK-RTL 2026.xlsx", "05_master_data/Stock_on_hand_2026-10-26_0900.xlsx", "12_integrations/edi_samples/ORDERS_4500091877.edi", "12_integrations/edi_samples/ORDERS_ORD-88213.edi", "12_integrations/edi_samples/ORDERS_ORD-88240.edi", "06_transactions/reports/Bill of materials listing 2026 (printed).pdf", "06_transactions/sales_orders_2026.csv"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code prefix | FG- |
| Description | Finished goods parent e-bikes |
| HS code | 8711.60 |
| Standard BOM lines | 38 |
| Planner / Buyer | LMORENO |

The `FG-*` item family comprises Northbridge Cycles' assembled finished good parent e-bikes, spanning model ranges such as Ancoats (`FG-ANC-*`), Deansgate (`FG-DEA-*`), Medlock (`FG-MED-*`), Irk (`FG-IRK-*`), Tame (`FG-TAM-*`), Sprinter (`FG-SPR-*`), and Rochdale (`FG-ROC-*`)[^r9][^r10][^r11][^r27]. Parent bikes are structured across standard frame sizes S, M, L, and XL, each governed by a standardized 38-line single-level bill of materials detailing mechanical sub-assemblies, electric drive components, packaging, and regulatory labeling[^r10][^r11][^r25]. At 26 October 2026, finished bikes are managed in the item master under buyer [[user-lmoreno|LMORENO]], priced for retail distribution under price list PL-UK-RTL, and fulfilled through customer EDI channels[^r17][^r19][^r20][^r22][^r23].

## Item coding and models

Finished goods follow a standardized code structure identifying series, frame size, and finish color, with 140 distinct codes recorded in the 2026 sales orders register including models such as FG-MED-S-SLV, FG-ROC-M-RED, FG-ANC-L-GRN, FG-SPR-M-SLV, and FG-IRK-M-BLU[^r27]. Under the Ledgerline 6 migration, legacy item numbers mapped directly to Ledgerline 7 codes, such as legacy NB131730 mapping to `FG-ANC-M-BLK` for the Ancoats city e-bike in medium black[^r18]. In the [[data-item-master|ITEM_MASTER_2026-10-26]], `FG-ANC-M-BLK` carries HS code 8711.60, a standard cost of £1,481.28, a reorder level of 200, an average daily issue of 20, and a lead time of 42 days[^r17].

## Bill of materials structure

Finished goods parent bills of materials in [[data-bom-master|BOM_master_2026]] specify 38 distinct lines per parent e-bike, covering components, packaging, and pallets[^r10][^r25]. Typical single-level BOM component assignments across lines include:

* **Line 20 (Battery):** Standardized on 1 NOS of [[items-bat|BAT-500]] across models such as the Ancoats series (`FG-ANC-S-BLK`, `FG-ANC-S-GRN`, `FG-ANC-S-SLV`, `FG-ANC-S-RED`, `FG-ANC-S-BLU`, `FG-ANC-M-GRN`, `FG-ANC-M-SLV`, `FG-ANC-M-BLU`, `FG-ANC-L-GRN`, `FG-ANC-XL-BLK`) and Sprinter models (`FG-SPR-S-BLK`, `FG-SPR-L-GRN`), with scrap allowances ranging between 0% and 2%[^r1][^r3][^r4][^r5][^r6][^r12][^r13].
* **Line 40 (Charger):** Standardized on 1 NOS of [[items-chg|CHG-4A-01]] across Ancoats, Deansgate (`FG-DEA-S-BLK`, `FG-DEA-M-GRN`, `FG-DEA-M-SLV`), Medlock (`FG-MED-*`), Tame (`FG-TAM-*`), Rochdale (`FG-ROC-*`), and Sprinter lines, with scrap allowances between 0% and 2%[^r2][^r3][^r5][^r6][^r7][^r8][^r9][^r11][^r12][^r13].
* **Line 50 (Motor & Controller):** Incorporates drive units such as motor [[items-mtr|MTR-HUB-250]] on `FG-ANC-M-BLK` and controller [[items-ctl|CTL-04]] on `FG-ANC-S-BLK` with a 2% scrap allowance[^r1][^r2].
* **Line 70–110 (Running gear & Brakes):** Single-level BOM structures specify running gear such as [[items-frm|FRM-ANC-M-BLK]] and 72 spokes of [[items-spk|SPK-14G-266]] on `FG-ANC-M-BLK`, and 2 NOS of [[items-brk|BRK-PAD-01]] at line 110 with 0% scrap on `FG-ANC-M-BLU`[^r2][^r4].
* **Line 210 (Accessories):** Allocates 1 NOS of bell [[items-bel|BEL-STD-01]] on models including `FG-DEA-S-BLK` (0.50% scrap), `FG-DEA-M-GRN` (0% scrap), `FG-SPR-L-GRN` (1% scrap), `FG-SPR-XL-BLK`, `FG-TAM-*`, and `FG-ROC-*`[^r7][^r8][^r11][^r13][^r14].
* **Lines 340–380 (Mounts, packaging, and labels):** Battery mount [[items-mnt|MNT-FRM-01]] is specified at line 340 on `FG-TAM-*`, `FG-ROC-*`, and `FG-SPR-XL-BLK` (while `FG-ANC-L-BLU` uses rear rack battery mount MNT-RCK-03 alongside cargo rack ACC-RCC and basket ACC-BSK)[^r11][^r14][^r26]. Outer packaging specifies bike carton [[items-box|BOX-BIKE-01]] at line 350 for `FG-TAM-*`, `FG-ROC-*`, `FG-SPR-S-BLK`, and `FG-SPR-XL-RED` (or BOX-BAT-01 for battery packaging on `FG-ANC-M-BLK`)[^r2][^r11][^r12][^r15]. UN classification labels [[items-pkg|PKG-LBL-UN]] occupy lines 360 to 380, requiring 7 NOS on line 360 and 3 NOS on line 370 with 0.50% scrap on `FG-SPR-XL-SLV`[^r11][^r16].

## Inventory, sales, and pricing

Retail pricing on price list [[data-price-list-pl-uk-rtl|PL-UK-RTL]] (effective 2026-04-01) lists `FG-ANC-S-BLK` at £1,614.05 excluding VAT and `FG-ANC-M-BLK` at £2,370.05 excluding VAT[^r19][^r20]. As of 26 October 2026 at 09:00, finished good `FG-ANC-M-BLK` at warehouse WH-MAN-FG in [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]] records 799 units on hand, 0 allocated, and 0 on order[^r21]. Inbound EDI sales orders—including order 4500091877, customer C01012 order ORD-88213, and order ORD-88240—order quantities of 2 units of `FG-ANC-M-BLK` at net unit contract prices of £1,499.00[^r22][^r23][^r24].

## See also

* [[data-item-master|ITEM_MASTER_2026-10-26]]
* [[data-bom-master|BOM_master_2026]]
* [[data-price-list-pl-uk-rtl|Price list PL-UK-RTL 2026]]
* [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]
* [[items-bat|BAT-* items]]
* [[items-chg|CHG-* items]]
* [[items-mtr|MTR-* items]]
* [[items-ctl|CTL-* items]]
* [[items-frm|FRM-* items]]
* [[items-bel|BEL-* items]]
* [[items-mnt|MNT-* items]]
* [[items-box|BOX-* items]]
* [[items-pkg|PKG-* items]]
* [[items-brk|BRK-* items]]
* [[items-spk|SPK-* items]]
* [[user-lmoreno|Luis Moreno (LMORENO)]]

## References

[^r9]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-DEA-M-SLV
[^r10]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, SHEET BOM
[^r11]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row 3822, SHEET BOM
[^r27]: 06_transactions/sales_orders_2026.csv, sheet csv, SHEET csv
[^r25]: 06_transactions/reports/Bill of materials listing 2026 (printed).pdf, row FG-ANC-L-BLK, p. 1, PARENT FG-ANC-L-BLK E-bike, Ancoats city, size L, black
[^r17]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Items, row FG-ANC-M-BLK, first 5 rows, then the 10 rows whose key appears in the narrative documents
[^r19]: 05_master_data/Price list PL-UK-RTL 2026.xlsx, sheet PL-UK-RTL, row FG-ANC-S-BLK, SHEET PL-UK-RTL
[^r20]: 05_master_data/Price list PL-UK-RTL 2026.xlsx, sheet PL-UK-RTL, row FG-ANC-M-BLK, SHEET PL-UK-RTL
[^r22]: 12_integrations/edi_samples/ORDERS_4500091877.edi, whole file
[^r23]: 12_integrations/edi_samples/ORDERS_ORD-88213.edi, ORDERS_ORD-88213.edi
[^r18]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Legacy code map, row NB131730, SHEET Legacy code map
[^r1]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-S-BLK, SHEET BOM
[^r3]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-S-GRN, SHEET BOM
[^r4]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-M-BLU
[^r5]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-L-GRN
[^r6]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-XL-BLK
[^r12]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-SPR-S-BLK, SHEET BOM
[^r13]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-SPR-L-GRN, SHEET BOM
[^r2]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-M-BLK, SHEET BOM
[^r7]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-DEA-S-BLK
[^r8]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-DEA-M-GRN
[^r14]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row 5165, SHEET BOM
[^r26]: 06_transactions/reports/Bill of materials listing 2026 (printed).pdf, row FG-ANC-L-BLU, p. 2, PARENT FG-ANC-L-BLU E-bike, Ancoats city, size L, canal blue
[^r15]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row 5280, SHEET BOM
[^r16]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row 5243, SHEET BOM
[^r21]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row FG-ANC-M-BLK@WH-MAN-FG, SHEET Stock
[^r24]: 12_integrations/edi_samples/ORDERS_ORD-88240.edi, whole file
