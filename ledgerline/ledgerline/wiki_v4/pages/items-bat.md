---
title: "BAT-* items"
type: "item-family"
slug: "items-bat"
summary: "Battery packs, individual cells, and management boards (BAT-*) including safety, storage limits, BOM usage, stock levels, and procurement controls."
audience: "staff"
status: "mixed"
sources: ["05_master_data/BOM_master_2026.xlsx", "05_master_data/ITEM_MASTER_2026-10-26.xlsx", "05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx", "05_master_data/Stock_on_hand_2026-10-26_0900.xlsx", "05_master_data/old/item_master_export_2025-03.csv", "01_policies/AMD-SUP-2026-02 Amendment 2 Supplier Policy.pdf", "01_policies/POL-BAT-004 Battery Safety and Handling Policy v1.2.pdf", "01_policies/POL-QUA-005 Quality Policy v3.0.pdf", "01_policies/old/purchase_policy_v3_2019.docx", "02_procedures/SOP-INV-002 Returns to Vendor (RTV) v1.3.pdf", "02_procedures/SOP-INV-004 Battery Pack Storage and Handling v1.0.pdf", "02_procedures/SOP-PRD-001 Work Order Release and Backflush v1.5.pdf", "02_procedures/SOP-PUR-004 Rate Contract Maintenance v2.0.pdf", "02_procedures/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf", "02_procedures/SOP-PUR-006 Quotations and Supplier Selection v1.0.pdf", "02_procedures/SOP-QUA-001 Incoming Inspection v2.0.pdf", "02_procedures/SOP-QUA-002 Damaged Battery Pack Quarantine v1.1.pdf", "03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "08_release_notes/RN-7.2.3-P5 Ledgerline Patch Notes.pdf", "11_training/BHT-01 Battery handling course slides.pdf", "11_training/QRC-04 Goods receipt.pdf", "11_training/QRC-06 Your approval inbox.pdf", "10_meeting_notes/2026-09-17 Supplier review - Voltway Cells.docx", "10_meeting_notes/2026-09-30 S&OP meeting.docx", "10_meeting_notes/2026-10-19 Weekly purchasing meeting.md", "09_email_archive/2026/2026-06-15_Voltway battery packs - receive straight into main stores.eml", "09_email_archive/2026/2026-07-28_Failed battery lot - incoming abuse test.eml", "09_email_archive/2026/2026-09-02_Approving orders for lithium-cell parts - CERT OK in the approval comment.eml", "09_email_archive/2026/2026-09-24_Voltway Cells - BAT-500 price from 1 October 2026.eml", "09_email_archive/2026/2026-09-25_FW_ Voltway Cells - BAT-500 price from 1 October 2026.eml", "09_email_archive/2026/2026-09-25_RE_ FW_ Voltway Cells - BAT-500 price from 1 October 2026.eml", "09_email_archive/2026/2026-09-25_RE_ RE_ FW_ Voltway Cells - BAT-500 price from 1 October 2026.eml", "09_email_archive/2026/2026-10-01_CERT EXPIRED - DO NOT ORDER_ Nordic Cell Co. (NC-GDA-0063).eml", "09_email_archive/2026/2026-10-22_Quotation Q-BE-26-0917 - Brightcell Energy.eml", "09_email_archive/2026/2026-10-23_Brightcell quote - can we switch from Voltway_.eml", "09_email_archive/2026/2026-10-26_Battery packs for the spring launch run.eml", "06_transactions/PO_extract_2026-01_to_2026-10.xlsx", "06_transactions/reports/Goods Receipt Register Jan-Oct 2026 (printed).pdf", "06_transactions/reports/Item master listing 2026-10 (printed).pdf", "06_transactions/reports/PO register 2026-01 (printed).pdf", "06_transactions/reports/PO register 2026-02 (printed).pdf", "06_transactions/reports/PO register 2026-03 (printed).pdf", "06_transactions/reports/PO register 2026-04 (printed).pdf", "06_transactions/reports/PO register 2026-05 (printed).pdf", "06_transactions/reports/PO register 2026-06 (printed).pdf", "06_transactions/reports/PO register 2026-07 (printed).pdf", "06_transactions/reports/PO register 2026-08 (printed).pdf", "06_transactions/reports/PO register 2026-09 (printed).pdf", "06_transactions/reports/Stock status listing 2026-10-26 (printed).pdf", "06_transactions/stock_ledger_2026-Q3.csv", "99_scans/2026_signed_approval_PO-2026-00452.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| family | BAT |
| description | Battery packs, cells, and BMS modules |
| buyer | [[user-lmoreno|LMORENO]] |
| lead_days | 42 |
| hazard_class | UN3480 / UN3481 |
| storage_location | WH-MAN-STR (fire cells BAT-Z1 to BAT-Z4) |
| safety_flag | cell_safety = 1 (LC) |

The `BAT-*` item family comprises traction battery packs, replacement cells, and battery management boards used across Northbridge Cycles e-bike production and spare parts fulfillment [^r7][^r10][^r76]. All battery packs and loose cells are designated dangerous goods subject to mandatory UN 38.3 transport certification, serial tracking, and strict fire-cell storage limits [^r27][^r28][^r30][^r42]. As of 26 October 2026, active production sourcing for high-volume packs is concentrated with [[sup-vc-ein-0042|Voltway Cells]], while alternate vendor [[sup-nc-gda-0063|Nordic Cell Co.]] remains suspended from order placement due to an expired certificate [^r17][^r132].

## Items in this family

| Item code | Description | Category | Std cost | ROL | ADI | Lead days | HS code | UN no. | Legacy code | Buyer | cell_safety |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BAT-250 | Battery pack, 36 V 250 Wh | SPARES | — | 560 | 40 | — | — | — | — | — | 1 [^r70] |
| BAT-300 | Battery pack, 36 V 300 Wh | SPARES | — | 560 | 40 | — | — | — | — | — | 1 [^r70] |
| BAT-300-OLD | Battery pack, 2014 model (inactive) | — | — | 0 | 0 | — | — | — | NB104551 | — | — [^r75] |
| BAT-375 | Battery pack, 36 V 375 Wh | SPARES | 92.00 | 1,500 | 250 | 42 | 8507.60 | UN3480 | NB104274 | [[user-lmoreno|LMORENO]] | 1 [^r10][^r15][^r68] |
| BAT-400-OLD | Battery pack, 36 V 400 Wh (old model, inactive) | — | 105.58 | 0 | 0 | — | — | — | NB104273 | LMORENO | 1 [^r9][^r14][^r67] |
| BAT-418 | Battery pack, 36 V 418 Wh | — | — | 800 | — | — | — | — | — | — | 1 [^r71] |
| BAT-500 | Battery pack, 36 V 500 Wh | SPARES | 111.00 | 3,000 | 600 | 42 | 8507.60 | UN3480 | NB104237 | LMORENO | 1 [^r7][^r12][^r65] |
| BAT-500-R | Battery pack, 36 V 500 Wh refurbished | — | 167.74 | 0 | 0 | 42 | 8507.60 | UN3480 | NB104263 | LMORENO | 1 [^r8][^r13][^r66] |
| BAT-500-48 | Battery pack, 48 V 500 Wh | — | — | 35 | — | — | — | — | — | — | 1 [^r73] |
| BAT-625 | Battery pack, 36 V 625 Wh | — | — | 2,500 | — | — | — | — | — | — | 1 [^r71] |
| BAT-625-48 | Battery pack, 48 V 625 Wh | — | — | 12,600 | — | — | — | — | — | — | 1 [^r73] |
| BAT-625-INT | Battery pack, in-tube 36 V 625 Wh | — | — | 200 | 20 | — | — | — | — | — | 1 [^r74] |
| BAT-720 | Battery pack, 36 V 720 Wh | — | — | 70 | 5 | — | — | — | NB104458 | — | 1 [^r72] |
| BAT-750 | Battery pack, 48 V 750 Wh | SPARES | 146.00 | 600 | 90 | 42 | 8507.60 | UN3480 | NB104288 | LMORENO | 1 [^r11][^r16][^r69] |
| BAT-960-48 | Battery pack, 48 V 960 Wh | — | — | 3,500 | — | — | — | — | — | — | 1 [^r73] |
| BAT-BMS-36 | Battery management board 36 V | — | — | 0 | 0 | — | — | — | — | — | 0 [^r76] |
| BAT-CEL-21700 | Lithium-ion cell 21700 | — | — | 140 | 10 | — | — | — | — | — | 1 [^r76] |
| BAT-RNG-250 | Range extender pack 250 Wh | — | — | 0 | 0 | — | — | — | — | — | 1 [^r74] |

Item details and master parameters are maintained in [[data-item-master|ITEM_MASTER_2026-10-26]] [^r7][^r10].

## BOM and manufacturing usage

BAT-500 serves as the standard battery component specified on BOM line 20 (quantity 1 NOS) across multiple finished bicycle models:
* Ancoats variants: FG-ANC-S-BLK, FG-ANC-S-GRN, FG-ANC-S-SLV, FG-ANC-S-RED, FG-ANC-S-BLU, FG-ANC-M-BLK, FG-ANC-M-GRN, FG-ANC-M-SLV (0% scrap) [^r1]; FG-ANC-M-RED (0% scrap) and FG-ANC-L-BLU (0.50% scrap) [^r2]; FG-ANC-XL-RED (0% scrap) [^r3].
* Sprint variants: Specified across FG-SPR models at line 20 with scrap rates between 0% and 2% [^r4], including FG-SPR-M-BLK (2% scrap) [^r5], as well as FG-SPR-L-RED, FG-SPR-L-BLU, FG-SPR-XL-BLK, FG-SPR-XL-GRN, FG-SPR-XL-SLV, FG-SPR-XL-RED, and FG-SPR-XL-BLU [^r6].

Battery packs do not clear through standard backflush routine JOB-PRD-015 because each individual unit requires serial tracking; packs must be issued by serial number on [[screen-inv-mrn-08|INV-MRN-08]] [^r34]. Serial numbers are taken from the supplier's carton label and entered at goods receipt [^r42]. At full rate, the Medlock 2 launch pack assembly line is planned to produce approximately 600 packs per day [^r120].

## Storage and safety rules

Under [[pol-bat-004|POL-BAT-004]], strict safety controls govern all lithium-cell inventory:
* **Storage locations:** Battery packs must be booked to warehouse WH-MAN-STR exclusively within fire cells BAT-Z1 to BAT-Z4 [^r28][^r33].
* **Capacity limits:** No single fire cell may exceed 1,500 packs, and total fire-cell capacity is capped at 6,000 packs [^r28][^r33][^r44]. Deliveries of raw cells arrive in planned weekly drops to avoid exceeding battery store floor-loading limits [^r121].
* **State of charge (SoC):** Stored packs must remain between 30% and 50% SoC and must never be charged within the store area [^r29][^r44].
* **Stacking and rotation:** Packs are stacked at most four cartons high on pallets and issued under FIFO control by carton label date [^r33].
* **Quarantine:** All compromised packs must be moved to the red quarantine bin in fire cell BAT-Z4 using protective gloves and eye protection in accordance with [[sop-qua-002|SOP-QUA-002]] [^r41].

## Quality and incoming inspection

Under POL-QUA-005 and [[sop-qua-001|SOP-QUA-001]], incoming lithium-cell consignments are inspected at AQL 0.65 [^r31]. Inspectors must verify open-circuit voltage for every sample pack using calibrated meters before booking into stores [^r31][^r39]. If any sample pack exhibits an SoC below 30% or above 50%, the entire lot must be rejected [^r39]. Inspectors are strictly prohibited from averaging voltages across packs, passing out-of-spec packs for balancing in stores, or re-sampling failed lots [^r40]. 

By operational exception, BAT-* packs received from Voltway Cells are moved directly into storage location WH-MAN-STR rather than remaining in general goods inward or WH-MAN-QC, whereas other lithium-cell deliveries route through inspection [^r46][^r124].

## Transport and returns

Standalone battery pack consignments must be declared as UN3480, while packs shipped inside or alongside bicycles are declared as UN3481 [^r30][^r45]. Packages require label PKG-LBL-UN and must ship using carrier dangerous-goods service DGX [^r30][^r43][^r45]. Rejected or defective battery packs constitute hazardous freight and may only be returned via dangerous-goods carrier services with UN3480 labels attached to approved crates [^r32]. Lithium-ion battery packs cannot legally be moved by carriers, accepted at Manchester works, or transferred to Leeds without a matching, valid UN 38.3 test summary [^r36].

## Procurement and contracts

Purchase orders for lithium-cell items cannot be raised unless an active [[topic-un-38-3-certificates|UN 38.3 certificate]] is on file that was issued within the preceding 12 months and remains valid for at least 60 days following the PO date [^r27]. Any modification to battery chemistry, casing seals, or BMS circuitry invalidates existing test reports and requires recertification before ordering [^r37]. Quotation comparisons require technical compliance verification before unit price evaluation [^r38]. Approvers must confirm documentation by writing 'CERT OK' alongside the certificate reference in the PO approval comment [^r47][^r127].

Battery rate contracts may be established for 6-month durations rather than standard 12-month cycles [^r35]. Rate contracts for 2026-27 include:
* **BAT-375:** Contracted with Voltway Cells at £92.00 (2026-04-01 to 2027-03-31) [^r18].
* **BAT-750:** Contracted with Voltway Cells at £146.00 (2026-04-01 to 2027-03-31) [^r18].
* **BAT-500:** Contracted with Nordic Cell Co. at £111.00 for the full year [^r17], and with Voltway Cells at £114.00 through 2026-09-30, rising to £119.00 from 2026-10-01 to 2027-03-31 [^r17][^r118][^r123][^r128][^r129][^r130]. Order placement with Nordic Cell Co. is currently suspended due to an expired UN 38.3 certificate [^r132].

Orders for the upcoming spring launch run are procured under Voltway's contract (£119.00 per unit for 2,000 units of BAT-500) and allocated against cost centre [[cc-prd-07|PRD-07]] [^r122][^r135]. Voltway battery packs operate on a six-week order lead time [^r119]. An alternative quotation (Q-BE-26-0917) from Brightcell Energy offers 36 V 500 Wh packs at £104.00 DAP Manchester (MOQ 500 packs, 6-week lead time) [^r133][^r134].

Historical transaction records and purchase registers show procurement across cost centres [[cc-prd-02|PRD-02]], [[cc-prd-03|PRD-03]], [[cc-prd-04|PRD-04]], [[cc-prd-05|PRD-05]], and [[cc-lds-prd-01|LDS-PRD-01]] documented in [[data-po-extract-2026|PO_extract_2026-01_to_2026-10]] [^r48][^r49][^r50][^r52][^r53][^r56][^r59][^r60][^r77][^r78][^r84][^r87][^r88].

## Stock status (as of 26 October 2026, 09:00 GMT)

Inventory balances recorded in [[data-stock-on-hand|Stock_on_hand_2026-10-26_0900]]:
* **BAT-500:** 5,400 on hand at WH-MAN-STR; 1,200 on hand at WH-LDS-STR (0 allocated, 0 on order) [^r21][^r92].
* **BAT-375:** 4,100 on hand at WH-MAN-STR (0 allocated, 0 on order) [^r22].
* **BAT-750:** 900 on hand at WH-MAN-STR (0 allocated, 0 on order) [^r22].
* **BAT-250:** 255 on hand at WH-MAN-STR [^r23].
* **BAT-300:** 595 on hand and 400 on order at WH-MAN-STR; 109 on hand at WH-LDS-STR [^r23][^r93].
* **BAT-418:** 1,982 on hand at WH-MAN-STR [^r24].
* **BAT-625:** 8,436 on hand at WH-MAN-STR [^r24].
* **BAT-625-INT:** 678 on hand at WH-MAN-STR [^r24].
* **BAT-720:** 178 on hand at WH-MAN-STR [^r24].
* **BAT-RNG-250:** 37 on hand at WH-MAN-STR [^r24].
* **BAT-500-48:** 46 on hand and 50 on order at WH-MAN-STR; 32 on hand at WH-LDS-STR [^r25].
* **BAT-625-48:** 18,705 on hand at WH-MAN-STR [^r25].
* **BAT-960-48:** 7,332 on hand at WH-MAN-STR [^r25].
* **BAT-CEL-21700:** 390 on hand at WH-MAN-STR [^r26].
* **BAT-BMS-36:** 33 on hand at WH-MAN-STR; 9 on hand at WH-LDS-STR [^r26][^r94].

## Versions and conflicts

* **BAT-500 Voltway pricing:** Today's rate contract and purchasing decisions fix the Voltway Cells BAT-500 unit price at £119.00 effective from 1 October 2026 through 31 March 2027 [^r17][^r123][^r128][^r129][^r130][^r134][^r135]. An internal email chain dated 25 September 2026 asserted that the order price remained £114.00 despite the notified increase [^r131]. The signed rate contract and subsequent S&OP procurement commitments confirm £119.00 is in force (`contradiction`) [^r17][^r123][^r135].
* **UN 38.3 test certificate rules:** Today's rule under AMD-SUP-2026-02 requires test summaries issued within the preceding 12 months with validity extending at least 60 days past order placement [^r27]. Under superseded policy [[pol-pur-001|POL-PUR-001]] v3.0 (2019), buyers were merely instructed to ensure a valid UN 38.3 test summary matched the casing stamp on engineering drawings (`superseded`) [^r138].

## See also

* [[data-item-master|data-item-master]] — Item master parameters and legacy item mappings
* [[data-stock-on-hand|data-stock-on-hand]] — Warehouse stock balances and reorder levels
* [[pol-bat-004|pol-bat-004]] — Battery Safety and Handling Policy
* [[sop-pur-005|sop-pur-005]] — UN 38.3 certificate compliance and renewal
* [[sop-qua-001|sop-qua-001]] — Incoming inspection and open-circuit voltage checks
* [[sop-qua-002|sop-qua-002]] — Quarantine of damaged or non-conforming battery packs
* [[sup-vc-ein-0042|sup-vc-ein-0042]] — Primary supplier Voltway Cells
* [[sup-nc-gda-0063|sup-nc-gda-0063]] — Nordic Cell Co. supplier record
* [[topic-un-38-3-certificates|topic-un-38-3-certificates]] — Transport safety compliance requirements

## References

[^r7]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Items, row BAT-500, first 5 rows, then the 10 rows whose key appears in the narrative documents
[^r10]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Items, row BAT-375, first 5 rows, then the 10 rows whose key appears in the narrative documents
[^r76]: 06_transactions/reports/Item master listing 2026-10 (printed).pdf, row BAT-CEL-21700, p. 1, LEDGERLINE ERP 7.2 REPORT INV-R001 ITEM MASTER LISTING
[^r27]: 01_policies/AMD-SUP-2026-02 Amendment 2 Supplier Policy.pdf, p. 1, §3. What purchase staff must do
[^r28]: 01_policies/POL-BAT-004 Battery Safety and Handling Policy v1.2.pdf, p. 2, §2. Storage
[^r30]: 01_policies/POL-BAT-004 Battery Safety and Handling Policy v1.2.pdf, p. 4, §4. Transport
[^r42]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 29, Questions users ask
[^r17]: 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx, sheet 2026-27, row NC-GDA-0063/BAT-500/2026-04-01, SHEET 2026-27
[^r132]: 09_email_archive/2026/2026-10-01_CERT EXPIRED - DO NOT ORDER_ Nordic Cell Co. (NC-GDA-0063).eml, body
[^r70]: 06_transactions/reports/Item master listing 2026-10 (printed).pdf, row BAT-250, p. 1, LEDGERLINE ERP 7.2 REPORT INV-R001 ITEM MASTER LISTING
[^r75]: 06_transactions/reports/Item master listing 2026-10 (printed).pdf, row BAT-300-OLD, p. 1, LEDGERLINE ERP 7.2 REPORT INV-R001 ITEM MASTER LISTING
[^r15]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Legacy code map, row NB104274, SHEET Legacy code map
[^r68]: 06_transactions/reports/Item master listing 2026-10 (printed).pdf, row BAT-375, p. 1, LEDGERLINE ERP 7.2 REPORT INV-R001 ITEM MASTER LISTING
[^r9]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Items, row BAT-400-OLD, first 5 rows, then the 10 rows whose key appears in the narrative documents
[^r14]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Legacy code map, row NB104273, SHEET Legacy code map
[^r67]: 06_transactions/reports/Item master listing 2026-10 (printed).pdf, row BAT-400-OLD, p. 1, LEDGERLINE ERP 7.2 REPORT INV-R001 ITEM MASTER LISTING
[^r71]: 06_transactions/reports/Item master listing 2026-10 (printed).pdf, row BAT-418, p. 1, LEDGERLINE ERP 7.2 REPORT INV-R001 ITEM MASTER LISTING
[^r12]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Legacy code map, row NB104237, SHEET Legacy code map
[^r65]: 06_transactions/reports/Item master listing 2026-10 (printed).pdf, row BAT-500, p. 1, LEDGERLINE ERP 7.2 REPORT INV-R001 ITEM MASTER LISTING
[^r8]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Items, row BAT-500-R, first 5 rows, then the 10 rows whose key appears in the narrative documents
[^r13]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Legacy code map, row NB104263, SHEET Legacy code map
[^r66]: 06_transactions/reports/Item master listing 2026-10 (printed).pdf, row BAT-500-R, p. 1, LEDGERLINE ERP 7.2 REPORT INV-R001 ITEM MASTER LISTING
[^r73]: 06_transactions/reports/Item master listing 2026-10 (printed).pdf, row BAT-500-48, p. 1, LEDGERLINE ERP 7.2 REPORT INV-R001 ITEM MASTER LISTING
[^r74]: 06_transactions/reports/Item master listing 2026-10 (printed).pdf, row BAT-625-INT, p. 1, LEDGERLINE ERP 7.2 REPORT INV-R001 ITEM MASTER LISTING
[^r72]: 06_transactions/reports/Item master listing 2026-10 (printed).pdf, row BAT-720, p. 1, LEDGERLINE ERP 7.2 REPORT INV-R001 ITEM MASTER LISTING
[^r11]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Items, row BAT-750, first 5 rows, then the 10 rows whose key appears in the narrative documents
[^r16]: 05_master_data/ITEM_MASTER_2026-10-26.xlsx, sheet Legacy code map, row NB104288, SHEET Legacy code map
[^r69]: 06_transactions/reports/Item master listing 2026-10 (printed).pdf, row BAT-750, p. 1, LEDGERLINE ERP 7.2 REPORT INV-R001 ITEM MASTER LISTING
[^r1]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-M-BLK, SHEET BOM
[^r2]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-M-RED
[^r3]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-ANC-XL-RED
[^r4]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-SPR-S-BLK, SHEET BOM
[^r5]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row FG-SPR-M-BLK, SHEET BOM
[^r6]: 05_master_data/BOM_master_2026.xlsx, sheet BOM, row 5285, SHEET BOM
[^r34]: 02_procedures/SOP-PRD-001 Work Order Release and Backflush v1.5.pdf, p. 3, §5. Procedure: notes and common mistakes
[^r120]: 10_meeting_notes/2026-09-30 S&OP meeting.docx, Spring launch run
[^r33]: 02_procedures/SOP-INV-004 Battery Pack Storage and Handling v1.0.pdf, p. 3, §5. Procedure
[^r44]: 11_training/BHT-01 Battery handling course slides.pdf, p. 3, Storage
[^r121]: 10_meeting_notes/2026-09-30 S&OP meeting.docx, Supply chain and demand scheduling
[^r29]: 01_policies/POL-BAT-004 Battery Safety and Handling Policy v1.2.pdf, p. 2, §2. Storage
[^r41]: 02_procedures/SOP-QUA-002 Damaged Battery Pack Quarantine v1.1.pdf, p. 3, §5. Procedure
[^r31]: 01_policies/POL-QUA-005 Quality Policy v3.0.pdf, p. 2, §3. Incoming inspection
[^r39]: 02_procedures/SOP-QUA-001 Incoming Inspection v2.0.pdf, p. 3, §5. Procedure
[^r40]: 02_procedures/SOP-QUA-001 Incoming Inspection v2.0.pdf, p. 4, §5. Procedure: notes and common mistakes
[^r46]: 11_training/QRC-04 Goods receipt.pdf, p. 1, Voltway battery packs
[^r124]: 09_email_archive/2026/2026-06-15_Voltway battery packs - receive straight into main stores.eml, body
[^r45]: 11_training/BHT-01 Battery handling course slides.pdf, p. 5, Shipping
[^r43]: 08_release_notes/RN-7.2.3-P5 Ledgerline Patch Notes.pdf, p. 2, Sales: Carrier labels print the dangerous-goods service code
[^r32]: 02_procedures/SOP-INV-002 Returns to Vendor (RTV) v1.3.pdf, p. 4, Common mistakes
[^r36]: 02_procedures/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf, p. 1, §1. Purpose
[^r37]: 02_procedures/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf, p. 4, What to check on the screen
[^r38]: 02_procedures/SOP-PUR-006 Quotations and Supplier Selection v1.0.pdf, p. 3, §5. Procedure: notes and common mistakes
[^r47]: 11_training/QRC-06 Your approval inbox.pdf, p. 1, Lithium-cell items
[^r127]: 09_email_archive/2026/2026-09-02_Approving orders for lithium-cell parts - CERT OK in the approval comment.eml, body
[^r35]: 02_procedures/SOP-PUR-004 Rate Contract Maintenance v2.0.pdf, p. 3, §5. Procedure
[^r18]: 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx, sheet 2026-27, row VC-EIN-0042/BAT-375/2026-04-01, SHEET 2026-27
[^r118]: 10_meeting_notes/2026-09-17 Supplier review - Voltway Cells.docx, Meeting Notes
[^r123]: 10_meeting_notes/2026-10-19 Weekly purchasing meeting.md, Discussion
[^r128]: 09_email_archive/2026/2026-09-24_Voltway Cells - BAT-500 price from 1 October 2026.eml, body
[^r129]: 09_email_archive/2026/2026-09-25_FW_ Voltway Cells - BAT-500 price from 1 October 2026.eml, body
[^r130]: 09_email_archive/2026/2026-09-25_RE_ FW_ Voltway Cells - BAT-500 price from 1 October 2026.eml, Voltway Cells - BAT-500 price from 1 October 2026
[^r122]: 10_meeting_notes/2026-10-19 Weekly purchasing meeting.md, Spring launch
[^r135]: 09_email_archive/2026/2026-10-26_Battery packs for the spring launch run.eml, body
[^r119]: 10_meeting_notes/2026-09-17 Supplier review - Voltway Cells.docx, Certificate
[^r133]: 09_email_archive/2026/2026-10-22_Quotation Q-BE-26-0917 - Brightcell Energy.eml, body
[^r134]: 09_email_archive/2026/2026-10-23_Brightcell quote - can we switch from Voltway_.eml, body
[^r48]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-01, row PO/2026/00028, SHEET 2026-01
[^r49]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-01, row PO/2026/00040, SHEET 2026-01
[^r50]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-02, row PO/2026/00175, SHEET 2026-02
[^r52]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-03, row PO/2026/00395, SHEET 2026-03
[^r53]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-03, row PO/2026/00415, SHEET 2026-03
[^r56]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-04, row PO/2026/00542, SHEET 2026-04
[^r59]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-07, row PO/2026/00890, SHEET 2026-07
[^r60]: 06_transactions/PO_extract_2026-01_to_2026-10.xlsx, sheet 2026-07, row PO/2026/00902, SHEET 2026-07
[^r77]: 06_transactions/reports/PO register 2026-01 (printed).pdf, row PO/2026/00028, p. 1, PUR-R010
[^r78]: 06_transactions/reports/PO register 2026-01 (printed).pdf, row PO/2026/00085, p. 3, PUR-R010
[^r84]: 06_transactions/reports/PO register 2026-04 (printed).pdf, row PO/2026/00542, p. 3, PUR-R010 PURCHASE ORDER REGISTER
[^r87]: 06_transactions/reports/PO register 2026-07 (printed).pdf, row PO/2026/00890, p. 1, PUR-R010 PURCHASE ORDER REGISTER
[^r88]: 06_transactions/reports/PO register 2026-07 (printed).pdf, row PO/2026/00902, p. 1, PUR-R010 PURCHASE ORDER REGISTER
[^r21]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BAT-500@WH-MAN-STR, SHEET Stock
[^r92]: 06_transactions/reports/Stock status listing 2026-10-26 (printed).pdf, row BAT-500, p. 1, Stock listing
[^r22]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BAT-375@WH-MAN-STR, SHEET Stock
[^r23]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BAT-300@WH-MAN-STR, SHEET Stock
[^r93]: 06_transactions/reports/Stock status listing 2026-10-26 (printed).pdf, row BAT-300, p. 1, Stock listing
[^r24]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BAT-625@WH-MAN-STR, SHEET Stock
[^r25]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BAT-500-48@WH-MAN-STR, SHEET Stock
[^r26]: 05_master_data/Stock_on_hand_2026-10-26_0900.xlsx, sheet Stock, row BAT-CEL-21700@WH-MAN-STR, SHEET Stock
[^r94]: 06_transactions/reports/Stock status listing 2026-10-26 (printed).pdf, row BAT-BMS-36, p. 1, Stock listing
[^r131]: 09_email_archive/2026/2026-09-25_RE_ RE_ FW_ Voltway Cells - BAT-500 price from 1 October 2026.eml, body
[^r138]: 01_policies/old/purchase_policy_v3_2019.docx, §6. Supplier qualification
