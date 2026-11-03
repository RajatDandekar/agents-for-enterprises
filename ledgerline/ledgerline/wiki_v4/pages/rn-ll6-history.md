---
title: "Ledgerline 6 release history 2004-2012"
type: "release"
slug: "rn-ll6-history"
summary: "Release history of legacy ERP Ledgerline 6 from 2004 to 2012, covering versions 6.0 through 6.4.5 prior to Ledgerline 7 migration."
audience: "staff"
status: "current"
sources: ["04_service_definitions/_legacy_6x/PO_ENTRY_SAVE.xml", "04_service_definitions/_legacy_6x/REQ_ENTRY.xml", "04_service_definitions/_legacy_6x/VENDOR_ADD.xml", "08_release_notes/LL6_release_history_2004-2012.txt", "09_email_archive/2015/2015-02-16_Moving to Ledgerline 7.eml", "99_scans/2004_LL6_manual_page_37_scan.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| system | Ledgerline 6 (LL6) |
| series | 6.x |
| period | March 2004 – June 2012 |
| final release | 6.4.5 |
| status | superseded |
| superseded by | Ledgerline 7.0 (February 2015) |

This page documents the release history and architecture of the legacy Ledgerline 6 ERP platform used at Northbridge Cycles between March 2004 and February 2015 [^r4][^r14]. Ledgerline 6 provided the core transaction environment for requisitions, vendor orders, store inventory, EDI retail order integration, and tax updates across its 6.0 through 6.4.5 lifecycle [^r4][^r5][^r7][^r9][^r10]. The entire 6.x platform is fully superseded and locked to read-only following the migration to Ledgerline 7.0, but remains relevant for historical reference and audit reconciliations [^r1][^r2][^r3][^r14].

## Changes

* **Ledgerline 6.0 (March 2004):** Replaced version 5.3 and introduced core modules for vendor orders, requisitions, and stores management [^r4]. Vendor order entry operated through [[screen-po-ent|screen PO-ENT]], where operators keyed the vendor number, pressed F4 for vendor details, entered up to 40 line items with quantity and price, and pressed F10 to post and immediately print the order [^r11][^r12][^r13].
* **Ledgerline 6.1 (October 2005):** Introduced EDI ORDERS capability for retailer order processing [^r5].
* **Ledgerline 6.2 (February 2007):** Added a SOAP gateway interface to support external bank and freight carrier connections [^r6].
* **Ledgerline 6.3 (November 2008):** Configured the temporary UK VAT reduction to 15% using tax code V15-UK under [[data-tax-codes|tax codes]], effective 1 December 2008 [^r7].
* **Ledgerline 6.3.2 (January 2010):** Restored the UK VAT standard rate to 17.5%, effective 1 January 2010 [^r8].
* **Ledgerline 6.4 (January 2011):** Implemented the 20% UK VAT rate under tax code VAT20-UK from 4 January 2011 [^r9]. Defined remote procedure call definitions under the LL6-RPC transport, including PO_ENTRY_SAVE, [[services-pur-req|REQ_ENTRY]], and [[services-sup-vendor|VENDOR_ADD]] [^r1][^r2][^r3].
* **Ledgerline 6.4.5 (June 2012):** Deployed as the final maintenance and service release of the Ledgerline 6.x platform [^r10].

## Effect at Northbridge

The Ledgerline 6 series provided Northbridge Cycles' transaction backbone for eleven years [^r4][^r14]. In February 2015, Northbridge Cycles initiated [[decision-2015-02-16-ledgerline-7-migration|cutover planning]] to transition from version 6.4.5 to Ledgerline 7.0, locking the legacy ledger system to read-only status [^r10][^r14]. The legacy LL6-RPC services PO_ENTRY_SAVE, REQ_ENTRY, and VENDOR_ADD were retired and superseded by Ledgerline 7 [[services-pur-po|PUR po services]], requisition services, and vendor master services, with legacy service definitions retained solely for reference [^r1][^r2][^r3].

## Versions and conflicts

* **Superseded platform:** Today, purchasing and order entry operate on Ledgerline 7 [[services-pur-po|services]] [^r1]. Historically, under Ledgerline 6.4, purchasing order transactions ran via the legacy LL6-RPC service definition PO_ENTRY_SAVE, REQ_ENTRY, and VENDOR_ADD, which were superseded upon the release of Ledgerline 7.0 in 2015 when the legacy ledger was locked to read-only [^r1][^r2][^r3][^r14].

## See also

* [[screen-po-ent]]
* [[services-pur-po]]
* [[services-pur-req]]
* [[services-sup-vendor]]
* [[data-tax-codes]]
* [[decision-2015-02-16-ledgerline-7-migration]]

## References

[^r4]: 08_release_notes/LL6_release_history_2004-2012.txt, LEDGERLINE 6 RELEASE HISTORY (COPIED FROM THE OLD INTRANET)
[^r14]: 09_email_archive/2015/2015-02-16_Moving to Ledgerline 7.eml, Moving to Ledgerline 7
[^r5]: 08_release_notes/LL6_release_history_2004-2012.txt, LEDGERLINE 6 RELEASE HISTORY (COPIED FROM THE OLD INTRANET)
[^r7]: 08_release_notes/LL6_release_history_2004-2012.txt, LEDGERLINE 6 RELEASE HISTORY (COPIED FROM THE OLD INTRANET)
[^r9]: 08_release_notes/LL6_release_history_2004-2012.txt, LEDGERLINE 6 RELEASE HISTORY (COPIED FROM THE OLD INTRANET)
[^r10]: 08_release_notes/LL6_release_history_2004-2012.txt, LEDGERLINE 6 RELEASE HISTORY (COPIED FROM THE OLD INTRANET)
[^r1]: 04_service_definitions/_legacy_6x/PO_ENTRY_SAVE.xml, rpc
[^r2]: 04_service_definitions/_legacy_6x/REQ_ENTRY.xml, whole file
[^r3]: 04_service_definitions/_legacy_6x/VENDOR_ADD.xml, whole file
[^r11]: 99_scans/2004_LL6_manual_page_37_scan.pdf, p. 1, §6.4 Vendor order entry (screen PO-ENT)
[^r12]: 99_scans/2004_LL6_manual_page_37_scan.pdf, p. 1, §6.4 Vendor order entry (screen PO-ENT)
[^r13]: 99_scans/2004_LL6_manual_page_37_scan.pdf, p. 1, §6.4 Vendor order entry (screen PO-ENT)
[^r6]: 08_release_notes/LL6_release_history_2004-2012.txt, LEDGERLINE 6 RELEASE HISTORY (COPIED FROM THE OLD INTRANET)
[^r8]: 08_release_notes/LL6_release_history_2004-2012.txt, LEDGERLINE 6 RELEASE HISTORY (COPIED FROM THE OLD INTRANET)
