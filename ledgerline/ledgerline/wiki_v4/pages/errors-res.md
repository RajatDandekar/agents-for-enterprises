---
title: "ERR-RES Stock Reservation Error Codes"
type: "error-list"
slug: "errors-res"
summary: "Reference catalogue of stock reservation error codes (ERR-RES) raised by Ledgerline inventory reservation services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/inventory/res_cancel.yaml", "04_service_definitions/inventory/res_get.yaml", "04_service_definitions/inventory/res_save.yaml", "04_service_definitions/inventory/res_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-RES |
| Domain | Inventory / Stock Reservation |
| Service group | services-inv-res |
| Status | current |

The ERR-RES error code list catalogues system errors produced by Ledgerline stock reservation services as of 26 October 2026. These validation and state codes are returned during reservation lookups, modifications, and cancellations across inventory operations. Each entry identifies the standard message text and the inventory services that trigger the condition.

### ERR-RES-0001
* **Message**: STOCK RESERVATION NOT FOUND [^r1][^r3]
* **Cause**: The requested stock reservation identifier does not exist in the system [^r1][^r3].
* **Remedy**: Verify the reservation identifier before retrying the transaction [^r1][^r3].
* **Raised by**: Raised by `res_cancel` and `res_get` [^r1][^r3]. Link: [[err-res-0001|ERR-RES-0001]].

### ERR-RES-0201
* **Message**: QTY MUST BE > 0 [^r4][^r5]
* **Cause**: The reservation quantity specified in the transaction request is not greater than zero [^r4][^r5].
* **Remedy**: Enter a positive quantity value greater than zero [^r4][^r5].
* **Raised by**: Raised by `res_save` and `res_search` [^r4][^r5]. Link: [[err-res-0201|ERR-RES-0201]].

### ERR-RES-0801
* **Message**: STOCK RESERVATION CLOSED (<status>) [^r2]
* **Cause**: A cancellation was attempted on a stock reservation that has already reached a closed status [^r2].
* **Remedy**: Check the current status of the reservation; closed reservations cannot be cancelled [^r2].
* **Raised by**: Raised by `res_cancel` [^r2]. Link: [[err-res-0801|ERR-RES-0801]].

## See also
* [[services-inv-res|INV res services]]
* [[screen-inv-res-12|INV-RES-12 Stock Reservation Entry]]
* [[err-res-0001|ERR-RES-0001 General reservation validation failure]]
* [[err-res-0201|ERR-RES-0201 Insufficient unreserved stock available]]
* [[err-res-0801|ERR-RES-0801 Cancellation rejected]]
* [[errors-itm|ERR-ITM error codes]]

## References

[^r1]: 04_service_definitions/inventory/res_cancel.yaml, errors
[^r3]: 04_service_definitions/inventory/res_get.yaml, errors
[^r4]: 04_service_definitions/inventory/res_save.yaml, errors
[^r5]: 04_service_definitions/inventory/res_search.yaml, errors
[^r2]: 04_service_definitions/inventory/res_cancel.yaml, errors
