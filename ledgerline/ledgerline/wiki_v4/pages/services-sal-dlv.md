---
title: "SAL dlv services"
type: "service-group"
slug: "services-sal-dlv"
summary: "Ledgerline sales delivery services supporting despatch entry, search, label streaming, posting, and cancellation on screen SAL-DLV-05."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/sales/dlv_cancel.yaml", "04_service_definitions/sales/dlv_get.yaml", "04_service_definitions/sales/dlv_label.yaml", "04_service_definitions/sales/dlv_post.yaml", "04_service_definitions/sales/dlv_save.yaml", "04_service_definitions/sales/dlv_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| service_group | services-sal-dlv |
| module | SAL |
| screen | SAL-DLV-05 |
| introduced | 7.0 |
| status | current |

The `services-sal-dlv` service group provides the backend operations for sales despatch management and parcel labelling in Ledgerline [^r10]. Associated with screen [[screen-sal-dlv-05|SAL-DLV-05]], these services handle delivery retrieval, searching, draft saving, carton label streaming, inventory issue posting, and cancellation [^r10]. All services run under the `SAL` module and require session token authentication via HTTP header `X-LL-Session` with an authorized user role [^r18][^r23][^r28][^r32][^r39][^r43].

## Services

### dlv_get
Retrieves existing despatch details or delivery and pick records into the active screen buffer, verifying the pick state [^r4][^r12].
* **Type**: Read [^r12][^r22]
* **Endpoint**: `POST /ll72/svc/dlv_get` [^r22]
* **Screen**: [[screen-sal-dlv-05|SAL-DLV-05]] [^r12]
* **Underlying procedure**: None [^r12]
* **Required fields**: `dlv_no` (DLV NO, string) [^r12][^r24]
* **Optional fields**: None [^r12][^r24]
* **Response**: Envelope returning return code `rc` (`S | W | E`), `err_cd`, `msg`, and `data` result [^r25].
* **Errors**: Specific domain error `ERR-DLV-0001` (DESPATCH NOT FOUND), and common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r12][^r26].
* **Source file**: `04_service_definitions/sales/dlv_get.yaml` [^r22]

### dlv_search
Opens a selection grid and executes search queries for open delivery and despatch records by account, area, pick number, carrier, parcel count, or status [^r5][^r13][^r44].
* **Type**: Read [^r13][^r42]
* **Endpoint**: `POST /ll72/svc/dlv_search` [^r43]
* **Screen**: [[screen-sal-dlv-05|SAL-DLV-05]] [^r13]
* **Underlying procedure**: None [^r13]
* **Required fields**: None [^r13][^r44]
* **Optional fields**: `pck_no` (PICK NO, string), `carrier_cd` (CARRIER, string), `parcels` (PARCELS, integer), and `status` (STATUS, string) [^r13][^r44]
* **Errors**: Common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r45].
* **Source file**: `04_service_definitions/sales/dlv_search.yaml` [^r42]

### dlv_save
Commits entered gross weights and parcel counts, creates a despatch record, and generates a unique delivery reference into `DLV NO` [^r6][^r11].
* **Type**: Write [^r11][^r38]
* **Endpoint**: `POST /ll72/svc/dlv_save` [^r39]
* **Screen**: [[screen-sal-dlv-05|SAL-DLV-05]] [^r11][^r38]
* **Underlying procedure**: `sp_dlv_save` [^r11][^r39]
* **Required fields**: `pck_no` (PICK NO, string), `carrier_cd` (CARRIER, string), and `parcels` (PARCELS, integer) [^r11][^r40]
* **Optional fields**: `weight_kg` (WEIGHT KG, float) [^r11][^r40]
* **Errors**: `ERR-DLV-0301` (PICK NOT CONFIRMED) if pick confirmation is missing, alongside common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r2][^r11][^r41].
* **Source file**: `04_service_definitions/sales/dlv_save.yaml` [^r38]

### dlv_label
Transmits parcel details to the label service, verifies carrier and weight values, and streams barcoded carton labels to the despatch bench label printer [^r7][^r16].
* **Type**: Write [^r16][^r27]
* **Endpoint**: `POST /ll72/svc/dlv_label` [^r27]
* **Screen**: [[screen-sal-dlv-05|SAL-DLV-05]] [^r16][^r27]
* **Underlying procedure**: `sp_dlv_label` [^r16][^r30]
* **Required fields**: `dlv_no` (DLV NO, string) [^r16][^r29]
* **Optional fields**: None [^r16][^r29]
* **Errors**: `ERR-DLV-0001` (DESPATCH NOT FOUND), and common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r16][^r30].
* **Source file**: `04_service_definitions/sales/dlv_label.yaml` [^r27]

