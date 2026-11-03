---
title: "ERR-GRN-0102 Purchase order not released"
type: "error"
slug: "err-grn-0102"
summary: "Ledgerline error raised during goods receipt when the referenced purchase order is not in released status."
audience: "staff"
status: "current"
sources: ["02_procedures/sop_inv_001_goods_receipt_v2.docx"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | ERR-GRN-0102 |
| Message | Purchase order not released |
| Module | Inventory / Goods Receipt |
| Trigger | Attempting goods receipt against an unreleased purchase order |
| Remedy | Contact purchasing to release the order |

ERR-GRN-0102 is a Ledgerline error encountered during the goods receiving workflow governed by [[sop-inv-001|SOP-INV-001 Goods Receipt]][^r1]. It blocks staff from posting a receipt whenever the referenced purchase order has not reached released status[^r1]. Receiving staff cannot bypass this check on screen and must coordinate with purchasing to advance the order before processing the delivery[^r2].

## Meaning

The error signifies that a goods receipt cannot be posted because the specified purchase order is not in released (RL) status within Ledgerline[^r1].

## Cause

Ledgerline raises ERR-GRN-0102 when a user attempts to perform a goods receipt against a purchase order that has not yet been released[^r1].

## How to fix

Receiving staff must not attempt to force the receipt or alter the reference on screen[^r2]. Instead, staff must contact purchasing to release the purchase order[^r2].

## Raised by

The error is raised by Ledgerline during the goods receipt process in [[sop-inv-001|SOP-INV-001]][^r1].

## See also

* [[sop-inv-001|SOP-INV-001 Goods Receipt]]
* [[screen-inv-grn-03|INV-GRN-03 Goods Receipt Note (Grn)]]
* [[err-grn-0204|ERR-GRN-0204 Over-receipt exceeds order balance]]

## References

[^r1]: 02_procedures/sop_inv_001_goods_receipt_v2.docx, §5. Procedure
[^r2]: 02_procedures/sop_inv_001_goods_receipt_v2.docx, §5. Procedure: notes and common mistakes
