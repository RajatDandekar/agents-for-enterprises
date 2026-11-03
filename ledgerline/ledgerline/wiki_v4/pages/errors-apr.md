---
title: "Errors APR"
type: "error-list"
slug: "errors-apr"
summary: "Catalogue of Ledgerline APR approval error codes covering self-approval restrictions, authority threshold limits, and missing routing hierarchy approvers."
audience: "staff"
status: "current"
sources: ["07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx", "01_policies/POL-APR-002 Approval Matrix v3.0.pdf", "03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "04_service_definitions/accounts_payable/adv_approve.yaml", "04_service_definitions/accounts_payable/exp_approve.yaml", "04_service_definitions/accounts_payable/pay_approve.xml", "04_service_definitions/inventory/adj_approve.yaml", "04_service_definitions/inventory/scr_approve.yaml", "04_service_definitions/production/ecn_approve.yaml", "04_service_definitions/purchase/pr_submit.yaml", "04_service_definitions/sales/rma_approve.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-APR |
| Module | APR (Approval Routing) |
| System | Ledgerline ERP 7.2 |
| Status | current |

The `ERR-APR-*` error code family governs transaction sign-off, authority validation, and management hierarchy routing within Ledgerline ERP 7.2 [^r1][^r2][^r3]. These validation errors prevent unapproved expenditure by enforcing policy restrictions against self-approval and checking assigned transaction value limits across purchasing, accounts payable, inventory, production, and sales workflows [^r5][^r8][^r9]. They also halt transactions when routing fails to find an approver with adequate authority in the hierarchy [^r4][^r10].

### ERR-APR-0003
* **Message**: `SELF APPROVAL NOT ALLOWED` [^r8][^r11][^r13][^r15][^r17][^r19][^r21][^r23]
* **Cause**: Raised when a creator or operator attempts to approve their own document or transaction, violating segregation of duties under [[pol-pur-001|Purchase Policy]] §5.3 [^r1][^r5][^r8][^r11][^r13][^r19].
* **Remedy**: Reassign or submit the transaction to an independent authorised manager within the approval hierarchy [^r5][^r8].
* **Raised by**: `pr_approve`, `po_approve`, `adj_approve`, `scr_approve`, `pay_approve`, `adv_approve`, `exp_approve`, `rma_approve`, and `ecn_approve` [^r8][^r11][^r13][^r15][^r17][^r19][^r21][^r23].
* **Detailed page**: [[err-apr-0003]]

### ERR-APR-0004
* **Message**: `VALUE ABOVE YOUR LIMIT` [^r9][^r12][^r14][^r16][^r18][^r20][^r21][^r24]
* **Cause**: The document or transaction total exceeds the authorised role approval limit assigned to the user attempting sign-off [^r2][^r9][^r12][^r14][^r18][^r20][^r24].
* **Remedy**: Escalate the transaction to a higher-level approver whose delegation threshold covers the full value of the submission [^r9][^r20].
* **Raised by**: `pr_approve`, `po_approve`, `adj_approve`, `scr_approve`, `pay_approve`, `adv_approve`, `exp_approve`, `rma_approve`, and `ecn_approve` [^r8][^r9][^r12][^r14][^r16][^r18][^r20][^r21][^r24].
* **Detailed page**: [[err-apr-0004]]

### ERR-APR-0009
* **Message**: `NO APPROVER FOUND` [^r10][^r22]
* **Cause**: Raised during routing validation when no manager in the organizational hierarchy possesses an approval limit covering the total value of the document [^r3][^r10]. Under [[pol-apr-002|POL-APR-002]], orders exceeding £5,000,000 trigger this error because they require written approval from the Managing Director outside Ledgerline [^r4].
* **Remedy**: Check the organizational approval hierarchy settings, or route transactions over £5,000,000 for offline Managing Director sign-off [^r4][^r10].
* **Raised by**: `pr_submit`, `po_save`, and `po_amend` [^r10][^r22].
* **Detailed page**: [[err-apr-0009]]

## Versions and conflicts

* **Contradiction**: In general Ledgerline tables, core error definitions, and service schemas, ERR-APR-0003 is `SELF APPROVAL NOT ALLOWED` (creator approving own transaction) and ERR-APR-0004 is `VALUE ABOVE YOUR LIMIT` (transaction exceeds approver threshold) [^r1][^r2][^r8][^r9][^r11][^r12][^r13][^r14][^r15][^r16][^r17][^r18][^r19][^r20][^r21][^r23][^r24]. However, manual MAN-AP-72 v7.2.3 (2025-01-15) defines ERR-APR-0003 as lacking authority level to sign off disbursements for a chosen bank account, and ERR-APR-0004 as a segregation of duties violation where the pay proposal clerk attempts approval or release [^r6][^r7].

## See also

* [[err-apr-0003|ERR-APR-0003 Self-approval not permitted]]
* [[err-apr-0004|ERR-APR-0004 Advance amount exceeds PO unbilled commitment]]
* [[err-apr-0009|ERR-APR-0009 No approver found]]
* [[pol-apr-002|POL-APR-002 Approval Matrix for Purchasing]]
* [[pol-pur-001|POL-PUR-001 Purchase Policy]]
* [[services-ap-adv|AP adv services]]
* [[services-ap-exp|AP exp services]]
* [[services-ap-pay|AP pay services]]
* [[services-prd-ecn|PRD ecn services]]
* [[services-pur-po|PUR po services]]
* [[services-pur-pr|PUR pr services]]
* [[services-sal-rma|SAL rma services]]

## References

[^r1]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-APR-0003, SHEET Error codes
[^r2]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-APR-0004, SHEET Error codes
[^r3]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-APR-0009, SHEET Error codes
[^r5]: 01_policies/POL-APR-002 Approval Matrix v3.0.pdf, p. 2, §4. Who may not approve
[^r8]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 2, §2. Codes
[^r9]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 2, §2. Codes
[^r4]: 01_policies/POL-APR-002 Approval Matrix v3.0.pdf, p. 1, §3. The limits
[^r10]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 2, §2. Codes
[^r11]: 04_service_definitions/accounts_payable/adv_approve.yaml, errors
[^r13]: 04_service_definitions/accounts_payable/exp_approve.yaml, errors
[^r15]: 04_service_definitions/accounts_payable/pay_approve.xml, ll:errors
[^r17]: 04_service_definitions/inventory/adj_approve.yaml, errors
[^r19]: 04_service_definitions/inventory/scr_approve.yaml, errors
[^r21]: 04_service_definitions/production/ecn_approve.yaml, errors
[^r23]: 04_service_definitions/sales/rma_approve.yaml, errors
[^r12]: 04_service_definitions/accounts_payable/adv_approve.yaml, errors
[^r14]: 04_service_definitions/accounts_payable/exp_approve.yaml, errors
[^r16]: 04_service_definitions/accounts_payable/pay_approve.xml, ll:errors
[^r18]: 04_service_definitions/inventory/adj_approve.yaml, errors
[^r20]: 04_service_definitions/inventory/scr_approve.yaml, errors
[^r24]: 04_service_definitions/sales/rma_approve.yaml, errors
[^r22]: 04_service_definitions/purchase/pr_submit.yaml, errors
[^r6]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 20, Messages
[^r7]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 20, Messages
