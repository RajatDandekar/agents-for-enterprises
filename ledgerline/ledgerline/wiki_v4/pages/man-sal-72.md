---
title: "MAN-SAL-72 Ledgerline ERP 7.2 User Manual: Sales and"
type: "manual"
slug: "man-sal-72"
summary: "User manual for Ledgerline ERP 7.2 Sales and Distribution covering quotations, sales orders, allocations, pick lists, despatches, and invoicing."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | MAN-SAL-72 |
| Title | Ledgerline ERP 7.2 User Manual: Sales and Distribution |
| Version | 7.2.3 |
| Effective date | 2025-01-15 |
| Author | Documentation Group |
| Status | current |
| Module | Sales and Distribution |

MAN-SAL-72 is the vendor reference manual for the Sales and Distribution module of Ledgerline ERP 7.2 [^r1]. It details the operational procedures, core screens, backend services, and validation error codes for processing quotations, sales orders, stock allocations, pick lists, physical despatches, and customer billing [^r8][^r9][^r13][^r20][^r23][^r27]. The manual documents active integration rules between sales transactions and finished goods inventory across Northbridge Cycles' Manchester and Leeds sites [^r3][^r15].

| Field | Value |
|---|---|
| Document Code | MAN-SAL-72 |
| System Version | Ledgerline ERP 7.2 (v7.2.3) |
| Author | Documentation Group |
| Effective Date | 2025-01-15 |
| Module | Sales and Distribution |
| Status | Current |

## Overview and system integration

Ledgerline ERP 7.2 automatically terminates any session left idle for 20 minutes, which closes the session and clears unsaved work from temporary memory [^r2]. 

Sales processing connects directly with inventory, purchasing, and finance modules [^r3][^r4][^r5]:
* **Inventory**: Entering a sales order line checks finished goods stock at the relevant facility, and recording a despatch deducts physical stock across both Manchester and Leeds [^r3].
* **Purchasing**: Out-of-stock items and bicycle frames scheduled from external production batches feed directly from sales lines into the reorder schedule to generate purchase orders [^r4].
* **Finance**: Confirming a despatch sends transaction data to the sales ledger, and final invoicing debits the customer account, records turnover in the general ledger, and recalculates customer credit limits [^r5].

## Screens and processes

### Quotation (`SAL-QUO-02`)
The [[screen-sal-quo-02|SAL-QUO-02]] screen (menu **Sales > Quotation**) manages price indications using [[services-sal-quo|quo services]] (`quo_save`, `quo_get`, `quo_search`, `quo_convert`, and `quo_cancel`) [^r9].
* **Creation**: Users enter `CUST CD`, line item `ITEM CD`, `QTY`, `PRICE`, `VALID TO`, and an optional `COMMENT` before calling `quo_save`, which triggers `QUOTATION SAVE`, assigns a sequential `QUO NO`, and sets the record `STATUS` to open [^r10].
* **Conversion**: Pressing `quo_convert` executes `QUOTATION CONVERT` to transfer quotation lines into sales order processing, create a sales order reference, and update `STATUS` to closed by conversion [^r11].
* **Cancellation**: Cancelling or recording a lapsed quotation requires an explanation entered in the mandatory `REASON` field before pressing `quo_cancel`, which triggers `QUOTATION CANCEL` and locks all record fields [^r12].

### Sales Order (`SAL-SO-01`)
The [[screen-sal-so-01|SAL-SO-01]] screen is accessed via menu **Sales > Sales order** [^r8]. It operates using [[services-sal-so|so services]], specifically `so_fetch`, `so_save`, `so_get`, `so_search`, `so_confirm`, `so_cancel`, `so_amend`, `so_hold`, and `so_release` [^r8].

### Allocation (`SAL-ALC-03`)
Screen [[screen-sal-alc-03|SAL-ALC-03]] (menu **Sales > Allocation**) earmarks finished goods stock against confirmed sales orders prior to warehouse picking [^r13]. At Northbridge Cycles, assembled electric bicycles at Manchester and stored units at Leeds must be formally reserved using this screen to prevent stock depletion by counter sales or competing despatches [^r15].
* **Fields**: Header entries require `SO NO` (`so_no`) and `REASON` (`reason`), while `COMMENT` (`comment`) remains optional [^r14].
* **Services**: Managed via [[services-sal-alc|alc services]] (`alc_run`, `alc_get`, and `alc_cancel`) [^r13]. Running `alc_run` executes `ALLOCATION RUN` to assign available physical stock in pickable bins across all eligible lines of the order [^r16][^r17]. 
* **De-allocation**: Lines awaiting future manufacturing runs can be cleared using `alc_cancel`, which triggers `ALLOCATION CANCEL` to return quantities to the unallocated inventory pool [^r16][^r17]. Internal audit rules require a full explanation in the `REASON` field whenever finished bicycles are de-allocated from a bike shop order [^r18].

### Pick List (`SAL-PCK-04`)
Screen [[screen-sal-pck-04|SAL-PCK-04]] (menu **Sales > Pick list**) generates picking documentation using [[services-sal-pck|pck services]] [^r20][^r22].
* **Prerequisites**: Sales orders must be in confirmed status with an approved credit position; orders in draft, suspended, or credit-stopped states cannot generate pick lists [^r21].
* **Fields**: Mandatory header fields are `SO NO` (`so_no`), `WHS CD` (`whs_cd`), and `PCK NO` (`pck_no`); `STATUS` (`status`) and `COMMENT` (`comment`) are optional [^r20].
* **Confirmation**: Running `pck_confirm` commits picked items, sets `STATUS` to fully confirmed, closes lines to prevent further allocation changes, and locks `COMMENT` from subsequent editing [^r22].

