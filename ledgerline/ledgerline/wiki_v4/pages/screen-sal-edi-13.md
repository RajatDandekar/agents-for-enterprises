---
title: "SAL-EDI-13 Edi Messages Ord In"
type: "screen"
slug: "screen-sal-edi-13"
summary: "Ledgerline screen for managing inbound EDI customer purchase orders, outbound order acknowledgements, despatches, invoices, and transmission error tracking."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/sales/edi_desadv_out.xml", "04_service_definitions/sales/edi_err_list.xml", "04_service_definitions/sales/edi_invoic_out.xml", "04_service_definitions/sales/edi_ord_ack.xml", "04_service_definitions/sales/edi_ord_in.xml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen | SAL-EDI-13 |
| Title | Edi Messages Ord In |
| Menu path | Sales > Edi messages |
| Authorized roles | SAL-EXEC, SAL-MGR, SYS-ADMIN |
| Primary services | edi_ord_in, edi_ord_ack, edi_desadv_out, edi_invoic_out, edi_err_list |
| Mandatory fields | msg_id |

SAL-EDI-13 (Edi Messages Ord In) is the Ledgerline screen used to oversee and process inbound and outbound electronic data interchange (EDI) documents for sales operations [^r1][^r8]. It allows sales operators to translate incoming customer purchase orders, transmit electronic order acknowledgements, generate electronic despatch advices, and post outbound sales invoices [^r3][^r4][^r5][^r6]. The screen also provides tools for monitoring transmission logs and diagnosing EDI partner communications [^r7].

## Fields

Screen SAL-EDI-13 contains core header fields displayed alongside operational document processing buttons [^r2]:

* `msg_id` (MSG ID): Mandatory message identifier [^r1][^r8]. It displays failing message references during transmission review and updates upon processing incoming orders or generating outbound despatches [^r3][^r5][^r7].
* `partner_cd` (PARTNER): Optional external partner identifier used to identify or review customer codes [^r1][^r7][^r8].
* `comment` (COMMENT): Optional free-text and diagnostic area displaying internal status notes, transmission fault diagnostics, or automatic updates after document processing [^r1][^r3][^r5][^r7][^r8].

Access to screen SAL-EDI-13 is restricted to user roles SAL-EXEC, SAL-MGR, and SYS-ADMIN under the Sales > Edi messages navigation path [^r1][^r8].

## Keys and services

SAL-EDI-13 exposes five primary command buttons linked to underlying EDI services [^r9]:

* **Ord In** (`edi_ord_in`): Write service that queries the electronic mailbox, converts external customer order segments into internal sales records, and populates the MSG ID and COMMENT fields [^r3][^r9][^r14].
* **Ord Ack** (`edi_ord_ack`): Write service that acknowledges incoming EDI messages and creates outbound acknowledgements containing pricing, scheduled plant locations, and delivery commitments pulled directly from accepted sales order lines [^r4][^r9][^r13].
* **Desadv Out** (`edi_desadv_out`): Outbound despatch advice write service that bundles carrier details, parcel information, and delivery destinations into standard electronic despatch advice notices while refreshing MSG ID and COMMENT [^r5][^r9][^r10].
* **Invoic Out** (`edi_invoic_out`): Outbound invoice write service that pulls currency specifics, net amounts, and tax figures from finalized sales billing runs to produce electronic invoices [^r6][^r9][^r12].
* **Err List** (`edi_err_list`): Read-kind service that queries internal transmission logs, populating MSG ID with failing references, PARTNER with partner codes, and COMMENT with error diagnostics [^r7][^r9][^r11].

## Messages

The screen can raise the following system error codes [^r9]:

* ERR-EDI-0001: Raised by screen processing routines [^r9].
* [[err-edi-0101|ERR-EDI-0101]]: Partner Not Set Up [^r9].
* [[err-edi-0140|ERR-EDI-0140]]: Unknown Buyer Item Code [^r9].
* ERR-EDI-0150: Raised during EDI processing [^r9].

Detailed fault handling across messages is catalogued under [[errors-edi|ERR-EDI error codes]] [^r9].

## See also

* [[services-sal-edi|SAL edi services]]
* [[errors-edi|ERR-EDI error codes]]
* [[err-edi-0101|ERR-EDI-0101 Partner Not Set Up]]
* [[err-edi-0140|ERR-EDI-0140 Unknown Buyer Item Code]]
* [[screen-sal-so-01|SAL-SO-01 Sales Order]]
* [[screen-sal-dlv-05|SAL-DLV-05 Despatch Entry]]
* [[screen-sal-inv-06|SAL-INV-06 Sales Invoice Entry]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 51, §16. Edi Messages (SAL-EDI-13)
[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 35, SAL-EDI-13 EDI MESSAGES ORD IN
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 52, Processing inbound purchase orders
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 53, Transmitting order acknowledgements
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 53, Generating outbound despatch advice notices
[^r6]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 53, Transmitting outbound sales invoices
[^r7]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 53, Reviewing transmission faults
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 52, Step by step
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 35, SAL-EDI-13 EDI MESSAGES ORD IN
[^r14]: 04_service_definitions/sales/edi_ord_in.xml, wsdl:documentation
[^r13]: 04_service_definitions/sales/edi_ord_ack.xml, wsdl:documentation
[^r10]: 04_service_definitions/sales/edi_desadv_out.xml, wsdl:documentation
[^r12]: 04_service_definitions/sales/edi_invoic_out.xml, wsdl:documentation
[^r11]: 04_service_definitions/sales/edi_err_list.xml, wsdl:documentation
