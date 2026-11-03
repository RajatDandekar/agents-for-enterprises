---
title: "POL-RET-006 Returns Policy"
type: "policy"
slug: "pol-ret-006"
summary: "Rules governing physical receipt, inspection, and system processing for supplier returns, customer credit notes, and bike shop warranty returns."
audience: "staff"
status: "current"
sources: ["01_policies/POL-RET-006 Returns Policy v2.1.pdf", "02_procedures/SOP-INV-002 Returns to Vendor (RTV) v1.3.pdf", "02_procedures/SOP-SAL-002 Warranty Claims (RMA) v1.1.pdf", "10_meeting_notes/2022-10-15 Battery safety committee.md"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | POL-RET-006 |
| Title | Returns Policy |
| Version | 2.1 |
| Owner | Purchase and Sales departments |
| Approved by | Henrik Weber |
| Effective date | 2025-01-01 |
| Status | current |

POL-RET-006 governs the physical receipt, quarantine, inspection, and system logging of stock returned by bike shops or individual riders across the Manchester works and Leeds unit [^r2]. Effective from 2025-01-01, the policy is jointly owned by the Purchase and Sales departments and was approved by plant head [[user-hweber|Henrik Weber]] [^r1]. It sets the rules for returning faulty items to suppliers, handling customer credit notes, and managing warranty claims for bicycle frames and [[items-bat|battery packs]] [^r3][^r5][^r8].

| Field | Value |
|---|---|
| Code | POL-RET-006 |
| Version | 2.1 |
| Owner | Purchase and Sales departments |
| Approver | Henrik Weber |
| Effective date | 2025-01-01 |
| Status | Current |

## Clauses

### 1. Scope
The policy governs the physical receipt, quarantine, inspection, and system logging of stock returned by bike shops or individual riders across the Manchester works and Leeds unit [^r2].

### 2. Returns to suppliers
Under clause 2.1, faulty or wrong goods are returned to the supplier within 30 days of receipt on a return to vendor (RTV) document using screen [[screen-inv-rtv-07|INV-RTV-07]] [^r3][^r9]. Under clause 2.2, if the supplier's invoice has already been posted, staff must raise a debit note on screen [[screen-ap-dbn-04|AP-DBN-04]] instead of an RTV credit, as Ledgerline refuses an RTV against an invoiced receipt with error [[err-rtv-0230|ERR-RTV-0230]] [^r4].

### 3. Warranty returns from bike shops
Under clause 3.1, bicycle frames carry a 5-year warranty, while battery packs, motors, chargers, and all other parts carry a 2-year warranty from the date of sale to the rider [^r5][^r10]. Under clause 3.2, a battery pack returned under warranty is never put back into stock, but is transferred directly to battery refurbishment (cost centre [[cc-prd-09|PRD-09]]) or sent for recycling [^r6]. Under clause 3.3, bike shops must send lithium battery returns using a carrier's dangerous-goods service, never by ordinary parcel delivery [^r7][^r11].

### 4. Credit notes to customers
Finance issues credit notes only after the Manchester plant or Leeds unit confirms receipt and inspection of returned items, matching the credit note directly to the original sales invoice [^r8].

## See also
* [[sop-inv-002|SOP-INV-002 Returns to Vendor (RTV)]]
* [[sop-sal-002|SOP-SAL-002 Warranty Claims from Bike Shops]]
* [[screen-inv-rtv-07|INV-RTV-07 Return To Vendor Entry]]
* [[screen-ap-dbn-04|AP-DBN-04 Debit Note Entry]]
* [[err-rtv-0230|ERR-RTV-0230 Invoice already posted against receipt]]
* [[cc-prd-09|PRD-09 Battery refurbishment]]
* [[items-bat|BAT-* items]]
* [[topic-battery-handling|Battery Handling and Dangerous Goods Logistics]]
* [[pol-bat-004|POL-BAT-004 Battery Safety and Handling Policy]]
* [[sop-qua-002|SOP-QUA-002 Damaged Battery Pack Quarantine]]

## References

[^r2]: 01_policies/POL-RET-006 Returns Policy v2.1.pdf, p. 1, §1. Scope
[^r1]: 01_policies/POL-RET-006 Returns Policy v2.1.pdf, p. 1, Returns Policy
[^r3]: 01_policies/POL-RET-006 Returns Policy v2.1.pdf, p. 1, §2. Returns to suppliers
[^r5]: 01_policies/POL-RET-006 Returns Policy v2.1.pdf, p. 2, §3. Warranty returns from bike shops
[^r8]: 01_policies/POL-RET-006 Returns Policy v2.1.pdf, p. 4, §4. Credit notes to customers
[^r9]: 02_procedures/SOP-INV-002 Returns to Vendor (RTV) v1.3.pdf, p. 3, Common mistakes
[^r4]: 01_policies/POL-RET-006 Returns Policy v2.1.pdf, p. 2, §2. Returns to suppliers
[^r10]: 02_procedures/SOP-SAL-002 Warranty Claims (RMA) v1.1.pdf, p. 3, §5. Procedure
[^r6]: 01_policies/POL-RET-006 Returns Policy v2.1.pdf, p. 3, §3. Warranty returns from bike shops
[^r7]: 01_policies/POL-RET-006 Returns Policy v2.1.pdf, p. 3, §3. Warranty returns from bike shops
[^r11]: 10_meeting_notes/2022-10-15 Battery safety committee.md, Discussion
