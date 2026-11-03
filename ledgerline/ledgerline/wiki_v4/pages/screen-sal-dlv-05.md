---
title: "SAL-DLV-05 Despatch Entry"
type: "screen"
slug: "screen-sal-dlv-05"
summary: "Ledgerline screen for recording, posting, labelling, and cancelling customer despatches against confirmed pick lists under Sales Despatch."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/sales/dlv_cancel.yaml", "04_service_definitions/sales/dlv_get.yaml", "04_service_definitions/sales/dlv_label.yaml", "04_service_definitions/sales/dlv_post.yaml", "04_service_definitions/sales/dlv_save.yaml", "04_service_definitions/sales/dlv_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen Code | SAL-DLV-05 |
| Module | Sales |
| Navigation | Sales > Despatch |
| Services | dlv_save, dlv_get, dlv_search, dlv_post, dlv_cancel, dlv_label |
| Primary Key | dlv_no |
| Status | current |

Screen SAL-DLV-05 provides the Despatch Entry interface in Ledgerline located under menu Sales > Despatch [^r1]. It allows users to record consignments against confirmed pick notes, generate despatch labels, post stock relief, or cancel consignments with mandatory justification [^r1][^r2][^r3]. Before creating or posting a delivery note on this screen, physical picking and packing must be complete, the paper pick note must be signed, parcels must be weighed on packing bench scales, label printers verified, and pick confirmation posted [^r2].

| Field | Value |
|---|---|
| Screen Code | SAL-DLV-05 |
| Module | Sales |
| Menu Path | Sales > Despatch |
| Status | current |

## Fields

* **DLV NO (`dlv_no`)**: The delivery number, which is blank until saved and required for lookups and processing [^r3][^r8][^r16].
* **PICK NO (`pck_no`)**: The confirmed pick number against which the despatch entry is recorded [^r13][^r14][^r16].
* **CARRIER (`carrier_cd`)**: Carrier code assigned to the shipment [^r14][^r16]. If a carrier changes after posting, users cannot edit this field directly; a supervisor must cancel the consignment using `dlv_cancel` and recreate it [^r5].
* **PARCELS (`parcels`)**: The total parcel count for the consignment [^r14][^r16].
* **WEIGHT (`weight_kg`)**: Optional total weight in kilograms weighed on bench scales [^r2][^r14].
* **STATUS (`status`)**: Displays system processing states such as open, posted, or cancelled [^r3].
* **REASON (`reason`)**: Mandatory justification text required when cancelling a recorded delivery [^r3][^r5][^r16].

## Keys and services

* **Save (F8)**: Invokes write service `dlv_save` to create or save despatch entries against confirmed pick numbers [^r6][^r13][^r14].
* **Get (F3)**: Invokes read service `dlv_get` using `dlv_no` to retrieve despatch records [^r6][^r8].
* **Search (F2 / Enter)**: Invokes read service `dlv_search` to query the despatch list using optional filters for pick number, carrier, parcel count, and status [^r6][^r15].
* **Post (F9)**: Invokes write service `dlv_post` via stored procedure `sp_dlv_post`, running inventory reconciliation, relieving finished stock balances, writing delivery ledger entries, updating status to fully posted, and producing driver manifests and pick documentation [^r4][^r6][^r10].
* **Cancel (Shift+F8)**: Invokes write service `dlv_cancel` to perform delivery cancellations with a mandatory justification reason [^r1][^r3][^r6][^r7].
* **Label**: Invokes write service `dlv_label` via endpoint `POST /ll72/svc/dlv_label` to print despatch labels [^r6][^r9].

All underlying service endpoints and parameter structures are maintained under [[services-sal-dlv|SAL dlv services]].

## Messages

* `ERR-DLV-0007`: Returned during `dlv_post` if the despatch record is not in DRAFT status [^r11].
* `ERR-DLV-0301`: Returned during `dlv_save` if the referenced pick note is not confirmed [^r14].
* [[err-dlv-0320|ERR-DLV-0320]]: Returned during `dlv_post` if a required lithium battery label has not been printed [^r12].

Other error codes triggered by delivery routines are catalogued in [[errors-dlv|ERR-DLV Despatch Error Codes]].

## See also

* [[services-sal-dlv|SAL dlv services]]
* [[screen-sal-pck-04|SAL-PCK-04 Pick List Entry]]
* [[services-sal-pck|SAL pck services]]
* [[screen-sal-frt-12|SAL-FRT-12 Carrier Booking Quote]]
* [[services-sal-frt|SAL frt services]]
* [[screen-sal-inv-06|SAL-INV-06 Sales Invoice Entry]]
* [[err-dlv-0320|ERR-DLV-0320 Lithium Battery Label Required]]
* [[errors-dlv|ERR-DLV Despatch Error Codes]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 22, Despatch (SAL-DLV-05)
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 22, Before you start
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 22, Screen layout
[^r8]: 04_service_definitions/sales/dlv_get.yaml, screen
[^r16]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 34, SAL-DLV-05 DESPATCH ENTRY
[^r13]: 04_service_definitions/sales/dlv_save.yaml, service: dlv_save
[^r14]: 04_service_definitions/sales/dlv_save.yaml, request.fields
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 25, Questions users ask
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 34, SAL-DLV-05 DESPATCH ENTRY
[^r15]: 04_service_definitions/sales/dlv_search.yaml, service: dlv_search
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 23, Step by step
[^r10]: 04_service_definitions/sales/dlv_post.yaml, service: dlv_post
[^r7]: 04_service_definitions/sales/dlv_cancel.yaml, screen
[^r9]: 04_service_definitions/sales/dlv_label.yaml, service: dlv_label
[^r11]: 04_service_definitions/sales/dlv_post.yaml, errors
[^r12]: 04_service_definitions/sales/dlv_post.yaml, errors
