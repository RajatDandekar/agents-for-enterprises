---
title: "Screen PO-ENT Vendor Order Entry (Ledgerline 6)"
type: "screen"
slug: "screen-po-ent"
summary: "Legacy Ledgerline 6 vendor order entry screen supporting up to 40 lines per order, replaced in modern Ledgerline versions."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/old/LL6_purchasing_quickguide.docx", "99_scans/2004_LL6_manual_page_37_scan.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | PO-ENT |
| Module | Purchasing |
| System | Ledgerline 6 |
| Status | Superseded |
| Function | Vendor order entry |
| Max lines | 40 |

Screen PO-ENT is the legacy vendor order entry screen from Ledgerline 6 [^r1]. It allowed users to raise vendor purchase orders with a capacity of up to 40 lines before posting [^r2]. In modern operations as of Monday 26 October 2026, the screen is superseded by current purchasing interfaces documented in [[man-pur-70|MAN-PUR-70 Ledgerline ERP 7.0 User Manual: Purchasing]] [^r4].

## Fields
* **Vendor number**: Entered to identify the supplier, with supplier ledger details populated upon lookup or saving [^r1][^r4].
* **Item, quantity, and price**: Line details entered per item, supporting up to 40 lines per order [^r2][^r4].
* **Delivery address**: Required manual review to specify delivery to assembly lines in Manchester or stores in Leeds [^r5].

## Keys and services
* **F4**: Pressed to retrieve vendor details after entering the vendor number [^r1].
* **F10**: Pressed to post the order [^r3].
* **Save**: Populated supplier ledger details and generated an internal document for authorisation [^r4].

## Messages
Posting the order via F10 triggered an immediate printout of the posted order [^r3].

## Versions and conflicts
* **Today's status**: Current purchasing workflows operate under updated systems such as Ledgerline 7.0 ([[man-pur-70]]), whereas Ledgerline 6 materials are obsolete [^r4].
* **Legacy rule**: Screen PO-ENT in Ledgerline 6 managed direct entry of vendor orders up to 40 lines, generated internal documents for authorisation upon saving, and printed posted orders immediately upon pressing F10 [^r1][^r2][^r3][^r4].
* **Sources and kind**: `99_scans/2004_LL6_manual_page_37_scan.pdf` (current scan of historical system) and `03_ledgerline_manuals/old/LL6_purchasing_quickguide.docx` (superseded); kind: `superseded`.

## See also
* [[man-pur-70|MAN-PUR-70 Ledgerline ERP 7.0 User Manual: Purchasing]]
* [[rn-ll6-history|Ledgerline 6 release history 2004-2012]]

## References

[^r1]: 99_scans/2004_LL6_manual_page_37_scan.pdf, p. 1, §6.4 Vendor order entry (screen PO-ENT)
[^r2]: 99_scans/2004_LL6_manual_page_37_scan.pdf, p. 1, §6.4 Vendor order entry (screen PO-ENT)
[^r4]: 03_ledgerline_manuals/old/LL6_purchasing_quickguide.docx, Raising a vendor order
[^r5]: 03_ledgerline_manuals/old/LL6_purchasing_quickguide.docx, Practical tips
[^r3]: 99_scans/2004_LL6_manual_page_37_scan.pdf, p. 1, §6.4 Vendor order entry (screen PO-ENT)
