---
title: "ERR-CFG error codes"
type: "error-list"
slug: "errors-cfg"
summary: "Reference list of ERR-CFG error codes raised by administrative configuration services in Ledgerline."
audience: "staff"
status: "current"
sources: ["04_service_definitions/admin/cfg_get.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-CFG |
| Domain | Administration Configuration |
| Total codes | 1 |
| Status | current |

This page catalogues the `ERR-CFG` error codes raised by Ledgerline administrative configuration services as of 26 October 2026. These errors occur during system configuration retrieval operations. Configuration maintenance is managed via [[screen-sys-cfg-16|SYS-CFG-16 Menu Config]].

### ERR-CFG-0001

* **Message**: `MENU CONFIG NOT FOUND` [^r1]
* **Cause**: The requested menu configuration record cannot be found [^r1].
* **Remedy**: Verify that the menu identifier exists in [[screen-sys-cfg-16|SYS-CFG-16 Menu Config]] or contact [[user-jfletcher|Joanna Fletcher]] to check configuration definitions.
* **Raised by**: Service `cfg_get` in [[services-adm-cfg|ADM cfg services]] [^r1].

## See also

* [[screen-sys-cfg-16|SYS-CFG-16 Menu Config]]
* [[services-adm-cfg|ADM cfg services]]
* [[user-jfletcher|Joanna Fletcher]]

## References

[^r1]: 04_service_definitions/admin/cfg_get.yaml, errors
