---
title: "MAN-DD-72-ALL Ledgerline ERP 7.2 Data Dictionary: all"
type: "manual"
slug: "man-dd-72-all"
summary: "Complete data dictionary specification for Ledgerline ERP 7.2 detailing database tables and fields across core business modules."
audience: "staff"
status: "current"
sources: ["07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf", "07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | MAN-DD-72-ALL |
| Title | Ledgerline ERP 7.2 Data Dictionary: all |
| Owner | Ledgerline Systems, Documentation Group |
| Version | 7.2.3 |
| Effective | 2025-01-15 |
| Status | current |
| Modules | PUR/core, INV, AP, SAL, PRD, ADM |

The Ledgerline ERP 7.2 Data Dictionary defines the database schema and table relationships across all operational modules at Northbridge Cycles [^r1]. Effective from 15 January 2025 under document version v7.2.3, it provides the definitive structural reference for transaction processing, reporting, and backend data integrity [^r1]. Across its covered modules, the full ERP implementation comprises 784 field definitions distributed over 114 distinct database tables [^r31].

| Property | Value |
|---|---|
| Document Code | MAN-DD-72-ALL [^r1] |
| Version | 7.2.3 [^r1] |
| Effective Date | 2025-01-15 [^r1] |
| Owner | Ledgerline Systems, Documentation Group [^r1] |
| Status | current [^r1] |
| Scope | PUR/core, INV, AP, SAL, PRD, ADM, Status codes [^r1] |

## Schema Overview

The complete Ledgerline ERP 7.2 database architecture comprises 784 field definitions across 114 distinct tables spanning the ADM, AP, INV, PRD, PUR/core, and SAL modules [^r31]. Structured technical definitions for each column are catalogued in the master spreadsheet [[data-data-dictionary|Ledgerline_7.2_tables_and_fields]] [^r31]. Purchasing-specific operational subsets of this schema are further summarized in [[man-dd-72|MAN-DD-72 Ledgerline ERP 7.2 Data Dictionary, Purchasing]].

## Module PUR/core

Module PUR/core encapsulates foundational organization structures, system access controls, procurement lifecycles, and financial accounting dimensions [^r1].

### Organization and Access Control

* **`org_unit`**: Represents operating entities using primary key `ou_cd`, alongside `name`, `state` (holding a two-letter country code following the 1998 naming convention), and `city` [^r2][^r32].
* **`app_user`**: Stores user authentication and hierarchy data with primary key `user_id`, `name`, `role_cd`, `ou_cd`, `appr_limit` (gross approval limit inclusive of VAT), `manager_id`, `password`, `default_cc`, `email`, and `slack` handle [^r3]. Approval ceilings link directly to purchasing thresholds in [[pol-apr-002|POL-APR-002 Approval Matrix for Purchasing]].
* **`role_perm`**: Associates permissions by mapping role codes (`role_cd`) to executable service codes (`svc`) [^r4]. Violations raise access errors documented in [[errors-usr|ERR-USR Error Codes]] or [[errors-per|ERR-PER Error Codes]].

### Items and Master Data

* **`item`**: Defines part numbers using primary key `itm_cd`, `descr`, `uom_cd`, `cell_safety` (a lithium-cell flag set to 1 or 0 by Quality), `category`, `active`, `reorder_lvl`, and `avg_daily_issue` [^r5]. Lithium safety compliance links to [[pol-bat-004|POL-BAT-004 Battery Safety and Handling Policy]] and [[topic-un-38-3-certificates|UN 38.3 Certificates]]. Data issues invoke [[errors-mat|ERR-MAT message and error codes]].
* **`supplier`**: Maintains vendor accounts via primary key `sup_cd`, `name`, `vat_no`, `state` (two-letter country code following the 1998 convention), `city`, `status`, payment term code `pt_cd`, `created_by`, and `created_on` [^r6]. Validation rules are enforced through [[errors-sup|ERR-SUP Error Codes]].
* **`sup_cert`**: Tracks vendor accreditations using `sup_cd`, `cert_type` (such as UN38.3 or ISO-9001), `doc_ref`, `valid_to`, `uploaded_by`, and `uploaded_on` [^r7].
* **`sup_rate`**: Details item contract pricing across `sup_cd`, `itm_cd`, contracted `rate`, `valid_from`, and `valid_to` [^r8].

### Warehousing and Financial Dimensions

* **`warehouse`**: Defines locations via primary key `whs_cd`, `name`, and owning organization unit `ou_cd` [^r9].
* **`stock`**: Aggregates site inventory per `itm_cd` and `whs_cd` across balances `on_hand`, `allocated`, and `on_order` [^r9].
* **`stk_ledger`**: Logs individual inventory transactions using integer primary key `id`, `itm_cd`, `whs_cd`, transaction date `dt`, transaction type `txn`, quantity `qty`, and reference `ref` [^r10].
* **`cost_centre`**: Establishes overhead tracking with primary key `cc_cd`, `name`, `status`, `closed_on`, and `owner` [^r11]. Processing constraints relate to [[errors-cc|Cost Centre Error Codes (ERR-CC-*)]].
* **`budget`**: Records financial allocations against `cc_cd`, `period`, baseline `amount`, and `committed` amount [^r11].
* **`tax_code`**: Governs tax rates through primary key `tax_cd`, `descr`, percentage `rate`, and tax `kind` [^r12]. Discrepancies between supplier state and tax code trigger [[err-po-0412|ERR-PO-0412 TAX CODE DOES NOT MATCH SUPPLIER COUNTRY]].
* **`pay_term`**: Holds settlement terms under primary key `pt_cd`, `descr`, and credit `days` [^r12]. Operational issues are recorded in [[errors-pay|Errors PAY]] or [[errors-bnk|Errors BNK]].
* **`doc_seq`**: Manages system numbering series using primary key `doc_type`, `prefix`, `next_no`, and zero-fill `width` [^r13].

### Purchasing Workflow

* **`pr_hdr`**: Stores purchase requisition headers identified by primary key `pr_no`, along with `ou_cd`, `pr_type`, `cc_cd`, `need_dt`, `whs_cd`, `remarks`, `status`, `raised_by`, `raised_on`, `approved_by`, and estimated gross value `est_value` (calculated as quantity multiplied by estimated rate multiplied by 1.20) [^r14]. Header errors generate [[errors-pr|ERR-PR Error Codes]]. Document states adhere to [[topic-status-codes|Document Status Codes]].
* **`pr_line`**: Tracks requisition detail lines using `pr_no`, `line_no`, `itm_cd`, `qty`, and `uom_cd` [^r15].
* **`po_hdr`**: Manages purchase order headers via primary key `po_no`, `ou_cd`, `sup_cd`, source `pr_no`, `po_type`, `cc_cd`, `tax_cd`, `pt_cd`, `need_dt`, `whs_cd`, `status`, `basic_value`, `tax_value`, `gross_value`, `created_by`, `created_on`, `approved_by`, `approved_on`, `released_on`, `client_ref`, and `warn_cd` [^r16]. Line or order failures surface in [[errors-po|ERR-PO Error Codes]].
* **`po_line`**: Details order line items under `po_no`, `line_no`, `itm_cd`, `qty`, `uom_cd`, and unit `rate` [^r17].
* **`approval`**: Maintains authorization histories with primary key `appr_id`, `doc_type`, `doc_no`, assigned `approver`, decision `status`, `requested_by`, `requested_on`, `decided_on`, and `comment` [^r18]. Rejections or routing failures produce [[errors-apr|Errors APR]].

### System Infrastructure and Messaging

* **`ntf_queue`**: Manages outbound communication queues using integer primary key `id`, dispatch `channel`, `recipient`, `subject`, `body`, and queue timestamp `created_on` [^r19].
* **`fetch_tok`**: Tracks stateful user interface fetch tokens using primary key `tok`, `user_id`, active `screen`, context `ctx`, `created_on`, and integer flag `used` [^r20].
* **`audit_trail`**: Captures low-level transaction logs through integer primary key `id`, timestamp `ts`, executing `user_id`, service name `svc`, XML/JSON `payload`, return code `rc`, and resulting error code `err_cd` [^r21].

## Module INV

Module INV governs physical goods receipts, storage allocations, warehouse transfers, adjustments, counting, and quality tracking [^r1].

### Receipts and Warehouse Movements

* **`grn_hdr`**: Records goods receipt headers under primary key `grn_no`, source `po_no`, destination `whs_cd`, `received_by`, `received_on`, and `remarks` [^r22]. Processing feeds into [[sop-ap-001|SOP-AP-001 Three-Way Invoice Matching]] and receipt validation in [[errors-grn|Errors GRN Goods Receipt Note]].
* **`grn_line`**: Details received item lines containing `grn_no`, `line_no`, `itm_cd`, and accepted `qty` [^r22].
* **`txf_hdr`**: Controls inter-warehouse transfers with primary key `txf_no`, transferred `itm_cd`, `from_whs`, `to_whs`, `qty`, transfer `reason`, document `status`, `created_by`, and `created_on` [^r23]. Processing exceptions report under [[errors-txf|Stock Transfer Error Codes (ERR-TXF-*)]].
* **`bin_hdr`**: Registers warehouse storage locations using primary key `bin_cd`, parent `whs_cd`, `bin_type`, capacity `max_qty`, `status`, `created_by`, and `created_on` [^r28].

### Inventory Adjustments and Returns

* **`adj_hdr`**: Manages manual stock adjustments using primary key `adj_no`, `itm_cd`, target `whs_cd`, adjusted `qty`, reason code `reason_cd`, explanatory `remarks`, `status`, `created_by`, and `created_on` [^r24]. Posting issues invoke [[errors-adj|Stock Adjustment Error Codes (ERR-ADJ-*)]].
* **`cnt_hdr`**: Facilitates physical stock cycle counts using primary key `cnt_no`, `whs_cd`, count methodology `cnt_type`, location limits `bin_from` and `bin_to`, count date `cnt_dt`, `status`, `created_by`, and `created_on` [^r25]. Counting exceptions map to [[errors-cnt|Stock Count Error Codes (ERR-CNT-*)]].
* **`rtv_hdr`**: Governs return-to-vendor transactions through primary key `rtv_no`, origin `grn_no`, returned `qty`, `reason_cd`, non-conformance reference `ncr_no`, `remarks`, `status`, `created_by`, and `created_on` [^r26]. Discrepancies generate [[errors-rtv|ERR-RTV Return to Vendor Error Codes]].
* **`mrn_hdr`**: Tracks shop-floor material returns with primary key `mrn_no`, production order reference `wo_no`, returned `itm_cd`, `qty`, target `whs_cd`, `status`, `created_by`, and `created_on` [^r27]. Reversals connect with [[sop-prd-001|SOP-PRD-001 Work Order Release and Backflush]], [[sop-prd-002|SOP-PRD-002 Engineering Change (ECN)]], and [[errors-wo|ERR-WO error codes]].

### Quality and Traceability

* **`lot_hdr`**: Establishes batch traceability through primary key `lot_no`, `itm_cd`, supplying vendor `sup_cd`, manufacturing date `mfg_dt`, originating `grn_no`, `status`, `created_by`, and `created_on` [^r29].
* **`qch_hdr`**: Coordinates quality inspection holds using primary key `qch_no`, source `grn_no`, inspected `itm_cd`, quantity under check `qty`, inspection `reason`, inspection `status`, `created_by`, and `created_on` [^r30]. Workflows are executed under [[sop-qua-001|SOP-QUA-001 Incoming Inspection]].

## See also

* [[data-data-dictionary|Ledgerline_7.2_tables_and_fields]]
* [[man-dd-72|MAN-DD-72 Ledgerline ERP 7.2 Data Dictionary, Purchasing]]
* [[pol-apr-002|POL-APR-002 Approval Matrix for Purchasing]]
* [[pol-bat-004|POL-BAT-004 Battery Safety and Handling Policy]]
* [[topic-status-codes|Document Status Codes]]
* [[sop-ap-001|SOP-AP-001 Three-Way Invoice Matching]]
* [[sop-qua-001|SOP-QUA-001 Incoming Inspection]]
* [[sop-prd-001|SOP-PRD-001 Work Order Release and Backflush]]

## References

[^r1]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 1, Contents
[^r31]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Fields, SHEET Fields
[^r2]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 2, Module PUR/core
[^r32]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Fields, row org_unit.state, SHEET Fields
[^r3]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 2, Module PUR/core
[^r4]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 2, Module PUR/core
[^r5]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 2, Module PUR/core
[^r6]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 2, Module PUR/core
[^r7]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 3, Module PUR/core
[^r8]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 3, Module PUR/core
[^r9]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 3, Module PUR/core
[^r10]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 3, Module PUR/core
[^r11]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 3, Module PUR/core
[^r12]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 4, Module PUR/core
[^r13]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 4, Module PUR/core
[^r14]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 4, Module PUR/core
[^r15]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 4, Module PUR/core
[^r16]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 5, Module PUR/core
[^r17]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 5, Module PUR/core
[^r18]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 5, Module PUR/core
[^r19]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 5, Module PUR/core
[^r20]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 6, Module PUR/core
[^r21]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 6, Module PUR/core
[^r22]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 6, Module INV
[^r23]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 6, Module INV
[^r28]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 8, Module INV
[^r24]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 7, Module INV
[^r25]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 7, Module INV
[^r26]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 7, Module INV
[^r27]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 7, Module INV
[^r29]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 8, Module INV
[^r30]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 8, Module INV
