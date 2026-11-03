---
title: "ERR-SES-* Error Codes"
type: "error-list"
slug: "errors-ses"
summary: "Error code catalogue for Ledgerline session administration errors (ERR-SES-*), including missing session lookups on termination services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/admin/ses_kill.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-SES-* |
| Domain | Session Administration |
| Source | Ledgerline Service Definitions |
| Status | current |

The ERR-SES-* series contains Ledgerline error codes raised during session management operations as of 26 October 2026 [^r1]. These errors occur when session administration services, including session termination routines, encounter an invalid or unresolvable session identifier [^r1].

### ERR-SES-0001

* **Message:** SESSION NOT FOUND [^r1]
* **Cause:** The target session identifier provided to session administration services does not correspond to an active or existing session [^r1].
* **Remedy:** Verify the session identifier and refresh the session list before re-invoking the command [^r1].
* **Raised by:** Session administration services such as `ses_kill` (part of [[services-adm-ses|ADM ses services]]) [^r1].

## See also
* [[screen-sys-ses-09|SYS-SES-09 Session]]
* [[services-adm-ses|ADM ses services]]

## References

[^r1]: 04_service_definitions/admin/ses_kill.yaml, errors
