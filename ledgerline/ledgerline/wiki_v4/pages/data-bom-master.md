---
title: "BOM_master_2026"
type: "data-source"
slug: "data-bom-master"
summary: "Master single-level bill of materials workbook defining assembly components, quantities, units, and scrap percentages for 140 finished e-bike parents."
audience: "staff"
status: "current"
sources: ["05_master_data/BOM_master_2026.xlsx", "06_transactions/reports/Bill of materials listing 2026 (printed).pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | BOM_master_2026.xlsx |
| sheet | BOM |
| rows | 5,320 |
| parents | 140 |
| components | 691 |
| system | Ledgerline ERP 7.2 (Report PRD-R002) |
| status | current |

The master single-level bill of materials register defines the component structure, quantities, units of measure, and scrap rates for Northbridge Cycles' finished e-bike assemblies [^r1][^r31]. As of 26 October 2026, the workbook contains 5,320 rows across 140 parent items and 691 distinct components [^r5]. Ledgerline ERP 7.2 mirrors this structure in single-level production report PRD-R002, run on 01-10-2026 at 05:00 [^r31][^r32].

| Attribute | Value |
|---|---|
| File | `05_master_data/BOM_master_2026.xlsx` [^r25] |
| Sheet | `BOM` [^r1] |
| Total rows | 5,320 [^r1] |
| Distinct parents | 140 [^r5] |
| Distinct components | 691 [^r5] |
| ERP report | PRD-R002 (Single-Level Bill of Materials) [^r31] |

## What it holds

The file holds the production recipe for all manufactured [[items-fg|finished e-bikes]] [^r1][^r31]. Each entry links a parent finished good to an engineering line item specifying raw materials, subassemblies, standard hardware, electrical drive components, and packaging [^r2][^r3][^r4].

Representative assembly allocations include:
* Frames and electrical drive: Parent `FG-ANC-S-BLK` allocates frame `FRM-ANC-S-BLK` at line 10 (0.50% scrap), [[items-bat|battery pack]] `BAT-500` at line 20 (0% scrap), [[items-mtr|hub motor]] `MTR-HUB-250` at line 30 (0% scrap), and [[items-chg|charger]] `CHG-4A-01` at line 40 (0% scrap) [^r2]. `FG-ANC-M-BLK` has 38 assembly lines including `FRM-ANC-M-BLK`, `BAT-500`, `MTR-HUB-250`, `CHG-4A-01`, controller `CTL-02`, display `DSP-02`, and down-tube mount `MNT-FRM-01` [^r3].
* Power and mounting components: Charger `CHG-4A-01` is allocated across finished good lines at 1 NOS with scrap ranging between 0% and 2% [^r6][^r14][^r20][^r21][^r23][^r24][^r26]. [[items-mnt|Battery frame mount]] `MNT-FRM-01` is allocated at line 340 at 1 NOS with scrap percentages between 0% and 2% on models such as `FG-ANC-L-BLK`, `FG-DEA-S-BLU`, `FG-DEA-L-GRN`, `FG-IRK-M-BLK`, `FG-IRK-L-RED`, `FG-TAM-S-BLK`, `FG-TAM-M-RED`, and `FG-TAM-L-GRN` [^r9][^r12][^r16][^r22][^r23][^r24][^r29].
* Hardware and braking: [[items-brk|Brake pads]] `BRK-PAD-01` are specified at line 110 as 2 NOS with scrap rates between 0% and 2% [^r8][^r17][^r20][^r21]. Standard [[items-bel|bell]] `BEL-STD-01` appears at line 210 as 1 NOS with scrap between 0.50% and 2% [^r11][^r18][^r21].
* Packaging and compliance: [[items-box|Shipping box]] `BOX-BIKE-01` is assigned at line 350 as 1 NOS with scrap between 0% and 1% [^r4][^r15][^r23][^r28]. UN battery [[items-pkg|packaging labels]] `PKG-LBL-UN` are specified on lines 360, 370, or 380 in both NOS and ROL units with scrap between 0% and 1% [^r4][^r10][^r15][^r20][^r22][^r23][^r27].
* Ledgerline report PRD-R002 confirms single-level breakdowns, such as `FG-ANC-L-BLK` specifying frame `FRM-ANC-L-BLK` (line 10, 0% scrap), `BAT-500` (line 20, 1% scrap), `MTR-HUB-250` (line 30, 0% scrap), `CHG-4A-01` (line 40, 1% scrap), controller `CTL-03` (line 50, 2% scrap), and display `DSP-04` (line 60, 2% scrap) [^r33][^r34][^r35]. Similarly, `FG-ANC-L-BLU` specifies frame `FRM-ANC-L-BLU`, `BAT-500` (0.50% scrap), `MTR-HUB-250` (2% scrap), `CHG-4A-01`, controller `CTL-04` (line 50, 0% scrap), display `DSP-01` (line 60, 1% scrap), cargo rack `ACC-RCC` (line 240, qty 5), basket `ACC-BSK` (qty 6), and rack mount `MNT-RCK-03` (line 250, qty 1, scrap 2%) [^r36][^r37][^r38].

## Columns

The `BOM` sheet comprises six columns [^r1][^r19]:

1. `parent`: Finished good item code (for example, `FG-ANC-S-BLK` or `FG-DEA-M-SLV`) [^r2][^r14].
2. `line`: Integer sequence number of the bill of materials line (for example, 10, 20, 40, 110, 210, 340, 350, 360, 370) [^r2][^r4][^r8][^r11][^r12][^r15].
3. `component`: Component item code required for assembly [^r1][^r13].
4. `qty`: Component quantity per parent build unit [^r1][^r6][^r8].
5. `uom`: Unit of measure (such as `NOS` or `ROL`) [^r6][^r10][^r27].
6. `scrap_pct`: Expected scrap allowance percentage [^r1][^r2][^r10].

## How to look up a row

1. Open `05_master_data/BOM_master_2026.xlsx` to sheet `BOM` [^r1][^r25].
2. Filter the `parent` column by the finished good item code (for example, `FG-ANC-M-RED` or `FG-MED-XL-SLV`) [^r7][^r20].
3. Sort ascending by `line` to review the single-level assembly sequence [^r2][^r3].
4. Read the `component`, `qty`, `uom`, and `scrap_pct` columns for that line [^r13][^r20].

## Size

The sheet contains 5,320 data rows covering 140 distinct parent items and 691 distinct components [^r5][^r13].

## See also

* [[items-fg|FG-* items]]
* [[items-bat|BAT-* items]]
* [[items-mtr|MTR-* items]]
* [[items-chg|CHG-* items]]
* [[items-mnt|MNT-* items]]
* [[items-bel|BEL-* items]]
* [[items-brk|BRK-* items]]
* [[items-pkg|PKG-* items]]
* [[items-box|BOX-* items]]

## References

[^r1]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, SHEET BOM
[^r31]: 06_transactions/reports/Bill of materials listing 2026 (printed).pdf, p. 1, REPORT PRD-R002 SINGLE-LEVEL BILL OF MATERIALS
[^r5]: 05_master_data/BOM_master_2026.xlsx, sheet BOM
[^r32]: 06_transactions/reports/Bill of materials listing 2026 (printed).pdf, p. 1, REPORT PRD-R002 SINGLE-LEVEL BILL OF MATERIALS
[^r25]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, SHEET BOM
[^r2]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-S-BLK, SHEET BOM
[^r3]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-M-BLK, SHEET BOM
[^r4]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-S-BLU, SHEET BOM
[^r6]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-M-SLV
[^r14]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-DEA-M-SLV
[^r20]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-MED-XL-SLV, SHEET BOM
[^r21]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-IRK-S-BLK, SHEET BOM
[^r23]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-IRK-L-RED, SHEET BOM
[^r24]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-TAM-S-BLK, SHEET BOM
[^r26]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row 3159, SHEET BOM
[^r9]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-L-BLK
[^r12]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-DEA-S-BLU
[^r16]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-DEA-L-GRN
[^r22]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-IRK-M-BLK, SHEET BOM
[^r29]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row 3379, SHEET BOM
[^r8]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-M-BLU
[^r17]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-DEA-XL-BLU
[^r11]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-XL-GRN
[^r18]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-MED-S-BLU
[^r15]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-DEA-M-RED
[^r28]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row 3304, SHEET BOM
[^r10]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-L-RED
[^r27]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row 3230, SHEET BOM
[^r33]: 06_transactions/reports/Bill of materials listing 2026 (printed).pdf, row FG-ANC-L-BLK/10, p. 1, PARENT FG-ANC-L-BLK E-bike, Ancoats city, size L, black
[^r34]: 06_transactions/reports/Bill of materials listing 2026 (printed).pdf, row FG-ANC-L-BLK/20-40, p. 1, PARENT FG-ANC-L-BLK E-bike, Ancoats city, size L, black
[^r35]: 06_transactions/reports/Bill of materials listing 2026 (printed).pdf, row FG-ANC-L-BLK/50-60, p. 1, PARENT FG-ANC-L-BLK E-bike, Ancoats city, size L, black
[^r36]: 06_transactions/reports/Bill of materials listing 2026 (printed).pdf, row FG-ANC-L-BLU/10-40, p. 2, PARENT FG-ANC-L-BLU E-bike, Ancoats city, size L, canal blue
[^r37]: 06_transactions/reports/Bill of materials listing 2026 (printed).pdf, row FG-ANC-L-BLU/50-60, p. 2, PARENT FG-ANC-L-BLU E-bike, Ancoats city, size L, canal blue
[^r38]: 06_transactions/reports/Bill of materials listing 2026 (printed).pdf, row FG-ANC-L-BLU/240-250, p. 2, PARENT FG-ANC-L-BLU E-bike, Ancoats city, size L, canal blue
[^r19]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, SHEET BOM
[^r13]: 05_master_data/BOM_master_2026.xlsx, sheet BOM
[^r7]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-M-RED
