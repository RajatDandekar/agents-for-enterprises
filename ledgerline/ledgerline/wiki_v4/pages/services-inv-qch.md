---
title: "INV qch services"
type: "service-group"
slug: "services-inv-qch"
summary: "Inventory module services for quality hold processing on screen INV-QCH-11, including save, get, search, release, and reject operations."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/qch_get.yaml", "04_service_definitions/inventory/qch_reject.yaml", "04_service_definitions/inventory/qch_release.yaml", "04_service_definitions/inventory/qch_save.yaml", "04_service_definitions/inventory/qch_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| module | INV |
| screen | INV-QCH-11 |
| services | qch_save, qch_get, qch_search, qch_release, qch_reject |
| version_introduced | 7.0 |
| current_manual | MAN-INV-72 v7.2.3 |

The INV qch services provide the Ledgerline ERP backend operations for managing inventory quality holds on [[screen-inv-qch-11|INV-QCH-11 Quality Hold Entry]][^r6][^r28]. These services allow users to place goods receipt lines on hold, query records, release cleared items back to free stock, or mark unallocated inventory as rejected[^r1][^r2][^r4][^r5]. All endpoints operate under the INV module and require session authentication via the `X-LL-Session` header alongside appropriate role-based permissions[^r11][^r12][^r16][^r17].

## Services

### qch_save

The `qch_save` service validates the goods receipt, verifies the item code against the receipt line, ensures that sufficient unallocated balance remains on hand, generates a new QCH NO, and sets STATUS to hold[^r1]. It executes the database stored procedure `sp_qch_save` on [[screen-inv-qch-11|screen INV-QCH-11]][^r6][^r28][^r31].
* **Type:** Write[^r6][^r28]
* **Endpoint:** `POST /ll72/svc/qch_save`[^r29]
* **Version:** Available since version 7.0[^r28]
* **Required fields:** `grn_no` (string), `itm_cd` (string), `qty` (integer)[^r30]. Manual MAN-SVC-72 also specifies `reason` as a required field[^r6].
* **Optional fields:** `reason` (string)[^r30].
* **Errors:** [[errors-qch|ERR-QCH-0201]], [[err-itm-0011|ERR-ITM-0011]][^r31].
* **Source file:** `04_service_definitions/inventory/qch_save.yaml`[^r28], `MAN-SVC-72`[^r6], `MAN-INV-72`[^r1].

### qch_get

The `qch_get` service retrieves an existing quality hold record using the QCH NO and populates GRN NO, ITEM CD, QTY, REASON, STATUS, and COMMENT on [[screen-inv-qch-11|INV-QCH-11]][^r2][^r7].
* **Type:** Read[^r11]
* **Endpoint:** `POST /ll72/svc/qch_get`[^r11]
* **Version:** Available since version 7.0[^r11]
* **Required fields:** `qch_no` (string)[^r7][^r13].
* **Optional fields:** None[^r13].
* **Errors:** ERR-QCH-0001, ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503[^r7][^r14][^r15].
* **Source file:** `04_service_definitions/inventory/qch_get.yaml`[^r11], `MAN-SVC-72`[^r7], `MAN-INV-72`[^r2].

### qch_search

The `qch_search` service executes the QUALITY HOLD LIST function to return matching quality hold records based on partial search criteria on [[screen-inv-qch-11|screen INV-QCH-11]][^r3][^r8][^r32]. Responses follow standard envelopes containing `rc`, `err_cd`, `msg`, and `data`[^r35].
* **Type:** Read[^r32]
* **Endpoint:** `POST /ll72/svc/qch_search`[^r32]
* **Version:** Available since version 7.0[^r32]
* **Required fields:** None[^r34].
* **Optional fields:** `grn_no` (string), `itm_cd` (string), `qty` (integer), `status` (string)[^r8][^r34].
* **Errors:** [[errors-qch|ERR-QCH-0201]], [[err-itm-0011|ERR-ITM-0011]], ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503[^r8][^r36][^r37].
* **Source file:** `04_service_definitions/inventory/qch_search.yaml`[^r32], `MAN-SVC-72`[^r8], `MAN-INV-72`[^r3].

### qch_release

The `qch_release` service executes stored procedure `sp_qch_release` for [[screen-inv-qch-11|INV-QCH-11]], which clears the hold flag on the inventory ledger balance, restores stock to free inventory, and sets STATUS to cleared[^r4][^r9][^r21][^r25]. Standard responses return envelope elements `rc`, `err_cd`, `msg`, and `data`[^r24].
* **Type:** Write[^r9][^r21]
* **Endpoint:** `POST /ll72/svc/qch_release`[^r22]
* **Version:** Available since version 7.0[^r21]
* **Required fields:** `qch_no` (string)[^r9][^r23].
* **Optional fields:** `comment` (string)[^r9][^r23].
* **Errors:** ERR-QCH-0001, ERR-QCH-0007, ERR-QCH-0350, ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503[^r9][^r26][^r27].
* **Source file:** `04_service_definitions/inventory/qch_release.yaml`[^r21], `MAN-SVC-72`[^r9], `MAN-INV-72`[^r4].