### Despatch (`SAL-DLV-05`)
Screen [[screen-sal-dlv-05|SAL-DLV-05]] (menu **Sales > Despatch**) records outbound shipments and operates using [[services-sal-dlv|dlv services]] (`dlv_save`, `dlv_get`, `dlv_search`, `dlv_post`, `dlv_cancel`, and `dlv_label`) [^r23].
* **Fields**: Mandatory fields comprise `PICK NO` (`pck_no`), `CARRIER` (`carrier_cd`), `PARCELS` (`parcels`), `DLV NO` (`dlv_no`), and `REASON` (`reason`) [^r24]. Optional fields include `WEIGHT KG` (`weight_kg`), `STATUS` (`status`), and `COMMENT` (`comment`) [^r24].
* **Posting**: Executing a despatch reduces finished goods stock levels, marks the pick list completed, creates an internal delivery reference for invoicing, and officially logs the inventory as removed from company ownership [^r25].

### Sales Invoice (`SAL-INV-06`)
Screen [[screen-sal-inv-06|SAL-INV-06]] (menu **Sales > Sales invoice**) generates billing documents using [[services-sal-sinv|sinv services]] (`sinv_save`, `sinv_get`, `sinv_search`, `sinv_post`, `sinv_cancel`, and `sinv_print`) [^r27].
* **Draft Generation**: Standard invoicing starts by specifying the delivery reference in `DLV NO` or locating it via `sinv_search` [^r28].
* **Data Extraction**: Executing `sinv_get` retrieves customer accounts, payment terms, billed quantities, serial numbers, net prices, and freight additions, setting `INV DT` to the current system date and tagging `STATUS` as provisional or unposted [^r29].
* **Saving**: Running `sinv_save` validates line balances, issues the next sequential invoice number in `SINV NO`, and stores the record in draft status [^r30].

## Error codes and troubleshooting

* [[err-cus-0001|ERR-CUS-0001]]: Triggered during customer creation via `cust_save` (managed by [[services-sal-cust|cust services]]) if a required field such as `CUST NAME`, `CITY`, `COUNTRY CD (2)`, or `PAY TERM CD` is missing [^r6].
* [[err-cus-0801|ERR-CUS-0801]]: Indicates a duplicate database entry, usually caused by attempting to register a VAT number that is already assigned to an existing customer record [^r7].
* **ERR-ALC-0801**: If this allocation error appears when physical stock is present at the Manchester facility, unit supervisors must ensure final inspection sign-off has been completed, as bicycles marked as work in progress cannot be allocated [^r19]. Listed under [[errors-alc|ERR-ALC error codes]].
* [[err-dlv-0320|ERR-DLV-0320]]: Raised on [[screen-sal-dlv-05|SAL-DLV-05]] when attempting to post a despatch containing battery packs while system parameter `SAL.DG_LABEL_REQ` is set to `Y`; posting is blocked until the required lithium battery transport label is printed [^r26].

## See also

* [[sop-sal-001|SOP-SAL-001 Sales Order to Despatch]]
* [[screen-sal-so-01|SAL-SO-01 Sales Order]]
* [[screen-sal-quo-02|SAL-QUO-02 Quotation Entry]]
* [[screen-sal-alc-03|SAL-ALC-03 Allocation]]
* [[screen-sal-pck-04|SAL-PCK-04 Pick List Entry]]
* [[screen-sal-dlv-05|SAL-DLV-05 Despatch Entry]]
* [[screen-sal-inv-06|SAL-INV-06 Sales Invoice Entry]]
* [[services-sal-so|SAL so services]]
* [[services-sal-quo|SAL quo services]]
* [[services-sal-alc|SAL alc services]]
* [[services-sal-pck|SAL pck services]]
* [[services-sal-dlv|SAL dlv services]]
* [[services-sal-sinv|SAL sinv services]]
* [[services-sal-cust|SAL cust services]]
* [[err-cus-0001|ERR-CUS-0001 Mandatory Field Missing or Invalid in Customer Master]]
* [[err-cus-0801|ERR-CUS-0801 Invalid or Duplicate VAT Number]]
* [[err-dlv-0320|ERR-DLV-0320 Lithium Battery Label Required]]
* [[errors-alc|Errors ALC (ERR-ALC-*)]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 1, Version history
[^r8]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 7, §4. Sales Order (SAL-SO-01)
[^r9]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 11, §5. Quotation (SAL-QUO-02)
[^r13]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 15, §6. Allocation (SAL-ALC-03)
[^r20]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 18, §7. Pick List (SAL-PCK-04)
[^r23]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 22, Despatch (SAL-DLV-05)
[^r27]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 25, §9. Sales Invoice (SAL-INV-06)
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 2, Integration with other modules
[^r15]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 15, Purpose
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 2, §2. Signing in and sessions
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 2, Integration with other modules
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 2, Integration with other modules
[^r10]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 12, Raising a new quotation
[^r11]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 13, Converting a quotation to a firm order
[^r12]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 13, Cancelling or recording a lapsed quotation
[^r14]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 15, §6. Allocation (SAL-ALC-03)
[^r16]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 16, Step by Step
[^r17]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 17, Questions users ask
[^r18]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 17, Questions users ask
[^r22]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 21, Questions users ask
[^r21]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 18, Before you start
[^r24]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 22, Despatch (SAL-DLV-05)
[^r25]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 22, Purpose
[^r28]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 27, Step by step
[^r29]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 27, Step by step
[^r30]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 27, Step by step
[^r6]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 7, Questions users ask
[^r7]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 7, Questions users ask
[^r19]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 17, Questions users ask
[^r26]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 25, Questions users ask
