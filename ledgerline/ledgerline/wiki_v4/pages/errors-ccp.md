---
title: "ERR-CCP error codes"
type: "error-list"
slug: "errors-ccp"
summary: "Reference list of ERR-CCP error codes returned by Ledgerline cycle count plan inventory services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/inventory/ccp_generate.yaml", "04_service_definitions/inventory/ccp_get.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-CCP |
| Module | Inventory |
| Domain | Cycle Count Planning |
| Related services | services-inv-ccp |
| Status | Current |

The ERR-CCP error code catalogue defines messages returned during cycle count planning operations in Ledgerline. These errors are raised by inventory services when cycle count plan records cannot be located or validated. Users encountering these errors should confirm plan parameters and record status in the inventory system.

### ERR-CCP-0001

* **Message**: CYCLE COUNT PLAN NOT FOUND [^r1][^r2].
* **Cause**: A cycle count plan lookup fails or the requested plan cannot be located [^r1][^r2].
* **Remedy**: Verify that the specified plan ID exists and check the parameters provided [^r1][^r2]. Refer to [[err-ccp-0001|ERR-CCP-0001 Cycle count plan parameter error]] for detailed investigation steps.
* **Raised by**: `ccp_generate` [^r1], `ccp_get` [^r2].

## See also

* [[err-ccp-0001|ERR-CCP-0001 Cycle count plan parameter error]]
* [[services-inv-ccp|INV ccp services]]
* [[screen-inv-ccp-14|INV-CCP-14 Cycle Count Plan Entry]]

## References

[^r1]: 04_service_definitions/inventory/ccp_generate.yaml, errors
[^r2]: 04_service_definitions/inventory/ccp_get.yaml, errors
