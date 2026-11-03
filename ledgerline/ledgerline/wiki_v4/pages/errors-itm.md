---
title: "ERR-ITM error codes"
type: "error-list"
slug: "errors-itm"
summary: "Error code catalogue for Ledgerline ERR-ITM item master errors raised across inventory, production, purchase, and sales services."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "04_service_definitions/inventory/adj_save.yaml", "04_service_definitions/inventory/adj_search.yaml", "04_service_definitions/inventory/cnt_entry.yaml", "04_service_definitions/inventory/csg_save.yaml", "04_service_definitions/inventory/csg_search.yaml", "04_service_definitions/inventory/itm_block.yaml", "04_service_definitions/inventory/itm_save.yaml", "04_service_definitions/inventory/itm_uom_conv.yaml", "04_service_definitions/inventory/itm_update.yaml", "04_service_definitions/inventory/kbn_save.yaml", "04_service_definitions/inventory/kbn_search.yaml", "04_service_definitions/inventory/lot_save.yaml", "04_service_definitions/inventory/lot_search.yaml", "04_service_definitions/inventory/mrn_search.yaml", "04_service_definitions/inventory/qch_save.yaml", "04_service_definitions/inventory/qch_search.yaml", "04_service_definitions/inventory/res_save.yaml", "04_service_definitions/inventory/res_search.yaml", "04_service_definitions/inventory/scr_save.yaml", "04_service_definitions/inventory/scr_search.yaml", "04_service_definitions/inventory/stk_abc_run.yaml", "04_service_definitions/inventory/stk_age_query.yaml", "04_service_definitions/inventory/stk_move_query.yaml", "04_service_definitions/inventory/stk_snapshot.yaml", "04_service_definitions/inventory/stk_val_run.yaml", "04_service_definitions/inventory/txf_search.yaml", "04_service_definitions/production/bom_get.yaml", "04_service_definitions/production/bom_where_used.yaml", "04_service_definitions/production/btt_search.yaml", "04_service_definitions/production/mps_get.yaml", "04_service_definitions/production/mps_save.yaml", "04_service_definitions/production/mps_search.yaml", "04_service_definitions/production/ncr_search.yaml", "04_service_definitions/production/pkb_save.yaml", "04_service_definitions/production/rtg_get.yaml", "04_service_definitions/production/rtg_save.yaml", "04_service_definitions/production/rtg_search.yaml", "04_service_definitions/production/scp_save.yaml", "04_service_definitions/production/wo_save.yaml", "04_service_definitions/purchase/itm_get.yaml", "04_service_definitions/purchase/pr_fetch.yaml", "04_service_definitions/purchase/pr_save.yaml", "04_service_definitions/sales/dmo_save.yaml", "04_service_definitions/sales/dmo_search.yaml", "04_service_definitions/sales/fcs_save.yaml", "04_service_definitions/sales/fcs_upload.yaml", "04_service_definitions/sales/prc_copy.yaml", "04_service_definitions/sales/prc_save.yaml", "04_service_definitions/sales/prc_search.yaml", "04_service_definitions/sales/quo_save.yaml", "04_service_definitions/sales/quo_search.yaml", "04_service_definitions/sales/rma_save.yaml", "04_service_definitions/sales/rma_search.yaml", "04_service_definitions/sales/so_fetch.yaml", "04_service_definitions/sales/so_search.yaml", "04_service_definitions/sales/srl_reg.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-ITM |
| Domain | Item Master & Inventory |
| Type | Error catalogue |
| Status | Current |

The `ERR-ITM` error code catalogue defines system validation messages raised when querying, updating, or referencing item master records in Ledgerline. These codes enforce data integrity across inventory operations, bill of materials and routing definitions, purchase requisitions, and sales order processing. Detailed narrative explanations and resolution paths for specific errors are documented on dedicated error pages such as [[err-itm-0011|ERR-ITM-0011]], [[err-itm-0001|ERR-ITM-0001]], and [[err-itm-0801|ERR-ITM-0801]].

### ERR-ITM-0001
* **Message**: `ITEM MASTER NOT FOUND` [^r7][^r9][^r11]
* **Cause**: An attempted operation references an item master record that does not exist in the system [^r7][^r9][^r11].
* **Remedy**: Verify the item code and ensure the item has been created in the item master table [^r7][^r11].
* **Raised by**: [[services-inv-itm|itm_block]] [^r7], `itm_uom_conv` [^r9], and `itm_update` [^r11].
* **Detailed page**: [[err-itm-0001|ERR-ITM-0001: Item code already exists in Item Master]]

### ERR-ITM-0010
* **Message**: `ITEM NOT FOUND` [^r44][^r45][^r46]
* **Cause**: The requested item code (`itm_cd`) cannot be found during retrieval or saving operations [^r44][^r45][^r46].
* **Remedy**: Check that the item code exists in the master tables before querying or submitting records [^r45][^r46].
* **Raised by**: `itm_get` [^r44], `pr_fetch` [^r45], and `pr_save` [^r46] (under [[services-pur-pr|PUR pr services]]).

