---
title: "SAL frt services"
type: "service-group"
slug: "services-sal-frt"
summary: "Ledgerline SAL carrier booking SOAP gateway services connecting dispatch operations to external freight carriers via screen SAL-FRT-12."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/sales/frt_book.xml", "04_service_definitions/sales/frt_label.xml", "04_service_definitions/sales/frt_quote.xml", "04_service_definitions/sales/frt_track.xml", "12_integrations/Carrier API notes - Moorland Logistics.md", "12_integrations/wsdl/LedgerlineGateway.wsdl"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | SAL |
| Screen | SAL-FRT-12 |
| Object | frt (Carrier Freight Booking) |
| Endpoint | http://ll72-app01:8091/ws/sal/ |
| Namespace | urn:ledgerline:svc:sal |
| Gateway Port | 8091 |
| Maintainer | Joanna Fletcher (JFLETCHER) |
| Status | Current |

The SAL freight booking service group provides SOAP gateway interfaces between Ledgerline and external carrier systems, such as Moorland Logistics, for quoting, booking, tracking, and label generation [^r28]. The services are invoked from screen [[screen-sal-frt-12|SAL-FRT-12]] and run via a Ledgerline 6.2 compatibility listener hosted on port 8091 [^r6][^r12]. Service ownership sits within IT under [[user-jfletcher|Joanna Fletcher (JFLETCHER)]], having been transferred after the departure of [[user-dramsden|Derek Ramsden (DRAMSDEN)]] in 2012 [^r27][^r35].

## Services

### frt_quote
* **Description**: Read service that queries external carrier interfaces based on package dimensions and gross weight to return eligible carrier accounts, service levels, and estimated transport charges [^r2][^r7][^r20].
* **Screen**: [[screen-sal-frt-12|SAL-FRT-12]] [^r6][^r7].
* **Endpoint**: `http://ll72-app01:8091/ws/sal/frt_quote` under namespace `urn:ledgerline:svc:sal` [^r22].
* **Operation type**: Read [^r7][^r20].
* **Required fields**: `dlv_no`, `carrier_cd` [^r7][^r34].
* **Optional fields**: `service_lvl` [^r7][^r34].
* **Response elements**: `rc`, message `msg`, optional error code `err_cd`, and optional `data` [^r21].
* **Errors**: None documented in service definition [^r21].
* **Source file**: `04_service_definitions/sales/frt_quote.xml` [^r20][^r22].

### frt_book
* **Description**: Write service executing stored procedure `sp_frt_book` to transmit outbound consignment manifests to the carrier interface, returning a tracking reference to populate AWB NO and locking delivery carrier fields [^r3][^r8][^r11]. Freight bookings transmitted after 15:30 are scheduled for carrier collection on the next working day [^r29].
* **Screen**: [[screen-sal-frt-12|SAL-FRT-12]] [^r6][^r8].
* **Endpoint**: `http://ll72-app01:8091/ws/sal/frt_book` under namespace `urn:ledgerline:svc:sal` [^r11].
* **Operation type**: Write [^r8][^r11].
* **Required fields**: `dlv_no`, `carrier_cd` [^r8][^r13].
* **Optional fields**: `service_lvl` [^r13].
* **Response elements**: `rc`, optional `err_cd`, `msg`, and optional `data` [^r14].
* **Errors**: ERR-FRT-0001, [[err-frt-0501|ERR-FRT-0501]] (CARRIER BOOKING FAILED), ERR-FRT-0510 (DANGEROUS GOODS NOT ACCEPTED FOR SERVICE) [^r1][^r8].
* **Source file**: `04_service_definitions/sales/frt_book.xml` [^r11][^r13].

### frt_track
* **Description**: Read service triggering CARRIER BOOKING TRACK to query and display the latest transit event and carrier collection status [^r5][^r9][^r23].
* **Screen**: [[screen-sal-frt-12|SAL-FRT-12]] [^r6][^r9].
* **Endpoint**: `http://ll72-app01:8091/ws/sal/frt_track` under namespace `urn:ledgerline:svc:sal` [^r23].
* **Operation type**: Read [^r9][^r23].
* **Required fields**: `awb_no` [^r9][^r24].
* **Optional fields**: None [^r24].
* **Response elements**: `rc`, optional `err_cd`, `msg`, and optional `data` [^r25].
* **Errors**: ERR-FRT-0001 [^r9].
* **Source file**: `04_service_definitions/sales/frt_track.xml` [^r23][^r24].

