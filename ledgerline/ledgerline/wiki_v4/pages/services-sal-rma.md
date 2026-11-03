---
title: "SAL rma services"
type: "service-group"
slug: "services-sal-rma"
summary: "Ledgerline SAL module service group for managing warranty return (RMA) lifecycle operations, including creation, retrieval, searching, approval, receipt, and claim closure."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/sales/rma_approve.yaml", "04_service_definitions/sales/rma_close.yaml", "04_service_definitions/sales/rma_get.yaml", "04_service_definitions/sales/rma_receive.yaml", "04_service_definitions/sales/rma_save.yaml", "04_service_definitions/sales/rma_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| service_group | services-sal-rma |
| module | SAL |
| screen | SAL-RMA-07 |
| version_introduced | 7.0 |
| status | current |

The `services-sal-rma` service group provides the core backend services for managing warranty returns (RMA) in Ledgerline's SAL module [^r13][^r20]. Exposed primarily through [[screen-sal-rma-07|SAL-RMA-07]], these services govern the lifecycle of an RMA claim from draft creation and customer return authorisation to physical dock receiving and final record closure [^r5][^r8][^r9][^r10][^r13]. All endpoints operate over HTTP POST, require valid session token authentication, and enforce user role permissions [^r21][^r25][^r31][^r36][^r41][^r47].

## Services

### rma_save
* **Title**: WARRANTY RETURN (RMA) SAVE [^r5][^r40]
* **Type**: write [^r14][^r40]
* **Endpoint**: `POST /ll72/svc/rma_save` [^r41]
* **Screen**: [[screen-sal-rma-07|SAL-RMA-07]] (Save / F8) [^r13][^r14][^r40]
* **Stored procedure**: `sp_rma_save` [^r14][^r44]
* **Available since**: 7.0 [^r14][^r40]
* **Description**: Validates customer, item, and fault codes, allocates an RMA NO, and sets record STATUS to draft [^r5].
* **Required fields**: `cust_cd` (CUST CD), `itm_cd` (ITEM CD), `serial_no` (SERIAL NO), `fault_cd` (FAULT CD) [^r14][^r42]
* **Optional fields**: `remarks` (REMARKS) [^r14][^r42]
* **Errors**: [[err-itm-0011|ERR-ITM-0011]], ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r14][^r44][^r45]
* **Source file**: `04_service_definitions/sales/rma_save.yaml` [^r40]

### rma_get
* **Title**: WARRANTY RETURN (RMA) GET [^r6][^r30]
* **Type**: read [^r15][^r30]
* **Endpoint**: `POST /ll72/svc/rma_get` [^r31]
* **Screen**: SAL-RMA-07 (Get / F3) [^r13][^r15][^r30]
* **Stored procedure**: None [^r15]
* **Available since**: 7.0 [^r15][^r30]
* **Description**: Retrieves an existing RMA record by reference, populating all screen fields including STATUS and COMMENT [^r6].
* **Required fields**: `rma_no` (RMA NO) [^r15][^r32]
* **Optional fields**: None [^r32]
* **Errors**: ERR-RMA-0001, ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r1][^r15][^r34]
* **Source file**: `04_service_definitions/sales/rma_get.yaml` [^r30]

### rma_search
* **Title**: WARRANTY RETURN (RMA) LIST [^r7][^r46]
* **Type**: read [^r16][^r46]
* **Endpoint**: `POST /ll72/svc/rma_search` [^r47]
* **Screen**: SAL-RMA-07 (Search / F2/Enter) [^r13][^r16][^r46]
* **Stored procedure**: None [^r16]
* **Available since**: 7.0 [^r16][^r46]
* **Description**: Searches for matching warranty return files using criteria such as customer or item codes [^r7].
* **Required fields**: None [^r48]
* **Optional fields**: `cust_cd` (CUST CD), `itm_cd` (ITEM CD), `serial_no` (SERIAL NO), `status` (STATUS) [^r16][^r48]
* **Errors**: ERR-ITM-0011, ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r16][^r50]
* **Source file**: `04_service_definitions/sales/rma_search.yaml` [^r46]

### rma_approve
* **Title**: WARRANTY RETURN (RMA) APPROVE [^r8][^r17]
* **Type**: write [^r17][^r20]
* **Endpoint**: `POST /ll72/svc/rma_approve` [^r20]
* **Screen**: SAL-RMA-07 (Approve / F9) [^r13][^r17][^r20]
* **Stored procedure**: `sp_rma_approve` [^r17][^r20]
* **Available since**: 7.0 [^r17][^r20]
* **Description**: Verifies user authority and advances STATUS to indicate transport from the retailer is authorised, permitting subsequent physical receipt [^r8][^r12].
* **Required fields**: `rma_no` [^r17][^r22]
* **Optional fields**: `comment` [^r17][^r22]
* **Errors**: ERR-RMA-0001, ERR-RMA-0007, [[err-apr-0003|ERR-APR-0003]], [[err-apr-0004|ERR-APR-0004]], [[err-rma-0210|ERR-RMA-0210]], ERR-RMA-0211, ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r2][^r17][^r23]
* **Source file**: `04_service_definitions/sales/rma_approve.yaml` [^r20]

