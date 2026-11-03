---
title: "ERR-ROL error codes"
type: "error-list"
slug: "errors-rol"
summary: "Reference list of ERR-ROL Ledgerline role management error codes, causes, and raising services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/admin/role_get.yaml", "04_service_definitions/admin/role_svc_add.yaml", "04_service_definitions/admin/role_svc_remove.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-ROL |
| Domain | Role Administration |
| Module | admin |
| Services | [[services-adm-role|ADM role services]] |
| Status | Current |

This catalogue lists error codes with the prefix ERR-ROL used across Ledgerline role management services. As of 26 October 2026, it details the specific error messages and services that raise each condition during role retrieval and role-service mapping operations.

## ERR-ROL error codes

### ERR-ROL-0001
* **Message**: ROLE NOT FOUND [^r1][^r2][^r3]
* **Cause**: The requested role code cannot be located in the system [^r1].
* **Remedy**: Verify the role code exists or check configuration in [[screen-sys-rol-02|SYS-ROL-02 Role]].
* **Raised by**: `role_get` [^r1], `role_svc_add` [^r2], and `role_svc_remove` [^r3] in [[services-adm-role|ADM role services]].

## See also
* [[screen-sys-rol-02|SYS-ROL-02 Role]]
* [[services-adm-role|ADM role services]]

## References

[^r1]: 04_service_definitions/admin/role_get.yaml, errors
[^r2]: 04_service_definitions/admin/role_svc_add.yaml, errors
[^r3]: 04_service_definitions/admin/role_svc_remove.yaml, errors