### dlv_post
Executes the formal stock issue, relieves finished stock balances, creates final goods movements, writes delivery ledger entries, and closes the pick list [^r8][^r14].
* **Type**: Write [^r14][^r31]
* **Endpoint**: `POST /ll72/svc/dlv_post` [^r31]
* **Screen**: [[screen-sal-dlv-05|SAL-DLV-05]] [^r14][^r31]
* **Underlying procedure**: `sp_dlv_post` [^r14][^r35]
* **Required fields**: `dlv_no` (DLV NO, string) [^r14][^r33]
* **Optional fields**: `comment` (string) [^r14][^r33]
* **Response**: Envelope returning `rc` (`S | W | E`), `err_cd`, `msg`, and `data` result [^r34].
* **Errors**: Domain error codes `ERR-DLV-0001` (DESPATCH NOT FOUND), `ERR-DLV-0007` (DESPATCH NOT IN DRAFT (<status>)) if not in Draft or pending status, [[err-dlv-0320|ERR-DLV-0320]] (LITHIUM BATTERY LABEL NOT PRINTED) if required battery labels have not been printed, and [[err-frt-0501|ERR-FRT-0501]] (CARRIER BOOKING FAILED), alongside common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503` [^r1][^r3][^r14][^r36][^r37].
* **Source file**: `04_service_definitions/sales/dlv_post.yaml` [^r31]

### dlv_cancel
Revokes an unposted delivery draft or reverses a delivery subject to supervisor review [^r9][^r15].
* **Type**: Write [^r15][^r17]
* **Endpoint**: `POST /ll72/svc/dlv_cancel` [^r18]
* **Screen**: [[screen-sal-dlv-05|SAL-DLV-05]] [^r15][^r17]
* **Underlying procedure**: `sp_dlv_cancel` [^r15][^r20]
* **Required fields**: `dlv_no` (DLV NO, string) and `reason` (REASON, string) [^r9][^r15][^r19]
* **Optional fields**: None [^r15][^r19]
* **Response**: Envelope returning `rc` (`S | W | E`), `err_cd`, `msg`, and `data` result [^r21].
* **Errors**: `ERR-DLV-0001` (DESPATCH NOT FOUND) and `ERR-DLV-0801` [^r15].
* **Source file**: `04_service_definitions/sales/dlv_cancel.yaml` [^r17]

## See also
* [[screen-sal-dlv-05|SAL-DLV-05 Despatch Entry]]
* [[errors-dlv|ERR-DLV Despatch Error Codes]]
* [[err-dlv-0320|ERR-DLV-0320 Lithium Battery Label Required]]
* [[err-frt-0501|ERR-FRT-0501 Carrier interface failure]]
* [[services-sal-pck|SAL pck services]]
* [[services-sal-frt|SAL frt services]]
* [[services-sal-so|SAL so services]]

## References

[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 34, SAL-DLV-05 DESPATCH ENTRY
[^r18]: 04_service_definitions/sales/dlv_cancel.yaml, auth
[^r23]: 04_service_definitions/sales/dlv_get.yaml, auth
[^r28]: 04_service_definitions/sales/dlv_label.yaml, auth
[^r32]: 04_service_definitions/sales/dlv_post.yaml, auth
[^r39]: 04_service_definitions/sales/dlv_save.yaml, service: dlv_save
[^r43]: 04_service_definitions/sales/dlv_search.yaml, auth
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 22, Screen layout
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 43, dlv_get DESPATCH GET
[^r22]: 04_service_definitions/sales/dlv_get.yaml, service: dlv_get
[^r24]: 04_service_definitions/sales/dlv_get.yaml, request
[^r25]: 04_service_definitions/sales/dlv_get.yaml, response
[^r26]: 04_service_definitions/sales/dlv_get.yaml, errors
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 23, Screen layout
[^r13]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 43, dlv_search DESPATCH LIST
[^r44]: 04_service_definitions/sales/dlv_search.yaml, request.fields
[^r42]: 04_service_definitions/sales/dlv_search.yaml, service: dlv_search
[^r45]: 04_service_definitions/sales/dlv_search.yaml, common_errors
[^r6]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 23, Screen layout
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 43, dlv_save DESPATCH SAVE
[^r38]: 04_service_definitions/sales/dlv_save.yaml, service: dlv_save
[^r40]: 04_service_definitions/sales/dlv_save.yaml, request.fields
[^r2]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 8, ERR-DLV-0301
[^r41]: 04_service_definitions/sales/dlv_save.yaml, errors
[^r7]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 23, Screen layout
[^r16]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 44, dlv_label DESPATCH LABEL
[^r27]: 04_service_definitions/sales/dlv_label.yaml, service: dlv_label
[^r30]: 04_service_definitions/sales/dlv_label.yaml, errors
[^r29]: 04_service_definitions/sales/dlv_label.yaml, request.fields
[^r8]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 23, Screen layout
[^r14]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 44, dlv_post DESPATCH POST
[^r31]: 04_service_definitions/sales/dlv_post.yaml, service: dlv_post
[^r35]: 04_service_definitions/sales/dlv_post.yaml, procedures
[^r33]: 04_service_definitions/sales/dlv_post.yaml, request.fields
[^r34]: 04_service_definitions/sales/dlv_post.yaml, response.envelope
[^r1]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 8, ERR-DLV-0320
[^r3]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 8, ERR-DLV-0007
[^r36]: 04_service_definitions/sales/dlv_post.yaml, errors
[^r37]: 04_service_definitions/sales/dlv_post.yaml, common_errors
[^r9]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 23, Screen layout
[^r15]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 44, dlv_cancel DESPATCH CANCEL
[^r17]: 04_service_definitions/sales/dlv_cancel.yaml, service: dlv_cancel
[^r20]: 04_service_definitions/sales/dlv_cancel.yaml, procedures
[^r19]: 04_service_definitions/sales/dlv_cancel.yaml, request.fields
[^r21]: 04_service_definitions/sales/dlv_cancel.yaml, response.envelope
