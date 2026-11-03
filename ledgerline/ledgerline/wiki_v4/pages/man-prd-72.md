---
title: "MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production"
type: "manual"
slug: "man-prd-72"
summary: "User manual for Ledgerline ERP 7.2 Production module covering BOM, routing, backflushing, operation confirmation, MRP, and master scheduling."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Document Code | MAN-PRD-72 |
| Title | Ledgerline ERP 7.2 User Manual: Production |
| Owner | Ledgerline Systems Documentation Group |
| Version | 7.2.3 |
| Effective Date | 2025-01-15 |
| Status | current |

MAN-PRD-72 is the vendor user manual for the Production module of Ledgerline ERP 7.2, defining core system conventions, production master data, and execution procedures [^r1]. As of 26 October 2026, version 7.2.3 is in force across manufacturing operations at both the Manchester assembly plant and the Leeds sub-assembly unit [^r1][^r20]. It governs operational processes across screens, underlying service groups, and validation error routines from scheduling through to works order closure and nominal ledger posting [^r4][^r11][^r27].

| Field | Value |
|---|---|
| Document Code | MAN-PRD-72 [^r1] |
| System Version | Ledgerline ERP 7.2 [^r1][^r2] |
| Manual Version | 7.2.3 [^r1] |
| Effective Date | 2025-01-15 [^r1] |
| Owner | Ledgerline Systems Documentation Group [^r1] |
| Status | Current [^r1] |

## System conventions and integration

Ledgerline ERP 7.2 automatically closes sessions that remain idle for 20 minutes, which results in the loss of any unsaved work [^r2]. Within all data entry screens, pressing the F2 key in any data field brings up a search window displaying permitted values [^r3]. Upon final works order closure and quality sign-off, the module automatically posts variances between standard build costs and actual expenditure directly to the nominal ledger [^r4].

## Screens and processes

### Bill of materials (PRD-BOM-02)

Screen [[screen-prd-bom-02|PRD-BOM-02]] provides maintenance and inquiry functions for production bills of materials [^r11]. It operates using the [[services-prd-bom|BOM service group]], supporting services `bom_get`, `bom_save`, `bom_search`, `bom_copy`, `bom_explode`, and `bom_where_used` [^r11].

### Routing (PRD-RTG-03)

Accessed via menu path **Production > Routing**, screen [[screen-prd-rtg-03|PRD-RTG-03]] maintains routings and interfaces with the [[services-prd-rtg|routing service group]] through services `rtg_get`, `rtg_save`, and `rtg_search` [^r12]. In Ledgerline ERP, a routing establishes the operational sequence an item follows during manufacture for framed units produced at the Manchester plant or the Leeds unit, detailing designated work centres, standard labour or machine allowances in standard minutes, and administrative statuses [^r13]. Before creating a routing, the item master record must exist and be verified and saved as a manufactured or assembled part, and the physical shop-floor department, machine, or assembly location must be recognised as an authorised work centre [^r14].

### Backflush (PRD-BKF-08)

Screen [[screen-prd-bkf-08|PRD-BKF-08]] calculates the theoretical consumption of raw stock, frames, battery enclosures, and drive units from completed works order quantities, relieving line inventory, crediting finished goods, absorbing standard labour and overhead, and closing routing operations [^r15]. Backflushing cannot post if battery or motor serial numbers have not yet been scanned and registered [^r18]. Northbridge Cycles operational policy mandates entering shift details or testing station references into the `COMMENT` field on [[screen-prd-bkf-08|PRD-BKF-08]] to maintain traceability audits [^r19].

Reversing a backflush requires entering an explanation in the `REASON` field before reversal routines can proceed [^r16]. The reversal routine unwinds finished goods bookings, restores line component balances at standard cost, and cancels general ledger absorption journals [^r17].

### Operation confirmation (PRD-OPR-04)

Screen [[screen-prd-opr-04|PRD-OPR-04]] records shop-floor progress against works orders at both the Manchester assembly plant and the Leeds sub-assembly unit, operating through the [[services-prd-opr|operation confirmation service group]] via `opr_save`, `opr_get`, and `opr_search` [^r20][^r21]. Fields `wo_no` (WO NO), `op_no` (OP NO), and `qty_ok` (QTY OK) are mandatory, whereas `qty_rej` (QTY REJ) and `status` (STATUS) are optional [^r22]. Units requiring rework must not be booked in `QTY REJ`; they must remain in work-in-progress and be recorded in `QTY OK` only once brought up to standard [^r23].

Once `opr_save` completes on screen [[screen-prd-opr-04|PRD-OPR-04]], entered quantities post directly to the ledger and cannot be overwritten; corrections require the production control office in Manchester or the unit supervisor in Leeds to post an adjusting movement or reversal confirmation [^r24]. Screen [[screen-prd-opr-04|PRD-OPR-04]] operates identically across both Manchester and Leeds for sub-assemblies produced in Leeds for final assembly in Manchester, provided the correct works order identifier is supplied [^r25].

