---
title: "SAL so services"
type: "service-group"
slug: "services-sal-so"
summary: "Ledgerline sales order services handling creation, enquiry, confirmation, hold, amendment, release, and cancellation on screen SAL-SO-01."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/sales/so_amend.yaml", "04_service_definitions/sales/so_cancel.yaml", "04_service_definitions/sales/so_confirm.yaml", "04_service_definitions/sales/so_fetch.yaml", "04_service_definitions/sales/so_get.yaml", "04_service_definitions/sales/so_hold.yaml", "04_service_definitions/sales/so_release.yaml", "04_service_definitions/sales/so_save.yaml", "04_service_definitions/sales/so_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Service group | SAL so |
| Module | SAL |
| Screen | SAL-SO-01 |
| Introduced | Ledgerline 7.0 |
| Protocol | HTTP POST |
| Base path | /ll72/svc/ |

The `so` service group provides core sales order lifecycle management operations within the Ledgerline SAL module, hosted on screen [[screen-sal-so-01|SAL-SO-01]][^r17]. These services handle draft creation, inventory balance validation, order confirmation, holds, amendments, and cancellations[^r8][^r9][^r10][^r13][^r14][^r16]. All endpoints operate via POST requests requiring an active session token in the `X-LL-Session` header and authorized role permissions[^r28][^r34][^r39][^r45][^r50][^r55][^r60][^r65][^r71]. Standard responses return an envelope containing `rc` ('S | W | E'), `err_cd`, `msg`, and `data`[^r30][^r41][^r47][^r52][^r73].

| Field | Value |
|---|---|
| Service group | SAL so |
| Module | SAL |
| Primary screen | SAL-SO-01 |
| Introduced | Ledgerline 7.0 |
| Protocol | HTTP POST |
| Base path | `/ll72/svc/` |

## Services

### so_amend

The `so_amend` write service recalculates order totals, updates allocations, and stores revisions on screen SAL-SO-01 for sales orders that are not fully picked or invoiced, executing stored procedure `sp_so_amend`[^r13][^r24][^r27][^r31]. Available since version 7.0 at endpoint `POST /ll72/svc/so_amend`, execution requires session token authentication in header `X-LL-Session` and a role permitted to run the service[^r27][^r28].

* **Required fields:** `so_no` (str)[^r24][^r29].
* **Optional fields:** `cust_cd` (str), `itm_cd` (str), `qty` (int), `price` (float)[^r29].
* **Errors:** [[errors-so|ERR-SO-0001]], ERR-SO-0801, ERR-SO-0201, [[err-itm-0011|ERR-ITM-0011]], ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503[^r3][^r6][^r7][^r24][^r32].
* **Source file:** `04_service_definitions/sales/so_amend.yaml`[^r27].

### so_cancel

The `so_cancel` write service cancels an open sales order, unallocating reserved inventory in Manchester and Leeds stores through stored procedure `sp_so_cancel` on screen SAL-SO-01 via key shortcut Shift+F8[^r16][r17][^r23][^r36]. Available since version 7.0 at endpoint `POST /ll72/svc/so_cancel`, callers must authenticate with an `X-LL-Session` token and carry appropriate role permissions[^r33][^r34].

* **Required fields:** `so_no` (str), `reason` (str)[^r16][^r23][^r35].
* **Optional fields:** None[^r35].
* **Errors:** ERR-SO-0001, ERR-SO-0801, ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503[^r3][^r7][^r23][^r37].
* **Source file:** `04_service_definitions/sales/so_cancel.yaml`[^r33].

### so_confirm

The `so_confirm` write service validates inventory availability and customer credit standing, changes order status to confirmed, and advances demand to the warehouse queue using procedure `sp_so_confirm` on screen SAL-SO-01 via key shortcut F9[^r10][^r17][^r22][^r43]. Available since version 7.0 at endpoint `POST /ll72/svc/so_confirm`, it requires header `X-LL-Session` and permitted role access[^r38][^r39].

* **Required fields:** `so_no` (str)[^r22][^r40].
* **Optional fields:** `comment` (str)[^r40].
* **Errors:** ERR-SO-0001, ERR-SO-0007, [[err-crd-0207|ERR-CRD-0207]], [[err-prc-0001|ERR-PRC-0001]], ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503[^r1][^r3][^r4][^r22][^r42][^r43].
* **Source file:** `04_service_definitions/sales/so_confirm.yaml`[^r38].

### so_fetch

The `so_fetch` read service checks warehouse stock balances at the default shipping site and loads contract or trade list pricing into PRICE on screen SAL-SO-01 via key shortcut F3[^r8][^r17][^r18][^r44]. Introduced in version 7.0 at endpoint `POST /ll72/svc/so_fetch`, requests require session header `X-LL-Session` and authorized role permissions[^r44][^r45].

