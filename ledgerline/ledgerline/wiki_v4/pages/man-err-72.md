---
title: "MAN-ERR-72 Ledgerline ERP 7.2 Message and Error Code"
type: "manual"
slug: "man-err-72"
summary: "Ledgerline ERP 7.2 message and error code manual detailing code structure, prefix definitions, and module error listings."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | MAN-ERR-72 |
| Title | Ledgerline ERP 7.2 Message and Error Code Manual |
| Version | v7.2.3 |
| Effective Date | 2025-01-15 |
| Status | current |
| Module | Ledgerline System-wide |

MAN-ERR-72 provides the definitive system reference for message and diagnostic codes raised across Ledgerline ERP 7.2 [^r1]. It defines the standard structure distinguishing blocking validation errors from non-blocking alerts, cataloguing their associated business rules, database entities, and backend service calls [^r1][^r2]. As of 26 October 2026, version 7.2.3 remains the operational manual across all functional modules [^r1].

| Field | Detail |
|---|---|
| Code | MAN-ERR-72 |
| Version | v7.2.3 |
| Date | 2025-01-15 |
| Status | Current |

## Structure of Ledgerline Messages

Ledgerline error codes prefixed with `ERR-` refuse the requested action and prevent saving, whereas warning codes prefixed with `W-` allow the transaction to complete while alerting the user to required follow-up [^r1]. The second element within any message code denotes the specific system module or functional area, such as PO for purchase order, SUP for supplier, or GRN for goods receipt [^r2].

## Core Modules and Cross-Functional Codes

### Approvals and Budgetary Control
Approval validations enforce segregation of duties and authority thresholds across multiple document workflows:
* [[err-apr-0003|ERR-APR-0003]] prevents self-approval when an approver attempts to approve a document they raised across PR, PO, adjustment, scrap, payment, advance, expense, RMA, and ECN workflows [^r3].
* [[err-apr-0004|ERR-APR-0004]] is raised by approval services when a document's value exceeds the approver's authorization limit [^r4].
* [[err-apr-0009|ERR-APR-0009]] is raised during `pr_submit`, `po_save`, or `po_amend` when no user in the submitter's management line holds an approval limit covering the document value [^r5].
* Error ERR-BUD-0207 is triggered by `po_save`, `po_amend`, `bud_check`, and `bud_transfer` when a document's gross value exceeds the cost centre's available quarterly budget [^r8].

### Banking and Payables
Supplier banking validations ensure disbursement security prior to settlement:
* [[err-bnk-0101|ERR-BNK-0101]] indicates bank details for the supplier are unverified, preventing payment approval and payment file generation [^r6].
* [[err-bnk-0125|ERR-BNK-0125]] is triggered by `bnk_verify` when a supplier bank detail verification call-back has not been recorded [^r7].
* Error ERR-CRN-0001 ('SUPPLIER CREDIT NOTE NOT FOUND') is raised by `crn_get` and `crn_post` when no supplier credit note record exists for that key [^r24].
* Error ERR-CRN-0007 ('SUPPLIER CREDIT NOTE NOT IN DRAFT (<status>)') is raised by `crn_post` when the supplier credit note is not in Draft or pending status [^r25].

### Cost Centres and System Configuration
* [[err-cc-0310|ERR-CC-0310]] ('OPEN DOCUMENTS ON COST CENTRE') indicates the rule 'open documents on cost centre' failed, and is raised by `cc_close` [^r9].
* Error ERR-CC-0801 ('COST CENTRE CLOSED (<status>)') indicates the cost centre document is closed, cancelled, or rejected, and is raised by `cc_close` [^r10].
* Error ERR-CFG-0001 ('MENU CONFIG NOT FOUND') is raised by `cfg_get` when no menu configuration record exists for that key [^r12].
* [[err-cur-0001|ERR-CUR-0001]] ('CURRENCY RATE NOT FOUND') is raised by `cur_get` when no currency rate record exists for that key [^r28].

