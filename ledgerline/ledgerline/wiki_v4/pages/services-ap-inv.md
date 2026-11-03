---
title: "AP inv services"
type: "service-group"
slug: "services-ap-inv"
summary: "Ledgerline AP supplier invoice services handling creation, query, posting, hold, release, and cancellation on screen AP-INV-01."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/accounts_payable/inv_cancel.yaml", "04_service_definitions/accounts_payable/inv_get.yaml", "04_service_definitions/accounts_payable/inv_hold.yaml", "04_service_definitions/accounts_payable/inv_post.yaml", "04_service_definitions/accounts_payable/inv_release.yaml", "04_service_definitions/accounts_payable/inv_save.yaml", "04_service_definitions/accounts_payable/inv_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| service_group | ap-inv |
| module | Accounts Payable (AP) |
| screen | AP-INV-01 |
| introduced | Ledgerline 7.0 |
| status | current |
| endpoint_base | /ll72/svc/ |

The Accounts Payable invoice service group provides the core transaction services for entering, retrieving, posting, holding, and cancelling supplier invoices in Ledgerline [^r1][^r2][^r3][^r4][^r5][^r7][^r17][^r22][^r33]. All operations execute against screen [[screen-ap-inv-01|AP-INV-01]] using authenticated HTTP POST endpoints that require valid session tokens [^r9][^r17][^r18][^r23][^r34]. These services enforce purchase order validation, duplicate invoice checking, and three-way matching tolerances prior to general ledger posting [^r3][^r4][^r10][^r38].

## Services

### inv_cancel (SUPPLIER INVOICE CANCEL)
Cancels an unposted draft voucher or generates a reversing entry, releasing matched invoice quantities back to the purchase order [^r7][^r17]. The service executes stored procedure `sp_inv_cancel` and requires role execution authorization via header `X-LL-Session` [^r14][^r18][^r20].
* **Source file:** `04_service_definitions/accounts_payable/inv_cancel.yaml` [^r17]
* **Endpoint:** `POST /ll72/svc/inv_cancel` [^r17]
* **Required fields:** `ap_doc` (AP DOC), `reason` (REASON) [^r14][^r19]
* **Optional fields:** none [^r19]
* **Errors:** ERR-INV-0001 (SUPPLIER INVOICE NOT FOUND), ERR-INV-0801 (SUPPLIER INVOICE CLOSED (<status>)), ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r8][^r14][^r20][^r21]

### inv_get (SUPPLIER INVOICE GET)
Retrieves an existing invoice voucher using its internal document reference or supplier record [^r2][^r22]. It returns the standard Ledgerline response envelope containing return code `rc` (`S`, `W`, or `E`), error code `err_cd`, message `msg`, and the invoice payload under `data` [^r25].
* **Source file:** `04_service_definitions/accounts_payable/inv_get.yaml` [^r22]
* **Endpoint:** `POST /ll72/svc/inv_get` [^r23]
* **Required fields:** `ap_doc` (AP DOC) [^r11][^r24]
* **Optional fields:** none [^r24]
* **Errors:** ERR-INV-0001 (SUPPLIER INVOICE NOT FOUND), ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r11][^r26]

### inv_hold (SUPPLIER INVOICE HOLD)
Applies a hold flag on an invoice voucher via procedure `sp_inv_hold` to block it from selection during payment runs [^r5][^r15][^r31].
* **Source file:** `04_service_definitions/accounts_payable/inv_hold.yaml` [^r27]
* **Endpoint:** `POST /ll72/svc/inv_hold` [^r28]
* **Required fields:** `ap_doc` (AP DOC) [^r15][^r29]
* **Optional fields:** `reason` (REASON) [^r15][^r29]
* **Errors:** ERR-INV-0001 (SUPPLIER INVOICE NOT FOUND), ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r15][^r31][^r32]

