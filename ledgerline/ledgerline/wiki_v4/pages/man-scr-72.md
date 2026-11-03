---
title: "MAN-SCR-72 Ledgerline ERP 7.2 Screen Reference"
type: "manual"
slug: "man-scr-72"
summary: "Reference manual defining screen layouts, service field names, function key mappings, and status bar messages across Ledgerline ERP 7.2."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | MAN-SCR-72 |
| owner | Ledgerline Systems Documentation Group |
| version | 7.2.3 |
| effective | 2025-01-15 |
| status | current |
| audience | staff |

MAN-SCR-72 is the comprehensive screen reference manual for Ledgerline ERP 7.2, covering interface layouts, data dictionary service field names, and service integrations across all enterprise modules [^r1][^r2]. As of 26 October 2026, version 7.2.3 serves as the current operational specification for Northbridge Cycles [^r1]. It establishes core navigational standards, lookup mechanisms, and direct function key mappings for terminal and desktop users [^r2][^r3].

| Attribute | Details |
|---|---|
| Document Code | MAN-SCR-72 [^r1] |
| Title | Ledgerline ERP 7.2 Screen Reference [^r1] |
| Version | 7.2.3 [^r1] |
| Effective Date | 2025-01-15 [^r1] |
| Owner | Ledgerline Systems Documentation Group [^r1] |
| Classification | CURRENT internal documentation [^r1] |

## Navigation, Lookups, and System Integration

Every screen entry in the reference specifies the full menu navigation path, authorized user roles, functional action buttons linked to underlying services, and terminal notifications, with Northbridge-customised interfaces explicitly designated by '(NBC)' [^r2]. When working in data entry screens, pressing F2 opens an interactive lookup selection list for system entities that require predefined codes, such as part numbers and supplier records [^r3]. Retrieved system details populate directly into read-only grey display fields that cannot be altered on screen [^r4].

System prompts, input alerts, validation notices, and execution messages print along the bottom status bar rather than inside modal pop-up dialogue boxes [^r6]. Furthermore, external software interfaces, automated system jobs, and operational reports interact exclusively through standardized service field names specified in the system data dictionary, ignoring descriptive user interface labels [^r5].

## Financial and Accounts Payable Screens

The reference establishes specifications and service mappings for standard Accounts Payable workflows:

