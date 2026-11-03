---
title: "ERR-GRN-0204 Over-receipt exceeds order balance"
type: "error"
slug: "err-grn-0204"
summary: "Ledgerline error raised during goods receipt when the entered receipt quantity exceeds the open purchase order line balance."
audience: "staff"
status: "current"
sources: ["02_procedures/sop_inv_001_goods_receipt_v2.docx"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-GRN-0204 |
| Module | INV |
| Trigger | Over-receipt exceeds order balance |
| Block type | Hard stop |
| Procedure | SOP-INV-001 |

ERR-GRN-0204 is a Ledgerline error that blocks processing when a user attempts to book in more items than remain on a purchase order line [^r1]. It enforces purchase order quantity controls during the receipt workflow defined in [[sop-inv-001|SOP-INV-001 Goods Receipt]] [^r1]. Stores staff encountering this code must stop the transaction and resolve the over-delivery without manipulating system quantities [^r2].

## Meaning
Ledgerline raises error ERR-GRN-0204 to indicate that the entered receipt quantity exceeds the remaining open balance on the specified purchase order line [^r1].

## Cause
The error occurs when a supplier delivers more stock than ordered, or when a user enters a quantity greater than the outstanding order line balance during goods receipt [^r1][^r2].

## How to fix
Stores staff must halt the transaction immediately upon triggering the error [^r2]. Users must never adjust system figures to absorb extra stock [^r2]. Depending on instructions, staff must either receive only the valid remaining balance or hold the entire delivery while contacting purchasing [^r2].

## Raised by
The error is raised by Ledgerline during the goods receipt procedure [^r1].

## See also
* [[sop-inv-001|SOP-INV-001 Goods Receipt]]
* [[screen-inv-grn-03|INV-GRN-03 Goods Receipt Note (Grn)]]
* [[err-grn-0102|ERR-GRN-0102 Purchase order not released]]

## References

[^r1]: 02_procedures/sop_inv_001_goods_receipt_v2.docx, §5. Procedure
[^r2]: 02_procedures/sop_inv_001_goods_receipt_v2.docx, §5. Procedure: notes and common mistakes
