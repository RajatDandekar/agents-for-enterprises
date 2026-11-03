---
title: "CHG-* items"
type: "item-family"
slug: "items-chg"
summary: "Battery charger components (CHG-*) across 2A to 6A ratings used across bike production lines, with lithium-cell safety controls and purchasing details."
audience: "staff"
status: "mixed"
sources: ["05_master_data/BOM_master_2026.xlsx", "05_master_data/ITEM_MASTER_2026-10-26.xlsx", "05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx", "05_master_data/Stock_on_hand_2026-10-26_0900.xlsx", "05_master_data/old/item_master_export_2025-03.csv", "09_email_archive/2026/2026-09-02_Approving orders for lithium-cell parts - CERT OK in the approval comment.eml", "06_transactions/PO_extract_2026-01_to_2026-10.xlsx", "06_transactions/reports/Item master listing 2026-10 (printed).pdf", "06_transactions/reports/PO register 2026-04 (printed).pdf", "06_transactions/reports/PO register 2026-07 (printed).pdf", "06_transactions/stock_ledger_2026-Q3.csv", "99_scans/2023_stock_count_sheet_MAN_aisle_B.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | CHG-* |
| category | COMPONENTS |
| lead_buyer | [[user-lmoreno|LMORENO]] |
| hs_code | 8504.40 |
| cell_safety | 1 |
| standard_cost_chg_4a_01 | £96.00 |

The `CHG-*` family comprises battery charger units spanning 2 A, 3 A, 4 A, 5 A, and 6 A configurations specified as line 40 components in [[data-bom-master|BOM_master_2026]] bills of materials [^r1][^r24]. As of 26 October 2026, the high-volume variant is CHG-4A-01, managed by buyer [[user-lmoreno|LMORENO]] with standard cost £96.00 and classified under HS code 8504.40 [^r9]. Chargers carrying the lithium-cell flag (`cell_safety = 1` or `LC = 1`) require mandatory compliance annotations during procurement approval [^r9][^r24][^r45].

| Item code | Description | Legacy code | Status | Lead days | ROL | ADI | Cell safety |
|---|---|---|---|---|---|---|---|
| CHG-2A-01 | Charger, 2 A | — | Active | — | — | — | 1 [^r24] |
| CHG-2A-02 | Charger, 2 A | — | Active | — | — | — | 1 [^r24] |
| CHG-3A-01 | Charger, 3 A | — | Active | — | — | — | 1 [^r24] |
| CHG-3A-02 | Charger, 3 A | — | Active | — | — | — | 1 [^r24] |
| CHG-4A-01 | Charger, 4 A | NB104427 | Active [^r22] | 21 [^r9] | 15,000 [^r9] | 6,000 [^r9] | 1 [^r9] |
| CHG-4A-02 | Charger, 4 A | — | Active | — | — | — | 1 [^r24] |
| CHG-4A-UK | Charger, 4 A (UK) | NB104756 | Inactive [^r23] | — | 0 [^r23] | 0 [^r23] | — |
| CHG-5A-01 | Charger, 5 A | — | Active | — | — | — | 1 [^r24] |
| CHG-5A-02 | Charger, 5 A | — | Active | — | — | — | 1 [^r24] |
| CHG-6A-01 | Charger, 6 A | — | Active | — | — | — | 1 [^r24] |
| CHG-6A-02 | Charger, 6 A | — | Active | — | — | — | 1 [^r24] |

## Bill of materials allocation

Component CHG-4A-01 is assigned at BOM line 40 with a standard quantity of 1 NOS across multiple finished good lines in [[data-bom-master|BOM_master_2026]] [^r1][^r2]:
* **Ancoats models**: FG-ANC-S-BLK, FG-ANC-S-GRN, FG-ANC-S-SLV, FG-ANC-S-RED, FG-ANC-S-BLU, FG-ANC-M-BLK, FG-ANC-M-GRN, and FG-ANC-L-SLV (0.50% scrap) [^r1][^r2].
* **Deansgate models**: FG-DEA-S-RED (1% scrap), FG-DEA-M-BLK (0.50% scrap), FG-DEA-M-SLV, FG-DEA-M-RED, FG-DEA-M-BLU, FG-DEA-L-BLK, FG-DEA-L-GRN, and FG-DEA-L-SLV [^r2][^r3][^r4].
* **Medlock, Irk, and Tame models**: FG-MED-S-BLK, Irk variants (such as FG-IRK-S-BLK), and Tame variants (including FG-TAM-S-RED and FG-TAM-M-BLK), with scrap allowances ranging between 0% and 2% [^r4][^r5][^r6].
* **Rochdale and Sprint models**: FG-ROC variants (including FG-ROC-S-BLK and FG-ROC-L-RED) and FG-SPR variants (including FG-SPR-L-RED, FG-SPR-L-BLU, and all FG-SPR-XL colour options) [^r6][^r7][^r8].

## Procurement and rate contracts

Supplier CC-SAL-0031 holds a 2026–27 rate contract recorded in [[data-rate-contracts|Rate Contracts 2025-26 and 2026-27]] for CHG-4A-01 at £96.00 per unit, valid from 2026-04-01 through 2027-03-31 [^r11].

Purchase orders placed in 2026 recorded in [[data-po-extract-2026|PO_extract_2026-01_to_2026-10]] include:
* **PO/2026/00333** (2026-03-13): 2,500 units of CHG-3A-02 from SCC-BOL-0183 at £115.82 for cost centre [[cc-prd-02|PRD-02]], delivered to WH-MAN-STR [^r15].
* **PO/2026/00539** (2026-04-23): 270,000 units of CHG-4A-01 from CC-SAL-0031 by [[user-kmensah|KMENSAH]] at £96.00 per unit (£31,104,000.00 gross including VAT20-UK) for cost centre [[cc-prd-04|PRD-04]] [^r16][^r25].
* **PO/2026/00562** (2026-04-28): 450 units of CHG-5A-01 from SCC-BOL-0183 by [[user-kmensah|KMENSAH]] at £71.57 per unit (£38,647.80 gross) for cost centre [[cc-prd-05|PRD-05]] [^r26].
* **PO/2026/00937** (2026-07-13): 200 units of CHG-2A-01 from SCC-BOL-0183 by [[user-eclarke|ECLARKE]] at £74.60 per unit (£17,904.00 gross) for cost centre [[cc-prd-03|PRD-03]] [^r17].
* **PO/2026/01005** (2026-07): 1,200 units of CHG-6A-01 from KPS-BRN-0177 at £90.85 per unit (£109,020.00 basic) [^r18][^r27].
* **PO/2026/01014** (2026-07): 180,000 units of CHG-4A-01 from CC-SAL-0031 at £96.00 per unit (£17,280,000.00 basic, £20,736,000.00 gross) [^r19][^r28].
* **PO/2026/01094** (2026-08-31): 200 units of CHG-5A-01 from KPS-BRN-0177 at £72.19 per unit for delivery to WH-MAN-STR [^r20].
* **PO/2026/01179** (2026-10-23): 4,000 units of CHG-4A-01 from CC-SAL-0031 by [[user-eclarke|ECLARKE]] at £96.00 per unit (£460,800.00 gross) for cost centre [[cc-prd-07|PRD-07]] [^r21].

Per procedural instructions issued on 2 September 2026, purchase orders for `CHG-` items flagged with lithium-cell requirements cannot be approved without entering 'CERT OK' and the certificate's document reference in the approval comment [^r45].

## Stock and warehouse positions

According to [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]], stock balances as of 26 October 2026 at 09:00 GMT are [^r12][^r13][^r14]:
* **CHG-2A-01**: 491 on hand, 8 allocated at WH-MAN-STR [^r13].
* **CHG-2A-02**: 454 on hand, 212 allocated at WH-MAN-STR [^r13].
* **CHG-3A-01**: 275 on hand, 36 allocated at WH-MAN-STR [^r13].
* **CHG-3A-02**: 5,370 on hand, 300 allocated, 2,500 on order at WH-MAN-STR [^r13].
* **CHG-4A-01**: 52,000 on hand at WH-MAN-STR [^r12]. Historically, 980 units were recorded in bin B-03-02 on 25 March 2023 [^r44].
* **CHG-4A-02**: 13,054 on hand, 357 allocated, 9,000 on order at WH-MAN-STR [^r12].
* **CHG-5A-01**: 95 on hand, 5 allocated, 100 on order at WH-MAN-STR [^r14].
* **CHG-5A-02**: 13 on hand at WH-MAN-STR, 8 on hand at WH-LDS-STR [^r14].
* **CHG-6A-01**: 2,803 on hand, 137 allocated at WH-MAN-STR [^r14].
* **CHG-6A-02**: 33 on hand, 1 allocated at WH-MAN-STR, 1 on hand at WH-LDS-STR [^r14].

