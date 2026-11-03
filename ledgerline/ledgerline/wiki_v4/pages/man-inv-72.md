---
title: "MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory"
type: "manual"
slug: "man-inv-72"
summary: "User manual for Ledgerline ERP 7.2 Inventory covering stock management screens, transaction services, validation rules, cycle counts, and adjustments."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | MAN-INV-72 |
| Title | Ledgerline ERP 7.2 User Manual: Inventory |
| Owner | Ledgerline Systems Documentation Group |
| Version | 7.2.3 |
| Effective date | 2025-01-15 |
| Status | current |
| Classification | internal |

MAN-INV-72 is the Ledgerline ERP 7.2 User Manual for the Inventory module, currently in force at version 7.2.3 effective 2025-01-15 [^r1]. It provides operational procedures, screen fields, transaction service groups, and validation rules across inventory handling, cycle counts, and store keeping [^r1][^r4][^r7]. Every physical inventory transaction posts an automated balancing entry to nominal ledger balance sheets to keep perpetual inventory valuations aligned with the general ledger [^r3]. An idle Ledgerline session terminates after 20 minutes and unsaved changes are lost [^r2].

| Field | Value |
|---|---|
| Code | MAN-INV-72 [^r1] |
| Owner | Ledgerline Systems Documentation Group [^r1] |
| Version | 7.2.3 [^r1] |
| Effective date | 2025-01-15 [^r1] |
| Status | current [^r1] |
| Classification | internal [^r1] |

## Screens and processes

The manual defines the standard transaction screens and processes used across the Manchester works and the Leeds unit [^r7][^r17]:

