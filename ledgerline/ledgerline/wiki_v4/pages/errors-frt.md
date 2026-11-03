---
title: "ERR-FRT Freight and Carrier Error Codes"
type: "error-list"
slug: "errors-frt"
summary: "Error codes under the ERR-FRT prefix returned by freight and carrier booking services, including carrier booking failures and dangerous goods rejections."
audience: "staff"
status: "current"
sources: ["04_service_definitions/sales/dlv_post.yaml", "04_service_definitions/sales/frt_book.xml", "04_service_definitions/sales/frt_label.xml", "04_service_definitions/sales/frt_track.xml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-FRT |
| Domain | Freight and Carrier Integration |
| Module | Sales (SAL) |
| Status | current |

Freight error codes under the `ERR-FRT` prefix are raised during carrier booking, label generation, tracking, and despatch posting operations. These codes report integration faults with third-party carriers as well as shipment validation rejections such as dangerous goods compliance issues. Detailed handling for carrier interface failures is documented on [[err-frt-0501|ERR-FRT-0501]].

### ERR-FRT-0001

* **Message**: `CARRIER BOOKING NOT FOUND` [^r2]
* **Cause**: The carrier booking reference specified in the request does not exist or cannot be located [^r2].
* **Remedy**: Verify the booking reference ID and ensure the carrier booking step was completed prior to requesting labels or tracking status.
* **Raised by**: [[services-sal-frt|frt_book]] [^r2], `frt_label` [^r5], and `frt_track` [^r6].

### ERR-FRT-0501

* **Message**: `CARRIER BOOKING FAILED` [^r1][^r3]
* **Cause**: The external carrier system rejected the booking request or the interface call failed [^r1][^r3].
* **Remedy**: Inspect the carrier interface response, validate shipment details, and retry; see [[err-frt-0501]] for detailed recovery steps.
* **Raised by**: [[services-sal-dlv|dlv_post]] [^r1] and `frt_book` [^r3].

### ERR-FRT-0510

* **Message**: `DANGEROUS GOODS NOT ACCEPTED FOR SERVICE` [^r4]
* **Cause**: The booking request includes dangerous goods items that are not permitted under the selected carrier service level [^r4].
* **Remedy**: Select a carrier service tier certified to transport dangerous goods or reassign the consignment items.
* **Raised by**: `frt_book` [^r4].

## See also

* [[err-frt-0501|ERR-FRT-0501 Carrier interface failure]]
* [[errors-dlv|ERR-DLV Despatch Error Codes]]
* [[services-sal-frt|SAL frt services]]
* [[services-sal-dlv|SAL dlv services]]
* [[screen-sal-frt-12|SAL-FRT-12 Carrier Booking Quote]]
* [[screen-sal-dlv-05|SAL-DLV-05 Despatch Entry]]

## References

[^r2]: 04_service_definitions/sales/frt_book.xml, ll:errors
[^r5]: 04_service_definitions/sales/frt_label.xml, ll:errors
[^r6]: 04_service_definitions/sales/frt_track.xml, ll:errors
[^r1]: 04_service_definitions/sales/dlv_post.yaml, errors
[^r3]: 04_service_definitions/sales/frt_book.xml, ll:errors
[^r4]: 04_service_definitions/sales/frt_book.xml, ll:errors