### frt_label
* **Description**: Write service calling `sp_frt_label` to stream raw carrier barcoded shipping labels directly to the thermal printer assigned to the packing terminal [^r4][^r10][^r15].
* **Screen**: [[screen-sal-frt-12|SAL-FRT-12]] [^r6][^r10].
* **Endpoint**: `http://ll72-app01:8091/ws/sal/frt_label` under namespace `urn:ledgerline:svc:sal` [^r16].
* **Operation type**: Write [^r10][^r15].
* **Required fields**: `awb_no` [^r10][^r17].
* **Optional fields**: None [^r17].
* **Response elements**: `rc`, optional `err_cd`, `msg`, and optional `data` [^r18].
* **Errors**: ERR-FRT-0001 (CARRIER BOOKING NOT FOUND) [^r10][^r19].
* **Source file**: `04_service_definitions/sales/frt_label.xml` [^r15][^r19].

## Integration notes
All four carrier booking operations are declared in `GatewayPort` within the Ledgerline SOAP gateway [^r33]. Several operational failure modes affect the gateway integration:
* Connection drops occurring after remote record acceptance mark local consignments as failed, causing resubmitted bookings to generate duplicate requests and double charges on transport invoices [^r30].
* Payload formatting mismatches returned from `frt_label` stall the legacy print spooler, resulting in endless blank labels or garbled text across sheets [^r31].
* Consignments voided internally do not synchronise cancellations back through the SOAP gateway, requiring telephone notification to cancel carrier collection vans [^r32].

## See also
* [[screen-sal-frt-12|SAL-FRT-12 Carrier Booking Quote]]
* [[err-frt-0501|ERR-FRT-0501 Carrier interface failure]]
* [[services-sal-dlv|SAL dlv services]]
* [[services-sal-pck|SAL pck services]]
* [[user-jfletcher|Joanna Fletcher (JFLETCHER)]]

## References

[^r28]: 12_integrations/Carrier API notes - Moorland Logistics.md, Booking
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 36, SAL-FRT-12 CARRIER BOOKING QUOTE
[^r12]: 04_service_definitions/sales/frt_book.xml, wsdl:definitions
[^r27]: 04_service_definitions/sales/frt_track.xml, Header comment
[^r35]: 04_service_definitions/sales/frt_quote.xml, comment
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 49, Step by step
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 49, frt_quote CARRIER BOOKING QUOTE
[^r20]: 04_service_definitions/sales/frt_quote.xml, wsdl:documentation
[^r22]: 04_service_definitions/sales/frt_quote.xml, wsdl:service / frt_quoteService
[^r34]: 04_service_definitions/sales/frt_quote.xml, wsdl:types / frt_quoteRequest
[^r21]: 04_service_definitions/sales/frt_quote.xml, wsdl:types / frt_quoteResponse
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 49, Step by step
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 49, frt_book CARRIER BOOKING BOOK
[^r11]: 04_service_definitions/sales/frt_book.xml, wsdl:definitions
[^r29]: 12_integrations/Carrier API notes - Moorland Logistics.md, Booking
[^r13]: 04_service_definitions/sales/frt_book.xml, wsdl:types
[^r14]: 04_service_definitions/sales/frt_book.xml, wsdl:types
[^r1]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 10
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 49, Step by step
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 49, frt_track CARRIER BOOKING TRACK
[^r23]: 04_service_definitions/sales/frt_track.xml, wsdl:documentation
[^r24]: 04_service_definitions/sales/frt_track.xml, wsdl:types / frt_trackRequest
[^r25]: 04_service_definitions/sales/frt_track.xml, wsdl:types / frt_trackResponse
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 49, Step by step
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 49, frt_label CARRIER BOOKING LABEL
[^r15]: 04_service_definitions/sales/frt_label.xml, wsdl:documentation
[^r16]: 04_service_definitions/sales/frt_label.xml, header comment
[^r17]: 04_service_definitions/sales/frt_label.xml, frt_labelRequest
[^r18]: 04_service_definitions/sales/frt_label.xml, frt_labelResponse
[^r19]: 04_service_definitions/sales/frt_label.xml, ll:errors
[^r33]: 12_integrations/wsdl/LedgerlineGateway.wsdl, GatewayPort
[^r30]: 12_integrations/Carrier API notes - Moorland Logistics.md, Known problems
[^r31]: 12_integrations/Carrier API notes - Moorland Logistics.md, Known problems
[^r32]: 12_integrations/Carrier API notes - Moorland Logistics.md, Known problems
