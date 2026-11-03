---
title: "Legacy Service REQ_ENTRY"
type: "service-group"
slug: "services-pur-req"
summary: "Service definition for superseded Ledgerline 6.4 purchase requisition entry RPC service REQ_ENTRY."
audience: "staff"
status: "current"
sources: ["04_service_definitions/_legacy_6x/REQ_ENTRY.xml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Service | REQ_ENTRY |
| Module | PUR |
| Transport | LL6-RPC |
| Status | Superseded |
| Platform | Ledgerline 6.4 |

This page documents the legacy purchase requisition creation interface `REQ_ENTRY` from the [[rn-ll6-history|Ledgerline 6.x]] architecture. The service is superseded and preserved only for historical reference regarding 6.4 integration points. It defines the remote procedure call parameters originally used to capture purchase requisition details.

## Services

### REQ_ENTRY

The legacy `REQ_ENTRY` service is a superseded Ledgerline 6.4 remote procedure call definition that operates over the `LL6-RPC` transport mechanism.[^r1]

* **Required fields**: None defined as strictly required in the schema definition.[^r2]
* **Optional fields**: Input fields comprise character (`CHAR`) fields `ITEM_NO`, `QTY`, `CC`, `DUE_DATE`, and `REQUESTER`.[^r2]
* **Errors and return codes**: Output fields returned upon execution are `RETCODE` and `DOCNO`.[^r3]
* **Source file**: `04_service_definitions/_legacy_6x/REQ_ENTRY.xml`.[^r1]

## Versions and conflicts

* **Today's rule**: Ledgerline 7 services supersede legacy Ledgerline 6.x RPC definitions.
* **Older rule**: In Ledgerline 6.4, purchase requisition entry was executed via the `REQ_ENTRY` service using `LL6-RPC` transport with character input fields `ITEM_NO`, `QTY`, `CC`, `DUE_DATE`, and `REQUESTER`, returning `RETCODE` and `DOCNO`.[^r1][^r2][^r3]
* **Kind**: `superseded`. Sources: `04_service_definitions/_legacy_6x/REQ_ENTRY.xml`.[^r1]

## See also

* [[rn-ll6-history|Ledgerline 6 release history 2004-2012]]

## References

[^r1]: 04_service_definitions/_legacy_6x/REQ_ENTRY.xml, rpc
[^r2]: 04_service_definitions/_legacy_6x/REQ_ENTRY.xml, input
[^r3]: 04_service_definitions/_legacy_6x/REQ_ENTRY.xml, output
