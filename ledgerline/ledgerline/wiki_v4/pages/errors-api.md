---
title: "ERR-API Error Codes"
type: "error-list"
slug: "errors-api"
summary: "Reference list of ERR-API error codes raised by Ledgerline administrative API key management services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/admin/api_key_issue.yaml", "04_service_definitions/admin/api_key_list.yaml", "04_service_definitions/admin/api_key_revoke.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-API |
| Domain | API key administration |
| Module | ADM |
| Raised by | api_key_issue, api_key_list, api_key_revoke |
| Status | Current |

The ERR-API error code series covers exceptions raised during Ledgerline service account and API key administration routines. As of 26 October 2026, these codes prevent the issuance, listing, or revocation of API credentials when accounts or keys cannot be located or lack required ownership metadata. Technical teams encounter these errors across the [[services-adm-api|ADM api services]] when managing service account credentials according to [[sop-it-002|SOP-IT-002 Service Account Management]].

### ERR-API-0001
* **Message**: SERVICE ACCOUNT KEY NOT FOUND [^r1][^r3][^r4]
* **Cause**: The targeted service account key record cannot be found in the system.
* **Remedy**: Verify the service account key identifier before retrying the operation.
* **Raised by**: `api_key_issue` [^r1], `api_key_list` [^r3], and `api_key_revoke` [^r4].

### ERR-API-0120
* **Message**: SERVICE ACCOUNT HAS NO OWNER [^r2]
* **Cause**: The specified service account does not have a designated owner assigned.
* **Remedy**: Assign an owner to the service account record, such as [[user-jfletcher|Joanna Fletcher (JFLETCHER)]], before issuing keys.
* **Raised by**: `api_key_issue` [^r2].

## See also
* [[screen-sys-api-14|SYS-API-14 Service Account Key Key Issue]]
* [[services-adm-api|ADM api services]]
* [[sop-it-002|SOP-IT-002 Service Account Management]]
* [[user-jfletcher|Joanna Fletcher (JFLETCHER)]]

## References

[^r1]: 04_service_definitions/admin/api_key_issue.yaml, errors
[^r3]: 04_service_definitions/admin/api_key_list.yaml, errors
[^r4]: 04_service_definitions/admin/api_key_revoke.yaml, errors
[^r2]: 04_service_definitions/admin/api_key_issue.yaml, errors