* [[screen-ap-adv-07|AP-ADV-07]] (Advance Payment Entry): Menu path `Accounts payable > Advance payment`, restricted to roles `AP-CLERK`, `AP-MGR`, `FIN-CTRL`, and `SYS-ADMIN` [^r7]. Captures `sup_cd`, `po_no`, `amount`, `adv_no`, `status`, and `comment` [^r7]. Maps F8 to `adv_save`, F3 to `adv_get`, F2/Enter to `adv_search`, F9 to `adv_approve`, and provides `adv_adjust` via an unkeyed control button [^r8].
* [[screen-ap-bnk-06|AP-BNK-06]] (Supplier Bank Details Entry): Menu path `Accounts payable > Supplier bank`, accessible by `AP-CLERK`, `AP-MGR`, `FIN-CTRL`, and `SYS-ADMIN` [^r9]. Maintains bank attributes `sup_cd`, `acct_name`, `sort_cd`, `acct_no`, `iban`, `bic`, `reason`, and `status` [^r9]. Binds F8 to `bnk_save`, F2/Enter to `bnk_search`, and executes `bnk_get`, `bnk_verify`, and `bnk_block`, triggering warnings like `W-BNK-120` and errors such as [[err-bnk-0118|ERR-BNK-0118]] and [[err-bnk-0125|ERR-BNK-0125]] [^r10].
* [[screen-ap-crn-05|AP-CRN-05]] (Supplier Credit Note Entry): Menu path `Accounts payable > Supplier credit` [^r11]. Requires mandatory fields `sup_cd`, `sup_crn_no`, `amount`, and `crn_no`, with optional parameters `ap_doc`, `status`, and `comment` [^r11].
* [[screen-ap-cur-13|AP-CUR-13]] (Currency Rate): Menu path `Accounts payable > Currency rate` [^r12]. Manages currency conversions to GBP via mandatory fields `cur_cd`, `rate_dt`, and `rate`, utilizing services `cur_get` (F3), `cur_save` (F8), and `cur_list` [^r12].
* [[screen-ap-dbn-04|AP-DBN-04]] (Debit Note Entry): Menu path `Accounts payable > Debit note` [^r13]. Requires mandatory inputs `sup_cd`, `ref_doc`, `amount`, `reason_cd`, `dbn_no`, and `reason` [^r13]. Maps F8 to `dbn_save`, F3 to `dbn_get`, F2/Enter to `dbn_search`, F9 to `dbn_post`, and Shift+F8 to `dbn_cancel` [^r13].
* [[screen-ap-exp-09|AP-EXP-09]] (Expense Claim Entry): Menu path `Accounts payable > Expense claim` [^r14]. Requires `user_id`, `claim_dt`, `amount`, `cc_cd`, `exp_type`, `exp_no`, and `reason` [^r14]. Binds F8 to `exp_save`, F3 to `exp_get`, F2/Enter to `exp_search`, F9 to `exp_submit` and `exp_approve`, Shift+F9 to `exp_reject`, and provides `exp_pay` [^r14].
* [[screen-ap-gl-14|AP-GL-14]] (GL Posting): Menu path `Accounts payable > Gl posting` [^r15]. Binds F9 to `gl_post` alongside `gl_query` and `gl_reverse`, requiring mandatory `jv_no` alongside optional fields `comment`, `jv_dt`, `acct_cd`, `amount`, and `reason` [^r15].
* [[screen-ap-inv-01|AP-INV-01]] (Supplier Invoice Entry): Menu path `Accounts payable > Supplier invoice` [^r16]. Mandates fields `sup_cd`, `sup_inv_no`, `inv_dt`, `basic`, `tax_cd`, `gross`, `ap_doc`, and `reason` [^r16]. Controls `inv_save` (F8), `inv_get` (F3), `inv_search` (F2/Enter), `inv_post` (F9), `inv_cancel` (Shift+F8), `inv_hold`, and `inv_release` (F9) [^r16].
* [[screen-ap-mat-02|AP-MAT-02]] (Three-Way Match): Menu path `Accounts payable > Three-Way match` [^r17]. Operates on mandatory `ap_doc` and optional attributes `comment`, `tol_pct`, and `status`, exposing services `mat_run`, `mat_get` (F3), `mat_override`, and `mat_search` (F2/Enter) [^r17].
* [[screen-ap-pay-03|AP-PAY-03]] (Payment Run): Menu path `Accounts payable > Payment run` [^r18]. Governs payment cycles via mandatory `run_dt`, `bank_cd`, `due_upto`, `run_no`, and `reason`, handling `pay_propose`, `pay_get` (F3), `pay_approve` (F9), `pay_release` (F9), `pay_file`, `pay_cancel` (Shift+F8), and `pay_search` (F2/Enter) [^r18].
* [[screen-ap-pcs-15|AP-PCS-15]] (Petty Cash Entry): Menu path `Accounts payable > Petty cash`, authorized for roles `AP-CLERK`, `AP-MGR`, `FIN-CTRL`, and `SYS-ADMIN` [^r19].
* [[screen-ap-per-11|AP-PER-11]] (AP Period): Handles accounting period lifecycle via services `per_list`, `per_close`, `per_open`, and `per_status` [^r20].
* [[screen-ap-sbl-08|AP-SBL-08]] (Supplier Balance): Accepts optional criteria `sup_cd` and `as_on`, binding queries to `sbal_query`, `sbal_ageing`, and `sbal_stmt` [^r21].
* [[screen-ap-spy-16|AP-SPY-16]] (Supplier Payment Hold Hold): Maps hold execution to `sup_pay_hold` and release execution to `sup_pay_release` (F9) [^r22].
* [[screen-ap-tax-17|AP-TAX-17]] (Tax Code Master): Governs tax definition tables using mandatory fields `TAX CD`, `DESCR`, `RATE`, and `INTRA/INTER`, assigning `tax_get` to F3 and `tax_save` to F8 [^r23].
* [[screen-ap-vat-12|AP-VAT-12]] (Vat Return): Binds execution button Run to `vat_run`, Get to F3 (`vat_get`), and Rc List to `vat_rc_list` [^r24].

