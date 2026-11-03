---
title: "SOP-SAL-001 Sales Order to Despatch"
type: "procedure"
slug: "sop-sal-001"
summary: "Standard operating procedure governing sales order entry, credit checks, picking, carrier booking, dangerous goods labelling, and despatch from Manchester and Leeds."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-SAL-001 Sales Order to Despatch v2.2.pdf", "03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "08_release_notes/RN-7.2.3-P5 Ledgerline Patch Notes.pdf", "11_training/QRC-07 Lithium battery labels.pdf", "12_integrations/Carrier API notes - Moorland Logistics.md", "10_meeting_notes/2022-02-10 Sales meeting.docx", "10_meeting_notes/2024-03-10 Sales meeting.md", "10_meeting_notes/2026-01-11 IT steering.docx", "10_meeting_notes/2026-04-18 Stores and logistics meeting.docx", "09_email_archive/2025/2025-04-17_Bike shop orders ahead of the spring range.eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | SOP-SAL-001 |
| Title | Sales Order to Despatch |
| Owner | [[user-imorgan|Isla Morgan]] |
| Approver | [[user-hweber|Henrik Weber]] |
| Version | 2.2 |
| Effective date | 2025-03-01 |
| Status | CURRENT |

SOP-SAL-001 governs the end-to-end sales fulfilment cycle from order entry through to warehouse despatch and commercial invoicing [^r1][^r5]. The procedure covers standard electric bicycles, framesets, and replacement parts supplied from both the Manchester factory and the Leeds distribution unit to retailer or commercial accounts [^r2][^r3]. As of 26 October 2026, version 2.2 remains current under the ownership of sales manager [[user-imorgan|Isla Morgan]] and approval of plant head [[user-hweber|Henrik Weber]] [^r1].

## Steps

### 1. Pre-requisites and order intake
Before creating a sales order, the customer account must be active in the debtor ledger with an approved credit limit assigned by Manchester credit control, and an official written purchase order specifying delivery address and requested date must be held [^r11]. For orders spanning multiple delivery dates across several weeks, staff must enter separate order lines using distinct dates in the REQ DT field on a single sales order rather than generating multiple sales orders [^r12]. Provisional delivery commitments must not be made to bike shops until incoming frames have passed inspection under [[sop-qua-001|SOP-QUA-001]] in Manchester and electrical drive sets are fully staged for final fitting [^r30].

### 2. Order entry and credit validation
Staff enter and confirm retailer orders on screen [[screen-sal-so-01|SAL-SO-01]] [^r6]. Confirming an order initiates an automated credit check; if the customer's balance or order value exceeds the credit threshold, Ledgerline halts the process with error [[err-crd-0207|ERR-CRD-0207]] [^r6][^r21]. The credit control team investigates accounts on hold and releases them once incoming bank remittances clear through the bank, enabling the sales desk to advance the order [^r4][^r24]. Sales representatives should be monitored using weekly credit reports to address overdue balances before transaction blocking occurs [^r22].

### 3. Stock verification and pick allocation
Complete bicycle frames and finished electric bikes are sourced from the Manchester plant, whereas boxed accessories and spare [[items-bat|battery]] packs may be allocated from the Leeds unit [^r2]. Because stock availability on sales inquiry screens does not instantly reflect factory works allocations, sales staff must confirm physical stock availability with the warehouse desk before committing to narrow delivery windows, keeping sales backlogs reconciled against physical finished stock [^r23][^r25]. Sales orders confirmed by 15:30 are scheduled for same-day picking and next working day delivery in the UK [^r7]. For split shipments, the despatch desk must refrain from printing consignment paperwork until the complete trade package is ready in the warehouse [^r29].

### 4. Packing and dangerous goods labelling
Despatch parcels containing traction battery packs require hazardous goods markings prior to posting the despatch transaction [^r8][^r16]. Staff must generate label PKG-LBL-UN from [[items-pkg|PKG-* items]], categorising consignments under UN3480 for standalone batteries or UN3481 for battery packs contained in or packed with bicycles [^r16]. Attempting to post a despatch transaction without printing the lithium battery label causes Ledgerline to halt with error [[err-dlv-0320|ERR-DLV-0320]] [^r8]. Following system patch updates, carrier labels automatically derive and print the dangerous-goods service code within the service banner directly from parts book master data without requiring manual code entry by packing staff [^r14][^r15]. Finished bicycle pallets at Manchester must be banded and labelled earlier in the afternoon to prevent loading lane blockages during carrier delays [^r28]. In Leeds, despatch personnel must verify printed delivery notes against vehicle manifests before lorries leave the yard to prevent pallets departing without required battery declarations [^r26][^r27].

### 5. Carrier booking and collection
Carrier bookings are registered on screen [[screen-sal-frt-12|SAL-FRT-12]] with contract carrier Moorland Logistics [^r9]. Moorland Logistics operates four primary service options: NXT (Next working day, UK), ECO (Economy, 2-3 days), DGX (Dangerous goods lithium batteries, UK and EU road), and PAL (Pallet) [^r17]. Consignments containing batteries must be booked under service DGX [^r9][^r16]. Carrier bookings completed after 15:30 are collected by Moorland Logistics on the following working day [^r18]. Staff must ensure address premises text does not exceed field lengths, as external carrier integration interfaces silently truncate oversized address lines [^r19].

### 6. Order cancellation and collection voiding
If an order must be cancelled using service `so_cancel` on screen [[screen-sal-so-01|SAL-SO-01]], staff must first verify with the despatch bay that items have not already been staged onto pallets or assembled, and any staged stock must immediately be returned to warehouse racking [^r13]. Because collection note cancellations do not synchronise remotely over the carrier API, warehouse personnel must immediately phone Moorland Logistics directly to cancel collection vehicles [^r20].

