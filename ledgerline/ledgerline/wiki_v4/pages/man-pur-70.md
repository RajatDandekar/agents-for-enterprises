---
title: "MAN-PUR-70 Ledgerline ERP 7.0 User Manual: Purchasing"
type: "manual"
slug: "man-pur-70"
summary: "Superseded user manual for Ledgerline ERP 7.0 purchasing procedures across Manchester and Leeds, replaced by MAN-PUR-72."
audience: "staff"
status: "superseded"
sources: ["03_ledgerline_manuals/old/LL6_purchasing_quickguide.docx", "03_ledgerline_manuals/old/Ledgerline 7.0 Purchasing Manual (2015).pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Document code | MAN-PUR-70 |
| Version | 7.0 |
| Effective date | 2015-03-02 |
| Status | Superseded |
| Replaced by | MAN-PUR-72 |
| Scope | Manchester works and Leeds unit |

`MAN-PUR-70` is the superseded user manual for purchasing in Ledgerline ERP 7.0, originally effective 2015-03-02 [^r4]. It governed standard purchasing procedures across the Manchester works and Leeds unit until it was replaced by [[man-pur-72|MAN-PUR-72]] [^r4]. The manual is retained for historical audit reference regarding legacy order entry behaviours and role-based approval limits [^r5][^r8].

## Overview and processes

The manual defines the standard purchasing workflow across the Manchester works and Leeds unit [^r4]. During purchase order entry, the fetch operation was optional, permitting operators to manually input the rate, tax code, and payment terms [^r5]. Once raised, unauthorized purchase orders remained visible within the system, though they could not be received at goods inwards bays [^r6].

Order validation evaluated gross financial thresholds: purchase order approval limits assessed the gross order value in pounds, incorporating carriage charges and standard taxes [^r7][^r9]. Furthermore, approval limits were configured against each role rather than against individual user logins [^r8].

## Messages

The manual details operational system diagnostics, including:

* [[err-po-0412|ERR-PO-0412]]: Indicates that the tax code's region does not match the supplier's state, requiring the operator to alter the tax code [^r7].

A full catalogue of related purchasing errors is maintained under [[errors-po|ERR-PO Error Codes]] [^r7].

## Versions and conflicts

* **Current status vs legacy ERP 7.0**: Current purchasing procedures are governed by [[man-pur-72|MAN-PUR-72]], which supersedes `MAN-PUR-70` (effective 2015-03-02) [^r4]. Under `MAN-PUR-70`, fetch was optional at order entry, allowing manual entry of rates, tax codes, and payment terms [^r5], and approval limits were assigned by role over gross values including carriage and tax [^r8][^r9].
* **Ledgerline 6 legacy procedure**: Prior to `MAN-PUR-70`, the superseded Ledgerline 6 Purchasing Quick Guide version 6.4 took effect on 2009-05-01 under owner [[user-dramsden|Derek Ramsden (IT)]] with status SUPERSEDED [^r3]. In Ledgerline 6, vendor orders were accessed via Purchasing > Vendor Orders > New on [[screen-po-ent|screen PO-ENT]], where exiting the screen without pressing Save discarded line entries without warning and left orders unposted [^r1][^r2].

## See also

* [[man-pur-72|MAN-PUR-72 Ledgerline ERP 7.2 User Manual, Purchasing]]
* [[screen-po-ent|Screen PO-ENT Vendor Order Entry (Ledgerline 6)]]
* [[err-po-0412|ERR-PO-0412 TAX CODE DOES NOT MATCH SUPPLIER COUNTRY]]
* [[errors-po|ERR-PO Error Codes]]
* [[user-dramsden|Derek Ramsden (DRAMSDEN)]]
* [[data-tax-codes|Tax codes]]

## References

[^r4]: 03_ledgerline_manuals/old/Ledgerline 7.0 Purchasing Manual (2015).pdf, p. 1, §1. About this manual
[^r5]: 03_ledgerline_manuals/old/Ledgerline 7.0 Purchasing Manual (2015).pdf, p. 2, §11. Purchase order entry
[^r8]: 03_ledgerline_manuals/old/Ledgerline 7.0 Purchasing Manual (2015).pdf, p. 4, §23. Approval limits
[^r6]: 03_ledgerline_manuals/old/Ledgerline 7.0 Purchasing Manual (2015).pdf, p. 2, §11. Purchase order entry
[^r7]: 03_ledgerline_manuals/old/Ledgerline 7.0 Purchasing Manual (2015).pdf, p. 3, §17. Messages
[^r9]: 03_ledgerline_manuals/old/Ledgerline 7.0 Purchasing Manual (2015).pdf, p. 4, §23. Approval limits
[^r3]: 03_ledgerline_manuals/old/LL6_purchasing_quickguide.docx, Practical advice
[^r1]: 03_ledgerline_manuals/old/LL6_purchasing_quickguide.docx, Raising a vendor order
[^r2]: 03_ledgerline_manuals/old/LL6_purchasing_quickguide.docx, Common errors to avoid
