---
title: "INV-GRN-03 Goods Receipt Note (Grn)"
type: "screen"
slug: "screen-inv-grn-03"
summary: "Ledgerline screen for receipting physical deliveries against released purchase orders, capturing received quantities, and writing delivery notes to generate GRNs."
audience: "staff"
status: "current"
sources: ["02_procedures/sop_inv_001_goods_receipt_v2.docx", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/inventory/grn_save.yaml", "11_training/QRC-04 Goods receipt.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | INV-GRN-03 |
| Title | Goods Receipt Note (GRN) |
| Module | Inventory |
| Read service | po_get |
| Write service | grn_save |
| Status | Current |

INV-GRN-03 is the Ledgerline inventory screen used by stores personnel to record incoming physical deliveries against existing purchase orders [^r1][^r7]. It verifies that the target purchase order is released and has an outstanding balance before committing receipts into stock [^r2][^r6]. Each transaction posts through underlying inventory services, generating a distinct Goods Receipt Note (GRN) even for partial shipments and automatically closing orders when balances reach zero [^r6][^r7][^r15].

| Field | Value |
|---|---|
| Screen code | INV-GRN-03 [^r4] |
| Title | Goods Receipt Note (GRN) [^r4] |
| Primary write service | grn_save [^r7][^r8] |
| Primary read service | po_get [^r5] |
| Key search lookups | po_search (F2), whs_list (F2), grn_search [^r4][^r5] |

## Fields

* **PO NO (`po_no`)**: Mandatory purchase order number entry field, supporting `po_search` lookup via F2 [^r4]. Users fetch the record by entering the number and triggering the retrieve action [^r1][^r9].
* **SUP CD**: Read-only supplier code populated upon fetching the order [^r4]. Operators must check that the retrieved supplier matches the physical delivery paperwork before receipting goods [^r10].
* **PO STATUS**: Read-only document status [^r4]. The order must be in released status (`RL`) to allow processing [^r2][^r6].
* **GRN NO**: Read-only system-assigned Goods Receipt Note identifier [^r4]. A distinct GRN number is assigned to each delivery, including partial orders [^r15].
* **PO BALANCE**: Read-only outstanding quantity remaining on the purchase order lines [^r4].
* **Receipts grid**: Read-only display of fetched order line items [^r4].
* **QTY RECD (`qty`)**: Mandatory quantity received against each displayed purchase order line, entered after completing physical counts of the delivered items [^r4][^r11].
* **WHS CD (`whs_cd`)**: Optional destination warehouse code, supporting selection via F2 `whs_list` [^r4]. For sensitive items such as lithium cells, receiving personnel must verify that this destination is set to `WH-MAN-QC` prior to saving [^r3].
* **DELIVERY NOTE NO / REMARKS (`remarks`)**: Optional text field used to capture the supplier's delivery note reference and carrier details [^r1][^r4]. Recording the delivery note reference accurately is required for Accounts to complete invoice matching, and any visible carrier transit damage to outer cartons must be noted here [^r12][^r13].

## Keys and services

* **F2**: Invokes `po_search` when focused on the PO NO field, or `whs_list` when focused on the WHS CD field [^r4].
* **F3 (Fetch)**: Executes the `po_get` service to retrieve purchase order lines, balances, and status [^r5]. Users can alternatively trigger this by clicking the on-screen Fetch button [^r1][^r9].
* **F8 (Save)**: Invokes write service `grn_save` via `POST /ll72/svc/grn_save` to commit verified line quantities and generate the receipt note record [^r5][^r8][^r14].
* **Fetch History**: Executes `grn_search` to review historical goods receipts [^r5].

## Messages

* **[[err-grn-0102|ERR-GRN-0102]]**: Raised when attempting to fetch or process a purchase order whose document status is not released (`RL`) [^r2][^r6].
* **[[err-grn-0204|ERR-GRN-0204]]**: Raised when an entered received quantity exceeds the available line balance on the purchase order [^r6].
* **Order closure (`CL`)**: An automatic system status transition that closes the purchase order once all outstanding line items have been fully received [^r6].

## See also

* [[services-inv-grn|INV grn services]]
* [[services-pur-po|PUR po services]]
* [[err-grn-0102|ERR-GRN-0102 Purchase order not released]]
* [[err-grn-0204|ERR-GRN-0204 Over-receipt exceeds order balance]]
* [[screen-pur-por-05|PUR-POR-05 Purchase Order Release]]
* [[screen-qa-ins-01|QA-INS-01 Incoming Inspection Entry]]
* [[screen-ap-mat-02|AP-MAT-02 Three-Way Match]]

## References

[^r1]: 02_procedures/sop_inv_001_goods_receipt_v2.docx, §5. Procedure
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 8, §3. Inventory services
[^r2]: 02_procedures/sop_inv_001_goods_receipt_v2.docx, §5. Procedure: notes and common mistakes
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 14, INV-GRN-03 GOODS RECEIPT NOTE (GRN)
[^r15]: 11_training/QRC-04 Goods receipt.pdf, p. 1, Steps
[^r4]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 14, INV-GRN-03 GOODS RECEIPT NOTE (GRN)
[^r8]: 04_service_definitions/inventory/grn_save.yaml, whole file
[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 14, INV-GRN-03 GOODS RECEIPT NOTE (GRN)
[^r9]: 11_training/QRC-04 Goods receipt.pdf, p. 1, Steps
[^r10]: 11_training/QRC-04 Goods receipt.pdf, p. 1, Fetching purchase orders
[^r11]: 11_training/QRC-04 Goods receipt.pdf, p. 1, Physical checks and counts
[^r3]: 02_procedures/sop_inv_001_goods_receipt_v2.docx, §5. Procedure: notes and common mistakes
[^r12]: 11_training/QRC-04 Goods receipt.pdf, p. 1, Delivery paperwork and remarks
[^r13]: 11_training/QRC-04 Goods receipt.pdf, p. 1, Delivery paperwork and remarks
[^r14]: 11_training/QRC-04 Goods receipt.pdf, p. 1, Saving receipts and part orders
