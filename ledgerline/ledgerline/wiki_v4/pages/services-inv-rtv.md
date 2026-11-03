---
title: "INV rtv services"
type: "service-group"
slug: "services-inv-rtv"
summary: "INV return to vendor service group covering draft creation, inquiry, posting, and cancellation on screen INV-RTV-07."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/rtv_cancel.yaml", "04_service_definitions/inventory/rtv_get.yaml", "04_service_definitions/inventory/rtv_post.yaml", "04_service_definitions/inventory/rtv_save.yaml", "04_service_definitions/inventory/rtv_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | INV |
| Screen | [[screen-inv-rtv-07|INV-RTV-07]] |
| Services | rtv_save, rtv_get, rtv_search, rtv_post, rtv_cancel |
| Available since | Ledgerline 7.0 |
| Protocol | POST (/ll72/svc/*) |
| Status | current |

The INV rtv service group manages the return to vendor workflow in Ledgerline on screen [[screen-inv-rtv-07|INV-RTV-07]][^r12][^r17]. Available since version 7.0, these services handle the validation, draft reservation, ledger posting, and cancellation of goods returned against goods receipt notes[^r6][^r9][^r17]. Every service requires session authentication via the `X-LL-Session` header and an authorized user role[^r18][^r24][^r29][^r34][^r39].

## Services

### rtv_save

The `rtv_save` service is a write service linked to screen [[screen-inv-rtv-07|INV-RTV-07]] that invokes stored procedure `sp_rtv_save` via endpoint `POST /ll72/svc/rtv_save`[^r12][^r33][^r34]. It validates input fields against current inventory balances and the supplier master record, generates the next sequential RTV number, reserves inventory stock, and sets the document status to pending/saved[^r6].

* **Required fields:** `grn_no` (string), `qty` (integer), `reason_cd` (string)[^r35].
* **Optional fields:** `ncr_no` (string), `remarks` (string)[^r35].
* **Errors:** [[errors-rtv|ERR-RTV-0201]] (quantity zero or negative), ERR-RTV-0204 (quantity exceeds received quantity), and [[err-rtv-0230|ERR-RTV-0230]] (GRN already invoiced, raise debit note)[^r3][^r36]. Common errors include ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503[^r37].
* **Source file:** `04_service_definitions/inventory/rtv_save.yaml`[^r33].

### rtv_get

The `rtv_get` service is a read service on screen [[screen-inv-rtv-07|INV-RTV-07]] accessed via endpoint `POST /ll72/svc/rtv_get`[^r13][^r23].

* **Required fields:** `rtv_no` (string)[^r25].
* **Optional fields:** none[^r25].
* **Errors:** [[errors-rtv|ERR-RTV-0001]] (return to vendor not found)[^r1][^r26]. Common errors include ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503[^r27].
* **Source file:** `04_service_definitions/inventory/rtv_get.yaml`[^r23].

### rtv_search

The `rtv_search` service is a read service titled RETURN TO VENDOR LIST on screen [[screen-inv-rtv-07|INV-RTV-07]] accessed via endpoint `POST /ll72/svc/rtv_search`[^r14][^r38]. It returns a standard response envelope containing `rc`, `err_cd`, `msg`, and `data`[^r41].

* **Required fields:** none[^r40].
* **Optional fields:** `grn_no` (string), `qty` (integer), `reason_cd` (string), `status` (string)[^r40].
* **Errors:** [[errors-rtv|ERR-RTV-0201]] (search quantity zero or negative)[^r5][^r42]. Common errors include ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503[^r42].
* **Source file:** `04_service_definitions/inventory/rtv_search.yaml`[^r38].

### rtv_post

The `rtv_post` service is a write service linked to screen [[screen-inv-rtv-07|INV-RTV-07]] that executes stored procedure `sp_rtv_post` via endpoint `POST /ll72/svc/rtv_post`[^r15][^r28][^r29][^r30]. It validates on-hand bin stock, updates the ledger, sets the return status to complete, and relieves quarantine stock[^r7][^r9].

* **Required fields:** `rtv_no` (string)[^r30].
* **Optional fields:** `comment` (string)[^r30].
* **Errors:** [[errors-rtv|ERR-RTV-0001]] (not found), ERR-RTV-0007 (not in draft or pending status), and ERR-RTV-0801 (insufficient on-hand bin stock, inventory location locks, or closed accounting periods)[^r2][^r7][^r9][^r31]. Common errors include ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503[^r32].
* **Source file:** `04_service_definitions/inventory/rtv_post.yaml`[^r28].

### rtv_cancel

The `rtv_cancel` service is a write service linked to screen [[screen-inv-rtv-07|INV-RTV-07]] that invokes stored procedure `sp_rtv_cancel` via endpoint `POST /ll72/svc/rtv_cancel`[^r16][^r17][^r20]. Bound to Shift+F8, it releases reserved inventory balances and transitions unposted return drafts to abandoned or cancelled status[^r8][^r10][^r11]. It returns an envelope with `rc`, `err_cd`, `msg`, and `data`[^r20].

* **Required fields:** `rtv_no` (string), `reason` (string)[^r19].
* **Optional fields:** none[^r19].
* **Errors:** [[errors-rtv|ERR-RTV-0001]] (record not found), [[err-rtv-0230|ERR-RTV-0230]] (invoked against an already posted document), and ERR-RTV-0801 (document already closed, cancelled, or rejected)[^r4][^r10][^r21]. Common errors include ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503[^r22].
* **Source file:** `04_service_definitions/inventory/rtv_cancel.yaml`[^r17].

## Versions and conflicts

* **`rtv_cancel` error scope contradiction:** Today's service specification and inventory manual document that `rtv_cancel` handles [[errors-rtv|ERR-RTV-0001]], [[err-rtv-0230|ERR-RTV-0230]], and ERR-RTV-0801[^r4][^r10][^r21]. However, screen reference MAN-SCR-72 attributes the full return error suite (ERR-RTV-0201, ERR-RTV-0204, ERR-RTV-0230, ERR-RTV-0001, ERR-RTV-0007, and ERR-RTV-0801) directly to the Shift+F8 `rtv_cancel` button keybinding[^r11].
* **Superseded manual v7.2.2:** The 2024-06-10 manual v7.2.2 previously outlined the five RTV services and error codes ERR-RTV-0001, ERR-RTV-0007, ERR-RTV-0201, ERR-RTV-0204, ERR-RTV-0230, and ERR-RTV-0801, which are superseded by the v7.2.3 manuals and service definitions[^r43].

## See also

* [[screen-inv-rtv-07|INV-RTV-07 Return To Vendor Entry]]
* [[screen-inv-mrn-08|INV-MRN-08 Material Issue Entry]]
* [[errors-rtv|ERR-RTV Return to Vendor Error Codes]]
* [[err-rtv-0230|ERR-RTV-0230 Invoice already posted against receipt]]
* [[services-inv-grn|INV grn services]]

## References

[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 13, rtv_save RETURN TO VENDOR SAVE
[^r17]: 04_service_definitions/inventory/rtv_cancel.yaml, rtv_cancel
[^r6]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 16, Saving the draft record
[^r9]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 18, §7. Material Issue (INV-MRN-08)
[^r18]: 04_service_definitions/inventory/rtv_cancel.yaml, auth
[^r24]: 04_service_definitions/inventory/rtv_get.yaml, auth
[^r29]: 04_service_definitions/inventory/rtv_post.yaml, auth
[^r34]: 04_service_definitions/inventory/rtv_save.yaml, whole file
[^r39]: 04_service_definitions/inventory/rtv_search.yaml, auth
[^r33]: 04_service_definitions/inventory/rtv_save.yaml, whole file
[^r35]: 04_service_definitions/inventory/rtv_save.yaml, request.fields
[^r3]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 21
[^r36]: 04_service_definitions/inventory/rtv_save.yaml, errors
[^r37]: 04_service_definitions/inventory/rtv_save.yaml, common_errors
[^r13]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 13, rtv_get RETURN TO VENDOR GET
[^r23]: 04_service_definitions/inventory/rtv_get.yaml, whole file
[^r25]: 04_service_definitions/inventory/rtv_get.yaml, request.fields
[^r1]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 21
[^r26]: 04_service_definitions/inventory/rtv_get.yaml, errors
[^r27]: 04_service_definitions/inventory/rtv_get.yaml, common_errors
[^r14]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 13, rtv_search RETURN TO VENDOR LIST
[^r38]: 04_service_definitions/inventory/rtv_search.yaml, service: rtv_search
[^r41]: 04_service_definitions/inventory/rtv_search.yaml, response.envelope
[^r40]: 04_service_definitions/inventory/rtv_search.yaml, request.fields
[^r5]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 21
[^r42]: 04_service_definitions/inventory/rtv_search.yaml, errors
[^r15]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 13, rtv_post RETURN TO VENDOR POST
[^r28]: 04_service_definitions/inventory/rtv_post.yaml, service: rtv_post
[^r30]: 04_service_definitions/inventory/rtv_post.yaml, request.fields
[^r7]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 17, Messages
[^r2]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 21
[^r31]: 04_service_definitions/inventory/rtv_post.yaml, errors
[^r32]: 04_service_definitions/inventory/rtv_post.yaml, common_errors
[^r16]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 13, rtv_cancel RETURN TO VENDOR CANCEL
[^r20]: 04_service_definitions/inventory/rtv_cancel.yaml, response.envelope
[^r8]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 16, Reversing or cancelling an unposted draft
[^r10]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 18, §7. Material Issue (INV-MRN-08)
[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 19, Button Key Service Needs
[^r19]: 04_service_definitions/inventory/rtv_cancel.yaml, request.fields
[^r4]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 22
[^r21]: 04_service_definitions/inventory/rtv_cancel.yaml, errors
[^r22]: 04_service_definitions/inventory/rtv_cancel.yaml, common_errors
[^r43]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 7, §6. Return To Vendor (INV-RTV-07)
