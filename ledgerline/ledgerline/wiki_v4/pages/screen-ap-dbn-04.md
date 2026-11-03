---
title: "AP-DBN-04 Debit Note Entry"
type: "screen"
slug: "screen-ap-dbn-04"
summary: "Ledgerline screen for creating, retrieving, posting, and cancelling debit notes against supplier accounts when invoices are already posted."
audience: "staff"
status: "current"
sources: ["01_policies/POL-RET-006 Returns Policy v2.1.pdf", "03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/accounts_payable/dbn_cancel.yaml", "04_service_definitions/accounts_payable/dbn_get.yaml", "04_service_definitions/accounts_payable/dbn_post.yaml", "04_service_definitions/accounts_payable/dbn_save.yaml", "04_service_definitions/accounts_payable/dbn_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen | AP-DBN-04 |
| Title | Debit Note Entry |
| Menu path | Accounts payable > Debit note |
| Roles | AP-CLERK, AP-MGR, FIN-CTRL, SYS-ADMIN |
| Read service | dbn_get |
| Write services | dbn_save, dbn_post, dbn_cancel |
| Status | Current |

AP-DBN-04 Debit Note Entry is the Ledgerline screen used to raise and manage debit notes against supplier accounts [^r2]. When a supplier invoice has already been posted, staff must enter a debit note on this screen rather than processing an RTV credit [^r1]. Posting a debit note on AP-DBN-04 creates an open credit item in the purchase ledger, reducing the balance owed to the supplier for matching during payment run preparation [^r3].

| Field | Value |
|---|---|
| Screen | AP-DBN-04 |
| Name | Debit Note Entry |
| Menu path | Accounts payable > Debit note |
| Allowed roles | AP-CLERK, AP-MGR, FIN-CTRL, SYS-ADMIN |
| Services | dbn_save, dbn_get, dbn_search, dbn_post, dbn_cancel |
| Status | Current |

## Fields

Screen AP-DBN-04 contains the following fields [^r10][^r20]:

* **DBN NO** (`dbn_no`): Mandatory [^r10][^r20]. When creating a new draft, this field must be left blank because Ledgerline assigns the serial sequence automatically upon saving [^r5].
* **SUP CD** (`sup_cd`): Mandatory; the supplier code [^r10][^r20].
* **REF DOC** (`ref_doc`): Mandatory; the reference document number [^r10][^r20].
* **AMOUNT** (`amount`): Mandatory; the monetary debit note amount [^r10][^r20].
* **REASON CD** (`reason_cd`): Mandatory; validated against the reason dictionary [^r6][^r10][^r20].
* **REASON** (`reason`): Mandatory; protected field automatically populated with the description corresponding to the entered reason code [^r6][^r10][^r20].
* **STATUS** (`status`): Optional [^r10][^r20].
* **COMMENT** (`comment`): Optional [^r10][^r20].

If a retrieved debit note is already posted or cancelled, all fields remain display-only and cannot be modified [^r4].

## Keys and services

AP-DBN-04 is accessed via menu path Accounts payable > Debit note by roles AP-CLERK, AP-MGR, FIN-CTRL, and SYS-ADMIN [^r2][^r9]. It executes the following function keys and underlying [[services-ap-dbn|AP dbn services]]:

* **Save (F8)**: Calls write service `dbn_save` to create or update draft records, requiring `sup_cd`, `ref_doc`, `amount`, and `reason_cd` [^r11][^r18].
* **Get (F3)**: Calls read service `dbn_get` to retrieve debit note details using `dbn_no` [^r11][^r14]. Voided records remain visible for audit via this function [^r8].
* **Search (F2 / Enter)**: Calls service `dbn_search` to find and list debit notes using optional criteria such as supplier code, reference document, amount, and status [^r11][^r19].
* **Post (F9)**: Calls write service `dbn_post` via endpoint `POST /ll72/svc/dbn_post` and stored procedure `sp_dbn_post` [^r11][^r15]. It requires `dbn_no`, accepts an optional `comment`, updates `STATUS` to posted, applies the debit balance to the supplier account ledger, and locks the record against further edits [^r7][^r16].
* **Cancel (Shift+F8)**: Calls write service `dbn_cancel` to cancel an unposted debit note [^r11][^r13]. This marks the record as void, preventing future reactivation [^r8].

## Messages

The screen enforces validation rules using the following messages:

* [[err-sup-0030|ERR-SUP-0030]]: Supplier Not Found [^r12].
* [[err-dbn-0001|ERR-DBN-0001]]: Debit Note Not Found [^r12][^r17].
* [[err-dbn-0007|ERR-DBN-0007]]: Debit Note Not In Draft (`<Status>`) [^r12][^r17].
* [[err-dbn-0801|ERR-DBN-0801]]: Debit Note Closed (`<Status>`) [^r12].

## See also

* [[pol-ret-006|POL-RET-006 Returns Policy]]
* [[services-ap-dbn|AP dbn services]]
* [[screen-ap-pay-03|AP-PAY-03 Payment Run]]
* [[screen-inv-rtv-07|INV-RTV-07 Return To Vendor Entry]]
* [[err-dbn-0001|ERR-DBN-0001]]
* [[err-dbn-0007|ERR-DBN-0007]]
* [[err-dbn-0801|ERR-DBN-0801]]
* [[err-sup-0030|ERR-SUP-0030]]

## References

[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 10, §5. Debit Note (AP-DBN-04)
[^r1]: 01_policies/POL-RET-006 Returns Policy v2.1.pdf, p. 2, §2. Returns to suppliers
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 11, Purpose
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 6, AP-DBN-04 DEBIT NOTE ENTRY
[^r20]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 10, §5. Debit Note (AP-DBN-04)
[^r5]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 12, To create and save a new draft debit note:
[^r6]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 12, To create and save a new draft debit note:
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 12, To create and save a new draft debit note:
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 5, AP-DBN-04 DEBIT NOTE ENTRY
[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 6, AP-DBN-04 DEBIT NOTE ENTRY
[^r18]: 04_service_definitions/accounts_payable/dbn_save.yaml, service: dbn_save
[^r14]: 04_service_definitions/accounts_payable/dbn_get.yaml, service: dbn_get
[^r8]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 12, To cancel an unposted debit note:
[^r19]: 04_service_definitions/accounts_payable/dbn_search.yaml, whole file
[^r15]: 04_service_definitions/accounts_payable/dbn_post.yaml, header
[^r7]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 12, To post the debit note:
[^r16]: 04_service_definitions/accounts_payable/dbn_post.yaml, request.fields
[^r13]: 04_service_definitions/accounts_payable/dbn_cancel.yaml, whole file
[^r12]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 6, AP-DBN-04 DEBIT NOTE ENTRY
[^r17]: 04_service_definitions/accounts_payable/dbn_post.yaml, errors
