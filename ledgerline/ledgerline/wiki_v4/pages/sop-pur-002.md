---
title: "SOP-PUR-002 Purchase Request to Purchase Order"
type: "procedure"
slug: "sop-pur-002"
summary: "Standard operating procedure for raising purchase requests, converting them to purchase orders, and releasing orders to suppliers in Ledgerline ERP 7.2."
audience: "staff"
status: "mixed"
sources: ["02_procedures/SOP-PUR-002 PR to PO v1.3 (FINAL).pdf", "02_procedures/SOP-PUR-002 PR to PO v1.4.pdf", "11_training/QRC-01 Raising a purchase request.pdf", "11_training/QRC-06 Your approval inbox.pdf", "11_training/intranet_export_2016/how_to_raise_an_order.html", "11_training/intranet_export_2016/page_how_we_work_with_finance.html", "11_training/intranet_export_2016/page_ledgerline_tips_and_tricks.html", "11_training/intranet_export_2016/page_purchasing_team_news__spring_2016.html", "11_training/intranet_export_2016/page_suppliers_in_europe.html", "11_training/intranet_export_2016/supplier_list.html", "10_meeting_notes/2023-02-14 Ledgerline 7.2 upgrade steering.md", "10_meeting_notes/2025-12-12 Finance and purchasing catch-up.md", "09_email_archive/2024/2024-03-10_Month-end_ release your approved orders.eml", "09_email_archive/2026/2026-05-14_Voltway freight.eml", "09_email_archive/2026/2026-09-02_Approving orders for lithium-cell parts - CERT OK in the approval comment.eml", "06_transactions/PR_extract_2026.csv", "06_transactions/reports/Purchase Request Register Jan-Oct 2026 (printed).pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | SOP-PUR-002 |
| Title | Purchase Request to Purchase Order |
| Owner | Daniel Okafor |
| Approver | Henrik Weber |
| Effective date | 2025-02-01 |
| Version | 1.4 |
| Status | current |

SOP-PUR-002 defines the operational workflow for entering purchase requests, securing approvals, generating standard purchase orders, and releasing orders to vendors in Ledgerline ERP 7.2 [^r1][^r6][^r10]. It is owned by purchase manager [[user-dokafor|Daniel Okafor]] and approved by plant head [[user-hweber|Henrik Weber]], with version 1.4 in force from 2025-02-01 [^r1]. The procedure enforces mandatory Fetch actions, cost centre validation, correct VAT assignment, and safety certificate logging before commitments are dispatched to suppliers [^r2][^r4][^r8][^r13].

| Field | Value |
|---|---|
| Document Code | SOP-PUR-002 [^r1] |
| Version | 1.4 [^r1] |
| Effective Date | 2025-02-01 [^r1] |
| Owner | [[user-dokafor|Daniel Okafor]] (DOKAFOR) [^r1] |
| Approver | [[user-hweber|Henrik Weber]] (HWEBER) [^r1] |
| Status | Current [^r1] |

## Steps

### 1. Pre-requisite checks and verification
* Before entering a purchase request, staff must verify that the operational need is genuine and that the parts or services cannot be supplied from existing stock held at the Manchester plant or the Leeds unit [^r15].
* Pending purchase requisitions awaiting electronic approval inbox sign-off do not impede stock issues for parts already held in stores, but formal purchase orders cannot be created until approval sign-off is complete [^r42]. Prior to the Ledgerline 7.2 approval inbox, requisitions circulated on paper slips between departments [^r41].
* Buyers should review open requirements each morning and confirm delivery dates with suppliers before moving orders to firm status [^r32].
* Requesters must confirm that the vendor is active and approved on the system; creating a new supplier record must be cleared through accounts before entering requisitions [^r16]. Purchasing against unlisted vendors or using obsolete delivery points creates goods inward discrepancies and blocks purchase order matching [^r38].
* If a supplier account is suspended or marked for query, Ledgerline prevents generating formal paperwork until the accounts team lifts the hold [^r27]. Buyers must review aged creditor balance summaries issued by finance prior to ordering cycles to prevent placing orders with frame or battery suppliers on credit stop [^r44].

### 2. Raising a purchase request
* Purchase requests are logged on [[screen-pur-pr-01|PUR-PR-01]], generating an identifier formatted as `PR/YYYY/NNNNN` that tracks estimated values and cost centre allocations [^r3][^r39]. Requisition records utilise standard types including MRO, SRV, STD, and TRF, tracking statuses AP, CL, CN, DR, PA, and RJ [^r40].
* On [[screen-pur-pr-01|PUR-PR-01]], entering an item code and pressing F3 (Fetch) populates the unit, warehouse, default cost centre, and an estimated rate based on the last released order [^r3].
* Requesters must verify cost centres on [[screen-fin-cc-01|FIN-CC-01]] before saving, because Ledgerline does not issue a warning on the request screen if a default cost centre was closed by Finance [^r4].
* Pressing F8 saves the request in draft status DR [^r5].
* Pressing F9 submits the request; requisitions within the user's personal spending limit approve immediately (AP), while requests exceeding personal authority route automatically to the manager's approval queue (PA) [^r5][^r12].

### 3. Converting an approved request to a purchase order
* Purchase orders must be raised and approved prior to committing the business [^r22]. If an emergency order is required to maintain the assembly line, the order record must be generated before the close of business on the same day [^r26]. Staff must never place verbal purchase orders over the telephone without obtaining a system-generated order reference, as goods inwards turns away deliveries lacking a reference on carrier paperwork [^r21].
* Once a request reaches status AP, a purchase order is raised on [[screen-pur-po-01|PUR-PO-01]] with order type STD and the request identifier entered into Source PR [^r6].
* After entering the supplier code and item code on [[screen-pur-po-01|PUR-PO-01]], the user must press F3 (Fetch); omitting Fetch will cause saving to be refused with [[err-scr-0221|ERR-SCR-0221]] [^r7].
* Fetch defaults the line tax code to VAT20-UK, which must be manually edited to VAT20-RC for suppliers outside the United Kingdom to prevent save failure [[err-po-0412|ERR-PO-0412]] [^r8].
* All purchase orders for continental European vendors must be entered in Ledgerline ERP in pounds before commitment, with foreign exchange handled separately by finance [^r35].
* Purchasing staff must confirm carriage terms, carton quantities, and unit prices in pounds before transmitting orders to vendors [^r33]. Part descriptions, carriage terms, and agreed lead times must match the master vendor file [^r36].
* Order prices must match the latest agreed terms, including any carriage allowances [^r23]. Each line item must be entered with a clear description, required quantity, and agreed unit price; users must not leave prices blank or enter estimates without confirming quotes with suppliers [^r18].
* Users must never add a freight line or freight charge to any purchase order placed with [[sup-vc-ein-0042|Voltway Cells]], whose rates are delivered DAP Manchester [^r48].
* When ordering electric bicycle assembly components, users must ensure the unit of purchase matches the manufacturer pack size to prevent warehouse balance errors [^r29].
* Users must enter a fresh purchase order line rather than reusing closed or cancelled lines for replacement goods [^r30]. Free-text remarks on order lines appear on internal audit extracts and must state the operational rationale for any non-standard pricing or delivery arrangements [^r31].
* Delivery addresses must be verified at placement so frame deliveries or motor assemblies are routed to Manchester for assembly while service stock is delivered directly to Leeds [^r17][^r34][^r37]. Stock destined for Leeds must have Leeds set as the destination delivery site at the header stage, as redirecting lines after partial receipt causes discrepancies in stock reporting between sites [^r28].
* Delivery dates entered on orders must reflect realistic lead times agreed with suppliers rather than desired floor dates [^r19][^r24]. Carriage instructions such as oversized consignments or pallet drops must be noted in delivery remarks for goods inwards [^r20]. Any verbal amendments agreed with suppliers must be recorded immediately on the system [^r25].

### 4. Saving and approval
* Pressing F8 saves the purchase order on [[screen-pur-po-01|PUR-PO-01]] [^r9]. The message SAVED appears on the status bar regardless of whether the document status header is DR (held or closed cost centre with warning [[w-cc-114|W-CC-114]]), PA (awaiting approval), or AP (approved and ready for release) [^r9].
* If an order covers work spanning both Manchester and Leeds, approvers must confirm that charges are assigned to the correct operating unit [^r14].
* For purchase orders containing lithium-cell items ([[items-bat|BAT-*]], [[items-mtr|MTR-*]], [[items-chg|CHG-*]]), the approver must confirm active safety documentation is held on file and record `CERT OK` plus the certificate reference (e.g. `CERT OK UN38.3-TR/VC/2026/118`) in the comment field on [[screen-pur-poa-04|PUR-POA-04]], or approval cannot be completed [^r13][^r49].
* Upon placing requisitions or purchase orders requiring pro-forma advance deposits with overseas component suppliers, purchasing must provide pro-forma copies and receipts directly to the ledger clerk [^r43].

### 5. Order release and period-end housekeeping
* Approved purchase orders are released on [[screen-pur-por-05|PUR-POR-05]] using F9, and only orders reaching status RL have reached the supplier [^r10].
* The purchasing team batches purchase order releases during the working week rather than releasing on the same day purchase requests are raised [^r11].
* Requisitions that have received sign-off must be converted and released immediately ahead of month-end ledger close so commitments are recorded before period shut [^r45].
* Purchasing staff must review outstanding lists across both Manchester and Leeds to dispatch or release orders held in draft [^r46]. Approved orders that are no longer required must be cancelled cleanly rather than left parked on the system [^r47].

## Forms and screens

* [[screen-pur-pr-01|PUR-PR-01]]: Purchase request entry screen used to raise, fetch defaults for, and submit initial requisitions with F8 and F9 [^r3][^r5].
* [[screen-fin-cc-01|FIN-CC-01]]: Cost centre verification screen used to validate active accounting units prior to saving requisitions [^r4].
* [[screen-pur-po-01|PUR-PO-01]]: Standard purchase order entry screen used to create orders from approved requests, fetch supplier terms, assign tax codes, and save orders [^r6][^r7][^r8][^r9].
* [[screen-pur-poa-04|PUR-POA-04]]: Purchase order approval screen where operating unit splits are checked and lithium-cell safety certificate references are recorded [^r13][^r14][^r49].
* [[screen-pur-por-05|PUR-POR-05]]: Purchase order release screen where approved orders (AP) are transmitted with F9 to achieve released status (RL) [^r10].

## Versions and conflicts

Today's version 1.4 (effective 2025-02-01) mandates pressing F3 (Fetch) on [[screen-pur-po-01|PUR-PO-01]] after entering the supplier and item, without which saving is refused with [[err-scr-0221|ERR-SCR-0221]] [^r2][^r7]. In superseded version 1.3 (effective 2023-05-01), the Fetch step was described as auto-populating defaults but was not enforced as a mandatory check tied to [[err-scr-0221|ERR-SCR-0221]] [^r2][^r54].

## See also

* [[data-pr-extract-2026|PR_extract_2026]]
* [[decision-2023-02-14-ledgerline-7-2-upgrade|Ledgerline 7.2 Upgrade Steering Decisions (2023-02-14)]]
* [[decision-2025-12-12-finance-purchasing-catchup|Finance and purchasing catch-up decisions (12 December 2025)]]
* [[decision-2026-09-02-lithium-cell-po-approval-comment|Decision 2026-09-02 Lithium-cell PO approval comment requirement]]
* [[err-po-0412|ERR-PO-0412 TAX CODE DOES NOT MATCH SUPPLIER COUNTRY]]
* [[err-scr-0221|ERR-SCR-0221 FETCH NOT DONE]]
* [[items-bat|BAT-* items]]
* [[qrc-01|QRC-01 Raising a purchase request]]
* [[screen-fin-cc-01|FIN-CC-01 Cost Centre Entry]]
* [[screen-pur-po-01|PUR-PO-01 Purchase Order Entry]]
* [[screen-pur-poa-04|PUR-POA-04 Purchase Order Approval]]
* [[screen-pur-por-05|PUR-POR-05 Purchase Order Release]]
* [[screen-pur-pr-01|PUR-PR-01 Purchase Request Entry]]
* [[sup-vc-ein-0042|Voltway Cells (VC-EIN-0042)]]
* [[topic-un-38-3-certificates|UN 38.3 Certificates]]
* [[w-cc-114|W-CC-114]]

## References

[^r1]: 02_procedures/SOP-PUR-002 PR to PO v1.4.pdf, p. 1, Field / Value
[^r6]: 02_procedures/SOP-PUR-002 PR to PO v1.4.pdf, p. 3, §5. Procedure
[^r10]: 02_procedures/SOP-PUR-002 PR to PO v1.4.pdf, p. 3, §5. Procedure
[^r2]: 02_procedures/SOP-PUR-002 PR to PO v1.4.pdf, p. 1, Version history
[^r4]: 02_procedures/SOP-PUR-002 PR to PO v1.4.pdf, p. 3, §5. Procedure
[^r8]: 02_procedures/SOP-PUR-002 PR to PO v1.4.pdf, p. 3, §5. Procedure
[^r13]: 11_training/QRC-06 Your approval inbox.pdf, p. 1, Lithium-cell items
[^r15]: 11_training/intranet_export_2016/how_to_raise_an_order.html, How to raise an order
[^r42]: 10_meeting_notes/2023-02-14 Ledgerline 7.2 upgrade steering.md, Approval inbox workflow and authority limits
[^r41]: 10_meeting_notes/2023-02-14 Ledgerline 7.2 upgrade steering.md, Approval inbox workflow and authority limits
[^r32]: 11_training/intranet_export_2016/page_purchasing_team_news__spring_2016.html, Production demand and parts supply
[^r16]: 11_training/intranet_export_2016/how_to_raise_an_order.html, How to raise an order
[^r38]: 11_training/intranet_export_2016/supplier_list.html, Supplier list
[^r27]: 11_training/intranet_export_2016/page_ledgerline_tips_and_tricks.html, Purchase order entry and maintenance
[^r44]: 10_meeting_notes/2025-12-12 Finance and purchasing catch-up.md, Discussion
[^r3]: 02_procedures/SOP-PUR-002 PR to PO v1.4.pdf, p. 3, §5. Procedure
[^r39]: 06_transactions/reports/Purchase Request Register Jan-Oct 2026 (printed).pdf, p. 1
[^r40]: 06_transactions/PR_extract_2026.csv, sheet csv, SHEET csv
[^r5]: 02_procedures/SOP-PUR-002 PR to PO v1.4.pdf, p. 3, §5. Procedure
[^r12]: 11_training/QRC-01 Raising a purchase request.pdf, p. 1, Saving and submission
[^r22]: 11_training/intranet_export_2016/page_how_we_work_with_finance.html, Orders and commitments
[^r26]: 11_training/intranet_export_2016/page_how_we_work_with_finance.html, Orders and commitments
[^r21]: 11_training/intranet_export_2016/how_to_raise_an_order.html, How to raise an order
[^r7]: 02_procedures/SOP-PUR-002 PR to PO v1.4.pdf, p. 3, §5. Procedure
[^r35]: 11_training/intranet_export_2016/page_suppliers_in_europe.html, Ordering and Currency
[^r33]: 11_training/intranet_export_2016/page_purchasing_team_news__spring_2016.html, Order administration and receipts
[^r36]: 11_training/intranet_export_2016/page_suppliers_in_europe.html, Ordering and Currency
[^r23]: 11_training/intranet_export_2016/page_how_we_work_with_finance.html, Orders and commitments
[^r18]: 11_training/intranet_export_2016/how_to_raise_an_order.html, How to raise an order
[^r48]: 09_email_archive/2026/2026-05-14_Voltway freight.eml, body
[^r29]: 11_training/intranet_export_2016/page_ledgerline_tips_and_tricks.html, Purchase order entry and maintenance
[^r30]: 11_training/intranet_export_2016/page_ledgerline_tips_and_tricks.html, Purchase order entry and maintenance
[^r31]: 11_training/intranet_export_2016/page_ledgerline_tips_and_tricks.html, System performance and day-to-day use
[^r17]: 11_training/intranet_export_2016/how_to_raise_an_order.html, How to raise an order
[^r34]: 11_training/intranet_export_2016/page_purchasing_team_news__spring_2016.html, Order administration and receipts
[^r37]: 11_training/intranet_export_2016/supplier_list.html, Supplier list
[^r28]: 11_training/intranet_export_2016/page_ledgerline_tips_and_tricks.html, Purchase order entry and maintenance
[^r19]: 11_training/intranet_export_2016/how_to_raise_an_order.html, How to raise an order
[^r24]: 11_training/intranet_export_2016/page_how_we_work_with_finance.html, Orders and commitments
[^r20]: 11_training/intranet_export_2016/how_to_raise_an_order.html, How to raise an order
[^r25]: 11_training/intranet_export_2016/page_how_we_work_with_finance.html, Orders and commitments
[^r9]: 02_procedures/SOP-PUR-002 PR to PO v1.4.pdf, p. 3, §5. Procedure
[^r14]: 11_training/QRC-06 Your approval inbox.pdf, p. 1, Processing daily entries
[^r49]: 09_email_archive/2026/2026-09-02_Approving orders for lithium-cell parts - CERT OK in the approval comment.eml, body
[^r43]: 10_meeting_notes/2025-12-12 Finance and purchasing catch-up.md, Discussion
[^r11]: 11_training/QRC-01 Raising a purchase request.pdf, p. 1, Quantities and dates
[^r45]: 09_email_archive/2024/2024-03-10_Month-end_ release your approved orders.eml, body
[^r46]: 09_email_archive/2024/2024-03-10_Month-end_ release your approved orders.eml, body
[^r47]: 09_email_archive/2024/2024-03-10_Month-end_ release your approved orders.eml, body
[^r54]: 02_procedures/SOP-PUR-002 PR to PO v1.3 (FINAL).pdf, p. 3, §5. Procedure