### ERR-ITM-0011
* **Message**: `ITEM NOT FOUND OR INACTIVE` [^r2][^r3][^r4][^r5][^r6][^r7][^r8][^r10][^r13][^r14][^r15][^r16][^r17][^r18][^r19][^r20][^r21][^r22][^r23][^r24][^r25][^r26][^r27][^r28][^r29][^r30][^r31][^r32][^r33][^r34][^r35][^r36][^r37][^r38][^r39][^r40][^r41][^r42][^r43][^r46][^r47][^r48][^r49][^r50][^r51][^r52][^r53][^r54][^r55][^r56][^r57][^r58][^r59][^r60]
* **Cause**: The item code entered does not exist in the inventory master table or has been flagged as inactive or deactivated [^r1][^r19][^r38][^r46][^r56].
* **Remedy**: Verify that the item code is entered correctly and ensure its status is active in the inventory master [^r1].
* **Raised by**:
  * **Inventory**: [[services-inv-adj|adj_save]] [^r2], `adj_search` [^r3], [[services-inv-cnt|cnt_entry]] [^r4], [[services-inv-csg|csg_save]] [^r5], `csg_search` [^r6], `itm_block` [^r7], `itm_save` [^r8], `itm_uom_conv` [^r10], `itm_update` [^r13], [[services-inv-kbn|kbn_save]] [^r14], `kbn_search` [^r15], [[services-inv-lot|lot_save]] [^r16], `lot_search` [^r17], [[services-inv-mrn|mrn_search]] [^r18], [[services-inv-qch|qch_save]] [^r19], `qch_search` [^r20], [[services-inv-res|res_save]] [^r21], `res_search` [^r22], [[services-inv-scr|scr_save]] [^r23], `scr_search` [^r24], `stk_abc_run` [^r25], `stk_age_query` [^r26], `stk_move_query` [^r27], `stk_snapshot` [^r28], [[services-inv-stk|stk_val_run]] [^r29], and [[services-inv-txf|txf_search]] [^r30].
  * **Production**: [[services-prd-bom|bom_get]] [^r31], `bom_where_used` [^r32], `btt_search` [^r33], [[services-prd-mps|mps_get]] [^r34], `mps_save` [^r35], `mps_search` [^r36], `ncr_search` [^r37], `pkb_save` [^r38], [[services-prd-rtg|rtg_get]] [^r39], `rtg_save` [^r40], `rtg_search` [^r41], `scp_save` [^r42], and `wo_save` [^r43].
  * **Purchase**: `pr_save` [^r46].
  * **Sales**: `dmo_save` [^r47], `dmo_search` [^r48], [[services-sal-fcs|fcs_save]] [^r49], `fcs_upload` [^r50], `prc_copy` [^r51], [[services-sal-prc|prc_save]] [^r52], `prc_search` [^r53], [[services-sal-quo|quo_save]] [^r54], `quo_search` [^r55], [[services-sal-rma|rma_save]] [^r56], `rma_search` [^r57], [[services-sal-so|so_fetch]] [^r58], `so_search` [^r59], and `srl_reg` [^r60].
* **Detailed page**: [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]

### ERR-ITM-0801
* **Message**: `ITEM MASTER CLOSED (<status>)` [^r12]
* **Cause**: An update is attempted on an item master record that is in a closed status [^r12].
* **Remedy**: Reopen the item master record or adjust its status before executing master data updates [^r12].
* **Raised by**: `itm_update` [^r12].
* **Detailed page**: [[err-itm-0801|ERR-ITM-0801: Conversion factor invalid or calculation mismatch between units of measure]]

## See also
* [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]]
* [[screen-inv-adj-05|INV-ADJ-05 Stock Adjustment Entry]]
* [[screen-inv-cnt-06|INV-CNT-06 Stock Count Entry]]
* [[screen-inv-lot-10|INV-LOT-10 Lot / Serial Entry]]
* [[screen-inv-qch-11|INV-QCH-11 Quality Hold Entry]]
* [[screen-inv-res-12|INV-RES-12 Stock Reservation Entry]]
* [[screen-inv-kbn-13|INV-KBN-13 Kanban Card Entry]]
* [[screen-inv-scr-16|INV-SCR-16 Scrap Note Entry]]
* [[screen-inv-csg-17|INV-CSG-17 Consignment Stock Entry]]
* [[screen-inv-mrn-08|INV-MRN-08 Material Issue Entry]]
* [[screen-inv-trf-04|INV-TRF-04 Stock Transfer Entry]]
* [[screen-inv-stk-03|INV-STK-03 Stock Val]]
* [[screen-prd-bom-02|PRD-BOM-02 Bill Of Materials]]
* [[screen-prd-rtg-03|PRD-RTG-03 Routing]]
* [[screen-prd-mps-05|PRD-MPS-05 Master Schedule Entry]]
* [[screen-pur-pr-01|PUR-PR-01 Purchase Request Entry]]
* [[screen-sal-so-01|SAL-SO-01 Sales Order]]
* [[screen-sal-quo-02|SAL-QUO-02 Quotation Entry]]
* [[screen-sal-prc-08|SAL-PRC-08 Price List]]
* [[screen-sal-rma-07|SAL-RMA-07 Warranty Return (Rma) Entry]]
* [[screen-sal-fcs-14|SAL-FCS-14 Sales Forecast Entry]]
* [[screen-sal-dmo-17|SAL-DMO-17 Demo Bike Entry]]
* [[errors-stk|ERR-STK Error Codes]]

