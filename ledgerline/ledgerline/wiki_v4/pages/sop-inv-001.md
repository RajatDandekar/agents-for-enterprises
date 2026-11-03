---
title: "SOP-INV-001 Goods Receipt"
type: "procedure"
slug: "sop-inv-001"
summary: "Standard operating procedure governing physical intake, inspection, and Ledgerline booking of purchase order consignments at Manchester and Leeds."
audience: "staff"
status: "current"
sources: ["02_procedures/sop_inv_001_goods_receipt_v2.docx"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | SOP-INV-001 |
| Owner | Callum Shaw |
| Version | 2.0 |
| Effective | 2024-10-01 |
| Status | current |

SOP-INV-001 defines the physical intake, checking, and booking procedure for incoming consignments against purchase orders across Northbridge Cycles' Manchester plant and Leeds unit [^r1]. It requires all receipts to be recorded in Ledgerline against released orders and mandates quality hold routing and damage refusal protocols for lithium-cell consignments [^r2][^r5][^r6]. The procedure is in force today under version 2.0 [^r7].

## Steps

1. **Verify documentation**: Check the supplier delivery note against the purchase order number [^r2]. Only purchase orders with status RL can be received; unreleased orders will trigger [[err-grn-0102|ERR-GRN-0102]] [^r2].
2. **Retrieve order and enter details**: Access screen [[screen-inv-grn-03|INV-GRN-03]], enter the purchase order number, and press Fetch [^r3].
3. **Inspect and count**: Count the incoming goods and enter the quantity received [^r3]. Partial shipments generate an individual goods receipt note, but any attempt to exceed the open balance raises [[err-grn-0204|ERR-GRN-0204]] [^r4].
4. **Record references and save**: Enter the supplier delivery note number into the Remarks field and press Save [^r3].
5. **Route lithium-cell deliveries**: Book all lithium-cell components and parts into quality hold warehouse WH-MAN-QC until Quality authorizes transfer to the Manchester main stores fire-cell area [^r5].
6. **Handle damaged battery shipments**: If outer packaging damage is identified on a battery delivery, refuse the parcel immediately, take photographs while the carrier remains on site, and report the issue to Quality pursuant to [[sop-qua-002|SOP-QUA-002]] [^r6].

## Forms and screens

* [[screen-inv-grn-03|INV-GRN-03]] (Goods Receipt Note): Used to fetch released purchase orders, record received quantities, log the delivery note reference in Remarks, and generate the goods receipt note [^r3][^r4].

## See also

* [[err-grn-0102|ERR-GRN-0102 Purchase order not released]]
* [[err-grn-0204|ERR-GRN-0204 Over-receipt exceeds order balance]]
* [[screen-inv-grn-03|INV-GRN-03 Goods Receipt Note (Grn)]]
* [[sop-inv-004|SOP-INV-004 Battery Pack Storage and Handling]]
* [[sop-qua-002|SOP-QUA-002 Damaged Battery Pack Quarantine]]
* [[user-cshaw|Callum Shaw (CSHAW)]]

## References

[^r1]: 02_procedures/sop_inv_001_goods_receipt_v2.docx, §2. Scope
[^r2]: 02_procedures/sop_inv_001_goods_receipt_v2.docx, §5. Procedure
[^r5]: 02_procedures/sop_inv_001_goods_receipt_v2.docx, §5. Procedure
[^r6]: 02_procedures/sop_inv_001_goods_receipt_v2.docx, §5. Procedure
[^r7]: 02_procedures/sop_inv_001_goods_receipt_v2.docx, §7. Related documents
[^r3]: 02_procedures/sop_inv_001_goods_receipt_v2.docx, §5. Procedure
[^r4]: 02_procedures/sop_inv_001_goods_receipt_v2.docx, §5. Procedure
