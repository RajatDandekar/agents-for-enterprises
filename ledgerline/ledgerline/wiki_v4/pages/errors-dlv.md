---
title: "ERR-DLV Despatch Error Codes"
type: "error-list"
slug: "errors-dlv"
summary: "Error codes for sales despatch transactions under the ERR-DLV prefix in Ledgerline ERP."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "04_service_definitions/sales/dlv_cancel.yaml", "04_service_definitions/sales/dlv_get.yaml", "04_service_definitions/sales/dlv_label.yaml", "04_service_definitions/sales/dlv_post.yaml", "04_service_definitions/sales/dlv_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-DLV |
| Module | Sales (SAL) |
| Entity | Despatch |
| Governing manual | [[man-sal-72|MAN-SAL-72]] |
| Governing service group | [[services-sal-dlv|SAL dlv services]] |
| Status | current |

Error codes prefixed with ERR-DLV handle validation failures, status restrictions, and missing documentation during sales delivery processing in Ledgerline ERP [^r1][^r6]. They are raised across the [[services-sal-dlv|SAL dlv services]] API and the [[man-sal-72|MAN-SAL-72]] user interfaces [^r1][^r10].

### ERR-DLV-0001
* Message: DESPATCH NOT FOUND [^r6][^r8][^r9][^r10]
* Cause: The requested delivery number (`dlv_no`) does not exist in the active records, or the pick reference entered in PICK NO cannot be found in active sales orders tables [^r1][^r8][^r10].
* Remedy: Verify that the delivery number exists or re-check the entered pick reference against active sales orders [^r1][^r8][^r10].
* Raised by: `dlv_cancel` [^r6], `dlv_get` [^r8], `dlv_label` [^r9], `dlv_post` [^r10], and [[man-sal-72|MAN-SAL-72]] screen processing [^r1].

### ERR-DLV-0007
* Message: DESPATCH NOT IN DRAFT (<status>) [^r11]
* Cause: An attempt is made to post a despatch record that is not currently in draft status, or the entered pick list is printed but warehouse picking confirmation has not been posted in the preceding screen [^r2][^r11].
* Remedy: Ensure warehouse picking confirmation has been posted, or confirm the delivery record remains in draft status prior to posting [^r2][^r11].
* Raised by: `dlv_post` [^r11] and [[man-sal-72|MAN-SAL-72]] screen processing [^r2].

### ERR-DLV-0301
* Message: PICK NOT CONFIRMED [^r13]
* Cause: Warehouse picking confirmation has not been posted, or the delivery is already posted, preventing amendment, save, or re-posting of closed records [^r3][^r13].
* Remedy: Ensure picking confirmation is completed before calling save, and avoid saving or modifying deliveries that have already reached closed status [^r3][^r13].
* Raised by: `dlv_save` [^r13] and [[man-sal-72|MAN-SAL-72]] screen processing [^r3].

### ERR-DLV-0320
* Message: LITHIUM BATTERY LABEL NOT PRINTED [^r12]
* Cause: A battery pack lacks a printed DG label when `SAL.DG_LABEL_REQ` is set to `Y`, gross weight violates tolerance upon posting, or `dlv_cancel` is called with an empty REASON field [^r4][^r12].
* Remedy: Print the required dangerous goods label, correct gross weight discrepancies, or supply a cancellation reason [^r4][^r12]. See [[err-dlv-0320]] for detailed handling [^r4][^r12].
* Raised by: `dlv_post` [^r12] and [[man-sal-72|MAN-SAL-72]] screen processing [^r4].

### ERR-DLV-0801
* Message: DESPATCH CLOSED (<status>) [^r7]
* Cause: An attempt is made to cancel an already closed despatch, or PARCELS or WEIGHT KG are zero, negative, or exceed permissible range thresholds [^r5][^r7].
* Remedy: Verify that the despatch is not closed before requesting cancellation, or enter valid, positive parcel and weight values within permitted thresholds [^r5][^r7].
* Raised by: `dlv_cancel` [^r7] and [[man-sal-72|MAN-SAL-72]] screen processing [^r5].

## Versions and conflicts

* **ERR-DLV-0001**: In service definitions (`dlv_cancel`, `dlv_get`, `dlv_label`, `dlv_post`), the message is `DESPATCH NOT FOUND` when the delivery number does not exist [^r6][^r8][^r9][^r10]. [[man-sal-72|MAN-SAL-72]] (v7.2.3, 2025-01-15, p. 24) defines it as pick reference in PICK NO not found in active sales orders tables [^r1]. Kind: `contradiction`.
* **ERR-DLV-0007**: In `dlv_post`, the error message is `DESPATCH NOT IN DRAFT (<status>)` [^r11]. [[man-sal-72|MAN-SAL-72]] defines it as the pick list being printed but warehouse picking confirmation not posted [^r2]. Kind: `contradiction`.
* **ERR-DLV-0301**: In `dlv_save`, the error message is `PICK NOT CONFIRMED` [^r13]. [[man-sal-72|MAN-SAL-72]] defines it as a delivery being already posted, which prevents amendment, saving, or re-posting of closed records [^r3]. Kind: `contradiction`.
* **ERR-DLV-0320**: In `dlv_post`, the error is `LITHIUM BATTERY LABEL NOT PRINTED` [^r12]. [[man-sal-72|MAN-SAL-72]] defines it broadly to also include empty REASON fields on cancellation or gross weight tolerance violations [^r4]. Kind: `contradiction`.
* **ERR-DLV-0801**: In `dlv_cancel`, the message is `DESPATCH CLOSED (<status>)` [^r7]. [[man-sal-72|MAN-SAL-72]] defines it as PARCELS or WEIGHT KG being zero, negative, or exceeding thresholds [^r5]. Kind: `contradiction`.

## See also

* [[err-dlv-0320|ERR-DLV-0320 Lithium Battery Label Required]]
* [[services-sal-dlv|SAL dlv services]]
* [[man-sal-72|MAN-SAL-72 Ledgerline ERP 7.2 User Manual: Sales]]
* [[screen-sal-dlv-05|SAL-DLV-05 Despatch Entry]]
* [[sop-sal-001|SOP-SAL-001 Sales Order to Despatch]]
* [[errors-so|Errors SO (Sales Order)]]
* [[errors-po|ERR-PO Error Codes]]
* [[errors-rma|ERR-RMA Error Codes]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 24, Messages
[^r6]: 04_service_definitions/sales/dlv_cancel.yaml, errors
[^r10]: 04_service_definitions/sales/dlv_post.yaml, errors
[^r8]: 04_service_definitions/sales/dlv_get.yaml, errors
[^r9]: 04_service_definitions/sales/dlv_label.yaml, errors
[^r11]: 04_service_definitions/sales/dlv_post.yaml, errors
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 24, Messages
[^r13]: 04_service_definitions/sales/dlv_save.yaml, errors
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 24, Messages
[^r12]: 04_service_definitions/sales/dlv_post.yaml, errors
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 24, Messages
[^r7]: 04_service_definitions/sales/dlv_cancel.yaml, errors
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 24, Messages
