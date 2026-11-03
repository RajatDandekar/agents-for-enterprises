---
title: "IT Steering Meeting Notes - 2026-01-11"
type: "decision"
slug: "decision-2026-01-11-it-steering"
summary: "Operational decisions and action items from the IT steering meeting on 11 January 2026 covering assembly, despatch, goods inward, and system routines."
audience: "staff"
status: "current"
sources: ["10_meeting_notes/2026-01-11 IT steering.docx"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | DEC-2026-01-11-IT |
| Date | 2026-01-11 |
| Chair / Attendees | Bronwen Price, Callum Shaw, Emma Clarke, Marta Kowalski |
| Status | current |
| Topics | Production scheduling, Leeds despatch, unreceipted drive units, warranty stock, overnight maintenance |

The IT steering meeting held on 11 January 2026 addressed operational bottlenecks across Manchester assembly, Leeds distribution, goods inward, spares fulfillment, and nightly system jobs [^r1][^r2][^r5][^r8][^r10][^r12]. Key operational directives established include maintaining unreceipted drive units strictly within the quarantine holding pen until paperwork arrives, enforcing pre-despatch manifest checks for battery consignments, and preparing data archival schedules [^r7][^r9][^r13]. As of 26 October 2026, these recorded decisions govern cross-functional procedural actions between Ledgerline modules and warehouse operations [^r4][^r7][^r9][^r11][^r13].

## Meeting details

The meeting took place on 2026-01-11 and was attended by [[user-bprice|Bronwen Price]], Callum Shaw, Emma Clarke, and Marta Kowalski [^r1].

## Operational decisions and actions

### Manchester assembly scheduling
Delays in the daily works order generation for Manchester assembly lines hold up frame pre-assembly teams and create idle time at shift start [^r2]. Manchester staff rely on an offline spreadsheet to balance motor allocations before committing builds, causing discrepancies between physical bin stock and booked quantities in Ledgerline [^r3]. David was tasked with reviewing morning batch posting sequencing with Manchester supervisors to minimise system locking, and with arranging the removal of the offline scheduling sheet once records align [^r4].

### Leeds despatch and transport documentation
Despatch notes generated for Leeds pallet carriers print without required hazardous goods declarations for electric bicycle battery packs, forcing the Leeds warehouse team to type paper dockets manually [^r5]. In addition, independent bike shops received deliveries where carton labels failed to correspond with advice notes produced by the sales ledger module [^r6]. Karen was assigned to provide example delivery notes displaying missing battery transport text and to ensure Leeds despatch staff reconcile printed notes against lorry manifests before carrier departure [^r7].

### Goods inward holding and motor deliveries
Shipments of drive units and electronic control harnesses arrive at goods inward ahead of shipping paperwork, leaving pallet loads sitting unbooked in the holding area [^r8]. Stores personnel must keep unreceipted drive units in the quarantine pen until shipping paperwork arrives, maintaining strict financial matching controls [^r9].

### Warranty parts and spares allocations
When retailers request replacement wiring looms or display units, the sales order screen does not clearly indicate whether an item is allocated to assembly or free warranty stock, leading to unfulfillable orders [^r10]. Nicola was tasked with drafting a standard procedure for checking free stock levels prior to confirming telephone orders and compiling a list of fast-moving warranty components for segregated stock locations [^r11].

### Nightly housekeeping routines
Nightly file re-indexing and data backup routines overrun into early shift logins due to historical sales order lines and closed assembly postings dating back many years [^r12]. Colin was assigned to draft an archive timetable for a scheduled maintenance weekend to restore terminal network query speeds and monitor overnight backup completion times [^r13].

## See also

* [[sop-qua-001|SOP-QUA-001 Incoming Inspection]]
* [[sop-sal-001|SOP-SAL-001 Sales Order to Despatch]]
* [[sop-sal-002|SOP-SAL-002 Warranty Claims from Bike Shops]]
* [[user-bprice|Bronwen Price]]

## References

[^r1]: 10_meeting_notes/2026-01-11 IT steering.docx, IT steering
[^r2]: 10_meeting_notes/2026-01-11 IT steering.docx, Production Scheduling and Manchester Assembly
[^r5]: 10_meeting_notes/2026-01-11 IT steering.docx, Leeds Distribution and Despatch Documentation
[^r8]: 10_meeting_notes/2026-01-11 IT steering.docx, Purchasing, Parts Lead Times, and Motor Deliveries
[^r10]: 10_meeting_notes/2026-01-11 IT steering.docx, Spares, Warranty, and Retailer Orders
[^r12]: 10_meeting_notes/2026-01-11 IT steering.docx, System Housekeeping and Nightly Routines
[^r7]: 10_meeting_notes/2026-01-11 IT steering.docx, Leeds Distribution and Despatch Documentation
[^r9]: 10_meeting_notes/2026-01-11 IT steering.docx, Purchasing, Parts Lead Times, and Motor Deliveries
[^r13]: 10_meeting_notes/2026-01-11 IT steering.docx, System Housekeeping and Nightly Routines
[^r4]: 10_meeting_notes/2026-01-11 IT steering.docx, Production Scheduling and Manchester Assembly
[^r11]: 10_meeting_notes/2026-01-11 IT steering.docx, Spares, Warranty, and Retailer Orders
[^r3]: 10_meeting_notes/2026-01-11 IT steering.docx, Production Scheduling and Manchester Assembly
[^r6]: 10_meeting_notes/2026-01-11 IT steering.docx, Leeds Distribution and Despatch Documentation