## General Financial and Inventory Operations

* [[screen-fin-bud-02|FIN-BUD-02]] (Budget Entry): Menu path `System > Budget` for roles `IT-ADMIN` and `SYS-ADMIN` [^r25]. Binds F8 to `bud_save`, alongside actions `bud_transfer` and `bud_query` [^r25].
* [[screen-fin-cc-01|FIN-CC-01]] (Cost Centre Entry): Requires mandatory attributes `CC CD`, `NAME`, and `OWNER`, supporting `cc_save` via F8, `cc_close`, and `cc_reopen` [^r26].
* [[screen-inv-adj-05|INV-ADJ-05]] (Stock Adjustment Entry): Binds F9 to `adj_approve` and `adj_post`, and Shift+F8 to `adj_cancel` [^r27].
* [[screen-inv-bin-09|INV-BIN-09]] (Bin Master Entry): Requires mandatory identifiers `WHS CD` and `BIN CD`, linking blocking operations to `bin_block` [^r28].
* [[screen-inv-ccp-14|INV-CCP-14]] (Cycle Count Plan Entry): Contains mandatory criteria `whs_cd` and `freq_days`, binding schedule creation to `ccp_generate` [^r29].
* [[screen-inv-cnt-06|INV-CNT-06]] (Stock Count Entry): Provides count reconciliation via services `cnt_entry`, `cnt_freeze`, `cnt_post` (F9), and `cnt_cancel` (Shift+F8) [^r30].

## See also

* [[services-ap-adv]]
* [[services-ap-bnk]]
* [[services-ap-crn]]
* [[services-ap-dbn]]
* [[services-ap-inv]]
* [[services-ap-mat]]
* [[services-ap-pay]]
* [[services-adm-par]]
* [[services-pur-po]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 1, About this reference
[^r2]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 3, About this reference
[^r3]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 3, Keyboard lookups and fetch operations
[^r4]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 3, Keyboard lookups and fetch operations
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 3, Status bar notifications
[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 3, Service field names and system integrations
[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 4, AP-ADV-07 ADVANCE PAYMENT ENTRY
[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 4, AP-ADV-07 ADVANCE PAYMENT ENTRY
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 4, AP-BNK-06 SUPPLIER BANK DETAILS ENTRY
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 5, AP-BNK-06 SUPPLIER BANK DETAILS ENTRY
[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 5, AP-CRN-05 SUPPLIER CREDIT NOTE ENTRY
[^r12]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 5, AP-CUR-13 CURRENCY RATE
[^r13]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 5, AP-DBN-04 DEBIT NOTE ENTRY
[^r14]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 6, AP-EXP-09 EXPENSE CLAIM ENTRY
[^r15]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 7, AP-GL-14 GL POSTING
[^r16]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 7, AP-INV-01 SUPPLIER INVOICE ENTRY
[^r17]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 8, AP-MAT-02 THREE-WAY MATCH
[^r18]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 8, AP-PAY-03 PAYMENT RUN
[^r19]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 9, AP-PCS-15 PETTY CASH ENTRY
[^r20]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 9, AP-PER-11 AP PERIOD
[^r21]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 10, AP-SBL-08 SUPPLIER BALANCE
[^r22]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 10, AP-SPY-16 SUPPLIER PAYMENT HOLD HOLD
[^r23]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 10, AP-TAX-17 TAX CODE MASTER
[^r24]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 11, AP-VAT-12 VAT RETURN
[^r25]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 11, FIN-BUD-02 BUDGET ENTRY
[^r26]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 11, FIN-CC-01 COST CENTRE ENTRY
[^r27]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 12, INV-ADJ-05 STOCK ADJUSTMENT ENTRY
[^r28]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 12, INV-BIN-09 BIN MASTER ENTRY
[^r29]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 12, INV-CCP-14 CYCLE COUNT PLAN ENTRY
[^r30]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 13, INV-CNT-06 STOCK COUNT ENTRY
