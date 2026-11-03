---
title: "ERR-NTF Notification Error Codes"
type: "error-list"
slug: "errors-ntf"
summary: "Reference list of ERR-NTF error codes raised by notification queue and template services in Ledgerline."
audience: "staff"
status: "current"
sources: ["04_service_definitions/admin/ntf_queue_list.yaml", "04_service_definitions/admin/ntf_retry.yaml", "04_service_definitions/admin/ntf_tpl_get.yaml", "04_service_definitions/admin/ntf_tpl_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

The ERR-NTF error code series covers exceptions raised by Ledgerline's notification administration and queue management services [^r1][^r2]. These errors occur when referencing notifications or notification templates across queue monitoring and template maintenance operations [^r1][^r3].

### ERR-NTF-0001
* **Message**: NOTIFICATION NOT FOUND [^r1][^r2][^r3][^r4]
* **Cause**: The specified notification or template record cannot be found in the system [^r1][^r3].
* **Remedy**: Verify the notification or template identifier and ensure the target record exists [^r1][^r3].
* **Raised by**: `ntf_queue_list` [^r1], `ntf_retry` [^r2], `ntf_tpl_get` [^r3], `ntf_tpl_save` [^r4]

## See also
* [[screen-sys-ntf-11|SYS-NTF-11 Notification Queue]]
* [[services-adm-ntf|ADM ntf services]]

## References

[^r1]: 04_service_definitions/admin/ntf_queue_list.yaml, errors
[^r2]: 04_service_definitions/admin/ntf_retry.yaml, errors
[^r3]: 04_service_definitions/admin/ntf_tpl_get.yaml, errors
[^r4]: 04_service_definitions/admin/ntf_tpl_save.yaml, errors
