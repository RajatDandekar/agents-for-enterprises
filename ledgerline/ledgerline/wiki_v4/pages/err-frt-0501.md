---
title: "ERR-FRT-0501 Carrier interface failure"
type: "error"
slug: "err-frt-0501"
summary: "Carrier interface failure error raised when Ledgerline cannot validate consignment routing or format label requests for a carrier."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-FRT-0501 |
| module | SAL |
| source_document | MAN-SAL-72 |
| status | current |

`ERR-FRT-0501` is a Ledgerline sales delivery error code that signals a failure in the external carrier interface connection.[^r1] The error prevents despatch label creation when the system cannot route a consignment or prepare payload data for the selected freight provider.[^r1] As of 26 October 2026, handling this error requires verifying network links, confirming customer carrier codes, or retrying label generation after collection traffic peaks pass.[^r2]

## Meaning
`ERR-FRT-0501` indicates a carrier interface failure where Ledgerline is unable to validate the consignment route or format the label request for the carrier specified in `CARRIER`.[^r1]

## Cause
The error occurs when the system cannot communicate with the carrier endpoint, cannot verify routing rules for the consignment, or fails while constructing the formatting structure of the label request.[^r1]

## How to fix
To resolve `ERR-FRT-0501`, perform the following actions:[^r2]
* Check the network link to the freight service.[^r2]
* Verify that the customer carrier code is operational.[^r2]
* Retry the `dlv_label` service after afternoon collection traffic peaks have subsided.[^r2]

## Raised by
* `dlv_label` service under [[services-sal-dlv|SAL dlv services]][^r2]
* [[screen-sal-dlv-05|SAL-DLV-05 Despatch Entry]] and [[man-sal-72|MAN-SAL-72]][^r1][^r2]

## See also
* [[screen-sal-dlv-05|SAL-DLV-05 Despatch Entry]]
* [[screen-sal-frt-12|SAL-FRT-12 Carrier Booking Quote]]
* [[services-sal-dlv|SAL dlv services]]
* [[services-sal-frt|SAL frt services]]
* [[sop-sal-001|SOP-SAL-001 Sales Order to Despatch]]
* [[man-sal-72|MAN-SAL-72 Ledgerline ERP 7.2 User Manual: Sales and]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 24, Messages
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 24, Messages