During Q3 2026, stock ledgers recorded heavy consumption across production work orders: CHG-2A-02 opened at 4,165 on 1 July 2026 and closed at 454 on 30 September 2026 [^r29][^r30][^r31]; CHG-3A-02 opened at 17,224 and declined to 5,370 [^r32][^r34]; CHG-4A-01 opened at 189,113, received 180,000 on GRN/2026/29765 on 10 August 2026, and closed at 52,000 [^r33][^r35][^r36][^r37]; CHG-4A-02 opened at 57,713 and closed at 13,054 [^r38][^r39]; and CHG-6A-01 opened at 6,754 and closed at 2,803 [^r40][^r41][^r42][^r43].

## Versions and conflicts

* **Active versus inactive charger items**: In [[data-item-master|ITEM_MASTER_2026-10-26]], CHG-4A-01 is active with ROL 15,000, ADI 6,000, and legacy code NB10442, whereas CHG-4A-UK (legacy code NB104756) is inactive with ROL 0 and ADI 0 (`superseded`) [^r9][^r10][^r22][^r23].
* **Historical item master exports**: The March 2025 item master export listed CHG-4A-01 under legacy code NB104427 with identical active and safety flags, prior to the live October 2026 master dataset (`superseded`) [^r46].

## See also

* [[data-item-master|ITEM_MASTER_2026-10-26]]
* [[data-bom-master|BOM_master_2026]]
* [[data-rate-contracts|Rate Contracts 2025-26 and 2026-27]]
* [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]
* [[data-po-extract-2026|PO_extract_2026-01_to_2026-10]]
* [[items-bat|BAT-* items]]
* [[user-lmoreno|Luis Moreno (LMORENO)]]
* [[user-eclarke|Emma Clarke (ECLARKE)]]
* [[user-kmensah|Kwame Mensah (KMENSAH)]]

