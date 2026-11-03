---
title: "POL-PUR-001 Purchase Policy"
type: "policy"
slug: "pol-pur-001"
summary: "Core purchasing policy governing requests, order limits, approvals, supplier qualification, rate contract pricing, and taxation across Manchester and Leeds plants."
audience: "staff"
status: "mixed"
sources: ["01_policies/AMD-PUR-2026-03_Amendment3_PurchasePolicy_DIRlimit.pdf", "01_policies/POL-APR-002 Approval Matrix v3.0.pdf", "01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf", "01_policies/POL-SUP-003 Supplier Policy v2.3.pdf", "01_policies/old/Purchase Policy v4.0.docx", "01_policies/old/purchase_policy_v3_2019.docx", "02_procedures/SOP-PUR-006 Quotations and Supplier Selection v1.0.pdf", "08_release_notes/NBC_customisations_and_patch_log.xlsx", "11_training/intranet_export_2016/index.html", "09_email_archive/2026/2026-10-12_Amendment 3 - direct orders limited to _25,000 from 1 December.eml", "09_email_archive/2026/2026-10-23_RE_ Brightcell quote - can we switch from Voltway_.eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Document code | POL-PUR-001 |
| Type | policy |
| Version | 4.1 |
| Effective date | 2026-04-01 |
| Author | Daniel Okafor |
| Approver | Henrik Weber |
| Status | current |
| Audience | staff |

POL-PUR-001 is Northbridge Cycles' core purchase policy governing all procurement across the Manchester plant and Leeds unit in Ledgerline ERP [^r5]. Effective 1 April 2026, version 4.1 establishes mandatory purchase request workflows, approval ceilings based on gross value including VAT, strict UN 38.3 compliance for lithium-cell parts, and a 2% rate contract price variance threshold [^r3][^r4][^r13][^r18][^r22]. As of 26 October 2026, direct orders without a prior purchase request remain permitted up to £50,000 gross until the lower limit under [[amd-pur-2026-03|AMD-PUR-2026-03]] takes effect on 1 December 2026 [^r8][^r33][^r34][^r37].

## Clauses

### 1. Purpose and administration
Version 4.1 of POL-PUR-001 was authored by [[person-d-okafor|D. Okafor]] and approved by plant head [[user-hweber|Henrik Weber]], taking effect on 1 April 2026 [^r3].

### 2. Scope
The purchase policy applies to every purchase made for the Manchester plant (NBC-MAN-01) and the Leeds unit (NBC-LDS-01) through Ledgerline ERP [^r5].

### 3. Requests before orders
Every purchase must start with a purchase request in Ledgerline, unless it qualifies as a direct order under section 3.3 [^r6]. A purchase request specifies the item, quantity, need-by date, warehouse, and the cost centre bearing the expenditure [^r7]. Staff raising purchase requests must ensure an approved requisition is recorded in the system prior to committing company funds [^r30]. A direct purchase order without a prior request is permitted only when its gross value, including VAT, is £50,000 or less, configured in the system via parameter PUR.DIR_LIMIT [^r8][^r29]. A purchase order created against a purchase request is not permitted to exceed the requested quantity [^r9].

### 4. Cost centres and budgets
Every purchase request and order must be charged to an open cost centre [^r10]. Ledgerline automatically saves any order booked against a closed cost centre as a Draft, and Draft orders are never sent to suppliers [^r11]. Staff must check cost centre status in Ledgerline using screen [[screen-fin-cc-01|FIN-CC-01]] or verify with Finance before raising an order [^r12].

### 5. Approval limits
Approval limits are evaluated against the gross value including VAT rather than the basic net value [^r13]. The specific purchasing approval matrix referenced by this section is defined in [[pol-apr-002|POL-APR-002]] [^r1]. If an order exceeds the raiser's personal limit in the approval matrix, it must be approved by the next person up the line whose authority covers it [^r14]. Self-approval of purchase orders is strictly prohibited under all circumstances and is blocked in Ledgerline with error [[err-apr-0003|ERR-APR-0003]] [^r2][^r15]. Approval of a purchase request covers the resulting purchase order provided the approver's personal limit covers the order's gross value [^r16].

### 6. Supplier qualification
Purchase orders may only be placed with suppliers that are active in the supplier master [^r17]. Before placing orders with a new supplier, the supplier must be formally onboarded under [[pol-sup-003|POL-SUP-003]], which details master entry, document collection, blocking, and duplicate prevention [^r19][^r25]. Lithium-cell parts (including battery packs, hub motors, chargers, and any item with cell_safety = 1) may only be purchased from suppliers holding a verified, unexpired [[topic-un-38-3-certificates|UN 38.3 certificate]] in Ledgerline [^r18][^r26][^r35]. Purchasers must prefer suppliers with current rate contracts, and obtaining a cheaper quotation from a new supplier does not justify switching suppliers for a lithium-cell part [^r20][^r36].

### 7. Prices
Orders must apply rates from current rate contracts, treating historical order prices as reference only [^r21]. Items covered by an active rate contract require no competitive quotation and must be ordered directly at the contract rate per POL-PUR-001 §7.1, whereas requirements exceeding £100,000 gross necessitate three written quotations evaluated on form NBC-F-118 per [[sop-pur-006|SOP-PUR-006]] [^r27][^r28]. Any purchase order placed at a price more than 2% above the rate contract requires written justification from the manager in the order remarks [^r4][^r22].

### 8. Tax
UK suppliers are charged UK VAT using tax codes ending in -UK, whereas non-UK suppliers are charged VAT via reverse charge using tax codes ending in -RC [^r23].

### 9. Records
An order must carry an official Ledgerline document number and attain Released status before the supplier is instructed to deliver or the requester is told the order is placed [^r24]. Verbal orders with suppliers are strictly prohibited under any circumstances, and invoices received without an authorised order reference are held by finance pending departmental review [^r31]. Advice notes for all deliveries to Manchester or Leeds must clearly display the purchase order reference and be affixed to the outer packaging [^r32].

## Versions and conflicts

### Direct purchase order threshold
* **Today's rule:** Direct purchase orders without a preceding purchase request are permitted up to £50,000 gross value including VAT through 30 November 2026 [^r8][^r33].
* **Future rule:** From 1 December 2026, [[amd-pur-2026-03|AMD-PUR-2026-03]] amends clause §3.3 to restrict direct purchase orders without a request to £25,000 gross including VAT [^r34][^r37].
* **Superseded rule:** Under version 3.0 (effective 1 April 2019), direct orders without a request were permitted only up to £30,000 gross [^r49][^r53].
* **Kind:** `future_dated`, `superseded` [^r8][^r34][^r37][^r49]

### Price tolerance over rate contracts
* **Today's rule:** Orders placed at a price more than 2% above the rate contract require written justification from the manager in the remarks [^r4][^r22].
* **Superseded rule:** Under version 4.0, the price variance threshold requiring manager remarks was 5% [^r4][^r46].
* **Kind:** `superseded` [^r4][^r46]

### UN 38.3 certification scope
* **Today's rule:** Verified UN 38.3 certificates are mandatory for all lithium-cell parts, explicitly covering battery packs, hub motors, chargers, and any item marked cell_safety = 1 [^r4][^r18].
* **Superseded rule:** Under version 4.0, clause 6.2 covered battery packs and hub motors [^r45]; under version 3.0, only battery packs required certification while hub motors and chargers were explicitly exempt [^r51].
* **Kind:** `superseded` [^r4][^r45][^r51]

### Document history
* **Superseded history:** Version 1.0 was issued on 1 September 1998 by R. Ainsworth for Ledgerline 5 [^r52]. Version 2.0 was rewritten on 1 April 2004 by G. Sutcliffe for Ledgerline 6 to mandate requests before orders [^r52]. Version 3.0 was issued on 1 April 2019 by G. Sutcliffe for the Ledgerline 7.1 migration [^r53]. Version 4.0 established the £50,000 direct-order parameter PUR.DIR_LIMIT on 1 April 2025 [^r29][^r38][^r39].

## See also
* [[pol-apr-002|POL-APR-002 Approval Matrix for Purchasing]]
* [[pol-sup-003|POL-SUP-003 Supplier Policy]]
* [[sop-pur-001|SOP-PUR-001 Supplier Onboarding]]
* [[sop-pur-006|SOP-PUR-006 Quotations and Supplier Selection]]
* [[amd-pur-2026-03|AMD-PUR-2026-03 Amendment 3 to the Purchase Policy]]
* [[topic-un-38-3-certificates|UN 38.3 Certificates]]
* [[screen-fin-cc-01|FIN-CC-01 Cost Centre Entry]]
* [[err-apr-0003|ERR-APR-0003 Self-approval not permitted]]

## References

[^r5]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 1, §2. Scope
[^r3]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 1, Purchase Policy
[^r4]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 1, Version history
[^r13]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 2, §5. Approval limits
[^r18]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 2, §6. Supplier qualification
[^r22]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 2, §7. Prices
[^r8]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 1, §3. Requests before orders
[^r33]: 09_email_archive/2026/2026-10-12_Amendment 3 - direct orders limited to _25,000 from 1 December.eml, body
[^r34]: 09_email_archive/2026/2026-10-12_Amendment 3 - direct orders limited to _25,000 from 1 December.eml, body
[^r37]: 01_policies/AMD-PUR-2026-03_Amendment3_PurchasePolicy_DIRlimit.pdf, p. 1, §1. What changes
[^r6]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 1, §3. Requests before orders
[^r7]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 1, §3. Requests before orders
[^r30]: 11_training/intranet_export_2016/index.html, Purchasing home
[^r29]: 08_release_notes/NBC_customisations_and_patch_log.xlsx, sheet Log, row NBC-2025-002, SHEET Log
[^r9]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 1, §3. Requests before orders
[^r10]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 1, §4. Cost centres and budgets
[^r11]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 1, §4. Cost centres and budgets
[^r12]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 1, §4. Cost centres and budgets
[^r1]: 01_policies/POL-APR-002 Approval Matrix v3.0.pdf, p. 1, §1. Purpose
[^r14]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 2, §5. Approval limits
[^r2]: 01_policies/POL-APR-002 Approval Matrix v3.0.pdf, p. 2, §4. Who may not approve
[^r15]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 2, §5. Approval limits
[^r16]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 2, §5. Approval limits
[^r17]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 2, §6. Supplier qualification
[^r19]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 2, §6. Supplier qualification
[^r25]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 1, §1. Purpose
[^r26]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 2, §4. UN 38.3 certificates
[^r35]: 09_email_archive/2026/2026-10-23_RE_ Brightcell quote - can we switch from Voltway_.eml, body
[^r20]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 2, §6. Supplier qualification
[^r36]: 09_email_archive/2026/2026-10-23_RE_ Brightcell quote - can we switch from Voltway_.eml, body
[^r21]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 2, §7. Prices
[^r27]: 02_procedures/SOP-PUR-006 Quotations and Supplier Selection v1.0.pdf, p. 3, §5. Procedure
[^r28]: 02_procedures/SOP-PUR-006 Quotations and Supplier Selection v1.0.pdf, p. 3, §5. Procedure
[^r23]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 2, §8. Tax
[^r24]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 2, §9. Records
[^r31]: 11_training/intranet_export_2016/index.html, Purchasing home
[^r32]: 11_training/intranet_export_2016/index.html, Purchasing home
[^r49]: 01_policies/old/purchase_policy_v3_2019.docx, §3. Requests before orders
[^r53]: 01_policies/old/purchase_policy_v3_2019.docx, §6. Supplier qualification
[^r46]: 01_policies/old/Purchase Policy v4.0.docx, §7. Prices
[^r45]: 01_policies/old/Purchase Policy v4.0.docx, §6. Supplier qualification
[^r51]: 01_policies/old/purchase_policy_v3_2019.docx, §6. Supplier qualification
[^r52]: 01_policies/old/purchase_policy_v3_2019.docx, §6. Supplier qualification
[^r38]: 01_policies/old/Purchase Policy v4.0.docx, §2. Scope
[^r39]: 01_policies/old/Purchase Policy v4.0.docx, §3. Requests before orders
