---
title: "ERR-AUD Error Codes"
type: "error-list"
slug: "errors-aud"
summary: "Catalogue of Ledgerline audit module error codes prefixed with ERR-AUD raised by admin audit trail services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/admin/aud_export.yaml", "04_service_definitions/admin/aud_query.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-AUD |
| Module | Admin (Audit) |
| System | Ledgerline |
| Status | Current |
| Total codes | 1 |

This catalogue documents error codes prefixed with `ERR-AUD` across Ledgerline administration audit services as of 26 October 2026. These error codes indicate failure conditions encountered when searching or exporting system audit logs. The codes are returned by audit services within [[services-adm-aud|ADM aud services]].

### ERR-AUD-0001

* **Message:** AUDIT TRAIL NOT FOUND [^r1][^r2]
* **Cause:** The requested audit trail could not be located by the service [^r1][^r2].
* **Remedy:** Verify the query parameters and confirm that an audit trail record exists for the selected criteria.
* **Raised by:** Services `aud_export` [^r1] and `aud_query` [^r2] in [[services-adm-aud|ADM aud services]].

## See also

* [[screen-sys-aud-07|SYS-AUD-07 Audit Trail]]
* [[services-adm-aud|ADM aud services]]
* [[user-jfletcher|Joanna Fletcher (JFLETCHER)]]

## References

[^r1]: 04_service_definitions/admin/aud_export.yaml, errors
[^r2]: 04_service_definitions/admin/aud_query.yaml, errors
