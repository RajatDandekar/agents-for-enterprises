---
title: "INT-EDI-001 EDI ORDERS Interface Specification"
type: "procedure"
slug: "int-edi-001"
summary: "Technical and operational specification for receiving customer EDIFACT ORDERS into the sales ledger via service edi_ord_in."
audience: "staff"
status: "current"
sources: ["12_integrations/EDI ORDERS interface spec v2.1.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | INT-EDI-001 |
| Owner | J. Fletcher |
| Version | 2.1 |
| Effective date | 2022-05-01 |
| Status | current |

INT-EDI-001 defines the technical and operational interface specification for receiving electronic purchase orders from independent bike shops and multi-branch retailers into the sales ledger[^r1]. It processes EDIFACT ORDERS messages on a 10-minute cycle via scheduled background processing[^r4]. Validation enforces strict batch integrity, halting the full transmission whenever an item reference or carton quantity fails[^r3].

## Steps

Retailers transmit EDIFACT ORDERS messages directly to the EDI mailbox[^r4]. Background job JOB-SAL-010 executes every 10 minutes to ingest these messages and invokes [[services-sal-edi|service edi_ord_in]] for each individual order[^r4].

The ingestion mapping processes mandatory and optional segments into Ledgerline sales ledger records[^r5]:
* Message header and trailer: `UNH` maps to `msg_id`, and `UNT` closes the segment set[^r5].
* Order attributes: `BGM` maps to customer reference `cust_ref`, and `DTM` maps to requested delivery date `req_dt`[^r5].
* Customer identification: `NAD+BY` identifies the buyer and resolves to internal customer code `cust_cd` using the partner translation table[^r5].
* Line details: `LIN` maps to item code `itm_cd`, and `QTY+21` supplies the order quantity `qty`[^r5].
* Pricing: Segment `PRI` is optional and ignored by the ingestion routine, which prices orders against the active Ledgerline price list instead[^r5].

If validation encounters an unrecognised or unconfigured partner identifier, the transmission is refused with error [[err-edi-0101|ERR-EDI-0101]][^r6]. If a line contains an unmapped or unknown buyer item code, the system halts processing and rejects the order with [[err-edi-0140|ERR-EDI-0140]][^r6]. The interface halts the entire batch upon validation failure of an item reference or carton quantity rather than dropping invalid lines automatically[^r3].

Refused messages are logged for operational review and can be listed via service `edi_err_list`[^r7]. The sales team must clear all listed exceptions on the same day[^r7].

To prevent ingestion failures, every retailer partner configuration requires three primary associations: a unique customer account reference, a translation table mapping retailer part numbers to finished bicycle lines, and a default delivery depot assignment[^r8].

## Forms and screens

* EDI mailbox and background job JOB-SAL-010 for transmission capture[^r4].
* Ingestion service `edi_ord_in` and exception reporting service `edi_err_list` under [[services-sal-edi]][^r4][^r7].
* Ledgerline partner set-up tables for account matching, depot assignment, and item translation cross-references[^r5][^r8].

## See also

* [[err-edi-0101|ERR-EDI-0101 Partner Not Set Up]]
* [[err-edi-0140|ERR-EDI-0140 Unknown Buyer Item Code]]
* [[errors-edi|ERR-EDI error codes]]
* [[services-sal-edi|SAL edi services]]

## References

[^r1]: 12_integrations/EDI ORDERS interface spec v2.1.pdf, p. 1, §1. Purpose
[^r4]: 12_integrations/EDI ORDERS interface spec v2.1.pdf, p. 2, §2. Message flow
[^r3]: 12_integrations/EDI ORDERS interface spec v2.1.pdf, p. 1, §1. Purpose
[^r5]: 12_integrations/EDI ORDERS interface spec v2.1.pdf, p. 3, §3. Segments used
[^r6]: 12_integrations/EDI ORDERS interface spec v2.1.pdf, p. 3, §4. Errors
[^r7]: 12_integrations/EDI ORDERS interface spec v2.1.pdf, p. 3, §4. Errors
[^r8]: 12_integrations/EDI ORDERS interface spec v2.1.pdf, p. 4, §5. Partner set-up
