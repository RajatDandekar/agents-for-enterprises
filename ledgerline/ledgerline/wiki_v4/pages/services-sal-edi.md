---
title: "SAL edi services"
type: "service-group"
slug: "services-sal-edi"
summary: "Ledgerline SAL module EDI messaging services handling electronic orders, order acknowledgements, despatch advice, invoices, and transmission error listings via compatibility endpoints."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/sales/edi_desadv_out.xml", "04_service_definitions/sales/edi_err_list.xml", "04_service_definitions/sales/edi_invoic_out.xml", "04_service_definitions/sales/edi_ord_ack.xml", "04_service_definitions/sales/edi_ord_in.xml", "12_integrations/EDI ORDERS interface spec v2.1.pdf", "12_integrations/wsdl/LedgerlineGateway.wsdl"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | SAL |
| Object | edi |
| Screen | [[screen-sal-edi-13|SAL-EDI-13]] |
| Transport | SOAP gateway (compatibility port 8091) |
| Owner | IT ([[user-jfletcher|JFLETCHER]]) |
| Status | Current |

The `sal-edi` service group provides electronic data interchange (EDI) message processing for the sales module on screen [[screen-sal-edi-13|SAL-EDI-13]][^r2][^r8]. It consists of five services originally deployed as Ledgerline 6.2 SOAP gateway services and hosted in Ledgerline 7.2 on endpoint `http://ll72-app01:8091/ws/sal/<service>` via a compatibility listener on port 8091[^r15][^r21][^r23][^r24][^r25][^r30][^r35][^r41]. Ownership of the definitions transferred to IT under [[user-jfletcher|Joanna Fletcher]] following the departure of [[user-dramsden|Derek Ramsden]] in 2012[^r23].

| Field | Value |
|---|---|
| Module | SAL |
| Object | edi |
| Associated Screen | [[screen-sal-edi-13|SAL-EDI-13]] |
| Endpoint Base | `http://ll72-app01:8091/ws/sal/` |
| Transport | SOAP (port 8091 compatibility listener) |
| Current Owner | [[user-jfletcher|Joanna Fletcher (JFLETCHER)]] |

## Services

### edi_ord_in
The `edi_ord_in` write service imports inbound electronic orders from the mailbox and allocates internal sales references on screen [[screen-sal-edi-13|SAL-EDI-13]][^r2][^r3][^r9][^r34]. Scheduled job `JOB-SAL-010` queries the EDI mailbox every 10 minutes and invokes `edi_ord_in` for each incoming EDIFACT ORDERS transmission[^r38]. The service unpacks message envelopes, validates trading partner codes against sales ledger accounts, translates buyer part codes, and enters unconfirmed sales orders using stored procedure `sp_edi_ord_in`[^r9][^r39].

* **Kind:** Write service[^r9][^r34]
* **Endpoint:** `http://ll72-app01:8091/ws/sal/edi_ord_in`[^r35]
* **Stored procedure:** `sp_edi_ord_in`[^r9]
* **Required fields:** `msg_id`[^r9][^r36]
* **Optional fields:** `comment`[^r9][^r36]
* **Errors:** `ERR-EDI-0001` (EDI message not found), [[err-edi-0101|ERR-EDI-0101]] (Partner not set up), [[err-edi-0140|ERR-EDI-0140]] (Unknown buyer item code), and `ERR-EDI-0150` (Syntax error in segment)[^r1][^r9][^r37]
* **Source file:** `04_service_definitions/sales/edi_ord_in.xml`[^r34][^r35]

### edi_ord_ack
The `edi_ord_ack` write service generates electronic order acknowledgement structures using accepted sales order lines on screen [[screen-sal-edi-13|SAL-EDI-13]][^r2][^r4][^r10][^r29]. It runs stored procedure `sp_edi_ord_ack` and returns execution status strings[^r10][^r32].

* **Kind:** Write service[^r10][^r29]
* **Endpoint:** `http://ll72-app01:8091/ws/sal/edi_ord_ack`[^r30]
* **Stored procedure:** `sp_edi_ord_ack`[^r10]
* **Required fields:** `msg_id`[^r10][^r31]
* **Optional fields:** `comment`[^r10][^r31]
* **Response fields:** `rc`, `msg`, optional `err_cd`, and optional `data`[^r32]
* **Errors:** `ERR-EDI-0001` (EDI message not found)[^r10][^r33]
* **Source file:** `04_service_definitions/sales/edi_ord_ack.xml`[^r29][^r30]

### edi_desadv_out
The `edi_desadv_out` write service formats and transmits standardised electronic despatch advice messages from completed warehouse despatch records on screen [[screen-sal-edi-13|SAL-EDI-13]][^r2][^r5][^r11][^r14]. Processing is executed via database procedure `sp_edi_desadv_out`[^r11].

* **Kind:** Write service[^r11][^r14]
* **Endpoint:** `http://ll72-app01:8091/ws/sal/edi_desadv_out`[^r15]
* **Stored procedure:** `sp_edi_desadv_out`[^r11]
* **Required fields:** `msg_id`[^r11][^r16]
* **Optional fields:** `comment`[^r16]
* **Errors:** `ERR-EDI-0001` (EDI message not found)[^r11][^r17]
* **Source file:** `04_service_definitions/sales/edi_desadv_out.xml`[^r14][^r15]

### edi_invoic_out
The `edi_invoic_out` write service exports electronic outbound invoices on screen [[screen-sal-edi-13|SAL-EDI-13]] using billing run net amounts, tax totals, and currency codes via stored procedure `sp_edi_invoic_out`[^r2][^r6][^r12][^r24].

