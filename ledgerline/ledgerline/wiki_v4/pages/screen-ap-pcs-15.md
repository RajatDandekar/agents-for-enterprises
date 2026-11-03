---
title: "AP-PCS-15 Petty Cash Entry"
type: "screen"
slug: "screen-ap-pcs-15"
summary: "AP-PCS-15 Petty Cash Entry creates, retrieves, and posts petty cash vouchers to the nominal ledger."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/accounts_payable/pcs_get.yaml", "04_service_definitions/accounts_payable/pcs_post.yaml", "04_service_definitions/accounts_payable/pcs_save.yaml", "04_service_definitions/accounts_payable/pcs_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen | AP-PCS-15 |
| Title | Petty Cash Entry |
| Module | Accounts Payable |
| Save Key | F8 |
| Post Key | F9 |
| Fetch Key | F3 |
| Search Key | F2 / Enter |
| Status | Current |

Screen AP-PCS-15 (Petty Cash Entry) records, searches, and posts petty cash vouchers within Ledgerline Accounts Payable [^r1][^r5]. The voucher number is generated automatically on initial save and must be endorsed across physical receipts in permanent ink [^r2]. Posting through the screen validates against the nominal ledger and finalises the voucher into posted status [^r4].

| Field | Label | Type | Description |
|---|---|---|---|
| `ou_cd` | OU CD | Mandatory | Operating unit code [^r1][^r5]. |
| `amount` | AMOUNT | Mandatory | Petty cash voucher monetary amount [^r1][^r5]. |
| `purpose` | PURPOSE | Mandatory | Business justification or reason for expenditure [^r1][^r5]. |
| `cc_cd` | CC CD | Mandatory | Cost centre code assigned for the expense [^r1][^r5]. |
| `pcs_no` | PCS NO | Mandatory | Petty cash voucher number, left blank on new entry and assigned upon initial save [^r1][^r2][^r5]. |
| `status` | STATUS | Optional | Current state of the voucher record [^r1]. |
| `comment` | COMMENT | Optional | Additional narrative remarks [^r1][^r9]. |

## Fields

Mandatory inputs required on the screen are `ou_cd`, `amount`, `purpose`, `cc_cd`, and `pcs_no` [^r1][^r5]. On new voucher creation, `pcs_no` remains empty until system allocation upon initial save [^r2]. Optional fields comprise `status` and `comment` [^r1].

## Keys and services

* **F8 (Save):** Calls [[services-ap-pcs|pcs_save]] to store draft petty cash records using mandatory fields `ou_cd`, `amount`, `purpose`, and `cc_cd` [^r6][^r12].
* **F3 (Get):** Triggers `pcs_get` to retrieve an individual voucher by its mandatory `pcs_no` key [^r6][^r10].
* **F2 / Enter (Search):** Invokes `pcs_search` to list existing vouchers filtered by current site selection, matching on `ou_cd`, `amount`, `purpose`, or `status` [^r3][^r6][^r8][^r13].
* **F9 (Post):** Executes the backend posting routine via `pcs_post` (calling stored procedure `sp_pcs_post`) with `pcs_no` and optional `comment`, validating the nominal ledger, locking the transaction, and setting the voucher to posted status [^r4][^r6][^r9][^r11].

## Messages

* [[err-cc-0009|ERR-CC-0009]]: Cost Centre Not Found [^r7].
* [[err-pcs-0001|ERR-PCS-0001]]: Petty Cash Not Found, raised during voucher lookup or post handling [^r7][^r9].
* [[err-pcs-0007|ERR-PCS-0007]]: Petty Cash Not In Draft (<Status>), triggered when attempting to post a non-draft record [^r7][^r9].

## See also

* [[services-ap-pcs|AP pcs services]]
* [[err-cc-0009|ERR-CC-0009]]
* [[err-pcs-0001|ERR-PCS-0001]]
* [[err-pcs-0007|ERR-PCS-0007]]
* [[screen-ap-inv-01|AP-INV-01 Supplier Invoice Entry]]
* [[screen-ap-exp-09|AP-EXP-09 Expense Claim Entry]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 55, §17. Petty Cash (AP-PCS-15)
[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 9, AP-PCS-15 PETTY CASH ENTRY
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 57, Final posting:
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 57, Final posting:
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 37, pcs_post PETTY CASH POST
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 9, AP-PCS-15 PETTY CASH ENTRY
[^r12]: 04_service_definitions/accounts_payable/pcs_save.yaml, whole file
[^r10]: 04_service_definitions/accounts_payable/pcs_get.yaml, service: pcs_get
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 56, Retrieving existing records:
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 37, pcs_search PETTY CASH LIST
[^r13]: 04_service_definitions/accounts_payable/pcs_search.yaml, whole file
[^r11]: 04_service_definitions/accounts_payable/pcs_post.yaml, whole file
[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 9, AP-PCS-15 PETTY CASH ENTRY
