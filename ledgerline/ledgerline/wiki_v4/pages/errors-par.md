---
title: "ERR-PAR Error Codes Reference"
type: "error-list"
slug: "errors-par"
summary: "Reference list of ERR-PAR system parameter error codes raised by administrative parameter services in Ledgerline."
audience: "staff"
status: "current"
sources: ["04_service_definitions/admin/par_get.yaml", "04_service_definitions/admin/par_hist.yaml", "04_service_definitions/admin/par_set.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-PAR |
| Module | Admin (ADM) |
| Target object | System parameters |
| Sources | Service definitions |
| Status | current |

The ERR-PAR error code series covers exceptions raised during system parameter operations in Ledgerline. These errors are returned by administrative services when parameters cannot be found, are unrecognised, or receive invalid configuration values. Troubleshooting these codes ensures system-wide parameter integrity across configuration maintenance screens.

### ERR-PAR-0001
* **Message**: SYSTEM PARAMETER NOT FOUND [^r1]
* **Cause**: The requested system parameter does not exist or cannot be located in the database.
* **Remedy**: Verify the parameter key being accessed and confirm it is defined in the system.
* **Raised by**: `par_get` [^r1], `par_hist` [^r2], and `par_set` [^r3].

### ERR-PAR-0101
* **Message**: UNKNOWN PARAMETER [^r4]
* **Cause**: The parameter identifier supplied to the update routine is not recognized.
* **Remedy**: Check the spelling of the parameter code against standard administrative definitions before updating.
* **Raised by**: `par_set` [^r4].

### ERR-PAR-0110
* **Message**: VALUE OUT OF RANGE [^r5]
* **Cause**: The value supplied for the parameter falls outside the permitted upper or lower operational boundaries.
* **Remedy**: Adjust the parameter value to fall within allowable limits defined for that parameter.
* **Raised by**: `par_set` [^r5].

## See also
* [[services-adm-par|ADM par services]]
* [[screen-sys-par-04|SYS-PAR-04 System Parameter]]
* [[user-jfletcher|Joanna Fletcher (JFLETCHER)]]

## References

[^r1]: 04_service_definitions/admin/par_get.yaml, errors
[^r2]: 04_service_definitions/admin/par_hist.yaml, errors
[^r3]: 04_service_definitions/admin/par_set.yaml, errors
[^r4]: 04_service_definitions/admin/par_set.yaml, errors
[^r5]: 04_service_definitions/admin/par_set.yaml, errors