* **Warehouse and Master Data:** [[screen-inv-whs-01|INV-WHS-01]] manages warehouse storage location setup via services whs_get and whs_save [^r41]. [[screen-inv-itm-01|INV-ITM-01]] provides item registrations, UOM conversion multipliers, and lithium dangerous goods flagging using itm_save, itm_update, itm_block, and itm_uom_conv [^r42]. [[screen-inv-bin-09|INV-BIN-09]] allows stock controllers, supervisors, and warehouse clerks to manage physical racking, floor bays, inspection areas, and line-side decant points across Manchester and Leeds via bin_search, bin_get, bin_save, and bin_block [^r23][^r24][^r26]. Mandatory fields are WHS CD and BIN CD, and the REASON field justifies operational restrictions or decommissioning [^r23][^r25]. Executing bin_block logs REASON, changes STATUS, and stops incoming put-away transactions, but fails if pick lists are active [^r27][^r28].
* **Stock Transfers and Issues:** [[screen-inv-trf-04|INV-TRF-04]] handles transfers between locations with [[services-inv-txf|txf_save, txf_get, txf_search, txf_post, and txf_cancel]] [^r4]. [[screen-inv-mrn-08|INV-MRN-08]] records raw material, frame component, and sub-assembly withdrawals for manufacturing work orders, decreasing warehouse stock and debiting WIP balances [^r16][^r17]. Mandatory fields are WO NO, ITEM CD, QTY, MRN NO, and REASON, with non-mandatory fields WHS CD, STATUS, and COMMENT [^r18]. mrn_save assigns the MRN NO and sets STATUS to draft; mrn_post updates perpetual records, reduces warehouse balances, updates the build ledger, and sets STATUS to posted [^r19][^r20]. Unposted drafts can be abandoned with mrn_cancel, but cancelling posted issues triggers [[errors-inv|ERR-MRN-0007]] [^r21][^r22].
* **Stock Adjustments and Counts:** [[screen-inv-adj-05|INV-ADJ-05]] allows stores personnel and stock controllers to correct physical stock against verified counts, writing to stores ledgers and posting variance costs to general ledger cost centres once authorised [^r5][^r6]. [[screen-inv-cnt-06|INV-CNT-06]] manages rolling cycle checks and full plant counts across Manchester and Leeds [^r7]. All pending supplier receipts, factory work order issues, and shop despatches must be processed prior to freeze or post routines [^r8]. Shipped cycle-count tolerance is configured at 1.5% by value through INV.CNT_TOL_PCT; variances exceeding this limit halt posting with [[err-cnt-0240|ERR-CNT-0240]] until a recount is recorded [^r9]. Counting schedules by ABC classification are maintained via [[screen-inv-ccp-14|INV-CCP-14]] using ccp_save, ccp_get, ccp_search, and ccp_generate [^r45].
* **Returns to Vendor (RTV):** [[screen-inv-rtv-07|INV-RTV-07]] (Inventory > Return to) operates with [[services-inv-rtv|rtv_save, rtv_get, rtv_search, rtv_post, and rtv_cancel]] [^r10]. Saving a draft with rtv_save reserves inventory without relieving the stock ledger [^r11]. Posting via rtv_post relieves quarantine inventory, updates stock balances, releases reservations, generates credit expectations in purchase ledger, and sets STATUS to complete [^r12][^r13]. Posted RTV records cannot be cancelled, producing [[err-rtv-0230|ERR-RTV-0230]] if attempted [^r14]. An empty, incorrect, or open NCR NO raises ERR-RTV-0204, requiring a completed non-conformance report before goods can leave site [^r15]. If period locking or closure prevents posting, rtv_post returns ERR-RTV-0801 [^r13].
* **Tracking, Quality, and Other Flows:** [[screen-inv-lot-10|INV-LOT-10]] maintains lot and serial records using [[services-inv-lot|lot_save, lot_get, lot_search, lot_trace, lot_hold, and lot_release]], requiring ITEM CD and LOT/SERIAL [^r29][^r30]. [[screen-inv-qch-11|INV-QCH-11]] manages quality holds with qch_save, qch_get, qch_search, qch_release, and qch_reject for GRN NO, ITEM CD, QTY, and QCH NO [^r38]. [[screen-inv-res-12|INV-RES-12]] holds stock reservations via res_save, res_get, res_search, and res_cancel [^r39][^r40]. [[screen-inv-kbn-13|INV-KBN-13]] controls storage-to-line transfers using kbn_save, kbn_get, kbn_search, kbn_signal, and kbn_close [^r44]. [[screen-inv-pkg-15|INV-PKG-15]] tracks returnable packaging such as specialist pallets, motor transport frames, and [[items-bat|battery crates]] via pkg_save, pkg_get, pkg_search, and pkg_post [^r46]. [[screen-inv-scr-16|INV-SCR-16]] writes off obsolete or damaged inventory via scr_save, scr_get, scr_search, scr_approve, and scr_post [^r47]. [[screen-inv-csg-17|INV-CSG-17]] manages supplier consignment stock via csg_save, csg_get, csg_search, and csg_settle [^r48]. [[screen-inv-stk-03|INV-STK-03]] executes valuation and movement queries through stk_val_query, stk_val_run, stk_age_query, stk_abc_run, stk_move_query, and stk_snapshot [^r43].

## Error and warning codes

* **[[errors-cnt|ERR-CNT-0240]]:** Raised on INV-CNT-06 when physical inventory count variance exceeds the configured value tolerance of 1.5% [^r9].
* **ERR-RTV-0204:** Raised on INV-RTV-07 when the NCR NO field is missing, invalid, or linked to an unresolved non-conformance record [^r15].
* **ERR-RTV-0230:** Raised on INV-RTV-07 when attempting to invoke rtv_cancel on an already posted return [^r14].
* **ERR-RTV-0801:** Raised on INV-RTV-07 during rtv_post if inventory period locking or closure stops transaction posting [^r13].
* **ERR-MRN-0007:** Raised on INV-MRN-08 when attempting to cancel an already posted material issue transaction [^r22].
* **W-CNT-241:** Warning indicating count variance was noted but within acceptable tolerance [^r49].
* **Standard Catalogues:** Inventory transaction validations incorporate system message families including [[errors-adj|ERR-ADJ-*]], [[errors-itm|ERR-ITM-*]], [[errors-stk|ERR-STK-*]], [[errors-txf|ERR-TXF-*]], [[err-bin-0001|ERR-BIN-*]], [[err-csg-0001|ERR-CSG-*]], [[err-lot-0001|ERR-LOT-*]], [[err-pkg-0001|ERR-PKG-*]], [[err-res-0001|ERR-RES-*]], and [[err-whs-0001|ERR-WHS-*]] [^r49].