### rma_receive
* **Title**: WARRANTY RETURN (RMA) RECEIVE [^r9][^r18]
* **Type**: write [^r18][^r35]
* **Endpoint**: `POST /ll72/svc/rma_receive` [^r36]
* **Screen**: SAL-RMA-07 (Receive) [^r13][^r18][^r35]
* **Stored procedure**: `sp_rma_receive` [^r18][^r38]
* **Available since**: 7.0 [^r18][^r35]
* **Description**: Confirms receipt and updates STATUS to indicate that returned goods are physically held on site in the inspection area [^r9]. It must be executed before a claim can be closed [^r11].
* **Required fields**: `rma_no` [^r18][^r37]
* **Optional fields**: `comment` [^r18][^r37]
* **Errors**: ERR-RMA-0001, ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r3][^r18][^r39]
* **Source file**: `04_service_definitions/sales/rma_receive.yaml` [^r35]

### rma_close
* **Title**: WARRANTY RETURN (RMA) CLOSE [^r10][^r19]
* **Type**: write [^r19][^r24]
* **Endpoint**: `POST /ll72/svc/rma_close` [^r24]
* **Screen**: SAL-RMA-07 (Close) [^r13][^r19][^r24]
* **Stored procedure**: `sp_rma_close` [^r19][^r27]
* **Available since**: 7.0 [^r19][^r24]
* **Description**: Validates that receiving stages have been completed and locks the file in final closed status [^r10][^r11].
* **Required fields**: `rma_no` (RMA NO) [^r19][^r26]
* **Optional fields**: `comment` (COMMENT) [^r19][^r26]
* **Errors**: ERR-RMA-0001, ERR-RMA-0801, ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r4][^r11][^r19][^r28][^r29]
* **Source file**: `04_service_definitions/sales/rma_close.yaml` [^r24]

## See also
* [[screen-sal-rma-07|SAL-RMA-07 Warranty Return (Rma) Entry]]
* [[errors-rma|ERR-RMA Error Codes]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[err-rma-0210|ERR-RMA-0210 Serial not registered]]
* [[err-apr-0003|ERR-APR-0003 Self-approval not permitted]]
* [[err-apr-0004|ERR-APR-0004 Advance amount exceeds PO unbilled commitment]]
* [[services-sal-so|SAL so services]]
* [[services-sal-cust|SAL cust services]]

## References

[^r13]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 38, SAL-RMA-07 WARRANTY RETURN (RMA) ENTRY
[^r20]: 04_service_definitions/sales/rma_approve.yaml, service: rma_approve
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 30, Step by step
[^r8]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 31, Authorising the return
[^r9]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 31, Acknowledging goods receipt at the plant
[^r10]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 31, Concluding and closing the claim
[^r21]: 04_service_definitions/sales/rma_approve.yaml, auth
[^r25]: 04_service_definitions/sales/rma_close.yaml, auth
[^r31]: 04_service_definitions/sales/rma_get.yaml, whole file
[^r36]: 04_service_definitions/sales/rma_receive.yaml, whole file
[^r41]: 04_service_definitions/sales/rma_save.yaml, endpoint
[^r47]: 04_service_definitions/sales/rma_search.yaml, auth
[^r40]: 04_service_definitions/sales/rma_save.yaml, service: rma_save
[^r14]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 45, rma_save WARRANTY RETURN (RMA) SAVE
[^r44]: 04_service_definitions/sales/rma_save.yaml, errors
[^r42]: 04_service_definitions/sales/rma_save.yaml, request.fields
[^r45]: 04_service_definitions/sales/rma_save.yaml, common_errors
[^r6]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 30, Step by step
[^r30]: 04_service_definitions/sales/rma_get.yaml, whole file
[^r15]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 45, rma_get WARRANTY RETURN (RMA) GET
[^r32]: 04_service_definitions/sales/rma_get.yaml, request.fields
[^r1]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 20
[^r34]: 04_service_definitions/sales/rma_get.yaml, errors
[^r7]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 30, Step by step
[^r46]: 04_service_definitions/sales/rma_search.yaml, whole file
[^r16]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 45, rma_search WARRANTY RETURN (RMA) LIST
[^r48]: 04_service_definitions/sales/rma_search.yaml, request.fields
[^r50]: 04_service_definitions/sales/rma_search.yaml, errors
[^r17]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 46, rma_approve WARRANTY RETURN (RMA) APPROVE
[^r12]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 33, Questions users ask
[^r22]: 04_service_definitions/sales/rma_approve.yaml, request.fields
[^r2]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 21
[^r23]: 04_service_definitions/sales/rma_approve.yaml, errors
[^r18]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 46, rma_receive WARRANTY RETURN (RMA) RECEIVE
[^r35]: 04_service_definitions/sales/rma_receive.yaml, whole file
[^r38]: 04_service_definitions/sales/rma_receive.yaml, procedures
[^r11]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 32, PART 7 of 14 (pp. 32-36)
[^r37]: 04_service_definitions/sales/rma_receive.yaml, request.fields
[^r3]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 20
[^r39]: 04_service_definitions/sales/rma_receive.yaml, errors
[^r19]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 46, rma_close WARRANTY RETURN (RMA) CLOSE
[^r24]: 04_service_definitions/sales/rma_close.yaml, service: rma_close
[^r27]: 04_service_definitions/sales/rma_close.yaml, response.envelope
[^r26]: 04_service_definitions/sales/rma_close.yaml, request.fields
[^r4]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 21
[^r28]: 04_service_definitions/sales/rma_close.yaml, errors
[^r29]: 04_service_definitions/sales/rma_close.yaml, common_errors
