---
title: "ERR-EDI error codes"
type: "error-list"
slug: "errors-edi"
summary: "Reference list of Ledgerline ERR-EDI electronic data interchange error codes for sales messaging, interface processing, and syntax diagnostics."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "04_service_definitions/sales/edi_desadv_out.xml", "04_service_definitions/sales/edi_err_list.xml", "04_service_definitions/sales/edi_invoic_out.xml", "04_service_definitions/sales/edi_ord_ack.xml", "04_service_definitions/sales/edi_ord_in.xml", "12_integrations/EDI ORDERS interface spec v2.1.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-EDI |
| Module | Sales (EDI) |
| System | Ledgerline ERP |
| Status | Current |

This page catalogues the `ERR-EDI` error codes raised across Ledgerline electronic data interchange routines in the sales module. These messages handle network mailbox transmission errors, partner trading status verification, buyer item mapping discrepancies, and segment syntax parsing. Operational staff monitor and resolve these conditions when importing customer orders or dispatching outbound EDI acknowledgements and invoices.

### ERR-EDI-0001

* **Message:** EDI MESSAGES NOT FOUND [^r5][^r6][^r7][^r8][^r9]
* **Cause:** The system experiences a general communication failure connecting to the network or remote directory, or encounters an incoming mailbox transmission file that is incomplete or malformed [^r1]. It is also returned when expected EDI message batches are not found [^r5][^r6][^r7][^r8][^r9].
* **Remedy:** Check the remote directory connection, confirm mailbox availability, and verify that incoming transmission files are fully received and correctly formed [^r1].
* **Raised by:** Services `edi_desadv_out` [^r5], `edi_err_list` [^r6], `edi_invoic_out` [^r7], `edi_ord_ack` [^r8], and `edi_ord_in` [^r9]; see [[services-sal-edi|SAL edi services]]. Described in [[man-sal-72|MAN-SAL-72]] [^r1].

### ERR-EDI-0101

* **Message:** PARTNER NOT SET UP [^r10]
* **Cause:** The partner profile is not found or is inactive because the incoming EDI transmission sender trading partner identifier (`PARTNER`) contains an unrecognised account reference, is not linked to an active sales ledger account, or electronic trading is suspended [^r2][^r13].
* **Remedy:** Configure or activate the partner profile, ensure the sender trading partner identifier is mapped to an active sales ledger account, and verify that electronic trading is not suspended [^r2][^r13].
* **Raised by:** Service `edi_ord_in` [^r10]. Documented in [[INT-EDI-001|INT-EDI-001]] [^r13] and [[man-sal-72|MAN-SAL-72]] [^r2].
* **Detailed page:** [[err-edi-0101|ERR-EDI-0101 Partner Not Set Up]].

### ERR-EDI-0140

* **Message:** UNKNOWN BUYER ITEM CODE [^r11]
* **Cause:** In incoming order processing, an order line contains an unknown buyer item code that is not mapped in the customer cross-reference table [^r11][^r14]. [[man-sal-72|MAN-SAL-72]] also attributes this code to general message syntax, mapping errors caused by corrupted records or invalid segment tags, or customer accounts missing electronic trade parameters [^r3].
* **Remedy:** Set up the item mapping in the customer cross-reference table [^r14], validate account trade parameters, and inspect the incoming message records for corrupted data or invalid segment tags [^r3].
* **Raised by:** Service `edi_ord_in` [^r11]. Documented in [[INT-EDI-001|INT-EDI-001]] [^r14] and [[man-sal-72|MAN-SAL-72]] [^r3].
* **Detailed page:** [[err-edi-0140|ERR-EDI-0140 Unknown Buyer Item Code]].

### ERR-EDI-0150

* **Message:** SYNTAX ERROR IN SEGMENT (<segment>) [^r12]
* **Cause:** The inbound processor encounters a syntax error within the specified segment during parsing by `edi_ord_in` [^r12]. [[man-sal-72|MAN-SAL-72]] also documents this code as halting outbound document generation due to unapproved pricing lines, missing sales ledger data like delivery addresses, or failed network handshaking [^r4].
* **Remedy:** Correct the segment syntax formatting in the incoming file [^r12], or verify delivery addresses, line pricing approvals, and network handshaking parameters for outbound documents [^r4].
* **Raised by:** Service `edi_ord_in` [^r12]. Described in [[man-sal-72|MAN-SAL-72]] [^r4].

## Versions and conflicts

* **ERR-EDI-0140 definition:** In service definitions and integration specifications, ERR-EDI-0140 strictly represents 'UNKNOWN BUYER ITEM CODE' for unmapped cross-reference items (`edi_ord_in.xml`, INT-EDI-001 v2.1, 2022-05-01) [^r11][^r14]. [[man-sal-72|MAN-SAL-72]] (v7.2.3, 2025-01-15) defines it more broadly as a syntax or mapping error arising from corrupted records, invalid tags, or missing customer trade parameters [^r3]. Kind: `contradiction`.
* **ERR-EDI-0150 definition:** Service definitions record ERR-EDI-0150 specifically as 'SYNTAX ERROR IN SEGMENT (<segment>)' raised by `edi_ord_in` [^r12]. [[man-sal-72|MAN-SAL-72]] (v7.2.3, 2025-01-15) describes ERR-EDI-0150 as an outbound document halt caused by missing ledger delivery addresses, unapproved pricing, or failed network handshaking [^r4]. Kind: `contradiction`.

## See also

* [[err-edi-0101|ERR-EDI-0101 Partner Not Set Up]]
* [[err-edi-0140|ERR-EDI-0140 Unknown Buyer Item Code]]
* [[services-sal-edi|SAL edi services]]
* [[screen-sal-edi-13|SAL-EDI-13 Edi Messages Ord In]]
* [[sop-sal-001|SOP-SAL-001 Sales Order to Despatch]]
* [[man-sal-72|MAN-SAL-72 Ledgerline ERP 7.2 User Manual: Sales and Distribution]]

## References

[^r5]: 04_service_definitions/sales/edi_desadv_out.xml, ll:errors
[^r6]: 04_service_definitions/sales/edi_err_list.xml, ll:errors
[^r7]: 04_service_definitions/sales/edi_invoic_out.xml, ll:errors
[^r8]: 04_service_definitions/sales/edi_ord_ack.xml, ll:errors
[^r9]: 04_service_definitions/sales/edi_ord_in.xml, ll:errors
[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 54, Messages
[^r10]: 04_service_definitions/sales/edi_ord_in.xml, ll:errors
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 54, Messages
[^r13]: 12_integrations/EDI ORDERS interface spec v2.1.pdf, p. 3, §4. Errors
[^r11]: 04_service_definitions/sales/edi_ord_in.xml, ll:errors
[^r14]: 12_integrations/EDI ORDERS interface spec v2.1.pdf, p. 3, §4. Errors
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 54, Messages
[^r12]: 04_service_definitions/sales/edi_ord_in.xml, ll:errors
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 54, Messages