## Versions and conflicts

* **Cycle-count value tolerance:** Under v7.2.3 (effective 2025-01-15), cycle-count tolerance under parameter INV.CNT_TOL_PCT is 1.5% by value before ERR-CNT-0240 blocks posting [^r9]. Under superseded manual v7.2.2 (dated 2024-06-10), the threshold was 2.0% by value [^r32] (`superseded`).
* **ERR-RTV-0204 trigger condition:** Under v7.2.3, ERR-RTV-0204 indicates an empty, incorrect, or open non-conformance report (NCR NO) prior to dispatch [^r15]. Under superseded manual v7.2.2, ERR-RTV-0204 indicated that the entered quantity exceeded the GRN accepted quantity or that the purchase receipt line was already closed [^r33] (`superseded`).

## See also

* [[screen-inv-cnt-06|INV-CNT-06 Stock Count Entry]]
* [[screen-inv-rtv-07|INV-RTV-07 Return To Vendor Entry]]
* [[screen-inv-mrn-08|INV-MRN-08 Material Issue Entry]]
* [[screen-inv-bin-09|INV-BIN-09 Bin Master Entry]]
* [[screen-inv-lot-10|INV-LOT-10 Lot / Serial Entry]]
* [[screen-inv-adj-05|INV-ADJ-05 Stock Adjustment Entry]]
* [[screen-inv-trf-04|INV-TRF-04 Stock Transfer Entry]]
* [[sop-inv-002|SOP-INV-002 Returns to Vendor (RTV)]]
* [[err-cnt-0240|ERR-CNT-0240 Cycle Count Value Variance Exceeds Tolerance]]
* [[err-rtv-0230|ERR-RTV-0230 Invoice already posted against receipt]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 1, Version history
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 3, §3. Stock Transfer (INV-TRF-04)
[^r7]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 11, Stock Count (INV-CNT-06)
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 2, §1. About this manual
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 2, §2. Signing in and sessions
[^r17]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 18, Purpose
[^r41]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 16, §12. Warehouse Master (INV-WHS-01)
[^r42]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 18, §13. Item Master (INV-ITM-01)
[^r23]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 22, §8. Bin Master (INV-BIN-09)
[^r24]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 22, Purpose
[^r26]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 23, Step by step
[^r25]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 23, Step by step
[^r27]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 24, Restricting or blocking a location
[^r28]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 25, Questions users ask
[^r16]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 18, §7. Material Issue (INV-MRN-08)
[^r18]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 18, §7. Material Issue (INV-MRN-08)
[^r19]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 19, Step by step
[^r20]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 19, Step by step
[^r21]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 20, Step by step
[^r22]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 21, Questions users ask
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 7, Stock Adjustment (INV-ADJ-05)
[^r6]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 7, Stock Adjustment (INV-ADJ-05)
[^r8]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 11, Before you start
[^r9]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 14, Questions users ask
[^r45]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 23, §16. Cycle Count Plan (INV-CCP-14)
[^r10]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 14, §6. Return To Vendor (INV-RTV-07)
[^r11]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 16, Saving the draft record
[^r12]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 16, Posting the return
[^r13]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 18, §7. Material Issue (INV-MRN-08)
[^r14]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 18, §7. Material Issue (INV-MRN-08)
[^r15]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 18, §7. Material Issue (INV-MRN-08)
[^r29]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 25, §9. Lot / Serial (INV-LOT-10)
[^r30]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 25, §9. Lot / Serial (INV-LOT-10)
[^r38]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 13, §10. Quality Hold (INV-QCH-11)
[^r39]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 15, §11. Stock Reservation (INV-RES-12)
[^r40]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 16, Messages
[^r44]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 21, §15. Kanban Card (INV-KBN-13)
[^r46]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 24, Section: Returnable Packaging (INV-PKG-15)
[^r47]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 26, Scrap Note (INV-SCR-16)
[^r48]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 27, Consignment Stock (INV-CSG-17)
[^r43]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 20, §14. Stock (INV-STK-03)
[^r49]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 30, §20. Messages
[^r32]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 7, §5. Stock Count (INV-CNT-06)
[^r33]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 9, §7. Material Issue (INV-MRN-08)
