---
title: "ERR-LIC-* Licence Error Codes"
type: "error-list"
slug: "errors-lic"
summary: "Error codes under the ERR-LIC prefix returned by Ledgerline administration licence services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/admin/lic_status.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-LIC |
| Module | Administration |
| Service group | [[services-adm-lic|ADM lic services]] |
| Status | Current |

The ERR-LIC-* error codes identify system licence and activation failures within Ledgerline. These errors are raised by administration module services handling licence verification and operational limits. System administrators encounter these codes when running licence checks or querying the active licence state.

### ERR-LIC-0001
* **Message**: LICENCE NOT FOUND [^r1].
* **Cause**: The system cannot locate a valid licence record during execution [^r1].
* **Remedy**: Verify the installed licence key and configuration via [[screen-sys-lic-10|SYS-LIC-10 Licence Status]], or contact [[user-jfletcher|Joanna Fletcher]] for licence provisioning.
* **Raised by**: Service `lic_status` in [[services-adm-lic|ADM lic services]] [^r1].

## See also
* [[screen-sys-lic-10|SYS-LIC-10 Licence Status]]
* [[services-adm-lic|ADM lic services]]
* [[user-jfletcher|Joanna Fletcher]]

## References

[^r1]: 04_service_definitions/admin/lic_status.yaml, errors