* **Kind:** Write service[^r12][^r24]
* **Endpoint:** `http://ll72-app01:8091/ws/sal/edi_invoic_out`[^r24]
* **Stored procedure:** `sp_edi_invoic_out`[^r12]
* **Required fields:** `msg_id`[^r12][^r26]
* **Optional fields:** `comment`[^r12][^r26]
* **Response fields:** `rc`, `msg`, optional `err_cd`, and optional `data`[^r27]
* **Errors:** `ERR-EDI-0001` (EDI message not found)[^r12][^r28]
* **Source file:** `04_service_definitions/sales/edi_invoic_out.xml`[^r24][^r25]

### edi_err_list
The `edi_err_list` read service queries the transmission message log to display failing message IDs, trading partner codes, and diagnostic explanations on screen [[screen-sal-edi-13|SAL-EDI-13]][^r2][^r7][^r13][^r18]. The sales team uses this service to identify and remediate refused incoming transmissions on the day of receipt[^r40].

* **Kind:** Read service[^r13][^r18]
* **Endpoint:** `http://ll72-app01:8091/ws/sal/edi_err_list`[^r21]
* **Required fields:** None[^r13][^r19]
* **Optional fields:** `partner_cd`[^r13][^r19]
* **Response fields:** `rc`, `msg`, optional `err_cd`, and optional `data`[^r20]
* **Errors:** `ERR-EDI-0001` (EDI messages not found)[^r13][^r22]
* **Source file:** `04_service_definitions/sales/edi_err_list.xml`[^r18][^r21]

## See also
* [[screen-sal-edi-13|SAL-EDI-13 Edi Messages Ord In]]
* [[errors-edi|ERR-EDI error codes]]
* [[err-edi-0101|ERR-EDI-0101 Partner Not Set Up]]
* [[err-edi-0140|ERR-EDI-0140 Unknown Buyer Item Code]]
* [[services-sal-so|SAL so services]]
* [[services-sal-sinv|SAL sinv services]]
* [[user-jfletcher|Joanna Fletcher (JFLETCHER)]]

## References

[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 51, §16. Edi Messages (SAL-EDI-13)
[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 35, SAL-EDI-13 EDI MESSAGES ORD IN
[^r15]: 04_service_definitions/sales/edi_desadv_out.xml, Comment
[^r21]: 04_service_definitions/sales/edi_err_list.xml, wsdl:service
[^r23]: 04_service_definitions/sales/edi_err_list.xml, Comments
[^r24]: 04_service_definitions/sales/edi_invoic_out.xml, wsdl:documentation
[^r25]: 04_service_definitions/sales/edi_invoic_out.xml, Header comment
[^r30]: 04_service_definitions/sales/edi_ord_ack.xml, definitions comment
[^r35]: 04_service_definitions/sales/edi_ord_in.xml, comment
[^r41]: 12_integrations/wsdl/LedgerlineGateway.wsdl, GatewayPort
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 52, Processing inbound purchase orders
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 49, edi_ord_in EDI MESSAGES ORD IN
[^r34]: 04_service_definitions/sales/edi_ord_in.xml, wsdl:documentation
[^r38]: 12_integrations/EDI ORDERS interface spec v2.1.pdf, p. 2, §2. Message flow
[^r39]: 12_integrations/EDI ORDERS interface spec v2.1.pdf, p. 2, §2. Message flow
[^r36]: 04_service_definitions/sales/edi_ord_in.xml, wsdl:types
[^r1]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 9
[^r37]: 04_service_definitions/sales/edi_ord_in.xml, ll:errors
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 53, Transmitting order acknowledgements
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 49, edi_ord_ack EDI MESSAGES ORD ACK
[^r29]: 04_service_definitions/sales/edi_ord_ack.xml, wsdl:documentation
[^r32]: 04_service_definitions/sales/edi_ord_ack.xml, edi_ord_ackResponse
[^r31]: 04_service_definitions/sales/edi_ord_ack.xml, edi_ord_ackRequest
[^r33]: 04_service_definitions/sales/edi_ord_ack.xml, ll:errors
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 53, Generating outbound despatch advice notices
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 50, edi_desadv_out EDI MESSAGES DESADV OUT
[^r14]: 04_service_definitions/sales/edi_desadv_out.xml, wsdl:documentation
[^r16]: 04_service_definitions/sales/edi_desadv_out.xml, edi_desadv_outRequest
[^r17]: 04_service_definitions/sales/edi_desadv_out.xml, ll:errors
[^r6]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 53, Transmitting outbound sales invoices
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 50, edi_invoic_out EDI MESSAGES INVOIC OUT
[^r26]: 04_service_definitions/sales/edi_invoic_out.xml, xs:element name="edi_invoic_outRequest"
[^r27]: 04_service_definitions/sales/edi_invoic_out.xml, xs:element name="edi_invoic_outResponse"
[^r28]: 04_service_definitions/sales/edi_invoic_out.xml, ll:errors
[^r7]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 53, Reviewing transmission faults
[^r13]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 50, edi_err_list EDI MESSAGES ERR LIST
[^r18]: 04_service_definitions/sales/edi_err_list.xml, wsdl:documentation
[^r40]: 12_integrations/EDI ORDERS interface spec v2.1.pdf, p. 3, §4. Errors
[^r19]: 04_service_definitions/sales/edi_err_list.xml, wsdl:types / edi_err_listRequest
[^r20]: 04_service_definitions/sales/edi_err_list.xml, wsdl:types / edi_err_listResponse
[^r22]: 04_service_definitions/sales/edi_err_list.xml, ll:errors
