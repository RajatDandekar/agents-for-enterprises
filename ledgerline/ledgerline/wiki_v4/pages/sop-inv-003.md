---
title: "SOP-INV-003 Stock Count (cycle and annual)"
type: "procedure"
slug: "sop-inv-003"
summary: "Standard operating procedure governing regular cycle counts and the full annual physical inventory count across Manchester and Leeds stores."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-INV-003 Stock Count v1.2.pdf", "08_release_notes/RN-7.2.2 Ledgerline Release Notes.pdf", "11_training/intranet_export_2016/page_year_end_stock_count__2016.html", "10_meeting_notes/2022-10-16 Weekly purchasing meeting.docx", "10_meeting_notes/2024-10-01 Stores and logistics meeting.md", "10_meeting_notes/2026-04-18 Stores and logistics meeting.docx", "09_email_archive/2026/2026-01-21_Cycle count this Friday.eml", "99_scans/2023_stock_count_sheet_MAN_aisle_B.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | SOP-INV-003 |
| owner | [[user-cshaw|Callum Shaw]] |
| approver | [[user-gwhitaker|Grace Whitaker]] |
| effective | 2023-03-01 |
| status | current |

SOP-INV-003 governs regular cycle inventory checks and the full annual stock count across Northbridge Cycles' facilities [^r2]. It covers all physical stock across the Manchester plant and the Leeds unit, including raw materials, frame assemblies, electrical sub-units, finished electric bicycles, and maintenance spares [^r2]. As of 26 October 2026, the procedure remains under the ownership of Stores Manager [[user-cshaw|Callum Shaw]] and approval of Financial Controller [[user-gwhitaker|Grace Whitaker]] [^r1].

## Steps

### Cycle counting schedule and planning
Overall control of the count schedule sits with the finance team, who generate tally sheets from the system and set timetables [^r3]. Regular cycle counts follow cycle count plan [[screen-inv-ccp-14|INV-CCP-14]], which schedules category A items monthly, B items quarterly, and C items twice per year [^r7]. In addition, dispatch packaging materials such as cardboard cartons and packing foam must be included on the weekly perpetual inventory count rota rather than estimated visually [^r34][^r35].

### Pre-count preparation and stock cut-off
Before counting commences, the target storage area must be frozen in Ledgerline on [[screen-inv-cnt-06|INV-CNT-06]] [^r8]. Ledgerline prevents freezing if any open transactions exist in the area and raises [[err-cnt-0230|ERR-CNT-0230]] [^r8]. Stores supervisors must ensure that all transfer tickets between the Manchester warehouse and sub-assembly lines are entered before the end of each shift [^r33]. Prior to cycle counting, all goods inwards movements from earlier in the week must be fully cleared and booked in [^r36]. Components waiting on inspection benches or returned from assembly lines must be placed in assigned locations or marked clearly as held stock to prevent double counting [^r37]. 

For the annual stocktaking exercise, which occurs on the last Saturday of March when Ledgerline is closed to all stores transactions, extensive cut-off arrangements apply across both sites [^r10][^r16]. Purchasing staff must instruct regular suppliers of frames, drive units, battery assemblies, wheel sets, and wiring harnesses to suspend and hold dispatches [^r17]. Physical intake ceases entirely, and unscheduled deliveries arriving during the count are turned away at the gatehouse [^r18]. During regular cycle counts, any arriving supplier deliveries must be segregated in the holding area until aisle sheets are signed off [^r38]. 

Purchasing must review and expedite open purchase orders due prior to the count [^r19]. Revised delivery schedules must be arranged for the initial working days following the count to avoid congestion when assembly restarts [^r20]. Goods inwards staff must register all delivery notes for materials physically received on site before counting starts, and purchasing must clear disputed receipts, price differences, and quantity variations in the ledger query queue [^r21]. Returns to vendor for rework or credit must be fully registered prior to the count so rejected stock is excluded from sheets [^r22]. Approved supplier invoices must be posted against purchase orders and receiving logs before ledger closure [^r23]. Finally, purchasing must obtain certified stock declarations from external subcontractors handling frame coating, wheel building, and bracket fabrication, which are reconciled against the subcontract register and provided to accounts for valuation [^r24][^r25].

### Physical counting execution
Cycle count sheets are printed and handed out at the start of the morning [^r39]. Physical counts at Manchester are performed by warehouse staff working in pairs, with one person counting physical items and the second marking the tally sheet [^r4][^r39]. At Leeds, the unit supervisor organises the counting of frames, boxed motors, and finished machines using sheets supplied by Manchester [^r5]. Stores staff must report obvious discrepancies or damaged cartons immediately to [[user-atanaka|Aiko Tanaka]] rather than altering tallies directly [^r40].

