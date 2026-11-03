---
title: "AP-CRN-05 Supplier Credit Note Entry"
type: "screen"
slug: "screen-ap-crn-05"
summary: "Standard Accounts Payable screen for entering, searching, and posting credit notes issued by suppliers to offset invoices or create unallocated balances."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/accounts_payable/crn_get.yaml", "04_service_definitions/accounts_payable/crn_post.yaml", "04_service_definitions/accounts_payable/crn_save.yaml", "04_service_definitions/accounts_payable/crn_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | AP-CRN-05 |
| Title | Supplier Credit Note Entry |
| Module | Accounts Payable |
| Menu path | Accounts payable > Supplier credit |
| Authorised roles | AP-CLERK, AP-MGR, FIN-CTRL, SYS-ADMIN |
| Status | current |

Screen AP-CRN-05 provides the standard Accounts Payable routine for recording and posting credit notes issued by suppliers [^r1]. It is accessible via the menu path Accounts payable > Supplier credit by users holding the roles AP-CLERK, AP-MGR, FIN-CTRL, or SYS-ADMIN [^r8]. Saving a record assigns an internal reference and holds the document in draft, while posting locks all fields and commits the credit note to the ledger [^r4][^r7].

| Field | Key | Value |
|---|---|---|
| Screen code | `code` | AP-CRN-05 [^r8] |
| Title | `title` | SUPPLIER CREDIT NOTE ENTRY [^r8] |
| Navigation | `path` | Accounts payable > Supplier credit [^r8] |
| Authorised roles | `roles` | AP-CLERK, AP-MGR, FIN-CTRL, SYS-ADMIN [^r8] |

## Fields

The screen layout comprises four mandatory fields and three optional fields [^r2][^r9]:

* **SUP CD** (`sup_cd`): Mandatory supplier code [^r2][^r9][^r15].
* **SUP CRN NO** (`sup_crn_no`): Mandatory external credit note number supplied by the vendor [^r2][^r9][^r15].
* **AMOUNT** (`amount`): Mandatory credit value [^r2][^r9][^r15].
* **CRN NO** (`crn_no`): Mandatory internal credit note document number, generated upon initial save [^r2][^r4][^r9][^r12].
* **AP DOC** (`ap_doc`): Optional internal ledger voucher reference; it can be populated to offset a specific invoice or left blank when processing general account credits [^r2][^r3][^r9][^r15]. If a credit note spans multiple purchase orders or invoices across the Manchester and Leeds sites, leaving AP DOC blank and entering individual invoice references in COMMENT creates an unallocated balance [^r6].
* **STATUS** (`status`): Optional status display, marked as draft on save and updated to posted on post [^r2][^r4][^r9].
* **COMMENT** (`comment`): Optional free-text narrative [^r2][^r6][^r9].

Once a credit note is posted using `crn_post`, all screen fields are locked against further modification; correcting erroneous values requires a manual adjustment debit note or a ledger reversal [^r7].

## Keys and services

AP-CRN-05 interacts with the [[services-ap-crn|AP crn services]] group using standard function keys and backend routines [^r10]:

* **Search (F2 / Enter)**: Calls read service `crn_search` (endpoint `POST /ll72/svc/crn_search`) to query and list credit notes by supplier code, credit note number, amount, or status [^r10][^r16]. Entering a supplier code into SUP CD and executing `crn_search` invokes SUPPLIER CREDIT NOTE LIST [^r5].
* **Get (F3)**: Invokes read service `crn_get` using mandatory key `crn_no` to retrieve existing supplier credit note details [^r10][^r12].
* **Save (F8)**: Invokes write service `crn_save` (SUPPLIER CREDIT NOTE SAVE) with captured fields `sup_cd`, `sup_crn_no`, `amount`, and optional `ap_doc` to record the document, assign a `crn_no`, and mark STATUS as draft [^r4][^r10][^r14][^r15].
* **Post (F9)**: Invokes write service `crn_post`, executing stored procedure `sp_crn_post` to post the credit note directly to the ledger and set STATUS to posted [^r4][^r10][^r13].

## Messages

The screen validates transactions against the following error codes [^r11]:

* `ERR-SUP-0030`: Supplier Not Found (raised if the entered supplier code does not exist) [^r11].
* `ERR-CRN-0001`: Supplier Credit Note Not Found (raised during retrieval if the document number does not exist) [^r11].
* `ERR-CRN-0007`: Supplier Credit Note Not In Draft (<Status>) (raised if attempting to alter or post a document that is not in draft status) [^r11].

## See also

* [[err-sup-0030|ERR-SUP-0030]]
* [[screen-ap-dbn-04|AP-DBN-04 Debit Note Entry]]
* [[screen-ap-inv-01|AP-INV-01 Supplier Invoice Entry]]
* [[screen-ap-sbl-08|AP-SBL-08 Supplier Balance]]
* [[services-ap-crn|AP crn services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 15, Purpose
[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 5, AP-CRN-05 SUPPLIER CREDIT NOTE ENTRY
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 16, Entering a new credit note:
[^r7]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 18, Questions users ask
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 14, §6. Supplier Credit Note (AP-CRN-05)
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 5, AP-CRN-05 SUPPLIER CREDIT NOTE ENTRY
[^r15]: 04_service_definitions/accounts_payable/crn_save.yaml, request.fields
[^r12]: 04_service_definitions/accounts_payable/crn_get.yaml, screen: AP-CRN-05
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 15, Screen layout and fields
[^r6]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 17, Tips
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 5, AP-CRN-05 SUPPLIER CREDIT NOTE ENTRY
[^r16]: 04_service_definitions/accounts_payable/crn_search.yaml, service: crn_search
[^r5]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 16, Searching for credit notes:
[^r14]: 04_service_definitions/accounts_payable/crn_save.yaml, service: crn_save
[^r13]: 04_service_definitions/accounts_payable/crn_post.yaml, service: crn_post
[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 5, AP-CRN-05 SUPPLIER CREDIT NOTE ENTRY
