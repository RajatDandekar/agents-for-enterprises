---
title: "ERR-OU-* Error Codes"
type: "error-list"
slug: "errors-ou"
summary: "Reference catalogue for ERR-OU-* organization unit error codes raised by administrative services in Ledgerline."
audience: "staff"
status: "current"
sources: ["04_service_definitions/admin/ou_get.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

The `ERR-OU-*` error code family covers errors returned during organisation unit administration in Ledgerline. These codes are raised by administrative organisation unit backend services when looking up or managing structural units.

### ERR-OU-0001: ORGANISATION UNIT NOT FOUND
* **Message:** ORGANISATION UNIT NOT FOUND [^r1]
* **Cause:** The requested organisation unit does not exist in the system [^r1].
* **Remedy:** Verify the organisation unit code or identifier before re-executing the request [^r1].
* **Raised by:** Service `ou_get` in [[services-adm-ou]] [^r1].

## See also
* [[services-adm-ou]]
* [[screen-sys-ou-08]]
* [[user-jfletcher]]

## References

[^r1]: 04_service_definitions/admin/ou_get.yaml, errors
