---
title: "PO_extract_2026-01_to_2026-10"
type: "data-source"
slug: "data-po-extract-2026"
summary: "Transactional extract of 2026 purchase orders combining header and line attributes across operating units NBC-MAN-01 and NBC-LDS-01."
audience: "staff"
status: "current"
sources: ["06_transactions/PO_extract_2026-01_to_2026-10.xlsx", "06_transactions/reports/Draft orders report 2026-10-26.pdf", "06_transactions/reports/Open orders by supplier 2026-10-23.pdf", "06_transactions/reports/PO register 2026-01 (printed).pdf", "06_transactions/reports/PO register 2026-02 (printed).pdf", "06_transactions/reports/PO register 2026-03 (printed).pdf", "06_transactions/reports/PO register 2026-04 (printed).pdf", "06_transactions/reports/PO register 2026-05 (printed).pdf", "06_transactions/reports/PO register 2026-06 (printed).pdf", "06_transactions/reports/PO register 2026-07 (printed).pdf", "06_transactions/reports/PO register 2026-08 (printed).pdf", "06_transactions/reports/PO register 2026-09 (printed).pdf", "06_transactions/reports/PO register 2026-10 (printed).pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Source file | 06_transactions/PO_extract_2026-01_to_2026-10.xlsx |
| Type | Transaction extract |
| Operating units | NBC-MAN-01, NBC-LDS-01 |
| Key column | po_no |
| Periods covered | 2026-01 to 2026-10 |
| Status | Current |

`PO_extract_2026-01_to_2026-10.xlsx` is the primary structured transaction workbook recording purchase orders raised across Northbridge Cycles operating units between January 2026 and October 2026 [^r1][^r3]. Each monthly sheet combines purchase order header and line data into flat rows covering operational attributes, quantities, values, cost centres, and approval histories [^r1][^r2]. As of 26 October 2026, the extract provides the transactional foundation alongside monthly printed registers and open order status reports for tracking procurement spend and order progression [^r33][^r74].

## What it holds

The workbook stores flat purchase order records combining `po_hdr` and `po_line` tables, structured as one line per order [^r1][^r19]. The records encompass orders for operating units NBC-MAN-01 and NBC-LDS-01, routing materials to receiving warehouses WH-MAN-STR, WH-MAN-MRO, and WH-LDS-STR [^r3]. Orders document transactions across regular procurement, direct procurement, and maintenance across cost centres including [[cc-prd-02|PRD-02]], [[cc-prd-03|PRD-03]], [[cc-prd-04|PRD-04]], [[cc-prd-05|PRD-05]], [[cc-mnt-01|MNT-01]], and [[cc-lds-prd-01|LDS-PRD-01]] [^r26][^r27][^r28][^r45][^r52][^r68].

Recorded orders cover a wide range of component categories including [[items-frm|FRM-*]] frames, [[items-fst|FST-*]] fasteners, [[items-bat|BAT-*]] batteries, [[items-chg|CHG-*]] chargers, [[items-mtr|MTR-*]] motors, [[items-spk|SPK-*]] spokes, and direct MRO items [^r5][^r13][^r14][^r16][^r27][^r45][^r66]. Orders are recorded under four primary statuses: Closed (CL), Released (RL), Cancelled (CN), and Rejected (RJ) [^r3][^r20][^r64]. The extract tracks order creators such as [[user-eclarke|ECLARKE]], [[user-kmensah|KMENSAH]], [[user-lmoreno|LMORENO]], and [[user-hnakamura|HNAKAMURA]], alongside approval authority captured for Purchasing Manager [[user-dokafor|DOKAFOR]] and Plant Head [[user-hweber|HWEBER]] [^r5][^r7][^r8][^r9][^r13][^r17]. Payment terms, such as advance terms (ADV), are captured on applicable orders [^r10].

## Columns

Monthly sheets record 21 distinct transactional attributes [^r2][^r22]:

| Column | Description |
|---|---|
| `po_no` | Purchase order identifier (e.g. `PO/2026/00064`) [^r2][^r5] |
| `created_on` | Date the order was raised [^r2] |
| `ou_cd` | Operating unit (`NBC-MAN-01`, `NBC-LDS-01`) [^r2][^r3] |
| `sup_cd` | Supplier master identifier [^r2] |
| `itm_cd` | Item code ordered [^r2] |
| `qty` | Order quantity [^r2] |
| `uom_cd` | Unit of measure [^r2] |
| `rate` | Net unit price [^r2] |
| `basic_value` | Pre-tax basic order value [^r2] |
| `tax_cd` | Applied tax code (e.g. `VAT20-UK`, `VAT20-RC`) [^r2][^r45][^r50] |
| `tax_value` | Calculated tax amount [^r2] |
| `gross_value` | Total order gross value including tax [^r2] |
| `cc_cd` | Target cost centre [^r2] |
| `status` | Order lifecycle status (`CL`, `CN`, `RJ`, `RL`) [^r2][^r3] |
| `po_type` | Purchase order classification [^r2] |
| `pr_no` | Source purchase requisition reference [^r2][^r15] |
| `pt_cd` | Payment term code [^r2][^r10] |
| `whs_cd` | Destination warehouse identifier [^r2][^r3] |
| `created_by` | User ID of the creating buyer [^r2] |
| `approved_by` | User ID of the approving authority [^r2] |
| `released_on` | Date the purchase order was released [^r2][^r5] |

## How to look up a row

1. Identify the purchase order number (`po_no`) or creation date.
2. Select the monthly tab matching the creation date (e.g., `2026-01` for January 2026 orders, `2026-02` for February 2026 orders) [^r4][^r19].
3. Locate the order using the key column `po_no` in column 1 [^r2][^r5].
4. Read the corresponding line to retrieve item, financial, cost centre, supplier, and approval details [^r2][^r5].

## Size

* **Sheet 2026-01:** 127 data rows across 21 columns [^r1][^r4].
* **Sheet 2026-02:** 139 data rows across 21 columns [^r19][^r22].
* **Total structure:** Individual sheets organized by calendar month from January to October 2026 [^r1][^r19].

## See also

* [[sup-vc-ein-0042|Voltway Cells (VC-EIN-0042)]]
* [[user-eclarke|Emma Clarke (ECLARKE)]]
* [[user-kmensah|Kwame Mensah (KMENSAH)]]
* [[user-lmoreno|Luis Moreno (LMORENO)]]
* [[user-hnakamura|Hana Nakamura (HNAKAMURA)]]
* [[user-dokafor|Daniel Okafor (DOKAFOR)]]
* [[user-hweber|Henrik Weber (HWEBER)]]
* [[cc-prd-02|PRD-02 Deansgate step-through line]]
* [[cc-prd-03|PRD-03 Cargo e-bike line]]
* [[cc-prd-04|PRD-04 Medlock trekking line]]
* [[cc-prd-05|PRD-05 City e-bike line, regular production]]
* [[cc-mnt-01|MNT-01 Plant maintenance]]
* [[cc-lds-prd-01|LDS-PRD-01 Leeds assembly]]
* [[items-bat|BAT-* items]]
* [[items-frm|FRM-* items]]
* [[items-fst|FST-* items]]
* [[items-chg|CHG-* items]]
* [[items-mtr|MTR-* items]]
* [[items-spk|SPK-* items]]

## References

[^r1]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-01, SHEET 2026-01
[^r3]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-01, SHEET 2026-01
[^r2]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-01, SHEET 2026-01
[^r33]: 06_transactions/reports/Open orders by supplier 2026-10-23.pdf, p. 1, REPORT PUR-R051 OPEN ORDERS BY SUPPLIER
[^r74]: 06_transactions/reports/PO register 2026-10 (printed).pdf, p. 1, PURCHASE ORDER REGISTER
[^r19]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-02, SHEET 2026-02
[^r26]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-02, row PO/2026/00248, SHEET 2026-02
[^r27]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-02, row PO/2026/00250, SHEET 2026-02
[^r28]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-02, row PO/2026/00251, SHEET 2026-02
[^r45]: 06_transactions/reports/PO register 2026-02 (printed).pdf, row PO/2026/00175, p. 2, PUR-R010 PURCHASE ORDER REGISTER
[^r52]: 06_transactions/reports/PO register 2026-03 (printed).pdf, row PO/2026/00408, p. 4
[^r68]: 06_transactions/reports/PO register 2026-07 (printed).pdf, row PO/2026/01031, p. 4
[^r5]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-01, row PO/2026/00064, SHEET 2026-01
[^r13]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-01, row PO/2026/00122, SHEET 2026-01
[^r14]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-01, row PO/2026/00123, SHEET 2026-01
[^r16]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-01, row PO/2026/00125, SHEET 2026-01
[^r66]: 06_transactions/reports/PO register 2026-07 (printed).pdf, row PO/2026/01014, p. 4
[^r20]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-02, SHEET 2026-02
[^r64]: 06_transactions/reports/PO register 2026-07 (printed).pdf, row PO/2026/00878, p. 1, PUR-R010 PURCHASE ORDER REGISTER
[^r7]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-01, row PO/2026/00117, SHEET 2026-01
[^r8]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-01, row PO/2026/00078, SHEET 2026-01
[^r9]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-01, row PO/2026/00075, SHEET 2026-01
[^r17]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-01, row PO/2026/00126, SHEET 2026-01
[^r10]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-01, row PO/2026/00118, SHEET 2026-01
[^r22]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-02, PURCHASE ORDERS CREATED 2026-02 (po_hdr + po_line)
[^r50]: 06_transactions/reports/PO register 2026-03 (printed).pdf, row PO/2026/00395, p. 4
[^r15]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-01, row PO/2026/00124, SHEET 2026-01
[^r4]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-01, SHEET 2026-01
