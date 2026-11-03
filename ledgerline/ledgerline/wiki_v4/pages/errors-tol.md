---
title: "ERR-TOL Error Codes"
type: "error-list"
slug: "errors-tol"
summary: "Catalogue of Ledgerline ERR-TOL production tooling error codes, including tool master lookup failures raised by tool retrieval services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/production/tool_get.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-TOL |
| Module | Production (PRD) |
| Domain | Tooling |
| Source service | tool_get |
| Status | current |

Catalogue of `ERR-TOL` error codes raised by Ledgerline tooling services during production master lookups. These codes prevent invalid or missing tool references from being processed across tooling workflows. As of 26 October 2026, the list reflects errors returned by production tool definition services.

### ERR-TOL-0001

- **Message**: TOOL MASTER NOT FOUND [^r1]
- **Cause**: A tool master record cannot be found by the lookup service [^r1].
- **Remedy**: Verify that the tool code exists and is maintained on [[screen-prd-tol-14|PRD-TOL-14 Tool Master]]; refer to [[err-tol-0001|ERR-TOL-0001 Tool Master Validation Failure]] for detailed guidance.
- **Raised by**: The `tool_get` service in [[services-prd-tool|PRD tool services]] [^r1].

## See also

- [[err-tol-0001|ERR-TOL-0001 Tool Master Validation Failure]]
- [[screen-prd-tol-14|PRD-TOL-14 Tool Master]]
- [[services-prd-tool|PRD tool services]]

## References

[^r1]: 04_service_definitions/production/tool_get.yaml, errors