### inv_post (SUPPLIER INVOICE POST)
Commits invoice vouchers to the purchase and general ledgers via backend procedure `sp_inv_post`, updating purchase ledger balances and marking purchase order lines as invoiced [^r4][^r13][^r37].
* **Source file:** `04_service_definitions/accounts_payable/inv_post.yaml` [^r33]
* **Endpoint:** `POST /ll72/svc/inv_post` [^r34]
* **Required fields:** `ap_doc` (AP DOC) [^r13][^r35]
* **Optional fields:** `comment` (COMMENT) [^r35]
* **Errors:** ERR-INV-0001 (SUPPLIER INVOICE NOT FOUND), ERR-INV-0007 (SUPPLIER INVOICE NOT IN DRAFT (<status>)), ERR-MAT-0410 (MATCH FAILED: PRICE OUTSIDE TOLERANCE), ERR-MAT-0411 (MATCH FAILED: QTY INVOICED > QTY RECEIVED), ERR-PER-0003 (AP PERIOD CLOSED (<period>)), ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r13][^r38][^r39]

### inv_release (SUPPLIER INVOICE RELEASE)
Clears the hold status on an invoice voucher using stored procedure `sp_inv_release` to restore it to standard payment processing [^r6][^r16][^r43].
* **Source file:** `04_service_definitions/accounts_payable/inv_release.yaml` [^r40]
* **Endpoint:** `POST /ll72/svc/inv_release` [^r40]
* **Required fields:** `ap_doc` (AP DOC) [^r16][^r42]
* **Optional fields:** `comment` (COMMENT) [^r16][^r42]
* **Errors:** ERR-INV-0001 (SUPPLIER INVOICE NOT FOUND), ERR-INV-0007 (SUPPLIER INVOICE NOT IN DRAFT (<status>)), ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r16][^r44]

### inv_save (SUPPLIER INVOICE SAVE)
Validates entered invoice data, creates or updates draft vouchers, verifies unique supplier and invoice number combinations, and allocates the internal `ap_doc` document reference via procedure `sp_inv_save` [^r3][^r10][^r51].
* **Source file:** `04_service_definitions/accounts_payable/inv_save.yaml` [^r45]
* **Endpoint:** `POST /ll72/svc/inv_save` [^r46]
* **Required fields:** `sup_cd` (str), `sup_inv_no` (str), `inv_dt` (date), `basic` (float), `tax_cd` (str), `gross` (float) [^r10][^r47]
* **Optional fields:** `po_no` (str, PO NO), `tax` (float, TAX AMT) [^r10][^r48]
* **Errors:** [[err-sup-0030|ERR-SUP-0030]] (SUPPLIER NOT FOUND), [[err-inv-0118|ERR-INV-0118]] (DUPLICATE SUPPLIER INVOICE NO), ERR-PO-0001 (PO NOT FOUND), ERR-TAX-0101 (INVALID TAX CODE), ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r8][^r10][^r49][^r50]

### inv_search (SUPPLIER INVOICE LIST)
Opens the voucher query interface to search for existing supplier invoice vouchers using header parameters [^r1][^r12][^r52].
* **Source file:** `04_service_definitions/accounts_payable/inv_search.yaml` [^r52]
* **Endpoint:** `POST /ll72/svc/inv_search` [^r53]
* **Required fields:** none [^r54]
* **Optional fields:** `sup_cd` (str), `sup_inv_no` (str), `inv_dt` (date), `status` (str) [^r12][^r54]
* **Errors:** ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r56]

