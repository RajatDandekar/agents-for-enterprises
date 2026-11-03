---
title: "INV txf services"
type: "service-group"
slug: "services-inv-txf"
summary: "Ledgerline inventory stock transfer services for saving, retrieving, listing, posting, and cancelling warehouse transfers on screen INV-TRF-04."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/txf_cancel.yaml", "04_service_definitions/inventory/txf_get.yaml", "04_service_definitions/inventory/txf_post.yaml", "04_service_definitions/inventory/txf_save.yaml", "04_service_definitions/inventory/txf_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | INV |
| Screen | [[screen-inv-trf-04|INV-TRF-04]] |
| Service count | 5 |
| Transport | POST /ll72/svc/* |
| Status | Current |

The stock transfer service group manages inventory movements between warehouses in Ledgerline's INV module [^r1][^r25]. Executed primarily via screen [[screen-inv-trf-04|INV-TRF-04]], these services validate item status, warehouse separation, and available inventory before recording or committing transfers [^r5]. All five endpoints have been available since Ledgerline 7.0, operate over HTTP POST, and require an active session token in the `X-LL-Session` header with an authorised role [^r11][^r12][^r15][^r16][^r20][^r21][^r25][^r26][^r29][^r30].

## Services

### txf_save
The `txf_save` write service performs STOCK TRANSFER SAVE under module INV, calling database procedure `sp_txf_save` at endpoint `POST /ll72/svc/txf_save` [^r1][^r6][^r25]. It validates transfer entries, assigns a sequential TXF NO, sets the document status to saved, and is mapped to key F8 on screen [[screen-inv-trf-04|INV-TRF-04]] [^r1][^r5].

* **Required fields**: `itm_cd` (ITEM CD, str), `from_whs` (FROM WHS, str), `to_whs` (TO WHS, str), `qty` (QTY, int) [^r6][^r27].
* **Optional fields**: `reason` (REASON, str) [^r27].
* **Errors**: ERR-TXF-0201 (QTY MUST BE > 0), [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE), ERR-TXF-0310 (FROM AND TO WAREHOUSE ARE THE SAME), ERR-STK-0102 (INSUFFICIENT STOCK (<available>)) [^r6][^r28][^r36].
* **Source file**: `04_service_definitions/inventory/txf_save.yaml` [^r25].

### txf_get
The `txf_get` read service performs STOCK TRANSFER GET under module INV, fetching recorded transfer details at endpoint `POST /ll72/svc/txf_get` and mapping to key F3 on screen [[screen-inv-trf-04|INV-TRF-04]] [^r2][^r5][^r7][^r15][^r16]. Its response envelope provides `rc` ('S | W | E'), `err_cd`, `msg`, and `data` [^r18].

* **Required fields**: `txf_no` (TXF NO, str) [^r7][^r17].
* **Optional fields**: none [^r17].
* **Errors**: ERR-TXF-0001 (STOCK TRANSFER NOT FOUND), plus common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r7][^r14][^r19][^r34].
* **Source file**: `04_service_definitions/inventory/txf_get.yaml` [^r15].

### txf_search
The `txf_search` read service performs STOCK TRANSFER LIST querying under module INV at endpoint `POST /ll72/svc/txf_search`, opened via key F2/Enter on screen [[screen-inv-trf-04|INV-TRF-04]] [^r2][^r5][^r8][^r29][^r30]. The response envelope returns `rc`, `err_cd`, `msg`, and `data` [^r32].

* **Required fields**: none [^r31].
* **Optional fields**: `itm_cd` (ITEM CD, str), `from_whs` (FROM WHS, str), `to_whs` (TO WHS, str), `status` (STATUS, str) [^r8][^r31].
* **Errors**: [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE), alongside common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r8][^r33].
* **Source file**: `04_service_definitions/inventory/txf_search.yaml` [^r29].

### txf_post
The `txf_post` write service performs STOCK TRANSFER POST under module INV, invoking stored procedure `sp_txf_post` at endpoint `POST /ll72/svc/txf_post` and mapping to key F9 on screen [[screen-inv-trf-04|INV-TRF-04]] [^r3][^r5][^r9][^r20]. It commits stock movements by simultaneously debiting the source location and crediting the destination location, rendering the transfer permanently uneditable [^r3].

* **Required fields**: `txf_no` (str) [^r9][^r22].
* **Optional fields**: `comment` (str) [^r22].
* **Errors**: ERR-TXF-0001 (STOCK TRANSFER NOT FOUND), ERR-TXF-0007 (STOCK TRANSFER NOT IN DRAFT (<status>)), and common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r9][^r23][^r24][^r34][^r35].
* **Source file**: `04_service_definitions/inventory/txf_post.yaml` [^r20].

### txf_cancel
The `txf_cancel` write service performs STOCK TRANSFER CANCEL under module INV, invoking stored procedure `sp_txf_cancel` at endpoint `POST /ll72/svc/txf_cancel` and mapping to key Shift+F8 on screen [[screen-inv-trf-04|INV-TRF-04]] [^r4][^r5][^r10][^r11][^r14]. It marks unposted draft transfers as cancelled and fails if executed against closed or committed records [^r4].

* **Required fields**: `txf_no` (TXF NO, str), `reason` (REASON, str) [^r10][^r13].
* **Optional fields**: none [^r13].
* **Errors**: ERR-TXF-0001 (STOCK TRANSFER NOT FOUND), ERR-TXF-0801 (STOCK TRANSFER CLOSED (<status>)) [^r4][^r10][^r14][^r34][^r37].
* **Source file**: `04_service_definitions/inventory/txf_cancel.yaml` [^r11].

## Versions and conflicts

Today's operating baseline under Ledgerline v7.2.3 requires warehouse separation, available inventory, and specific document status validation across `txf_save`, `txf_get`, `txf_search`, `txf_post`, and `txf_cancel` [^r1][^r2][^r3][^r4][^r5][^r6][^r7][^r8][^r9][^r10]. In the superseded v7.2.2 documentation (dated 2024-06-10), the same five services and error classes were documented prior to the current maintenance manual baseline [^r38].

## See also

* [[screen-inv-trf-04|INV-TRF-04 Stock Transfer Entry]]
* [[errors-txf|Stock Transfer Error Codes (ERR-TXF-*)]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[services-inv-itm|INV itm services]]
* [[services-inv-stk|INV stk services]]
* [[services-inv-whs|INV whs services]]
* [[services-inv-rtv|INV rtv services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 4, Step by step
[^r25]: 04_service_definitions/inventory/txf_save.yaml, service: txf_save
[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 20, INV-TRF-04 STOCK TRANSFER ENTRY
[^r11]: 04_service_definitions/inventory/txf_cancel.yaml, whole file
[^r12]: 04_service_definitions/inventory/txf_cancel.yaml, auth
[^r15]: 04_service_definitions/inventory/txf_get.yaml, whole file
[^r16]: 04_service_definitions/inventory/txf_get.yaml, whole file
[^r20]: 04_service_definitions/inventory/txf_post.yaml, whole file
[^r21]: 04_service_definitions/inventory/txf_post.yaml, auth
[^r26]: 04_service_definitions/inventory/txf_save.yaml, auth
[^r29]: 04_service_definitions/inventory/txf_search.yaml, service
[^r30]: 04_service_definitions/inventory/txf_search.yaml, endpoint
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 9, txf_save STOCK TRANSFER SAVE
[^r27]: 04_service_definitions/inventory/txf_save.yaml, request.fields
[^r28]: 04_service_definitions/inventory/txf_save.yaml, errors
[^r36]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 26
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 4, Step by step
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 9, txf_get STOCK TRANSFER GET
[^r18]: 04_service_definitions/inventory/txf_get.yaml, response
[^r17]: 04_service_definitions/inventory/txf_get.yaml, request
[^r14]: 04_service_definitions/inventory/txf_cancel.yaml, errors
[^r19]: 04_service_definitions/inventory/txf_get.yaml, errors
[^r34]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 26
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 9, txf_search STOCK TRANSFER LIST
[^r32]: 04_service_definitions/inventory/txf_search.yaml, response.envelope
[^r31]: 04_service_definitions/inventory/txf_search.yaml, request.fields
[^r33]: 04_service_definitions/inventory/txf_search.yaml, errors
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 5, Step by step
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 10, txf_post STOCK TRANSFER POST
[^r22]: 04_service_definitions/inventory/txf_post.yaml, request.fields
[^r23]: 04_service_definitions/inventory/txf_post.yaml, errors
[^r24]: 04_service_definitions/inventory/txf_post.yaml, common_errors
[^r35]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 26
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 6, Questions users ask
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 10, txf_cancel STOCK TRANSFER CANCEL
[^r13]: 04_service_definitions/inventory/txf_cancel.yaml, request.fields
[^r37]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 26
[^r38]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 2, §3. Stock Transfer (INV-TRF-04)