Historical stock count sheets from the Manchester Main Stores annual count on 25 March 2023 illustrate aisle counting carried out by Count Team 3 (counted by [[person-a-tanaka|A. Tanaka]] and checked by [[person-c-shaw|C. Shaw]]) [^r27]:
* [[items-brk|BRK-PAD-01]] in bin B-01-01: 2,400 units [^r28]
* [[items-bel|BEL-STD-01]] in bin B-01-02: 1,150 units [^r29]
* [[items-box|BOX-BIKE-01]] in bin B-02-01: 3,600 units [^r30]
* [[items-mnt|MNT-FRM-01]] in bin B-02-04: 2,050 units [^r31]
* [[items-chg|CHG-4A-01]] in bin B-03-02: 980 units [^r32]

### Reconciliation, recounting, and posting
Completed count paperwork must be returned to the stores office so quantities can be keyed into Ledgerline before the shift ends [^r41]. Finance staff enter the completed counts, examine variances against book inventory, and secure formal approval from the financial controller before posting adjustments [^r6]. 

If a count sheet line has a value variance exceeding the tolerance threshold of 1.5%, Ledgerline displays [[err-cnt-0240|ERR-CNT-0240]], locks posting of the sheet, and demands a recount [^r14][^r15]. Recounts must never be performed by the original counter [^r11]. Purchasing staff assist in investigating discrepancies between physical counts and system balances [^r26]. 

The completed count pack comprises the original tally sheets, reconciliation reports, and written explanations for material discrepancies, signed by the stores lead and countersigned by finance before posting updates stock records [^r6][^r12]. Physical count documentation is archived chronologically by count cycle in the Manchester production office and Leeds main office, and electronic variance reports are retained on the network share [^r13].

## Forms and screens
* [[screen-inv-ccp-14|INV-CCP-14]] (Cycle Count Plan Entry): Used to schedule cycle counts by item classification (A monthly, B quarterly, C biannually) [^r7].
* [[screen-inv-cnt-06|INV-CNT-06]] (Stock Count Entry): Used to freeze count locations and input completed tallies [^r8][^r41]. Raises [[err-cnt-0230|ERR-CNT-0230]] if unposted transactions remain in the zone, and raises [[err-cnt-0240|ERR-CNT-0240]] if value variances exceed system tolerance [^r8][^r15].
* Tally sheets and reconciliation pack: Physical tally sheets, reconciliation reports, and written variance explanations signed by stores and finance leads [^r3][^r12].

## Versions and conflicts
* **Cycle count variance tolerance threshold**: Under [[rn-7-2-2|RN-7.2.2]] (effective 2024-06-10), the system default parameter `INV.CNT_TOL_PCT` is set to 1.5% by value, triggering [[err-cnt-0240|ERR-CNT-0240]] and blocking posting if exceeded [^r14][^r15]. SOP-INV-003 §5 (effective 2023-03-01) originally specified a 2.0% value variance threshold before mandating a recount [^r9]. Kind: `superseded`.
* **Perpetual inventory counting of packaging**: Decisions from the stores and logistics meetings on 2024-10-01 and 2026-04-18 mandate that packaging materials (cartons and foam) must be counted weekly on the perpetual inventory rota instead of relying on visual estimates [^r34][^r35]. Kind: `rule_not_in_policy`.

## See also
* [[screen-inv-cnt-06|INV-CNT-06 Stock Count Entry]]
* [[screen-inv-ccp-14|INV-CCP-14 Cycle Count Plan Entry]]
* [[err-cnt-0230|ERR-CNT-0230 Area has open transactions]]
* [[err-cnt-0240|ERR-CNT-0240 Cycle Count Value Variance Exceeds Tolerance]]
* [[errors-cnt|Stock Count Error Codes (ERR-CNT-*)]]
* [[rn-7-2-2|RN-7.2.2 Ledgerline ERP 7.2.2 Release Notes]]
* [[sop-inv-002|SOP-INV-002 Returns to Vendor (RTV)]]
* [[sop-ap-001|SOP-AP-001 Three-Way Invoice Matching]]
* [[user-cshaw|Callum Shaw (CSHAW)]]
* [[user-gwhitaker|Grace Whitaker (GWHITAKER)]]
* [[user-atanaka|Aiko Tanaka (ATANAKA)]]

## References