* **Required fields:** `cust_cd` (str), `itm_cd` (str), `qty` (int), `req_dt` (date)[^r18][^r46].
* **Optional fields:** `price` (float), `cust_ref` (str)[^r46].
* **Errors:** ERR-SO-0001, ERR-SO-0201, ERR-ITM-0011, ERR-SO-0105, ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503[^r3][^r5][^r6][^r18][^r48].
* **Source file:** `04_service_definitions/sales/so_fetch.yaml`[^r44].

### so_get

The `so_get` read service retrieves an existing sales order by order number, populating header fields, line items, and order STATUS on screen SAL-SO-01 via key shortcut F3[^r11][^r17][^r20][^r49]. It has been available since version 7.0 at endpoint `POST /ll72/svc/so_get` and requires an authorized role and `X-LL-Session` token[^r49][^r50].

* **Required fields:** `so_no` (str)[^r11][^r20][^r51].
* **Optional fields:** None[^r51].
* **Errors:** ERR-SO-0001, ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503[^r3][^r20][^r53].
* **Source file:** `04_service_definitions/sales/so_get.yaml`[^r49].

### so_hold

The `so_hold` write service updates a sales order to held status using procedure `sp_so_hold` on screen SAL-SO-01, blocking picking ticket generation and order dispatch[^r14][^r17][^r25][^r57]. Available since version 7.0 at endpoint `POST /ll72/svc/so_hold`, authentication requires an `X-LL-Session` token and a role permitted to run the service[^r54][^r55].

* **Required fields:** `so_no` (str)[^r25][^r56].
* **Optional fields:** `reason` (str)[^r14][^r56].
* **Errors:** ERR-SO-0001, ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503[^r3][^r25][^r58].
* **Source file:** `04_service_definitions/sales/so_hold.yaml`[^r54].

### so_release

The `so_release` write service returns a held sales order to confirmed status using database procedure `sp_so_release` on screen SAL-SO-01 via shortcut key F9, re-enabling active dispatch scheduling[^r15][^r17][^r26][^r62]. Available since version 7.0 at endpoint `POST /ll72/svc/so_release`, requests require `X-LL-Session` authentication and role authorization[^r59][^r60].

* **Required fields:** `so_no` (str)[^r26][^r61].
* **Optional fields:** `comment` (str)[^r61].
* **Errors:** ERR-SO-0001, ERR-SO-0007, ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503[^r3][^r4][^r26][^r63].
* **Source file:** `04_service_definitions/sales/so_release.yaml`[^r59].

### so_save

The `so_save` write service validates header and line details, calculates VAT and line extensions, creates the sales order, assigns draft status, and generates the new SO NO via stored procedure `sp_so_save` on screen SAL-SO-01 using key shortcut F8[^r9][^r17][^r19][^r67]. Introduced in version 7.0 at endpoint `POST /ll72/svc/so_save`, calls require an `X-LL-Session` token and an authorized user role[^r64][^r65].

* **Required fields:** `cust_cd` (str), `itm_cd` (str), `qty` (int), `req_dt` (date)[^r19][^r66].
* **Optional fields:** `price` (float), `cust_ref` (str)[^r66].
* **Errors:** ERR-SO-0201, ERR-ITM-0011, ERR-SO-0105, ERR-CUS-0031, ERR-PRC-0001, ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503[^r2][^r5][^r6][^r19][^r68][^r69].
* **Source file:** `04_service_definitions/sales/so_save.yaml`[^r64].

### so_search

The `so_search` read service executes sales order list inquiries on screen SAL-SO-01 via shortcut F2 or Enter, opening a search window to match orders across all records or filtered criteria[^r12][^r17][^r21][^r70]. Available since version 7.0 at endpoint `POST /ll72/svc/so_search`, it requires an `X-LL-Session` session header and permitted user role[^r70][^r71].

* **Required fields:** None[^r72].
* **Optional fields:** `cust_cd` (str), `itm_cd` (str), `qty` (int), `status` (str)[^r21][^r72].
* **Errors:** ERR-SO-0201, ERR-ITM-0011, ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503[^r6][^r21][^r74].
* **Source file:** `04_service_definitions/sales/so_search.yaml`[^r70].

## See also

* [[screen-sal-so-01|SAL-SO-01 Sales Order]]
* [[errors-so|Errors SO (Sales Order)]]
* [[err-crd-0207|ERR-CRD-0207 Customer Credit Limit Exceeded]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[err-prc-0001|ERR-PRC-0001 Mandatory parameters absent or pricing conflict]]
* [[services-sal-alc|SAL alc services]]
* [[services-sal-crd|SAL crd services]]
* [[services-sal-cust|SAL cust services]]
* [[services-sal-dlv|SAL dlv services]]
* [[services-sal-pck|SAL pck services]]
* [[services-sal-prc|SAL prc services]]
* [[services-sal-quo|SAL quo services]]
* [[services-sal-sinv|SAL sinv services]]

## References

