---
title: "SOP-PUR-003 Purchase Order Amendment and"
type: "procedure"
slug: "sop-pur-003"
summary: "Standard operating procedure for amending or cancelling purchase orders in Ledgerline, including field change rules, approval rollbacks, and cancellation notifications."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-PUR-003 PO Amendment and Cancellation v1.2.pdf", "11_training/intranet_export_2016/page_purchasing_team_news__spring_2016.html", "10_meeting_notes/2022-10-21 Supplier review.docx", "09_email_archive/2025/2025-05-18_Invoices on hold for price differences.eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | SOP-PUR-003 |
| owner | [[user-dokafor|Daniel Okafor]] |
| approved_by | [[user-hweber|Henrik Weber]] |
| version | 1.2 |
| effective | 2025-02-01 |
| status | current |

SOP-PUR-003 governs the amendment and cancellation of purchase orders within Ledgerline on screen [[screen-pur-pom-06|PUR-POM-06]][^r1][^r2]. As of 26 October 2026, buyers may modify only the line quantity, need-by date, or cost centre; changes to suppliers, items, or rates require cancelling and re-raising the order[^r2]. It also details required actions when orders revert to pending approval or when cancellations occur after deliveries commence[^r4][^r5][^r9].

| Field | Value |
|---|---|
| Document code | SOP-PUR-003 |
| Title | Purchase Order Amendment and Cancellation |
| Version | 1.2 |
| Effective date | 2025-02-01 |
| Owner | [[user-dokafor|Daniel Okafor]] |
| Approved by | [[user-hweber|Henrik Weber]] |
| Status | Current |

## Steps

### Purchase order amendment
1. On screen [[screen-pur-pom-06|PUR-POM-06]], open the target purchase order and select Fetch[^r2].
2. Amend only permitted fields: quantity, need-by date, or cost centre[^r2]. Any alterations to the supplier, item, or rate cannot be performed as an amendment and require the order to be cancelled and re-raised[^r2].
3. If an amendment increases the gross order value beyond current approval coverage, Ledgerline automatically reverts the purchase order to pending approval (PA), even if it was previously released[^r4]. The buyer must notify the supplier that the requested revision remains unconfirmed until the order is re-released[^r5].
4. Dispatch delay updates and schedule adjustments must be logged in the system immediately upon notification from domestic or overseas suppliers to prevent distortion of supplier compliance and lead time metrics[^r11][^r12].
5. If an order in Draft status is stalled on a closed cost centre displaying warning [[w-cc-114|W-CC-114]], amend the cost centre to an active code; the order will then transition to approved (AP) or pending approval (PA) under standard rules[^r3].
6. Orders currently in cancelled (CN), rejected (RJ), or closed (CL) status cannot be amended; attempting to modify them triggers error [[err-po-0801|ERR-PO-0801]][^r7].

### Partial receipts and line closures
If a purchase order has been partially received and the outstanding balance is no longer needed, staff must close the line against further receipt rather than reducing the original total order quantity[^r8].

### Purchase order cancellation
1. Open the order on [[screen-pur-pom-06|PUR-POM-06]], press Cancel, and input the required cancellation reason[^r6].
2. Because Ledgerline produces no automated supplier communication upon cancellation, the buyer must e-mail the supplier on the same day and store a copy of the message in the order file[^r6].
3. When an order is cancelled after delivery has already started, immediately transmit documentation copies to the goods inward desk to prevent unauthorised receipt[^r9].

### Invoice holds and query resolution
Buyers must inspect open orders, monitor query lists in the system, and issue instructions to accounts payable to release blocked invoices[^r13][^r14].

## Forms and screens
* [[screen-pur-pom-06|PUR-POM-06]] (Purchase Order Amendment): Core screen used to retrieve orders, modify allowable header and line fields, update cost centres, and trigger cancellations[^r2][^r3][^r6].
* Warning [[w-cc-114|W-CC-114]]: Displayed when a Draft order references a closed cost centre[^r3].
* Error [[err-po-0801|ERR-PO-0801]]: Displayed when attempting to amend orders in CN, RJ, or CL status[^r7].

## Versions and conflicts
* **Rate adjustments on open orders**: Today's rule (effective 2025-02-01 under SOP-PUR-003 v1.2) prohibits modifying rates on [[screen-pur-pom-06|PUR-POM-06]]; rate changes require cancelling and re-raising the order[^r2]. In contrast, historical training guidance from Spring 2016 and an e-mail dated 2025-05-18 directed buyers to amend price updates directly on live lines in the system prior to goods receipt or after manager review[^r10][^r13] (`contradiction`).

## See also
* [[screen-pur-pom-06|screen-pur-pom-06]]: PUR-POM-06 Purchase Order Amendment
* [[err-po-0801|err-po-0801]]: ERR-PO-0801 Order in CN, RJ or CL status cannot be amended
* [[w-cc-114|w-cc-114]]: W-CC-114 Closed cost centre warning
* [[user-dokafor|user-dokafor]]: Daniel Okafor, Purchase Manager
* [[user-hweber|user-hweber]]: Henrik Weber, Plant Head
* [[decision-2022-10-21-supplier-review|decision-2022-10-21-supplier-review]]: Supplier Review Meeting (2022-10-21)
* [[sop-pur-002|sop-pur-002]]: SOP-PUR-002 Purchase Request to Purchase Order
* [[sop-ap-001|sop-ap-001]]: SOP-AP-001 Three-Way Invoice Matching

## References

[^r1]: 02_procedures/SOP-PUR-003 PO Amendment and Cancellation v1.2.pdf, p. 1, Purchase Order Amendment and Cancellation
[^r2]: 02_procedures/SOP-PUR-003 PO Amendment and Cancellation v1.2.pdf, p. 3, §5. Procedure
[^r4]: 02_procedures/SOP-PUR-003 PO Amendment and Cancellation v1.2.pdf, p. 3, §5. Procedure
[^r5]: 02_procedures/SOP-PUR-003 PO Amendment and Cancellation v1.2.pdf, p. 3, §5. Procedure
[^r9]: 02_procedures/SOP-PUR-003 PO Amendment and Cancellation v1.2.pdf, p. 4, §6. Records
[^r11]: 11_training/intranet_export_2016/page_purchasing_team_news__spring_2016.html, Production demand and parts supply
[^r12]: 10_meeting_notes/2022-10-21 Supplier review.docx, Discussion
[^r3]: 02_procedures/SOP-PUR-003 PO Amendment and Cancellation v1.2.pdf, p. 3, §5. Procedure
[^r7]: 02_procedures/SOP-PUR-003 PO Amendment and Cancellation v1.2.pdf, p. 3, §5. Procedure
[^r8]: 02_procedures/SOP-PUR-003 PO Amendment and Cancellation v1.2.pdf, p. 3, §3. Responsibilities
[^r6]: 02_procedures/SOP-PUR-003 PO Amendment and Cancellation v1.2.pdf, p. 3, §5. Procedure
[^r13]: 09_email_archive/2025/2025-05-18_Invoices on hold for price differences.eml, Invoices on hold for price differences
[^r14]: 09_email_archive/2025/2025-05-18_Invoices on hold for price differences.eml, Invoices on hold for price differences
[^r10]: 11_training/intranet_export_2016/page_purchasing_team_news__spring_2016.html, Order administration and receipts
