---
title: "PUR po services"
type: "service-group"
slug: "services-pur-po"
summary: "Ledgerline ERP purchasing services for creating, fetching, approving, rejecting, releasing, amending, searching, and cancelling purchase orders."
audience: "staff"
status: "current"
sources: ["07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf", "07_data_dictionary/code_lists.csv", "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/_legacy_6x/PO_ENTRY_SAVE.xml", "04_service_definitions/purchase/po_amend.yaml", "04_service_definitions/purchase/po_approve.yaml", "04_service_definitions/purchase/po_cancel.yaml", "04_service_definitions/purchase/po_fetch.yaml", "04_service_definitions/purchase/po_get.yaml", "04_service_definitions/purchase/po_hist.yaml", "04_service_definitions/purchase/po_pending_appr.yaml", "04_service_definitions/purchase/po_reject.yaml", "04_service_definitions/purchase/po_release.yaml", "04_service_definitions/purchase/po_save.yaml", "04_service_definitions/purchase/po_search.yaml", "08_release_notes/RN-7.2.3 Ledgerline Release Notes.pdf", "08_release_notes/RN-7.2.3-P1 Ledgerline Patch Notes.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | PUR |
| Object | Purchase Order (po_*) |
| Transport | HTTP POST (/ll72/svc/po_*) |
| Auth header | X-LL-Session |
| Status | Current |

The `po_*` service group handles the purchase order lifecycle in Ledgerline ERP, covering order creation, line default retrieval, approval workflow, release, amendment, query, and cancellation [^r15][^r72][^r85]. Operating within module `PUR`, write operations execute validation, tax computation, stock on-order tracking, and budget reservation procedures [^r13][^r19][^r27][^r73]. For integrations and interactive screens alike, order creation via `po_save` enforces validation tokens obtained through `po_fetch` to ensure supplier and item parameters remain synchronized [^r1][^r80][^r81].

## Services

### po_fetch
The `po_fetch` service retrieves default parameters for a proposed purchase order line on screen [[screen-pur-po-01|PUR-PO-01]] [^r12][^r39]. It invokes stored procedure `sp_fetch_tok_new` and returns a single-use `fetch_tok` token valid exclusively for the specified supplier and item combination [^r1][^r43]. The service always defaults `tax_cd` to `VAT20-UK` regardless of supplier location, requiring overseas suppliers to be manually adjusted to `VAT20-RC` prior to saving to prevent error [[err-po-0412|ERR-PO-0412]] [^r44].
* **Kind**: Read [^r39].
* **Endpoint**: `POST /ll72/svc/po_fetch` [^r39].
* **Authentication**: Session token in `X-LL-Session` header and an authorized role [^r40].
* **Required fields**: `sup_cd`, `itm_cd` [^r41].
* **Optional fields**: `pr_no` [^r41].
* **Return envelope**: `rc` (`S`, `W`, or `E`), `err_cd`, `msg`, and `data` [^r3][^r42].
* **Errors**: [[err-sup-0030|ERR-SUP-0030]], `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, `ERR-SYS-0503` [^r45][^r46].
* **Source file**: `04_service_definitions/purchase/po_fetch.yaml` [^r39].

### po_save
The `po_save` service creates or updates purchase orders from screen [[screen-pur-po-01|PUR-PO-01]] [^r72]. It executes database procedures `sp_fetch_tok_chk`, `sp_po_hdr_save`, `sp_appr_route`, `sp_budget_chk`, `sp_budget_commit`, `sp_doc_no_next`, `sp_ntf_enqueue`, `sp_po_status_set`, `sp_tax_compute`, and `sp_tax_region_chk` [^r73]. The service validates need-by dates, line quantities, tax codes matching the supplier country, purchase requisition linkage, item and quantity conformance against the PR, and the 50,000 gross limit on direct (`DIR`) orders without a PR [^r4][^r5][^r14]. External callers must include `fetch_tok` from `po_fetch`, or the service rejects the request with [[err-scr-0221|ERR-SCR-0221]] [^r9][^r80][^r81]. If saved against a closed cost centre, the document is retained in draft status `DR` with warning `W-CC-114` instead of failing [^r2][^r82][^r84]. Responses return message `<PO NO> SAVED` with `data.status` reflecting `DR`, `PA`, or `AP` [^r74].
* **Kind**: Write [^r13][^r72].
* **Endpoint**: `POST /ll72/svc/po_save` [^r72].
* **Authentication**: Session token in `X-LL-Session` header and an authorized role [^r72].
* **Required fields**: `sup_cd`, `itm_cd`, `qty`, `rate`, `tax_cd`, `cc_cd`, `need_dt` [^r13][^r86].
* **Optional fields**: `po_type`, `pr_no`, `whs_cd`, `fetch_tok`, `client_ref` [^r2][^r86].
* **Errors and warnings**: [[err-scr-0221|ERR-SCR-0221]], [[err-po-0412|ERR-PO-0412]], [[err-po-0610|ERR-PO-0610]], [[err-sup-0030|ERR-SUP-0030]], [[err-sup-0031|ERR-SUP-0031]], `ERR-TAX-0101`, `W-CC-114` [^r5][^r9][^r10][^r11][^r14][^r81][^r84].
* **Source file**: `04_service_definitions/purchase/po_save.yaml` [^r72].

### po_get
The `po_get` service retrieves full header and line details for an existing purchase order [^r15][^r47].
* **Kind**: Read [^r47].
* **Endpoint**: `POST /ll72/svc/po_get` [^r47].
* **Authentication**: Session token in `X-LL-Session` header and an authorized role [^r47].
* **Required fields**: `po_no` [^r48].
* **Optional fields**: None [^r48].
* **Return envelope**: `rc` (`S`, `W`, or `E`), `err_cd`, `msg`, and `data` [^r3][^r49].
* **Errors**: `ERR-PO-0001`, `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, `ERR-SYS-0503` [^r50].
* **Source file**: `04_service_definitions/purchase/po_get.yaml` [^r47].

### po_search
The `po_search` service queries purchase orders by search criteria and returns matching order headers, including the `created_by` audit attribute [^r15][^r75][^r83].
* **Kind**: Read [^r75].
* **Endpoint**: `POST /ll72/svc/po_search` [^r76].
* **Authentication**: Session token in `X-LL-Session` header and an authorized role [^r76].
* **Required fields**: None [^r77].
* **Optional fields**: `sup_cd`, `itm_cd`, `status`, `client_ref`, `from_dt` [^r77].
* **Return envelope**: `rc` (`S`, `W`, or `E`), `err_cd`, `msg`, and `data` [^r3][^r78].
* **Errors**: `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, `ERR-SYS-0503` [^r79].
* **Source file**: `04_service_definitions/purchase/po_search.yaml` [^r75].

### po_hist
The `po_hist` service reads historical purchase orders for a specified inventory item on screen [[screen-pur-poh-02|PUR-POH-02]] [^r15][^r51].
* **Kind**: Read [^r51].
* **Endpoint**: `POST /ll72/svc/po_hist` [^r51].
* **Authentication**: Session token in `X-LL-Session` header and an authorized role [^r52].
* **Required fields**: `itm_cd` [^r53].
* **Optional fields**: `sup_cd` [^r53].
* **Return envelope**: `rc` (`S`, `W`, or `E`), `err_cd`, `msg`, and `data` [^r3][^r54].
* **Errors**: `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, `ERR-SYS-0503` [^r55].
* **Source file**: `04_service_definitions/purchase/po_hist.yaml` [^r51].

### po_pending_appr
The `po_pending_appr` service lists purchase orders awaiting authorization within the approval inbox [^r16][^r56][^r57].
* **Kind**: Read [^r57].
* **Endpoint**: `POST /ll72/svc/po_pending_appr` [^r57].
* **Authentication**: Session token in `X-LL-Session` header and an authorized role [^r58].
* **Required fields**: None [^r59].
* **Optional fields**: `approver` [^r16][^r59].
* **Return envelope**: `rc` (`S`, `W`, or `E`), `err_cd`, `msg`, and `data` [^r3][^r60].
* **Errors**: `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, `ERR-SYS-0503` [^r61].
* **Source file**: `04_service_definitions/purchase/po_pending_appr.yaml` [^r56].

### po_approve
The `po_approve` service approves purchase orders in pending approval status `PA` from screen [[screen-pur-poa-04|PUR-POA-04]] [^r6][^r29].
* **Kind**: Write [^r29].
* **Endpoint**: `POST /ll72/svc/po_approve` [^r29].
* **Authentication**: Session token in `X-LL-Session` header and an authorized role [^r30].
* **Required fields**: `po_no` [^r17][^r31].
* **Optional fields**: `comment` [^r17][^r31].
* **Return envelope**: `rc` (`S`, `W`, or `E`), `err_cd`, `msg`, and `data` [^r3][^r32].
* **Errors**: `ERR-PO-0001`, `ERR-PO-0702`, [[err-apr-0003|ERR-APR-0003]], [[err-apr-0004|ERR-APR-0004]], `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, `ERR-SYS-0503` [^r6][^r17][^r33][^r34].
* **Source file**: `04_service_definitions/purchase/po_approve.yaml` [^r29].

### po_reject
The `po_reject` service rejects purchase orders awaiting approval on screen [[screen-pur-poa-04|PUR-POA-04]] [^r62]. Rejection requires an explicit reason and fails if the document is not in `PA` status [^r6][^r18][^r64].
* **Kind**: Write [^r62].
* **Endpoint**: `POST /ll72/svc/po_reject` [^r62].
* **Authentication**: Session token in `X-LL-Session` header and an authorized role [^r63].
* **Required fields**: `po_no`, `comment` [^r18][^r64].
* **Optional fields**: None [^r64].
* **Return envelope**: `rc` (`S`, `W`, or `E`), `err_cd`, `msg`, and `data` [^r3][^r65].
* **Errors**: `ERR-PO-0702`, `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, `ERR-SYS-0503` [^r6][^r66].
* **Source file**: `04_service_definitions/purchase/po_reject.yaml` [^r62].

### po_release
The `po_release` service releases approved orders in status `AP` via procedures `sp_po_status_set`, `sp_stk_onorder_upd`, and `sp_ntf_enqueue`, updating stock on-order quantities and triggering notification e-mails to the vendor [^r7][^r19][^r67][^r70][^r71].
* **Kind**: Write [^r19][^r67].
* **Endpoint**: `POST /ll72/svc/po_release` [^r67].
* **Authentication**: Session token in `X-LL-Session` header and an authorized role [^r68].
* **Required fields**: `po_no` [^r19][^r69].
* **Optional fields**: None [^r69].
* **Errors**: `ERR-PO-0001`, `ERR-PO-0715` [^r7][^r19].
* **Source file**: `04_service_definitions/purchase/po_release.yaml` [^r67].

### po_amend
The `po_amend` service modifies existing purchase orders from screen [[screen-pur-pom-06|PUR-POM-06]] using stored procedures `sp_tax_compute`, `sp_budget_chk`, `sp_budget_commit`, `sp_appr_route`, and `sp_ntf_enqueue` [^r24][^r27]. It rejects attempts to amend orders in closed, cancelled, or rejected statuses (`CN`, `RJ`, `CL`) [^r8][^r20]. Amendments that increase order commitments beyond approved limits return the document to `PA` status, while modifications pointing to a closed cost centre return it to `DR` with advisory warning `W-CC-114` [^r20][^r28].
* **Kind**: Write [^r20][^r24].
* **Endpoint**: `POST /ll72/svc/po_amend` [^r24].
* **Authentication**: Session token in `X-LL-Session` header and an authorized role [^r25].
* **Required fields**: `po_no` [^r20][^r26].
* **Optional fields**: `qty`, `need_dt`, `cc_cd` [^r20][^r26].
* **Errors and warnings**: `ERR-PO-0001`, [[err-po-0801|ERR-PO-0801]], `ERR-TAX-0101`, [[err-cc-0009|ERR-CC-0009]], `ERR-BUD-0207`, [[err-apr-0009|ERR-APR-0009]], `W-CC-114` [^r8][^r20][^r84].
* **Source file**: `04_service_definitions/purchase/po_amend.yaml` [^r24].

### po_cancel
The `po_cancel` service cancels an order from screen [[screen-pur-pom-06|PUR-POM-06]], invoking `sp_stk_onorder_upd` and `sp_po_status_set` to release stock on-order allocations [^r21][^r35][^r37]. The system does not transmit cancellation notifications to the supplier [^r37]. Orders already in `CN`, `RJ`, or `CL` status cannot be cancelled [^r8][^r38].
* **Kind**: Write [^r21][^r35].
* **Endpoint**: `POST /ll72/svc/po_cancel` [^r35].
* **Authentication**: Session token in `X-LL-Session` header and an authorized role [^r35].
* **Required fields**: `po_no`, `reason` [^r21][^r36].
* **Optional fields**: None [^r36].
* **Return envelope**: `rc` (`S`, `W`, or `E`), `err_cd`, `msg`, and `data` [^r3][^r36].
* **Errors**: `ERR-PO-0001`, [[err-po-0801|ERR-PO-0801]] [^r8][^r21][^r38].
* **Source file**: `04_service_definitions/purchase/po_cancel.yaml` [^r35].

## Versions and conflicts

* **Today's rule**: Ledgerline 7.2 services operate via HTTP POST endpoints under `/ll72/svc/` using `X-LL-Session` authentication tokens and structured service definitions [^r24][^r30][^r72].
* **Older rule**: Under legacy Ledgerline 6.4, purchase order creation utilized RPC service `PO_ENTRY_SAVE` with `LL6-RPC` transport and fixed CHAR fields `VENDOR_NO`, `ITEM_NO`, `QTY`, `PRICE`, `TAX_REGION`, `CC`, and `DUE_DATE`, returning `RETCODE` and `DOCNO` [^r22][^r23].
* **Sources and dates**: `04_service_definitions/_legacy_6x/PO_ENTRY_SAVE.xml` (superseded 2015) vs `04_service_definitions/purchase/po_save.yaml` (Ledgerline 7.0/7.2) [^r22][^r72].
* **Kind**: `superseded` [^r22].

## See also

* [[screen-pur-po-01|screen-pur-po-01]]
* [[screen-pur-pom-06|screen-pur-pom-06]]
* [[screen-pur-poa-04|screen-pur-poa-04]]
* [[screen-pur-por-05|screen-pur-por-05]]
* [[screen-pur-poh-02|screen-pur-poh-02]]
* [[errors-po|errors-po]]
* [[services-pur-pr|services-pur-pr]]
* [[services-pur-bud|services-pur-bud]]
* [[services-pur-sup|services-pur-sup]]

## References

[^r15]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 6, §2. Purchase services
[^r72]: 04_service_definitions/purchase/po_save.yaml, service: po_save
[^r85]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 27, PUR-PO-01 PURCHASE ORDER ENTRY
[^r13]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 5, §2. Purchase services
[^r19]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 7, po_release PO RELEASE
[^r27]: 04_service_definitions/purchase/po_amend.yaml, procedures
[^r73]: 04_service_definitions/purchase/po_save.yaml, procedures
[^r1]: 07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf, p. 2, §6. Purchase order (po_*)
[^r80]: 08_release_notes/RN-7.2.3 Ledgerline Release Notes.pdf, p. 2, Save on PUR-PO-01 needs Fetch for the current supplier and item: ERR-SCR-0221 FETCH NOT DONE.
[^r81]: 08_release_notes/RN-7.2.3 Ledgerline Release Notes.pdf, p. 2, Save on PUR-PO-01 needs Fetch for the current supplier and item: ERR-SCR-0221 FETCH NOT DONE.
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 5, §2. Purchase services
[^r39]: 04_service_definitions/purchase/po_fetch.yaml, service: po_fetch
[^r43]: 04_service_definitions/purchase/po_fetch.yaml, procedures
[^r44]: 04_service_definitions/purchase/po_fetch.yaml, notes
[^r40]: 04_service_definitions/purchase/po_fetch.yaml, auth
[^r41]: 04_service_definitions/purchase/po_fetch.yaml, request.fields
[^r3]: 07_data_dictionary/code_lists.csv, sheet csv, row rc, ALL 14 ROWS
[^r42]: 04_service_definitions/purchase/po_fetch.yaml, response.envelope
[^r45]: 04_service_definitions/purchase/po_fetch.yaml, errors
[^r46]: 04_service_definitions/purchase/po_fetch.yaml, common_errors
[^r4]: 07_data_dictionary/code_lists.csv, sheet csv, row po_type, ALL 14 ROWS
[^r5]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 18, ERR-PO-0610
[^r14]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 6, §2. Purchase services
[^r9]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 23, ERR-SCR-0221 FETCH NOT DONE
[^r2]: 07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf, p. 2, §6. Purchase order (po_*)
[^r82]: 08_release_notes/RN-7.2.3 Ledgerline Release Notes.pdf, p. 3, Orders saved against a closed cost centre are kept as Draft with warning W-CC-114 instead of being refused.
[^r84]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 26
[^r74]: 04_service_definitions/purchase/po_save.yaml, notes
[^r86]: 04_service_definitions/purchase/po_save.yaml, request.fields
[^r10]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 25, ERR-SUP-0030 SUPPLIER NOT FOUND
[^r11]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 25, ERR-SUP-0031 SUPPLIER NOT ACTIVE
[^r47]: 04_service_definitions/purchase/po_get.yaml, service: po_get
[^r48]: 04_service_definitions/purchase/po_get.yaml, request.fields
[^r49]: 04_service_definitions/purchase/po_get.yaml, response.envelope
[^r50]: 04_service_definitions/purchase/po_get.yaml, errors
[^r75]: 04_service_definitions/purchase/po_search.yaml, whole file
[^r83]: 08_release_notes/RN-7.2.3-P1 Ledgerline Patch Notes.pdf, p. 2, §3. Details
[^r76]: 04_service_definitions/purchase/po_search.yaml, whole file
[^r77]: 04_service_definitions/purchase/po_search.yaml, request.fields
[^r78]: 04_service_definitions/purchase/po_search.yaml, response.envelope
[^r79]: 04_service_definitions/purchase/po_search.yaml, common_errors
[^r51]: 04_service_definitions/purchase/po_hist.yaml, whole file
[^r52]: 04_service_definitions/purchase/po_hist.yaml, auth
[^r53]: 04_service_definitions/purchase/po_hist.yaml, request.fields
[^r54]: 04_service_definitions/purchase/po_hist.yaml, response.envelope
[^r55]: 04_service_definitions/purchase/po_hist.yaml, common_errors
[^r16]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 7, po_pending_appr APPROVAL INBOX
[^r56]: 04_service_definitions/purchase/po_pending_appr.yaml, service: po_pending_appr
[^r57]: 04_service_definitions/purchase/po_pending_appr.yaml, service: po_pending_appr
[^r58]: 04_service_definitions/purchase/po_pending_appr.yaml, auth
[^r59]: 04_service_definitions/purchase/po_pending_appr.yaml, request.fields
[^r60]: 04_service_definitions/purchase/po_pending_appr.yaml, response.envelope
[^r61]: 04_service_definitions/purchase/po_pending_appr.yaml, common_errors
[^r6]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 18, ERR-PO-0702
[^r29]: 04_service_definitions/purchase/po_approve.yaml, whole file
[^r30]: 04_service_definitions/purchase/po_approve.yaml, auth
[^r17]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 7, po_approve PO APPROVE
[^r31]: 04_service_definitions/purchase/po_approve.yaml, request.fields
[^r32]: 04_service_definitions/purchase/po_approve.yaml, response.envelope
[^r33]: 04_service_definitions/purchase/po_approve.yaml, errors
[^r34]: 04_service_definitions/purchase/po_approve.yaml, common_errors
[^r62]: 04_service_definitions/purchase/po_reject.yaml, service: po_reject
[^r18]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 7, po_reject PO REJECT
[^r64]: 04_service_definitions/purchase/po_reject.yaml, request.fields
[^r63]: 04_service_definitions/purchase/po_reject.yaml, auth
[^r65]: 04_service_definitions/purchase/po_reject.yaml, response.envelope
[^r66]: 04_service_definitions/purchase/po_reject.yaml, errors
[^r7]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 18, ERR-PO-0715
[^r67]: 04_service_definitions/purchase/po_release.yaml, whole file
[^r70]: 04_service_definitions/purchase/po_release.yaml, procedures
[^r71]: 04_service_definitions/purchase/po_release.yaml, notes
[^r68]: 04_service_definitions/purchase/po_release.yaml, auth
[^r69]: 04_service_definitions/purchase/po_release.yaml, request
[^r24]: 04_service_definitions/purchase/po_amend.yaml, whole file
[^r8]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 18, ERR-PO-0801
[^r20]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 7, po_amend PO AMEND
[^r28]: 04_service_definitions/purchase/po_amend.yaml, notes
[^r25]: 04_service_definitions/purchase/po_amend.yaml, auth
[^r26]: 04_service_definitions/purchase/po_amend.yaml, request
[^r21]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 8, po_cancel PO CANCEL
[^r35]: 04_service_definitions/purchase/po_cancel.yaml, service: po_cancel
[^r37]: 04_service_definitions/purchase/po_cancel.yaml, procedures
[^r38]: 04_service_definitions/purchase/po_cancel.yaml, errors
[^r36]: 04_service_definitions/purchase/po_cancel.yaml, request
[^r22]: 04_service_definitions/_legacy_6x/PO_ENTRY_SAVE.xml, rpc
[^r23]: 04_service_definitions/_legacy_6x/PO_ENTRY_SAVE.xml, rpc