[^r17]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 39, SAL-SO-01 SALES ORDER
[^r8]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 8, Step by step
[^r9]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 8, Step by step
[^r10]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 8, Step by step
[^r13]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 9, Step by step
[^r14]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 9, Step by step
[^r16]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 9, Step by step
[^r28]: 04_service_definitions/sales/so_amend.yaml, whole file
[^r34]: 04_service_definitions/sales/so_cancel.yaml, auth
[^r39]: 04_service_definitions/sales/so_confirm.yaml, endpoint
[^r45]: 04_service_definitions/sales/so_fetch.yaml, auth
[^r50]: 04_service_definitions/sales/so_get.yaml, auth
[^r55]: 04_service_definitions/sales/so_hold.yaml, whole file
[^r60]: 04_service_definitions/sales/so_release.yaml, auth
[^r65]: 04_service_definitions/sales/so_save.yaml, service: so_save
[^r71]: 04_service_definitions/sales/so_search.yaml, auth
[^r30]: 04_service_definitions/sales/so_amend.yaml, response.envelope
[^r41]: 04_service_definitions/sales/so_confirm.yaml, response
[^r47]: 04_service_definitions/sales/so_fetch.yaml, response.envelope
[^r52]: 04_service_definitions/sales/so_get.yaml, response.envelope
[^r73]: 04_service_definitions/sales/so_search.yaml, response.envelope
[^r24]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 40, so_amend SALES ORDER AMEND
[^r27]: 04_service_definitions/sales/so_amend.yaml, whole file
[^r31]: 04_service_definitions/sales/so_amend.yaml, procedures
[^r29]: 04_service_definitions/sales/so_amend.yaml, request.fields
[^r3]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 24, ERR-SO-0001 SALES ORDER NOT FOUND
[^r6]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 24, ERR-SO-0201 QTY MUST BE > 0
[^r7]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 24, ERR-SO-0801 SALES ORDER CLOSED (<status>)
[^r32]: 04_service_definitions/sales/so_amend.yaml, errors
[^r23]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 40, so_cancel SALES ORDER CANCEL
[^r36]: 04_service_definitions/sales/so_cancel.yaml, procedures
[^r33]: 04_service_definitions/sales/so_cancel.yaml, whole file
[^r35]: 04_service_definitions/sales/so_cancel.yaml, request.fields
[^r37]: 04_service_definitions/sales/so_cancel.yaml, errors
[^r22]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 40, so_confirm SALES ORDER CONFIRM
[^r43]: 04_service_definitions/sales/so_confirm.yaml, common_errors
[^r38]: 04_service_definitions/sales/so_confirm.yaml, service
[^r40]: 04_service_definitions/sales/so_confirm.yaml, request
[^r1]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 6, ERR-CRD-0207
[^r4]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 24, ERR-SO-0007 SALES ORDER NOT IN DRAFT (<status>)
[^r42]: 04_service_definitions/sales/so_confirm.yaml, errors
[^r18]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 39, so_fetch SALES ORDER FETCH
[^r44]: 04_service_definitions/sales/so_fetch.yaml, service: so_fetch
[^r46]: 04_service_definitions/sales/so_fetch.yaml, request.fields
[^r5]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 24, ERR-SO-0105 DATE IN PAST
[^r48]: 04_service_definitions/sales/so_fetch.yaml, errors
[^r11]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 8, Step by step
[^r20]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 39, so_get SALES ORDER GET
[^r49]: 04_service_definitions/sales/so_get.yaml, service: so_get
[^r51]: 04_service_definitions/sales/so_get.yaml, request.fields
[^r53]: 04_service_definitions/sales/so_get.yaml, errors
[^r25]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 41, so_hold SALES ORDER HOLD
[^r57]: 04_service_definitions/sales/so_hold.yaml, procedures
[^r54]: 04_service_definitions/sales/so_hold.yaml, whole file
[^r56]: 04_service_definitions/sales/so_hold.yaml, request.fields
[^r58]: 04_service_definitions/sales/so_hold.yaml, errors
[^r15]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 9, Step by step
[^r26]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 41, so_release SALES ORDER RELEASE
[^r62]: 04_service_definitions/sales/so_release.yaml, procedures
[^r59]: 04_service_definitions/sales/so_release.yaml, service: so_release
[^r61]: 04_service_definitions/sales/so_release.yaml, request.fields
[^r63]: 04_service_definitions/sales/so_release.yaml, errors
[^r19]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 39, so_save SALES ORDER SAVE
[^r67]: 04_service_definitions/sales/so_save.yaml, procedures
[^r64]: 04_service_definitions/sales/so_save.yaml, service: so_save
[^r66]: 04_service_definitions/sales/so_save.yaml, request.fields
[^r2]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 7, ERR-CUS-0031
[^r68]: 04_service_definitions/sales/so_save.yaml, errors
[^r69]: 04_service_definitions/sales/so_save.yaml, common_errors
[^r12]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 8, Step by step
[^r21]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 40, so_search SALES ORDER LIST
[^r70]: 04_service_definitions/sales/so_search.yaml, service: so_search
[^r72]: 04_service_definitions/sales/so_search.yaml, request.fields
[^r74]: 04_service_definitions/sales/so_search.yaml, errors