[^r2]: 02_procedures/SOP-INV-003 Stock Count v1.2.pdf, p. 2, §2. Scope
[^r1]: 02_procedures/SOP-INV-003 Stock Count v1.2.pdf, p. 1, Field / Value
[^r3]: 02_procedures/SOP-INV-003 Stock Count v1.2.pdf, p. 2, §3. Responsibilities
[^r7]: 02_procedures/SOP-INV-003 Stock Count v1.2.pdf, p. 3, §5. Procedure
[^r34]: 10_meeting_notes/2024-10-01 Stores and logistics meeting.md, Discussion
[^r35]: 10_meeting_notes/2026-04-18 Stores and logistics meeting.docx, Discussion
[^r8]: 02_procedures/SOP-INV-003 Stock Count v1.2.pdf, p. 3, §5. Procedure
[^r33]: 10_meeting_notes/2022-10-16 Weekly purchasing meeting.docx, Discussion
[^r36]: 09_email_archive/2026/2026-01-21_Cycle count this Friday.eml, Cycle count this Friday
[^r37]: 09_email_archive/2026/2026-01-21_Cycle count this Friday.eml, Cycle count this Friday
[^r10]: 02_procedures/SOP-INV-003 Stock Count v1.2.pdf, p. 3, §5. Procedure
[^r16]: 11_training/intranet_export_2016/page_year_end_stock_count__2016.html, Year-end stock count (2016)
[^r17]: 11_training/intranet_export_2016/page_year_end_stock_count__2016.html, Supplier deliveries and cut-off arrangements
[^r18]: 11_training/intranet_export_2016/page_year_end_stock_count__2016.html, Supplier deliveries and cut-off arrangements
[^r38]: 09_email_archive/2026/2026-01-21_Cycle count this Friday.eml, Cycle count this Friday
[^r19]: 11_training/intranet_export_2016/page_year_end_stock_count__2016.html, Supplier deliveries and cut-off arrangements
[^r20]: 11_training/intranet_export_2016/page_year_end_stock_count__2016.html, Supplier deliveries and cut-off arrangements
[^r21]: 11_training/intranet_export_2016/page_year_end_stock_count__2016.html, Goods received and invoice matching
[^r22]: 11_training/intranet_export_2016/page_year_end_stock_count__2016.html, Goods received and invoice matching
[^r23]: 11_training/intranet_export_2016/page_year_end_stock_count__2016.html, Goods received and invoice matching
[^r24]: 11_training/intranet_export_2016/page_year_end_stock_count__2016.html, Subcontract work and off-site inventory
[^r25]: 11_training/intranet_export_2016/page_year_end_stock_count__2016.html, Subcontract work and off-site inventory
[^r39]: 09_email_archive/2026/2026-01-21_Cycle count this Friday.eml, Cycle count this Friday
[^r4]: 02_procedures/SOP-INV-003 Stock Count v1.2.pdf, p. 2, §3. Responsibilities
[^r5]: 02_procedures/SOP-INV-003 Stock Count v1.2.pdf, p. 2, §3. Responsibilities
[^r40]: 09_email_archive/2026/2026-01-21_Cycle count this Friday.eml, Cycle count this Friday
[^r27]: 99_scans/2023_stock_count_sheet_MAN_aisle_B.pdf, p. 1, ANNUAL STOCK COUNT 2023 MANCHESTER MAIN STORES
[^r28]: 99_scans/2023_stock_count_sheet_MAN_aisle_B.pdf, p. 1, ANNUAL STOCK COUNT 2023 MANCHESTER MAIN STORES
[^r29]: 99_scans/2023_stock_count_sheet_MAN_aisle_B.pdf, p. 1, ANNUAL STOCK COUNT 2023 MANCHESTER MAIN STORES
[^r30]: 99_scans/2023_stock_count_sheet_MAN_aisle_B.pdf, p. 1, ANNUAL STOCK COUNT 2023 MANCHESTER MAIN STORES
[^r31]: 99_scans/2023_stock_count_sheet_MAN_aisle_B.pdf, p. 1, ANNUAL STOCK COUNT 2023 MANCHESTER MAIN STORES
[^r32]: 99_scans/2023_stock_count_sheet_MAN_aisle_B.pdf, p. 1, ANNUAL STOCK COUNT 2023 MANCHESTER MAIN STORES
[^r41]: 09_email_archive/2026/2026-01-21_Cycle count this Friday.eml, Cycle count this Friday
[^r6]: 02_procedures/SOP-INV-003 Stock Count v1.2.pdf, p. 2, §3. Responsibilities
[^r14]: 08_release_notes/RN-7.2.2 Ledgerline Release Notes.pdf, p. 2, §2. Changes
[^r15]: 08_release_notes/RN-7.2.2 Ledgerline Release Notes.pdf, p. 2, §3. Details
[^r11]: 02_procedures/SOP-INV-003 Stock Count v1.2.pdf, p. 4, What to do when something does not look right
[^r26]: 11_training/intranet_export_2016/page_year_end_stock_count__2016.html, Subcontract work and off-site inventory
[^r12]: 02_procedures/SOP-INV-003 Stock Count v1.2.pdf, p. 4, Practice at Northbridge
[^r13]: 02_procedures/SOP-INV-003 Stock Count v1.2.pdf, p. 4, Practice at Northbridge
[^r9]: 02_procedures/SOP-INV-003 Stock Count v1.2.pdf, p. 3, §5. Procedure
