---
title: "SAL-CRN-09 Customer Credit Note Entry"
type: "screen"
slug: "screen-sal-crn-09"
summary: "Ledgerline screen SAL-CRN-09 records and posts customer credit notes against sales invoices with required approvals."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/sales/scn_get.yaml", "04_service_definitions/sales/scn_post.yaml", "04_service_definitions/sales/scn_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen | SAL-CRN-09 |
| Module | Sales |
| Path | Sales > Customer credit |
| Services | scn_save, scn_get, scn_post |
| Status | Current |

Screen SAL-CRN-09 is the Ledgerline interface used to issue formal credit entries against previously posted customer invoices [^r1][^r3]. It accommodates price corrections, minor paint blemish handling allowances, non-conforming returns, and transit damage compensation [^r3]. Prior to entering a transaction, written approval from the sales office manager or finance controller is mandatory [^r4]. Once posted, credit notes cannot be cancelled, amended, or reversed from within this screen [^r7].

| Key | Value |
|---|---|
| Screen Code | SAL-CRN-09 [^r1] |
| Screen Name | Customer Credit Note Entry [^r8] |
| Module | Sales [^r1] |
| Menu Path | Sales > Customer credit [^r1] |
| Primary Services | [[services-sal-scn\|scn_save]], scn_get, scn_post [^r1] |
| Status | Current [^r1] |

## Fields

The screen layout comprises both entry inputs and system-generated display fields [^r5].

* **CUST CD** (`cust_cd`): Customer code; mandatory input [^r2][^r8].
* **INV NO** (`sinv_no`): Reference invoice number; mandatory input [^r2][^r8].
* **AMOUNT** (`amount`): Credit amount; mandatory input [^r2][^r8].
* **REASON CD** (`reason_cd`): Reason code for the credit note; mandatory input [^r2][^r8].
* **SCN NO** (`scn_no`): Sales credit note number; mandatory output-only field populated automatically upon saving [^r2][^r5][^r6][^r8].
* **COMMENT** (`comment`): Additional descriptive details; optional input [^r2][^r5].

## Keys and services

SAL-CRN-09 interfaces with underlying Ledgerline services via standard functional hotkeys [^r1][^r9]:

* **scn_get (F3)**: Read service used to retrieve existing customer credit note records by `scn_no` [^r9][^r10].
* **scn_save (F8)**: Write service called via endpoint `POST /ll72/svc/scn_save` [^r9][^r12]. The screen submits mandatory fields `cust_cd`, `sinv_no`, `amount`, and `reason_cd` [^r13]. Executing `scn_save` validates active customer status, existing invoice references, and field formats before automatically populating the output-only `scn_no` field [^r6].
* **scn_post (F9)**: Posting service invoked via endpoint `POST /ll72/svc/scn_post` [^r9][^r11]. Once posted via `scn_post`, credit note transactions cannot be cancelled, reversed, or amended inside the screen [^r7].

## Messages

Validation failures during `scn_save` occur if customer status is inactive, the referenced invoice does not exist, or field formats are invalid [^r6].

## See also

* [[services-sal-scn|SAL scn services]]
* [[screen-sal-inv-06|SAL-INV-06 Sales Invoice Entry]]
* [[screen-sal-crd-11|SAL-CRD-11 Credit Control Check]]
* [[screen-sal-rma-07|SAL-RMA-07 Warranty Return (Rma) Entry]]
* [[screen-ap-dbn-04|AP-DBN-04 Debit Note Entry]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 41, §13. Customer Credit Note (SAL-CRN-09)
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 41, Purpose
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 41, Before you start
[^r7]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 44, Tips
[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 33, SAL-CRN-09 CUSTOMER CREDIT NOTE ENTRY
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 42, Screen layout and fields
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 41, §13. Customer Credit Note (SAL-CRN-09)
[^r6]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 43, Creating a new credit note
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 33, SAL-CRN-09 CUSTOMER CREDIT NOTE ENTRY
[^r10]: 04_service_definitions/sales/scn_get.yaml, service: scn_get
[^r12]: 04_service_definitions/sales/scn_save.yaml, service: scn_save
[^r13]: 04_service_definitions/sales/scn_save.yaml, request
[^r11]: 04_service_definitions/sales/scn_post.yaml, service: scn_post
