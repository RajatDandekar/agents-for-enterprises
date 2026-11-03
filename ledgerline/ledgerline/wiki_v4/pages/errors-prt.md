---
title: "Errors PRT (ERR-PRT-*)"
type: "error-list"
slug: "errors-prt"
summary: "Reference catalogue of PRT print subsystem error codes raised by Ledgerline administrative print services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/admin/prt_form_get.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-PRT |
| Module | Administration / Print |
| Related service group | services-adm-prt |
| Status | current |

This catalogue documents error codes beginning with the `ERR-PRT` prefix in Ledgerline. These messages are raised by print administration services when handling form templates and print configurations. As of 26 October 2026, the catalogue details errors generated during form retrieval operations.

### ERR-PRT-0001

* **Message:** PRINT FORMS NOT FOUND [^r1]
* **Cause:** The requested print form definition or template could not be located by the service [^r1].
* **Remedy:** Verify that the requested form template is correctly configured and registered in the system [^r1].
* **Raised by:** Service `prt_form_get` in [[services-adm-prt|ADM prt services]] [^r1].

## See also

* [[services-adm-prt|ADM prt services]]
* [[screen-sys-prt-12|SYS-PRT-12 Print Forms]]
* [[user-jfletcher|Joanna Fletcher (JFLETCHER)]]

## References

[^r1]: 04_service_definitions/admin/prt_form_get.yaml, errors