### qch_reject

The `qch_reject` service executes stored procedure `sp_qch_reject` on [[screen-inv-qch-11|INV-QCH-11]], updating the inventory ledger to mark stock as rejected to block release to production and updating the hold record STATUS accordingly[^r5][^r10][^r16][^r20]. Standard responses return envelope parameters `rc`, `err_cd`, `msg`, and `data`[^r19].
* **Type:** Write[^r10][^r16]
* **Endpoint:** `POST /ll72/svc/qch_reject`[^r16]
* **Version:** Available since version 7.0[^r16]
* **Required fields:** `qch_no` (string), `reason` (string)[^r10][^r18].
* **Optional fields:** None[^r18].
* **Errors:** ERR-QCH-0001[^r10].
* **Source file:** `04_service_definitions/inventory/qch_reject.yaml`[^r16], `MAN-SVC-72`[^r10], `MAN-INV-72`[^r5].

## Versions and conflicts

* Today's rule ([[man-inv-72|MAN-INV-72]] v7.2.3, 2025-01-15): `qch_save` sets STATUS to hold, `qch_release` updates STATUS to cleared, and `qch_reject` marks parts as rejected to prevent production release[^r1][^r4][^r5].
  * Older rule (MAN-INV-72 v7.2.2, 2024-06-10): `qch_save` set STATUS to detained, `qch_release` returned quarantined items to usable stock, and `qch_reject` marked parts for vendor return[^r38][^r39].
  * Kind: `superseded`[^r1][^r4][^r5][^r38][^r39].
* Today's rule conflict on `qch_save` parameters: MAN-SVC-72 v7.2.3 lists `reason` among mandatory inputs alongside `grn_no`, `itm_cd`, and `qty`[^r6], whereas service definition `qch_save.yaml` lists `reason` under optional fields[^r30].
  * Kind: `contradiction`[^r6][^r30].

## See also

* [[screen-inv-qch-11|INV-QCH-11 Quality Hold Entry]]
* [[errors-qch|ERR-QCH Quality Hold Error Codes]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]
* [[sop-inv-002|SOP-INV-002 Returns to Vendor (RTV)]]
* [[services-inv-rtv|INV rtv services]]

## References

[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 16, qch_save QUALITY HOLD SAVE
[^r28]: 04_service_definitions/inventory/qch_save.yaml, service: qch_save
[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 30, Step by step
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 30, Step by step
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 31, Step by step
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 31, Step by step
[^r11]: 04_service_definitions/inventory/qch_get.yaml, service: qch_get
[^r12]: 04_service_definitions/inventory/qch_get.yaml, auth
[^r16]: 04_service_definitions/inventory/qch_reject.yaml, service
[^r17]: 04_service_definitions/inventory/qch_reject.yaml, auth
[^r31]: 04_service_definitions/inventory/qch_save.yaml, errors
[^r29]: 04_service_definitions/inventory/qch_save.yaml, auth
[^r30]: 04_service_definitions/inventory/qch_save.yaml, request.fields
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 17, qch_get QUALITY HOLD GET
[^r13]: 04_service_definitions/inventory/qch_get.yaml, request
[^r14]: 04_service_definitions/inventory/qch_get.yaml, errors
[^r15]: 04_service_definitions/inventory/qch_get.yaml, common_errors
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 31, Step by step
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 17, qch_search QUALITY HOLD LIST
[^r32]: 04_service_definitions/inventory/qch_search.yaml, service: qch_search
[^r35]: 04_service_definitions/inventory/qch_search.yaml, response
[^r34]: 04_service_definitions/inventory/qch_search.yaml, request
[^r36]: 04_service_definitions/inventory/qch_search.yaml, errors
[^r37]: 04_service_definitions/inventory/qch_search.yaml, common_errors
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 17, qch_release QUALITY HOLD RELEASE
[^r21]: 04_service_definitions/inventory/qch_release.yaml, whole file
[^r25]: 04_service_definitions/inventory/qch_release.yaml, procedures
[^r24]: 04_service_definitions/inventory/qch_release.yaml, response.envelope
[^r22]: 04_service_definitions/inventory/qch_release.yaml, auth
[^r23]: 04_service_definitions/inventory/qch_release.yaml, request.fields
[^r26]: 04_service_definitions/inventory/qch_release.yaml, errors
[^r27]: 04_service_definitions/inventory/qch_release.yaml, common_errors
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 17, qch_reject QUALITY HOLD REJECT
[^r20]: 04_service_definitions/inventory/qch_reject.yaml, procedures
[^r19]: 04_service_definitions/inventory/qch_reject.yaml, response.envelope
[^r18]: 04_service_definitions/inventory/qch_reject.yaml, request.fields
[^r38]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 14, Step by step
[^r39]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 14, Step by step
