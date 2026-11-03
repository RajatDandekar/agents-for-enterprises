---
title: "IT Steering Meeting - 11 March 2022"
type: "topic"
slug: "topic-it-steering-2022-03-11"
summary: "Minutes of the IT Steering Meeting on 11 March 2022 covering inter-site inventory sync, finance reconciliation, and warehouse network issues."
audience: "staff"
status: "current"
sources: ["10_meeting_notes/2022-03-11 IT steering.docx"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Meeting | IT Steering Meeting |
| Date | 2022-03-11 |
| Attendees | Isla Morgan, Pieter Jansen, Kwame Mensah, Callum Shaw, Aiko Tanaka |
| Status | historical |

The IT steering group convened on 11 March 2022 to review critical cross-site systems issues between the Manchester and Leeds facilities [^r1]. The meeting identified operational bottlenecks in inventory synchronisation, purchase order invoice matching, network terminal drops, and BOM engineering updates [^r2][^r4][^r8][^r9]. It provides historical context for IT operational fixes including batch rescheduling and nightly sync reviews [^r3][^r10].

| Attribute | Value |
|---|---|
| Meeting | IT Steering Meeting |
| Date | 2022-03-11 |
| Attendees | Isla Morgan, Pieter Jansen, Kwame Mensah, Callum Shaw, Aiko Tanaka |
| Status | historical |

## Operations and Inventory Synchronisation

Stock synchronisation difficulties persisted between the Manchester plant floor and the Leeds unit, resulting in material issue discrepancies against the ledger, manual stock counts, and phone calls to verify parts availability [^r2]. In response, the steering group planned an investigation into nightly processing routines across both sites to establish why inventory postings failed to capture physical floor movements [^r3].

## Finance and Invoicing

Delayed electronic confirmations on parts supplier purchase orders caused incoming invoices to build up in an accounts payable holding queue, requiring manual line-by-line reconciliation [^r4]. In addition, foreign currency conversions for imported electrical drive units required manual review against bank statements during month-end closing [^r5].

## Despatch, Sales, and Engineering

Despatch notes and carriage manifests occasionally printed without complete customer details, creating collection delays at the loading bay for independent bike shops [^r6]. Traveling sales representatives experienced a lack of visibility into parts awaiting final inspection, preventing them from confirming build lead times [^r7]. Engineering drawing updates and bill of materials revisions failed to transfer reliably to works order generation screens, leaving shop-floor personnel to operate from older printed routing sheets [^r8].

## Infrastructure and Network Performance

Warehouse terminals suffered intermittent disconnections from the central server due to network latency between Manchester and Leeds when large reporting jobs were executed during daytime dispatch hours [^r9]. The steering group resolved to review terminal session time-out configurations and reschedule heavy reporting routines outside normal factory operational hours [^r10].

## Attendees

The meeting was attended by [[user-imorgan|Isla Morgan]], [[user-pjansen|Pieter Jansen]], [[user-kmensah|Kwame Mensah]], [[user-cshaw|Callum Shaw]], and [[user-atanaka|Aiko Tanaka]] [^r1].

## See also

* [[user-atanaka|Aiko Tanaka]]
* [[user-cshaw|Callum Shaw]]
* [[user-imorgan|Isla Morgan]]
* [[user-kmensah|Kwame Mensah]]
* [[user-pjansen|Pieter Jansen]]

## References

[^r1]: 10_meeting_notes/2022-03-11 IT steering.docx, IT steering
[^r2]: 10_meeting_notes/2022-03-11 IT steering.docx, Discussion
[^r4]: 10_meeting_notes/2022-03-11 IT steering.docx, Discussion
[^r8]: 10_meeting_notes/2022-03-11 IT steering.docx, Discussion
[^r9]: 10_meeting_notes/2022-03-11 IT steering.docx, Discussion
[^r3]: 10_meeting_notes/2022-03-11 IT steering.docx, Discussion
[^r10]: 10_meeting_notes/2022-03-11 IT steering.docx, Discussion
[^r5]: 10_meeting_notes/2022-03-11 IT steering.docx, Discussion
[^r6]: 10_meeting_notes/2022-03-11 IT steering.docx, Discussion
[^r7]: 10_meeting_notes/2022-03-11 IT steering.docx, Discussion