## See also
* [[screen-ap-inv-01|AP-INV-01 Supplier Invoice Entry]]
* [[screen-ap-mat-02|AP-MAT-02 Three-Way Match]]
* [[screen-ap-pay-03|AP-PAY-03 Payment Run]]
* [[screen-ap-per-11|AP-PER-11 Ap Period]]
* [[screen-ap-spy-16|AP-SPY-16 Supplier Payment Hold Hold]]
* [[screen-ap-tax-17|AP-TAX-17 Tax Code Master]]
* [[services-ap-mat|AP mat services]]
* [[services-ap-pay|AP pay services]]
* [[services-pur-po|PUR po services]]
* [[errors-inv|Errors INV (ERR-INV-*)]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 4, Layout and fields
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 4, Layout and fields
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 4, Layout and fields
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 4, Layout and fields
[^r5]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 4, Layout and fields
[^r7]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 4, Layout and fields
[^r17]: 04_service_definitions/accounts_payable/inv_cancel.yaml, service: inv_cancel
[^r22]: 04_service_definitions/accounts_payable/inv_get.yaml, service: inv_get
[^r33]: 04_service_definitions/accounts_payable/inv_post.yaml, service
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 7, AP-INV-01 SUPPLIER INVOICE ENTRY
[^r18]: 04_service_definitions/accounts_payable/inv_cancel.yaml, auth
[^r23]: 04_service_definitions/accounts_payable/inv_get.yaml, endpoint
[^r34]: 04_service_definitions/accounts_payable/inv_post.yaml, endpoint
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 25, inv_save SUPPLIER INVOICE SAVE
[^r38]: 04_service_definitions/accounts_payable/inv_post.yaml, errors
[^r14]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 26, inv_cancel SUPPLIER INVOICE CANCEL
[^r20]: 04_service_definitions/accounts_payable/inv_cancel.yaml, errors
[^r19]: 04_service_definitions/accounts_payable/inv_cancel.yaml, request
[^r8]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 11
[^r21]: 04_service_definitions/accounts_payable/inv_cancel.yaml, common_errors
[^r25]: 04_service_definitions/accounts_payable/inv_get.yaml, response.envelope
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 25, inv_get SUPPLIER INVOICE GET
[^r24]: 04_service_definitions/accounts_payable/inv_get.yaml, request.fields
[^r26]: 04_service_definitions/accounts_payable/inv_get.yaml, errors
[^r15]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 26, inv_hold SUPPLIER INVOICE HOLD
[^r31]: 04_service_definitions/accounts_payable/inv_hold.yaml, errors
[^r27]: 04_service_definitions/accounts_payable/inv_hold.yaml, whole file
[^r28]: 04_service_definitions/accounts_payable/inv_hold.yaml, whole file
[^r29]: 04_service_definitions/accounts_payable/inv_hold.yaml, request
[^r32]: 04_service_definitions/accounts_payable/inv_hold.yaml, common_errors
[^r13]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 25, inv_post SUPPLIER INVOICE POST
[^r37]: 04_service_definitions/accounts_payable/inv_post.yaml, procedures
[^r35]: 04_service_definitions/accounts_payable/inv_post.yaml, request.fields
[^r39]: 04_service_definitions/accounts_payable/inv_post.yaml, common_errors
[^r6]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 4, Layout and fields
[^r16]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 26, inv_release SUPPLIER INVOICE RELEASE
[^r43]: 04_service_definitions/accounts_payable/inv_release.yaml, response.envelope
[^r40]: 04_service_definitions/accounts_payable/inv_release.yaml, service: inv_release
[^r42]: 04_service_definitions/accounts_payable/inv_release.yaml, request.fields
[^r44]: 04_service_definitions/accounts_payable/inv_release.yaml, errors
[^r51]: 04_service_definitions/accounts_payable/inv_save.yaml, procedures
[^r45]: 04_service_definitions/accounts_payable/inv_save.yaml, service
[^r46]: 04_service_definitions/accounts_payable/inv_save.yaml, endpoint
[^r47]: 04_service_definitions/accounts_payable/inv_save.yaml, request.fields
[^r48]: 04_service_definitions/accounts_payable/inv_save.yaml, request.fields
[^r49]: 04_service_definitions/accounts_payable/inv_save.yaml, errors
[^r50]: 04_service_definitions/accounts_payable/inv_save.yaml, common_errors
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 25, inv_search SUPPLIER INVOICE LIST
[^r52]: 04_service_definitions/accounts_payable/inv_search.yaml, service: inv_search
[^r53]: 04_service_definitions/accounts_payable/inv_search.yaml, endpoint
[^r54]: 04_service_definitions/accounts_payable/inv_search.yaml, request.fields
[^r56]: 04_service_definitions/accounts_payable/inv_search.yaml, common_errors