### Inventory, Stock Counting, and Consignment
* [[err-ccp-0001|ERR-CCP-0001]] ('CYCLE COUNT PLAN NOT FOUND') is raised by `ccp_get` and `ccp_generate` when no cycle count plan record exists for the key [^r11].
* Error ERR-CNT-0001 ('STOCK COUNT NOT FOUND') is raised by `cnt_get`, `cnt_entry`, `cnt_freeze`, `cnt_post`, and `cnt_cancel` when no stock count document exists for the key [^r13].
* Error ERR-CNT-0007 ('STOCK COUNT NOT IN DRAFT (<status>)') is raised by `cnt_freeze` and `cnt_post` when the stock count is not in Draft or pending status [^r14].
* Error ERR-CNT-0105 ('DATE IN PAST') is raised by `cnt_save` when the date entered is before today [^r15].
* Error ERR-CNT-0201 ('QTY MUST BE > 0') is raised by `cnt_entry` when entered quantity is zero or negative [^r16].
* [[err-cnt-0230|ERR-CNT-0230]] ('OPEN TRANSACTIONS IN COUNT AREA') is raised by `cnt_freeze` when the open transactions validation in the count area fails [^r17].
* [[err-cnt-0240|ERR-CNT-0240]] ('VARIANCE ABOVE TOLERANCE, RECOUNT REQUIRED') is raised by `cnt_post` when recount tolerance validation fails [^r18].
* Error ERR-CNT-0801 ('STOCK COUNT CLOSED (<status>)') is raised by `cnt_cancel` when attempting to cancel a stock count that is already closed, cancelled, or rejected [^r19].
* [[err-csg-0001|ERR-CSG-0001]] ('CONSIGNMENT STOCK NOT FOUND') is raised by `csg_get` and `csg_settle` when no consignment stock record exists for that key [^r26].
* [[err-csg-0201|ERR-CSG-0201]] ('QTY MUST BE > 0') is raised by `csg_save`, `csg_search`, and `csg_settle` when quantity is zero or negative [^r27].

### Sales, Customers, and Credit Control
* [[err-com-0001|ERR-COM-0001]] ('SALES COMMISSION NOT FOUND') is raised by `com_get` when no commission document with that key exists [^r20].
* [[err-crd-0001|ERR-CRD-0001]] ('CREDIT CONTROL NOT FOUND') is raised by `crd_check`, `crd_hold_list`, and `crd_release` when no credit control record exists for that key [^r21].
* Error ERR-CRD-0007 ('CREDIT CONTROL NOT IN DRAFT (<status>)') is raised by `crd_release` when credit control is not in Draft or pending status [^r22].
* [[err-crd-0207|ERR-CRD-0207]] ('CREDIT LIMIT EXCEEDED (<cust_cd>)') is raised by `so_confirm` when credit limit validation fails for customer code `<cust_cd>` [^r23].
* [[err-cus-0001|ERR-CUS-0001]] ('CUSTOMER MASTER NOT FOUND') is raised by `cust_get`, `cust_update`, `cust_block`, and `cust_credit` when no customer master record exists for that key [^r29].
* Error ERR-CUS-0031 ('CUSTOMER ON HOLD') is raised by `so_save` when the customer on hold rule fails [^r30].

## See also

* [[errors-apr]]
* [[errors-bnk]]
* [[errors-bud]]
* [[errors-po]]
* [[errors-sup]]
* [[services-pur-po]]
* [[services-pur-bud]]
* [[services-ap-bnk]]
* [[services-inv-cnt]]
* [[services-sal-so]]

## References

[^r1]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 1, §1. How to read a message
[^r2]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 1, §1. How to read a message
[^r3]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 2, §2. Codes
[^r4]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 2, §2. Codes
[^r5]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 2, §2. Codes
[^r8]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 4, §2. Codes
[^r6]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 3, §2. Codes
[^r7]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 3, §2. Codes
[^r24]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 6, ERR-CRN-0001
[^r25]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 6, ERR-CRN-0007
[^r9]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 5, ERR-CC-0310
[^r10]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 5, ERR-CC-0801
[^r12]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 5, ERR-CFG-0001
[^r28]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 6, ERR-CUR-0001
[^r11]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 5, ERR-CCP-0001
[^r13]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 5, ERR-CNT-0001
[^r14]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 5, ERR-CNT-0007
[^r15]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 5, ERR-CNT-0105
[^r16]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 5, ERR-CNT-0201
[^r17]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 5, ERR-CNT-0230
[^r18]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 5, ERR-CNT-0240
[^r19]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 6, ERR-CNT-0801
[^r26]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 6, ERR-CSG-0001
[^r27]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 6, ERR-CSG-0201
[^r20]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 6, ERR-COM-0001
[^r21]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 6, ERR-CRD-0001
[^r22]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 6, ERR-CRD-0007
[^r23]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 6, ERR-CRD-0207
[^r29]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 7, ERR-CUS-0001
[^r30]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 7, ERR-CUS-0031
