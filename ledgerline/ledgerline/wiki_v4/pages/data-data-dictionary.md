---
title: "Ledgerline_7.2_tables_and_fields"
type: "data-source"
slug: "data-data-dictionary"
summary: "Data dictionary cataloguing Ledgerline 7.2 database tables, field specifications, document status codes, and system error message definitions across six core ERP modules."
audience: "staff"
status: "current"
sources: ["07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf", "07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Source file | 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx |
| Manual reference | MAN-DD-72-ALL |
| ERP version | 7.2 |
| Total tables | 114 |
| Total field definitions | 784 |
| Total error codes | 269 |
| Document status codes | 7 |

The Ledgerline 7.2 tables and fields data dictionary provides the authoritative schema structure for Northbridge Cycles' ERP system [^r9][^r15]. It defines table relations, field definitions, data types, standard document lifecycle statuses, and system error codes across core operational modules [^r9][^r16][^r19][^r27]. System users, administrators, and integrations rely on this dictionary to interpret table keys, validate error conditions, and maintain data consistency across purchasing, inventory, manufacturing, and finance workflows [^r1][^r2][^r4][^r27].

## What it holds

The workbook defines the complete relational schema and messaging architecture for Ledgerline 7.2 across four dedicated worksheets: `Tables`, `Fields`, `Status codes`, and `Error codes` [^r9][^r15][^r19][^r27].

The system organizes its data model into six functional modules: ADM, AP, INV, PRD, PUR/core, and SAL [^r9][^r16]. Core module tables cover purchasing and general system administration, such as `org_unit`, `app_user`, `role_perm`, `item`, `supplier`, `sup_cert`, `sup_rate`, `warehouse`, `stock`, `stk_ledger`, `cost_centre`, `budget`, `tax_code`, `pay_term`, `doc_seq`, `pr_hdr`, `pr_line`, `po_hdr`, `po_line`, `approval`, `ntf_queue`, `fetch_tok`, and `audit_trail` [^r1]. Administration and configuration tables also include `ou_hdr`, `cc_hdr`, `bud_hdr`, `ses_hdr`, `lic_hdr`, `ntf_hdr`, `prt_hdr`, `imp_hdr`, `api_hdr`, `sys_hdr`, and `cfg_hdr` [^r39]. Accounts payable tables catalogue financial transactions across `inv_hdr`, `mat_hdr`, `dbn_hdr`, `crn_hdr`, `pay_hdr`, `bnk_hdr`, `adv_hdr`, `sbal_hdr`, `acr_hdr`, `per_hdr`, `vat_hdr`, `exp_hdr`, `cur_hdr`, `gl_hdr`, `pcs_hdr`, `sup_pay_hdr`, and `tax_hdr` [^r4].

Inventory tables encompass `grn_hdr`, `grn_line`, `txf_hdr`, `adj_hdr`, `cnt_hdr`, `rtv_hdr`, `mrn_hdr`, `bin_hdr`, `lot_hdr`, `qch_hdr`, `res_hdr`, and `whs_hdr` [^r2]. Additional inventory tracking tables include `itm_hdr` (recording the `cell_safety` flag and `reorder_lvl`), `stk_hdr`, `kbn_hdr`, `ccp_hdr`, `pkg_hdr`, `scr_hdr`, and `csg_hdr` [^r3]. Sales distribution operates via `cust_hdr`, `so_hdr`, `quo_hdr`, `alc_hdr`, `pck_hdr`, `dlv_hdr`, `sinv_hdr`, `rma_hdr`, `prc_hdr`, and `dsc_hdr` [^r5]. Production tables include `btt_hdr` for recording battery test parameters such as open circuit voltage (`ocv`) and internal resistance (`ir_mohm`), as well as `ecn_hdr` for tracking engineering change notices with effective date `eff_dt`, change description, and reason [^r7][^r8]. User accounts are detailed in `usr_hdr`, which defines parameters including approval limits (`appr_limit`, gross including VAT) and default cost centres (`default_cc`) [^r6].

The dictionary records the seven universal document statuses: DR (Draft), PA (Pending approval), AP (Approved), RL (Released), RJ (Rejected), CN (Cancelled), and CL (Closed) [^r19][^r20][^r21][^r22][^r23][^r24][^r25][^r26][^r40]. It also inventories application error codes across modules, covering delivery, engineering changes, expenses, goods receipt notes, item masters, batch jobs, and three-way invoice matching [^r34]. Specific examples include [[err-acr-0001|ERR-ACR-0001]] ("GRNI ACCRUAL NOT FOUND"), ERR-API-0120 (unassigned service account owner), [[err-bnk-0125|ERR-BNK-0125]] (unrecorded supplier call-back), ERR-BTT-0120 (out-of-range open-circuit voltage), [[err-cc-0310|ERR-CC-0310]] (open documents assigned to cost centre), [[err-cnt-0240|ERR-CNT-0240]] (variance exceeding recount tolerance), and [[err-dlv-0320|ERR-DLV-0320]] ("LITHIUM BATTERY LABEL NOT PRINTED") [^r28][^r29][^r30][^r31][^r32][^r33][^r35]. Three-way matching error definitions include ERR-MAT-0410 ("MATCH FAILED: PRICE OUTSIDE TOLERANCE"), ERR-MAT-0411 ("MATCH FAILED: QTY INVOICED > QTY RECEIVED"), and ERR-MAT-0412 ("NO GRN FOR PO LINE") [^r36][^r37][^r38].

## Columns

* **Tables**: lists table metadata across Ledgerline ERP modules [^r9]. Columns include module and table definitions [^r9][^r10]. For example, `org_unit` contains 4 columns, `app_user` contains 10 columns, `role_perm` contains 2 columns, `item` contains 8 columns, and `supplier` contains 9 columns under the PUR/core module [^r10][^r11][^r12][^r13][^r14].
* **Fields**: contains 7 columns: `key`, `table`, `column`, `type`, `pk`, `description`, and `module` [^r15]. Column types are restricted to `INT`, `INTEGER`, `REAL`, and `TEXT` [^r16].
* **Status codes**: contains 2 columns: `code` and `meaning` [^r19].
* **Error codes**: contains 3 columns: `code`, `message`, and `module` [^r27].

## How to look up a row

* To inspect a specific database field, search sheet `Fields` using the composite key format `table.column` in the `key` column (for example, `org_unit.ou_cd` or `app_user.user_id`) [^r15][^r17][^r18].
* To identify table membership, filter the `Tables` sheet by table name or module [^r9][^r10].
* To resolve document processing states, match the two-character code in sheet `Status codes` against column `code` [^r19][^r20].
* To look up an ERP error message, search sheet `Error codes` by the primary error string in column `code` (such as `ERR-DLV-0320` or `ERR-CNT-0240`) [^r27][^r33][^r35].

## Size

* **Tables**: catalogues 114 database tables across 6 modules [^r9].
* **Fields**: contains 784 data rows across 114 tables, comprising 247 distinct column names, 4 distinct data types, and 105 designated primary keys [^r15][^r16].
* **Status codes**: contains 7 rows [^r19][^r40].
* **Error codes**: contains 269 data rows [^r27].

## See also

* [[man-dd-72-all|MAN-DD-72-ALL Ledgerline ERP 7.2 Data Dictionary: all]]
* [[topic-status-codes|Document Status Codes]]
* [[errors-cc|Cost Centre Error Codes (ERR-CC-*)]]
* [[errors-cnt|Stock Count Error Codes (ERR-CNT-*)]]
* [[errors-mat|ERR-MAT message and error codes]]
* [[errors-bnk|Errors BNK]]
* [[err-dlv-0320|ERR-DLV-0320 Lithium Battery Label Required]]
* [[err-cnt-0240|ERR-CNT-0240 Cycle Count Value Variance Exceeds Tolerance]]
* [[err-cc-0310|ERR-CC-0310 Cost centre has open documents]]
* [[sop-ap-001|SOP-AP-001 Three-Way Invoice Matching]]
* [[sop-prd-002|SOP-PRD-002 Engineering Change (ECN)]]
* [[pol-bat-004|POL-BAT-004 Battery Safety and Handling Policy]]

## References

[^r9]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Tables, SHEET Tables
[^r15]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Fields, SHEET Fields
[^r16]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Fields, SHEET Fields
[^r19]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Status codes, SHEET Status codes
[^r27]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, SHEET Error codes
[^r1]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 2, Module PUR/core
[^r2]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 6, Module INV
[^r4]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 10, Module AP
[^r39]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 23, Table ou_hdr
[^r3]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 9, Table itm_hdr
[^r5]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 13, Module SAL
[^r7]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 19, Table btt_hdr
[^r8]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 19, Table ecn_hdr
[^r6]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 21, Table usr_hdr
[^r20]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Status codes, row DR, ALL 7 ROWS
[^r21]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Status codes, row PA, ALL 7 ROWS
[^r22]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Status codes, row AP, ALL 7 ROWS
[^r23]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Status codes, row RL, ALL 7 ROWS
[^r24]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Status codes, row RJ, ALL 7 ROWS
[^r25]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Status codes, row CN, ALL 7 ROWS
[^r26]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Status codes, row CL, ALL 7 ROWS
[^r40]: 07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf, p. 24, Status codes
[^r34]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, SHEET Error codes
[^r28]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-ACR-0001, SHEET Error codes
[^r29]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-API-0120, SHEET Error codes
[^r30]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-BNK-0125, SHEET Error codes
[^r31]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-BTT-0120, SHEET Error codes
[^r32]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-CC-0310, SHEET Error codes
[^r33]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-CNT-0240, SHEET Error codes
[^r35]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-DLV-0320, SHEET Error codes
[^r36]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-MAT-0410, SHEET Error codes
[^r37]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-MAT-0411, SHEET Error codes
[^r38]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-MAT-0412, SHEET Error codes
[^r10]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Tables, row org_unit, SHEET Tables
[^r11]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Tables, row app_user, SHEET Tables
[^r12]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Tables, row role_perm, SHEET Tables
[^r13]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Tables, row item, SHEET Tables
[^r14]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Tables, row supplier, SHEET Tables
[^r17]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Fields, row org_unit.ou_cd, SHEET Fields
[^r18]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Fields, row app_user.user_id, SHEET Fields
