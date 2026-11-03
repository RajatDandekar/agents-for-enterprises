---
title: "MNT-* items"
type: "item-family"
slug: "items-mnt"
summary: "Battery mount components (MNT-*) including down-tube and rear rack brackets contracted under Voltway Cells for finished e-bike frames."
audience: "staff"
status: "mixed"
sources: ["05_master_data/BOM_master_2026.xlsx", "05_master_data/ITEM_MASTER_2026-10-26.xlsx", "05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx", "05_master_data/Stock_on_hand_2026-10-26_0900.xlsx", "05_master_data/old/item_master_export_2025-03.csv", "06_transactions/PO_extract_2026-01_to_2026-10.xlsx", "06_transactions/reports/Item master listing 2026-10 (printed).pdf", "99_scans/2023_stock_count_sheet_MAN_aisle_B.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | MNT |
| Family name | Battery mounts |
| Category | COMPONENTS |
| Buyer | [[user-eclarke|Emma Clarke (ECLARKE)]] |
| Primary supplier | [[sup-vc-ein-0042|Voltway Cells (VC-EIN-0042)]] |
| Base unit | NOS |

The `MNT-*` item family covers battery mounting brackets and assemblies used to secure power packs to bicycle frames and luggage racks [^r7][^r8]. As of 26 October 2026, high-volume production items include the down-tube mount MNT-FRM-01 and rack mount MNT-RCK-02, which support continuous assembly across multiple e-bike lines [^r1][^r4][^r14]. Sourcing is contracted through [[sup-vc-ein-0042|Voltway Cells (VC-EIN-0042)]] with purchasing managed by [[user-eclarke|Emma Clarke (ECLARKE)]] [^r7][^r9].

| Field | Value |
|---|---|
| Item prefix | MNT |
| Category | COMPONENTS |
| Default unit | NOS |
| Primary buyer | [[user-eclarke|ECLARKE]] |
| Contracted supplier | [[sup-vc-ein-0042|Voltway Cells (VC-EIN-0042)]] |

## Items in this family

* **MNT-FRM-01**: Down-tube battery mount (long), mapped from Ledgerline 6 legacy code NB104318 [^r7][^r8]. It carries standard cost £18.50, HS code 8714.99, a lead time of 21 days, reorder level (ROL) 20,000, and average daily issue (ADI) 4,000 [^r7][^r14].
* **MNT-FRM-02**: Battery mount with ROL 400 [^r15].
* **MNT-FRM-03**: Battery mount with ROL 560 [^r15].
* **MNT-RCK-01**: Rack battery mount with ROL 0 and ADI 0 [^r15].
* **MNT-RCK-02**: Active component rack battery mount with ROL 20,000 and ADI 4,000 [^r14].
* **MNT-RCK-03**: Rack battery mount with ROL 4,500 [^r15].

## Bill of materials usage

MNT-FRM-01 is assigned to line 340 of bills of materials at a quantity of 1 NOS across multiple finished good assemblies in [[data-bom-master|BOM_master_2026]] [^r1][^r4]. It is specified on:
* Ancoats variants: FG-ANC-S-GRN (0% scrap), FG-ANC-M-BLK (0% scrap), FG-ANC-M-RED (0% scrap), and FG-ANC-XL-GRN (1% scrap) [^r1][^r2][^r3].
* Deansgate variants: FG-DEA-L-GRN, FG-DEA-L-SLV, FG-DEA-XL-GRN, FG-DEA-XL-SLV, and FG-DEA-XL-BLU [^r4].
* Medlock variants: FG-MED-L-GRN [^r4].
* Irk variants: FG-IRK-M-BLK, FG-IRK-M-GRN, FG-IRK-L-GRN, FG-IRK-L-RED, and FG-IRK-XL-BLU [^r5].
* Tame variants: FG-TAM-S-BLK, FG-TAM-M-RED, and FG-TAM-L-GRN [^r5][^r6].

## Inventory and purchasing

Under active rate contracts valid from 1 April 2026 to 31 March 2027 in [[data-rate-contracts|Rate Contracts 2025-26 and 2026-27]], [[sup-vc-ein-0042|Voltway Cells]] supplies MNT-FRM-01 at £18.50 and MNT-RCK-02 at £15.75 [^r9]. Standard purchase order PO/2026/01152 ordered 25,000 units of MNT-FRM-01 at £18.50 under cost centre [[cc-prd-05|PRD-05]] for delivery to Manchester Main Stores (WH-MAN-STR) [^r13].

As of 09:00 on 26 October 2026 in [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]], stock levels at WH-MAN-STR are:
* MNT-FRM-01: 23,000 on hand [^r11].
* MNT-FRM-02: 863 on hand, 66 allocated, 400 on order [^r11].
* MNT-FRM-03: 104 on hand, 26 allocated [^r11].
* MNT-RCK-01: 24 on hand, 1 allocated [^r12].
* MNT-RCK-02: 31,000 on hand [^r12].
* MNT-RCK-03: 1,956 on hand, 996 allocated [^r12].