## References

[^r7]: 04_service_definitions/inventory/itm_block.yaml, errors
[^r9]: 04_service_definitions/inventory/itm_uom_conv.yaml, errors
[^r11]: 04_service_definitions/inventory/itm_update.yaml, errors
[^r44]: 04_service_definitions/purchase/itm_get.yaml, errors
[^r45]: 04_service_definitions/purchase/pr_fetch.yaml, errors
[^r46]: 04_service_definitions/purchase/pr_save.yaml, errors
[^r2]: 04_service_definitions/inventory/adj_save.yaml, errors
[^r3]: 04_service_definitions/inventory/adj_search.yaml, errors
[^r4]: 04_service_definitions/inventory/cnt_entry.yaml, errors
[^r5]: 04_service_definitions/inventory/csg_save.yaml, errors
[^r6]: 04_service_definitions/inventory/csg_search.yaml, errors
[^r8]: 04_service_definitions/inventory/itm_save.yaml, errors
[^r10]: 04_service_definitions/inventory/itm_uom_conv.yaml, errors
[^r13]: 04_service_definitions/inventory/itm_update.yaml, errors
[^r14]: 04_service_definitions/inventory/kbn_save.yaml, errors
[^r15]: 04_service_definitions/inventory/kbn_search.yaml, errors
[^r16]: 04_service_definitions/inventory/lot_save.yaml, errors
[^r17]: 04_service_definitions/inventory/lot_search.yaml, errors
[^r18]: 04_service_definitions/inventory/mrn_search.yaml, errors
[^r19]: 04_service_definitions/inventory/qch_save.yaml, errors
[^r20]: 04_service_definitions/inventory/qch_search.yaml, errors
[^r21]: 04_service_definitions/inventory/res_save.yaml, errors
[^r22]: 04_service_definitions/inventory/res_search.yaml, errors
[^r23]: 04_service_definitions/inventory/scr_save.yaml, errors
[^r24]: 04_service_definitions/inventory/scr_search.yaml, errors
[^r25]: 04_service_definitions/inventory/stk_abc_run.yaml, errors
[^r26]: 04_service_definitions/inventory/stk_age_query.yaml, errors
[^r27]: 04_service_definitions/inventory/stk_move_query.yaml, errors
[^r28]: 04_service_definitions/inventory/stk_snapshot.yaml, errors
[^r29]: 04_service_definitions/inventory/stk_val_run.yaml, errors
[^r30]: 04_service_definitions/inventory/txf_search.yaml, errors
[^r31]: 04_service_definitions/production/bom_get.yaml, errors
[^r32]: 04_service_definitions/production/bom_where_used.yaml, errors
[^r33]: 04_service_definitions/production/btt_search.yaml, errors
[^r34]: 04_service_definitions/production/mps_get.yaml, errors
[^r35]: 04_service_definitions/production/mps_save.yaml, errors
[^r36]: 04_service_definitions/production/mps_search.yaml, errors
[^r37]: 04_service_definitions/production/ncr_search.yaml, errors
[^r38]: 04_service_definitions/production/pkb_save.yaml, errors
[^r39]: 04_service_definitions/production/rtg_get.yaml, errors
[^r40]: 04_service_definitions/production/rtg_save.yaml, errors
[^r41]: 04_service_definitions/production/rtg_search.yaml, errors
[^r42]: 04_service_definitions/production/scp_save.yaml, errors
[^r43]: 04_service_definitions/production/wo_save.yaml, errors
[^r47]: 04_service_definitions/sales/dmo_save.yaml, errors
[^r48]: 04_service_definitions/sales/dmo_search.yaml, errors
[^r49]: 04_service_definitions/sales/fcs_save.yaml, errors
[^r50]: 04_service_definitions/sales/fcs_upload.yaml, errors
[^r51]: 04_service_definitions/sales/prc_copy.yaml, errors
[^r52]: 04_service_definitions/sales/prc_save.yaml, errors
[^r53]: 04_service_definitions/sales/prc_search.yaml, errors
[^r54]: 04_service_definitions/sales/quo_save.yaml, errors
[^r55]: 04_service_definitions/sales/quo_search.yaml, errors
[^r56]: 04_service_definitions/sales/rma_save.yaml, errors
[^r57]: 04_service_definitions/sales/rma_search.yaml, errors
[^r58]: 04_service_definitions/sales/so_fetch.yaml, errors
[^r59]: 04_service_definitions/sales/so_search.yaml, errors
[^r60]: 04_service_definitions/sales/srl_reg.yaml, errors
[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 5, Messages
[^r12]: 04_service_definitions/inventory/itm_update.yaml, errors