## References

[^r1]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-S-BLK, SHEET BOM
[^r24]: 06_transactions/reports/Item master listing 2026-10 (printed).pdf, row CHG-2A-01, p. 1, LEDGERLINE ERP 7.2 REPORT INV-R001 ITEM MASTER LISTING
[^r9]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Items, row CHG-4A-01, first 5 rows, then the 10 rows whose key appears in the narrative documents
[^r45]: 09_email_archive/2026/2026-09-02_Approving orders for lithium-cell parts - CERT OK in the approval comment.eml, body
[^r22]: 06_transactions/reports/Item master listing 2026-10 (printed).pdf, row CHG-4A-01, p. 1, LEDGERLINE ERP 7.2 REPORT INV-R001 ITEM MASTER LISTING
[^r23]: 06_transactions/reports/Item master listing 2026-10 (printed).pdf, row CHG-4A-UK, p. 2, LEDGERLINE ERP 7.2 REPORT INV-R001 ITEM MASTER LISTING
[^r2]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-L-SLV
[^r3]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-DEA-M-BLK
[^r4]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-DEA-M-SLV
[^r5]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-IRK-S-BLK, SHEET BOM
[^r6]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row 3235, SHEET BOM
[^r7]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ROC-L-RED, SHEET BOM
[^r8]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row 5059, SHEET BOM
[^r11]: 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx, sheet 2026-27, row CC-SAL-0031/CHG-4A-01/2026-04-01, SHEET 2026-27
[^r15]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-03, row PO/2026/00333, PURCHASE ORDERS CREATED 2026-03 (po_hdr + po_line)
[^r16]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-04, row PO/2026/00539, SHEET 2026-04
[^r25]: 06_transactions/reports/PO register 2026-04 (printed).pdf, row PO/2026/00539, p. 3, PUR-R010 PURCHASE ORDER REGISTER
[^r26]: 06_transactions/reports/PO register 2026-04 (printed).pdf, row PO/2026/00562, p. 4, PUR-R010 PURCHASE ORDER REGISTER
[^r17]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-07, row PO/2026/00937, SHEET 2026-07
[^r18]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-07, row PO/2026/01005, SHEET 2026-07
[^r27]: 06_transactions/reports/PO register 2026-07 (printed).pdf, row PO/2026/01005, p. 4
[^r19]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-07, row PO/2026/01014, SHEET 2026-07
[^r28]: 06_transactions/reports/PO register 2026-07 (printed).pdf, row PO/2026/01014, p. 4
[^r20]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-08, row PO/2026/01094, SHEET 2026-08
[^r21]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-10, row PO/2026/01179, SHEET 2026-10
[^r12]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CHG-4A-01@WH-MAN-STR, SHEET Stock
[^r13]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CHG-3A-02@WH-MAN-STR, SHEET Stock
[^r14]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row CHG-5A-01@WH-MAN-STR, SHEET Stock
[^r44]: 99_scans/2023_stock_count_sheet_MAN_aisle_B.pdf, p. 1, ANNUAL STOCK COUNT 2023 MANCHESTER MAIN STORES
[^r29]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2743, SHEET csv
[^r30]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2762, SHEET csv
[^r31]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2829, SHEET csv
[^r32]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2881, SHEET csv
[^r34]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2026-09-30, SHEET csv
[^r33]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2026-07-01, SHEET csv
[^r35]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2026-08-10
[^r36]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 2026-09-18
[^r37]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3013
[^r38]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3014
[^r39]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3103, SHEET csv
[^r40]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3104, SHEET csv
[^r41]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3121, SHEET csv
[^r42]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3122, SHEET csv
[^r43]: 06_transactions/stock_ledger_2026-Q3.csv, sheet csv, row 3190
[^r10]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Legacy code map, row NB104427, SHEET Legacy code map
[^r46]: 05_master_data/old/item_master_export_2025-03.csv, sheet csv, row CHG-4A-01, SHEET csv
