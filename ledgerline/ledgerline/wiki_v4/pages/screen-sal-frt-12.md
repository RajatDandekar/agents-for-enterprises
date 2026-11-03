---
title: "SAL-FRT-12 Carrier Booking Quote"
type: "screen"
slug: "screen-sal-frt-12"
summary: "Ledgerline screen for quoting, booking, tracking carrier freight, and printing dispatch labels under module Sales."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-SAL-001 Sales Order to Despatch v2.2.pdf", "03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/sales/frt_book.xml", "04_service_definitions/sales/frt_label.xml", "04_service_definitions/sales/frt_quote.xml", "04_service_definitions/sales/frt_track.xml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen | SAL-FRT-12 |
| Title | Carrier Booking Quote |
| Module | Sales |
| Path | Sales > Carrier booking |
| Roles | SAL-EXEC, SAL-MGR, SYS-ADMIN |
| Status | current |

Screen SAL-FRT-12 is the Ledgerline interface used to execute and manage carrier freight bookings, retrieve rate quotes, track consignments, and print dispatch labels [^r1][^r3][^r5]. Accessed via Sales > Carrier booking by roles SAL-EXEC, SAL-MGR, and SYS-ADMIN, it interfaces directly with external transport services [^r3][^r6]. Under [[sop-sal-001|SOP-SAL-001]], shipments containing battery packs must specify Moorland Logistics dangerous-goods service code DGX with complete parcel dimensions and descriptions to transfer successfully to the carrier system [^r1][^r2].

| Field | Detail |
|---|---|
| Screen code | SAL-FRT-12 [^r6] |
| Screen title | Carrier Booking Quote [^r6] |
| Navigation path | Sales > Carrier booking [^r3][^r6] |
| Module | Sales (SAL) [^r3][^r10] |
| Authorized roles | SAL-EXEC, SAL-MGR, SYS-ADMIN [^r6] |
| Services | frt_quote, frt_book, frt_track, frt_label [^r3][^r7] |

## Fields

Screen SAL-FRT-12 uses the following screen fields and mappings [^r4][^r6][^r11]:

* **DLV NO (`dlv_no`)**: Mandatory delivery reference identifier used to look up deliveries and request quotes [^r4][^r6][^r11]. Re-entering this field enables reprinting of existing dispatch labels [^r5].
* **CARRIER (`carrier_cd`)**: Mandatory carrier code identifier [^r4][^r6][^r11].
* **AWB NO (`awb_no`)**: Mandatory air waybill or carrier tracking number generated upon booking [^r4][^r6][^r9]. It must contain the generated tracking reference when reprinting dispatch labels [^r5].
* **SERVICE (`service_lvl`)**: Optional carrier service level code [^r4][^r6][^r11]. When booking Moorland Logistics shipments containing battery packs, service code DGX must be specified [^r1].

For Moorland Logistics bookings to accept code DGX and successfully transmit data to the carrier system, all parcel dimensions and descriptions must be populated [^r2].

## Keys and services

SAL-FRT-12 interfaces with [[services-sal-frt|SAL frt services]] providing the following functions and service calls [^r3][^r7]:

* **Quote (`frt_quote`)**: Executes a read service to retrieve rate quotes based on mandatory fields `dlv_no` and `carrier_cd`, alongside optional `service_lvl` [^r7][^r10][^r11].
* **Book (`frt_book`)**: Executes a write service to complete carrier booking operations [^r7][^r8].
* **Track (`frt_track`)**: Executes a read-kind tracking service to look up consignment status [^r7][^r12].
* **Label (`frt_label`)**: Executes a write service to generate or retrieve carrier booking dispatch labels using parameter `awb_no` [^r5][^r7][^r9]. Dispatch labels can be reprinted by re-entering the delivery reference into DLV NO, verifying that AWB NO contains the generated tracking reference, and clicking frt_label [^r5].

## Messages

The screen raises the following error codes [^r7]:

* `ERR-FRT-0001` [^r7]
* [[err-frt-0501|ERR-FRT-0501]] (Carrier interface failure) [^r7]
* `ERR-FRT-0510` [^r7]

## See also

* [[err-frt-0501|ERR-FRT-0501 Carrier interface failure]]
* [[screen-sal-dlv-05|SAL-DLV-05 Despatch Entry]]
* [[services-sal-dlv|SAL dlv services]]
* [[services-sal-frt|SAL frt services]]
* [[sop-sal-001|SOP-SAL-001 Sales Order to Despatch]]

## References

[^r1]: 02_procedures/SOP-SAL-001 Sales Order to Despatch v2.2.pdf, p. 3, §5. Procedure
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 48, §15. Carrier Booking (SAL-FRT-12)
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 51, Questions users ask
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 36, SAL-FRT-12 CARRIER BOOKING QUOTE
[^r2]: 02_procedures/SOP-SAL-001 Sales Order to Despatch v2.2.pdf, p. 4, §5. Procedure: notes and common mistakes
[^r10]: 04_service_definitions/sales/frt_quote.xml, wsdl:documentation
[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 36, SAL-FRT-12 CARRIER BOOKING QUOTE
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 48, §15. Carrier Booking (SAL-FRT-12)
[^r11]: 04_service_definitions/sales/frt_quote.xml, wsdl:types / frt_quoteRequest
[^r9]: 04_service_definitions/sales/frt_label.xml, wsdl:documentation
[^r8]: 04_service_definitions/sales/frt_book.xml, wsdl:documentation
[^r12]: 04_service_definitions/sales/frt_track.xml, wsdl:documentation
