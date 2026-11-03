---
title: "ERR-RTV-0230 Invoice already posted against receipt"
type: "error"
slug: "err-rtv-0230"
summary: "Ledgerline error when an RTV is attempted against a receipt whose invoice has already been matched and posted."
audience: "staff"
status: "current"
sources: ["01_policies/POL-RET-006 Returns Policy v2.1.pdf", "02_procedures/SOP-INV-002 Returns to Vendor (RTV) v1.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-RTV-0230 |
| Message | Invoice already posted against receipt |
| Module | Inventory / RTV |
| Screen | INV-RTV-07 |
| Status | Current |

Ledgerline raises error ERR-RTV-0230 when a user attempts a return to vendor against a goods receipt note whose supplier invoice has already been matched and posted [^r1][^r3]. The system blocks the direct receipt return to ensure inventory and accounts payable records remain balanced [^r1][^r3]. Users must not attempt to reverse the receipt or force the transaction, and must instead route the adjustment through accounts payable [^r2][^r4].

## Meaning
ERR-RTV-0230 indicates that an RTV cannot be processed because the selected purchase order receipt or goods receipt note has already been matched to a purchase invoice and passed for payment [^r1][^r3].

## Cause
The error is triggered when an RTV transaction is submitted against a receipt line where the corresponding supplier invoice has already been matched and posted in the financial records [^r1][^r3].

## How to fix
Staff must not attempt to reverse the original receipt or force the transaction in Ledgerline ERP [^r4]. Instead, staff must record the purchase order reference and notify accounts payable to enter a debit note against the vendor account on screen [[screen-ap-dbn-04|AP-DBN-04]] [^r2][^r4].

## Raised by
Raised by Ledgerline on screen [[screen-inv-rtv-07|INV-RTV-07]] during return to vendor entry [^r1].

## See also
* [[pol-ret-006|POL-RET-006 Returns Policy]]
* [[sop-inv-002|SOP-INV-002 Returns to Vendor (RTV)]]
* [[screen-inv-rtv-07|INV-RTV-07 Return To Vendor Entry]]
* [[screen-ap-dbn-04|AP-DBN-04 Debit Note Entry]]

## References

[^r1]: 01_policies/POL-RET-006 Returns Policy v2.1.pdf, p. 2, §2. Returns to suppliers
[^r3]: 02_procedures/SOP-INV-002 Returns to Vendor (RTV) v1.3.pdf, p. 4, What to do when something does not look right
[^r2]: 01_policies/POL-RET-006 Returns Policy v2.1.pdf, p. 2, §2. Returns to suppliers
[^r4]: 02_procedures/SOP-INV-002 Returns to Vendor (RTV) v1.3.pdf, p. 4, What to do when something does not look right