### MRP run (PRD-MRP-09)

Located under **Production > Mrp run**, screen [[screen-prd-mrp-09|PRD-MRP-09]] calculates net material requirements across manufacturing operations [^r26]. It interacts with the [[services-prd-mrp|MRP service group]], supporting services `mrp_run`, `mrp_get`, `mrp_exceptions`, and `mrp_firm` [^r26].

### Master schedule (PRD-MPS-05)

Located under **Production > Master schedule**, screen [[screen-prd-mps-05|PRD-MPS-05]] manages the weekly build plan using the [[services-prd-mps|master schedule service group]] via services `mps_save`, `mps_get`, and `mps_search` [^r27]. Entering `ITEM CD` and `WEEK` and calling `mps_get` populates `QTY` with the scheduled build volume and sets `STATUS` to the line's administrative state [^r28]. `QTY` must represent whole bicycle units or complete sub-assembly sets, as validation rules reject fractional values [^r29]. Executing `mps_save` commits the schedule transaction, recalculates production horizon flags, and refreshes the display [^r30].

## Error and message codes

The manual outlines the following validation errors encountered during production processing:

* [[err-cc-0009|ERR-CC-0009]]: Displayed when an invalid or closed cost centre code is entered in `CC CD` [^r5].
* [[err-bom-0001|ERR-BOM-0001]]: Raised during `wo_save` when the entered `ITEM CD` lacks an active, signed-off bill of materials in the engineering register [^r10].
* ERR-WO-0105: Raised during `wo_save` when the database fails to secure a unique sequence [^r6].
* ERR-WO-0201: Raised during `wo_release` when component availability checks fail due to unmet dependencies or failed stock reservations [^r7].
* [[err-wo-0310|ERR-WO-0310]]: Raised during `wo_close` when order closure is rejected due to unresolved work centre scrap bookings [^r8].
* ERR-WO-0007: Raised by `wo_cancel` if cancellation is attempted after processing on the works order has already begun [^r9].
* ERR-WO-0801: Triggered when general database failures occur during works order processing [^r9].

For comprehensive lists and resolution details, see [[errors-wo|ERR-WO error codes]] and the [[services-prd-wo|works order services]] documentation.

## See also

* [[screen-prd-bom-02|PRD-BOM-02 Bill Of Materials]]
* [[screen-prd-rtg-03|PRD-RTG-03 Routing]]
* [[screen-prd-bkf-08|PRD-BKF-08 Backflush]]
* [[screen-prd-opr-04|PRD-OPR-04 Operation Confirmation Entry]]
* [[screen-prd-mrp-09|PRD-MRP-09 Mrp Run]]
* [[screen-prd-mps-05|PRD-MPS-05 Master Schedule Entry]]
* [[services-prd-bom|PRD bom services]]
* [[services-prd-rtg|PRD rtg services]]
* [[services-prd-opr|PRD opr services]]
* [[services-prd-mrp|PRD mrp services]]
* [[services-prd-mps|PRD mps services]]
* [[services-prd-wo|PRD wo services]]
* [[errors-wo|ERR-WO error codes]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 1, Version history
[^r20]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 19, §7. Operation Confirmation (PRD-OPR-04)
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 2, Module integration
[^r11]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 7, §4. Bill Of Materials (PRD-BOM-02)
[^r27]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 26, §9. Master Schedule (PRD-MPS-05)
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 2, §2. Signing in and sessions
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 2, System conventions
[^r12]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 11, §5. Routing (PRD-RTG-03)
[^r13]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 12, framed units produced at the Manchester plant or the Leeds unit
[^r14]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 12, Before you start
[^r15]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 15, Purpose
[^r18]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 18, Questions users ask
[^r19]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 19, Questions users ask
[^r16]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 17, Messages
[^r17]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 17, Messages
[^r21]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 19, §7. Operation Confirmation (PRD-OPR-04)
[^r22]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 19, §7. Operation Confirmation (PRD-OPR-04)
[^r23]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 21, Tips
[^r24]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 22, §8. Mrp Run (PRD-MRP-09)
[^r25]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 22, §8. Mrp Run (PRD-MRP-09)
[^r26]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 22, §8. Mrp Run (PRD-MRP-09)
[^r28]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 27, Creating or amending schedule lines
[^r29]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 27, Creating or amending schedule lines
[^r30]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 27, Creating or amending schedule lines
[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 7
[^r10]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 7, Questions users ask
[^r6]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 7
[^r7]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 7
[^r8]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 7
[^r9]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 7