### 7. Documentation and billing
Signed carrier collection manifests must be paired with the office copy of the delivery note and retained chronologically by despatch sequence number in the despatch office [^r10]. Once carrier collection is confirmed, the accounts department generates final commercial sales invoices and posts the corresponding debtor ledger entries [^r5].

## Forms and screens
* [[screen-sal-so-01|SAL-SO-01 Sales Order]]: Order entry, order line scheduling, credit validation, and order cancellations [^r6][^r12][^r13].
* [[screen-sal-frt-12|SAL-FRT-12 Carrier Booking Quote]]: Carrier selection, transport rates, and booking consignments under services NXT, ECO, PAL, or DGX [^r9][^r17].
* Label PKG-LBL-UN: Mandatory dangerous-goods parcel label for UN3480 and UN3481 shipments [^r16].
* Carrier collection manifest and delivery note office copy: Paired physical documents retained in the despatch office [^r10].

## Versions and conflicts
* **Carrier dangerous-goods service code entry**: Under patch RN-7.2.3-P5 (effective 2026-10-19), Ledgerline automatically prints dangerous-goods carrier codes in the label service banner directly from parts book classifications without manual entry by warehouse packing operators [^r14][^r15]. This supersedes the earlier manual procedure in SOP-SAL-001 v2.2 (effective 2025-03-01), which instructed staff to manually select and input service codes on booking screens [^r9]. (`superseded`)

## See also
* [[screen-sal-so-01|SAL-SO-01 Sales Order]]
* [[screen-sal-frt-12|SAL-FRT-12 Carrier Booking Quote]]
* [[err-crd-0207|ERR-CRD-0207 Customer Credit Limit Exceeded]]
* [[err-dlv-0320|ERR-DLV-0320 Lithium Battery Label Required]]
* [[man-sal-72|MAN-SAL-72 Ledgerline ERP 7.2 User Manual: Sales and Despatch]]
* [[sop-qua-001|SOP-QUA-001 Incoming Inspection]]
* [[items-bat|BAT-* items]]
* [[items-pkg|PKG-* items]]

## References

[^r1]: 02_procedures/SOP-SAL-001 Sales Order to Despatch v2.2.pdf, p. 1, Sales Order to Despatch
[^r5]: 02_procedures/SOP-SAL-001 Sales Order to Despatch v2.2.pdf, p. 2, §3. Responsibilities
[^r2]: 02_procedures/SOP-SAL-001 Sales Order to Despatch v2.2.pdf, p. 1, §1. Purpose
[^r3]: 02_procedures/SOP-SAL-001 Sales Order to Despatch v2.2.pdf, p. 2, Scope
[^r11]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 7, Before you start
[^r12]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 10, Tips
[^r30]: 09_email_archive/2025/2025-04-17_Bike shop orders ahead of the spring range.eml, Bike shop orders ahead of the spring range
[^r6]: 02_procedures/SOP-SAL-001 Sales Order to Despatch v2.2.pdf, p. 3, §5. Procedure
[^r21]: 10_meeting_notes/2022-02-10 Sales meeting.docx, Retailer Accounts and Credit Holds
[^r4]: 02_procedures/SOP-SAL-001 Sales Order to Despatch v2.2.pdf, p. 2, §3. Responsibilities
[^r24]: 10_meeting_notes/2024-03-10 Sales meeting.md, Discussion
[^r22]: 10_meeting_notes/2022-02-10 Sales meeting.docx, Retailer Accounts and Credit Holds
[^r23]: 10_meeting_notes/2024-03-10 Sales meeting.md, Discussion
[^r25]: 10_meeting_notes/2024-03-10 Sales meeting.md, Discussion
[^r7]: 02_procedures/SOP-SAL-001 Sales Order to Despatch v2.2.pdf, p. 3, §5. Procedure
[^r29]: 09_email_archive/2025/2025-04-17_Bike shop orders ahead of the spring range.eml, Bike shop orders ahead of the spring range
[^r8]: 02_procedures/SOP-SAL-001 Sales Order to Despatch v2.2.pdf, p. 3, §5. Procedure
[^r16]: 11_training/QRC-07 Lithium battery labels.pdf, p. 1, Steps
[^r14]: 08_release_notes/RN-7.2.3-P5 Ledgerline Patch Notes.pdf, p. 2, Sales: Carrier labels print the dangerous-goods service code
[^r15]: 08_release_notes/RN-7.2.3-P5 Ledgerline Patch Notes.pdf, p. 2, Sales: Carrier labels print the dangerous-goods service code
[^r28]: 10_meeting_notes/2026-04-18 Stores and logistics meeting.docx, Discussion
[^r26]: 10_meeting_notes/2026-01-11 IT steering.docx, Leeds Distribution and Despatch Documentation
[^r27]: 10_meeting_notes/2026-01-11 IT steering.docx, Leeds Distribution and Despatch Documentation
[^r9]: 02_procedures/SOP-SAL-001 Sales Order to Despatch v2.2.pdf, p. 3, §5. Procedure
[^r17]: 12_integrations/Carrier API notes - Moorland Logistics.md, Services
[^r18]: 12_integrations/Carrier API notes - Moorland Logistics.md, Booking
[^r19]: 12_integrations/Carrier API notes - Moorland Logistics.md, Known problems
[^r13]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 10, Tips
[^r20]: 12_integrations/Carrier API notes - Moorland Logistics.md, Known problems
[^r10]: 02_procedures/SOP-SAL-001 Sales Order to Despatch v2.2.pdf, p. 4, §6. Records
