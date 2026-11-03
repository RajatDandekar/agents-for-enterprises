---
title: "Leeds to Manchester Data Transfer Gateway"
type: "topic"
slug: "topic-leeds-manchester-gateway"
summary: "Legacy 6.x interface used for automated polling of dispatch notes between the Leeds unit and Manchester server."
audience: "staff"
status: "current"
sources: ["09_email_archive/2026/2026-01-18_Old 6.x gateway still in use.eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Gateway type | Legacy 6.x file transfer interface |
| Locations | Leeds unit to Manchester server |
| Primary data | Dispatch notes |
| Status | Active (pending migration) |
| Owner | IT Operations |

The Leeds to Manchester data transfer gateway is an automated routine responsible for transmitting dispatch notes from the Leeds unit to the primary Manchester server.[^r1] As of 2026, the process continues to run over a legacy 6.x interface retained from an earlier major system release.[^r1] Because the interface lacks modern automated recovery tools, dropped connections during evening batch runs halt processing queues until staff intervene the next morning.[^r2]

## Operational Status

The automated polling routine for dispatch notes between the Leeds facility and the central Manchester server operates across a legacy 6.x gateway.[^r1] While the legacy pipeline continues to parse and process flat files without generating processing errors, it does not possess automated error recovery mechanisms.[^r2] Consequently, when network interruptions occur during evening batch transfers, the transfer queue freezes entirely and requires manual administrative intervention the following morning to resume processing.[^r2]

## Planned Migration

[[user-rpryce|Rhys Pryce]] requested that the remaining dispatch note polling routines be migrated from the legacy 6.x gateway over to the currently supported interface.[^r3] This migration was requested to permit full decommissioning of the legacy 6.x service ahead of the next scheduled stock audit.[^r3]

## See also

* [[user-rpryce|Rhys Pryce]]

## References

[^r1]: 09_email_archive/2026/2026-01-18_Old 6.x gateway still in use.eml, Subject: Old 6.x gateway still in use
[^r2]: 09_email_archive/2026/2026-01-18_Old 6.x gateway still in use.eml, Subject: Old 6.x gateway still in use
[^r3]: 09_email_archive/2026/2026-01-18_Old 6.x gateway still in use.eml, Subject: Old 6.x gateway still in use
