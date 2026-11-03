---
title: "ERR-SHF error codes"
type: "error-list"
slug: "errors-shf"
summary: "Reference list of ERR-SHF error codes raised by Ledgerline production shift services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/production/shf_get.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-SHF |
| Module | PRD (Production) |
| Service group | services-prd-shf |
| Status | Current |

This page catalogues the `ERR-SHF` message codes raised by shift-related production services in Ledgerline. It documents the standard error definitions, messages, and associated services for shift management. Operational details and remedies link to individual error pages where available.

## ERR-SHF error codes

### [[err-shf-0001|ERR-SHF-0001]]: SHIFT NOT FOUND
* **Message**: SHIFT NOT FOUND [^r1]
* **Cause**: The requested shift record could not be located in the system [^r1].
* **Remedy**: Verify the shift identifier or lookup parameters passed to the service [^r1].
* **Raised by**: Service `shf_get` [^r1].

## See also
* [[err-shf-0001|ERR-SHF-0001]]
* [[screen-prd-shf-11|PRD-SHF-11 Shift]]
* [[services-prd-shf|PRD shf services]]

## References

[^r1]: 04_service_definitions/production/shf_get.yaml, errors
