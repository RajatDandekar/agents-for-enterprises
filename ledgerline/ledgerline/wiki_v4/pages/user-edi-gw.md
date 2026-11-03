---
title: "EDI gateway account (6.x) (EDI_GW)"
type: "person"
slug: "user-edi-gw"
summary: "Legacy EDI gateway service account (EDI_GW) formerly used for INT-001 retailer orders, now disabled and replaced by SVC_EDI."
audience: "staff"
status: "current"
sources: ["12_integrations/Integration inventory.xlsx"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| User ID | EDI_GW |
| Type | Service account |
| Status | Disabled |
| Interface | INT-001 |
| Replaced by | SVC_EDI |

`EDI_GW` is a legacy service account formerly utilized for interface INT-001 (EDI ORDERS from retailers via SOAP gateway) [^r1]. As of 26 October 2026, the account is disabled and its responsibilities have transitioned to `SVC_EDI` [^r1]. 

## Account details

The account previously handled automated message exchange for inbound retailer orders through the SOAP gateway under interface INT-001 [^r1]. Operational records in the [[data-integration-inventory|Integration inventory]] mark the account status as disabled following the migration to `SVC_EDI` [^r1].

## Versions and conflicts

- **superseded**: Interface INT-001 uses service account `SVC_EDI`, and `EDI_GW` is disabled [^r1]. Previously, `EDI_GW` served as the active service account for inbound retailer SOAP orders [^r1].

## See also

* [[data-integration-inventory|Integration inventory]]

## References

[^r1]: 12_integrations/Integration inventory.xlsx, sheet Interfaces, row INT-001, SHEET Interfaces
