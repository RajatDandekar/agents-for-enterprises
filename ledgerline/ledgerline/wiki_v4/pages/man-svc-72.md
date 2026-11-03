---
title: "MAN-SVC-72 Ledgerline ERP 7.2 Service Reference"
type: "manual"
slug: "man-svc-72"
summary: "Vendor reference manual covering Ledgerline ERP 7.2 service architecture, HTTP invocation standards, error envelopes, and purchasing and inventory module services."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/README.md"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Document Code | MAN-SVC-72 |
| Title | Ledgerline ERP 7.2 Service Reference |
| Version | 7.2.3 |
| Effective Date | 2025-01-15 |
| Status | current |
| Module Scope | PUR, INV, AP, SAL, PRD, ADM |

MAN-SVC-72 is the technical vendor reference defining invocation protocols, service envelopes, and interface specifications for Ledgerline ERP 7.2 [^r1][^r31]. As of 26 October 2026, the active service registry contains 400 services across the PUR, INV, AP, SAL, PRD, and ADM modules invoked via flat JSON over HTTP POST [^r1][^r32]. Legacy SOAP gateways remain active under compatibility listeners for EDI, bank payment integration, and carrier booking [^r33].

| Attribute | Details |
|---|---|
| Document Code | MAN-SVC-72 [^r1] |
| Version | 7.2.3 [^r1] |
| Release Date | 2025-01-15 [^r1] |
| Endpoint Base | `/ll72/svc/<service>` [^r1] |
| Payload Structure | Flat JSON (maximum 12 fields) [^r1][^r31] |
| Registry Count | 400 active services [^r32] |

## Calling Services and Response Envelopes

Services are invoked via HTTP POST to `/ll72/svc/<service>` with a flat JSON request payload containing at most 12 fields, passing the active session token in the `X-LL-Session` header [^r1][^r31]. All responses use a standard legacy envelope containing `rc`, `err_cd`, `msg`, and `data` [^r2][^r31]. Return code `rc` evaluates to `S` for success, `W` for success accompanied by warnings, or `E` for errors [^r2].

Standard framework validations apply across all endpoints:
* Supplying unknown fields triggers error `ERR-SYS-0422` [^r3].
* Omitting mandatory fields triggers error `ERR-SYS-0421` [^r3].
* Insufficient role security privileges triggers error `ERR-SEC-0001` [^r3].

The active catalogue of 400 services is distributed across core modules: PUR (38), INV (84), AP (71), SAL (79), PRD (67), and ADM (61) [^r32]. XML-based SOAP gateways continue operation for EDI exchanges, carrier booking quotes via [[screen-sal-frt-12|SAL-FRT-12]], and bank interfaces [^r33].

## Purchasing Services

Purchasing operations link screen workflows to underlying database stored procedures:

* `po_pending_appr`: Read service introduced in version 7.0 that retrieves approval inbox entries, accepting an optional approver user ID [^r4].
* `po_approve`: Write service accessed from [[screen-pur-poa-04|PUR-POA-04]] taking mandatory `po_no` and optional `comment` [^r5]. It may raise errors `ERR-PO-0001`, `ERR-PO-0702`, [[err-apr-0003|ERR-APR-0003]], or [[err-apr-0004|ERR-APR-0004]] [^r5].
* `po_reject`: Write service accessed from [[screen-pur-poa-04|PUR-POA-04]] requiring mandatory `po_no` and mandatory `comment`, returning `ERR-PO-0702` if the purchase order is not pending approval [^r6].
* `po_release`: Executes on [[screen-pur-por-05|PUR-POR-05]] to transition purchase orders using procedures `sp_po_status_set`, `sp_stk_onorder_upd`, and `sp_ntf_enqueue`, potentially returning `ERR-PO-0001` or `ERR-PO-0715` [^r7].
* `po_amend`: Initiated from [[screen-pur-pom-06|PUR-POM-06]], invoking procedures `sp_tax_compute`, `sp_budget_chk`, `sp_budget_commit`, `sp_appr_route`, and `sp_ntf_enqueue` [^r8].
* `po_cancel`: Executes on [[screen-pur-pom-06|PUR-POM-06]] by running `sp_stk_onorder_upd` and `sp_po_status_set`, requiring mandatory `po_no` and `reason` [^r9].

Supporting purchasing utility services include:
* `tax_compute`: Read service invoking procedure `sp_tax_compute` with basic value and `tax_cd`, returning error `ERR-TAX-0101` if invalid [^r10].
* `bud_check`: Read service calling `sp_budget_chk` with mandatory `cc_cd` and `amount`, raising [[err-cc-0009|ERR-CC-0009]] or `ERR-BUD-0207` on failure [^r11].
* `ntf_send`: Write service invoking `sp_ntf_enqueue` with `channel` (EMAIL or SMS), `recipient`, and `msg` [^r12].

## Inventory Services

Inventory endpoints handle goods movement, counting, returns, and shop-floor material issuance:

* Goods Receipt: Service `grn_save` executes on [[screen-inv-grn-03|INV-GRN-03]] using mandatory `po_no` and `qty`, alongside optional `whs_cd` and `remarks` [^r13].
* Stock Transfers: Stock transfer processing on [[screen-inv-trf-04|INV-TRF-04]] is handled by services `txf_save`, `txf_get`, `txf_search`, `txf_post`, and `txf_cancel` [^r14].
* Stock Adjustments: Stock adjustments on [[screen-inv-adj-05|INV-ADJ-05]] execute via services `adj_save`, `adj_get`, `adj_search`, `adj_approve`, `adj_post`, and `adj_cancel` [^r15].
* Stock Counts: Stock count headers and records on [[screen-inv-cnt-06|INV-CNT-06]] operate via `cnt_save` (calling `sp_cnt_save`) and `cnt_get` [^r16]. Record listing is provided by `cnt_search` with optional filters `whs_cd`, `cnt_type`, `bin_from`, and `status` [^r17]. Detailed entries use `cnt_entry` executing `sp_cnt_entry` with `cnt_no`, `itm_cd`, and a positive integer `qty` [^r18]. Screen actions invoke `cnt_freeze` (calling `sp_cnt_freeze`, which fails with [[err-cnt-0230|ERR-CNT-0230]] if transactions remain open in the area), `cnt_post` (calling `sp_cnt_post`, returning error [[err-cnt-0240|ERR-CNT-0240]] if variance exceeds tolerance or warning `W-CNT-241` if within tolerance), and `cnt_cancel` (invoking `sp_cnt_cancel`, raising `ERR-CNT-0801` if already closed) [^r19][^r20][^r21].
* Return to Vendor: Returned vendor material operates on [[screen-inv-rtv-07|INV-RTV-07]] through `rtv_save` (invoking `sp_rtv_save` with mandatory `grn_no`, positive `qty`, `reason_cd`, and optional `ncr_no` and `remarks`), `rtv_get` (retrieving data by `rtv_no`), `rtv_search` (filtering by `grn_no`, `qty`, `reason_cd`, and `status`), `rtv_post` (executing `sp_rtv_post` with `rtv_no` and optional comment, requiring DRAFT status), and `rtv_cancel` (invoking `sp_rtv_cancel` with `rtv_no` and `reason`, raising `ERR-RTV-0801` if closed) [^r22][^r23][^r24][^r25][^r26].
* Material Issues: Shop floor material requisitions on [[screen-inv-mrn-08|INV-MRN-08]] are managed via `mrn_save` (calling `sp_mrn_save` with `wo_no`, `itm_cd`, `qty`, and optional `whs_cd`), `mrn_get` (retrieving data by `mrn_no`), `mrn_search` (filtering by `wo_no`, `itm_cd`, `qty`, and `status`), and `mrn_post` (calling `sp_mrn_post` with `mrn_no` and optional comment while enforcing DRAFT status) [^r27][^r28][^r29][^r30].

## See also

* [[services-pur-po]]
* [[services-pur-bud]]
* [[screen-pur-poa-04|PUR-POA-04 Purchase Order Approval]]
* [[screen-pur-por-05|PUR-POR-05 Purchase Order Release]]
* [[screen-pur-pom-06|PUR-POM-06 Purchase Order Amendment]]
* [[screen-inv-grn-03|INV-GRN-03 Goods Receipt Note (Grn)]]
* [[screen-inv-trf-04|INV-TRF-04 Stock Transfer Entry]]
* [[screen-inv-adj-05|INV-ADJ-05 Stock Adjustment Entry]]
* [[screen-inv-cnt-06|INV-CNT-06 Stock Count Entry]]
* [[screen-inv-rtv-07|INV-RTV-07 Return To Vendor Entry]]
* [[screen-inv-mrn-08|INV-MRN-08 Material Issue Entry]]
* [[err-cnt-0230|ERR-CNT-0230 Area has open transactions]]
* [[err-cnt-0240|ERR-CNT-0240 Cycle Count Value Variance Exceeds Tolerance]]
* [[err-apr-0003|ERR-APR-0003 Self-approval not permitted]]
* [[err-apr-0004|ERR-APR-0004 Advance amount exceeds PO unbilled commitment]]
* [[err-cc-0009|ERR-CC-0009]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 2, §1. Calling a service
[^r31]: 04_service_definitions/README.md, Ledgerline 7.2 service definitions
[^r32]: 04_service_definitions/README.md, Ledgerline 7.2 service definitions
[^r33]: 04_service_definitions/README.md, Ledgerline 7.2 service definitions
[^r2]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 2, §1. Calling a service
[^r3]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 2, §1. Calling a service
[^r4]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 7, po_pending_appr APPROVAL INBOX
[^r5]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 7, po_approve PO APPROVE
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 7, po_reject PO REJECT
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 7, po_release PO RELEASE
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 7, po_amend PO AMEND
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 8, po_cancel PO CANCEL
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 8, tax_compute TAX ENGINE
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 8, bud_check BUDGET CHECK
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 8, ntf_send NOTIFICATION SEND
[^r13]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 8, §3. Inventory services
[^r14]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 9, §3. Inventory services
[^r15]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 10, §3. Inventory services
[^r16]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 11, §3. Inventory services
[^r17]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 12, cnt_search STOCK COUNT LIST
[^r18]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 12, cnt_entry STOCK COUNT ENTRY
[^r19]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 12, cnt_freeze STOCK COUNT FREEZE
[^r20]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 12, cnt_post STOCK COUNT POST
[^r21]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 12, cnt_cancel STOCK COUNT CANCEL
[^r22]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 13, rtv_save RETURN TO VENDOR SAVE
[^r23]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 13, rtv_get RETURN TO VENDOR GET
[^r24]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 13, rtv_search RETURN TO VENDOR LIST
[^r25]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 13, rtv_post RETURN TO VENDOR POST
[^r26]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 13, rtv_cancel RETURN TO VENDOR CANCEL
[^r27]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 14, mrn_save MATERIAL ISSUE SAVE
[^r28]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 14, mrn_get MATERIAL ISSUE GET
[^r29]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 14, mrn_search MATERIAL ISSUE LIST
[^r30]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 14, mrn_post MATERIAL ISSUE POST