In the 2023 annual stock count for Manchester Main Stores aisle B, MNT-FRM-01 was recorded in bin B-02-04 with 2,050 units on 25 March 2023 [^r16].

## Versions and conflicts

* **Rate contract pricing**: In force today (2026-27 contract period from 2026-04-01 to 2027-03-31), rate contract prices from [[sup-vc-ein-0042|Voltway Cells]] are £18.50 for MNT-FRM-01 and £15.75 for MNT-RCK-02 [^r9]. Under the expired 2025-26 contract period, the contracted rates were £17.90 for MNT-FRM-01 and £15.20 for MNT-RCK-02 (`superseded`) [^r10].
* **Item master exports**: The active record in [[data-item-master|ITEM_MASTER_2026-10-26]] lists MNT-FRM-01 with buyer [[user-eclarke|ECLARKE]] and standard cost 18.50 [^r7]. In the superseded March 2025 export (`item_master_export_2025-03.csv`), MNT-FRM-01 had category COMPONENTS, active flag 1, cell_safety flag 0, ROL 20,000, and ADI 4,000 (`superseded`) [^r17].

## See also

* [[data-item-master|ITEM_MASTER_2026-10-26]]
* [[data-bom-master|BOM_master_2026]]
* [[data-rate-contracts|Rate Contracts 2025-26 and 2026-27]]
* [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]
* [[sup-vc-ein-0042|Voltway Cells (VC-EIN-0042)]]
* [[items-bat|BAT-* items]]
* [[items-frm|FRM-* items]]
* [[items-fg|FG-* items]]
* [[user-eclarke|Emma Clarke (ECLARKE)]]
* [[cc-prd-05|PRD-05 City e-bike line, regular production]]

## References

[^r7]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Items, row MNT-FRM-01, first 5 rows, then the 10 rows whose key appears in the narrative documents
[^r8]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Legacy code map, row NB104318, SHEET Legacy code map
[^r1]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-S-GRN, SHEET BOM
[^r4]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-DEA-L-GRN
[^r14]: 06_transactions/reports/Item master listing 2026-10 (printed).pdf, row MNT-FRM-01, p. 1, LEDGERLINE ERP 7.2 REPORT INV-R001 ITEM MASTER LISTING
[^r9]: 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx, sheet 2026-27, row VC-EIN-0042/MNT-FRM-01/2026-04-01, SHEET 2026-27
[^r15]: 06_transactions/reports/Item master listing 2026-10 (printed).pdf, row MNT-FRM-02, p. 2, LEDGERLINE ERP 7.2 REPORT INV-R001 ITEM MASTER LISTING
[^r2]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-M-RED
[^r3]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-XL-GRN
[^r5]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-IRK-M-BLK, SHEET BOM
[^r6]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row 3493, SHEET BOM
[^r13]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-10, row PO/2026/01152, SHEET 2026-10
[^r11]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row MNT-FRM-01@WH-MAN-STR, SHEET Stock
[^r12]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row MNT-RCK-02@WH-MAN-STR, SHEET Stock
[^r16]: 99_scans/2023_stock_count_sheet_MAN_aisle_B.pdf, p. 1, ANNUAL STOCK COUNT 2023 MANCHESTER MAIN STORES
[^r10]: 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx, sheet 2025-26, row VC-EIN-0042/MNT-FRM-01/2025-04-01, SHEET 2025-26
[^r17]: 05_master_data/old/item_master_export_2025-03.csv, sheet csv, row MNT-FRM-01, SHEET csv
