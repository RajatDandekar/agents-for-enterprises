---
title: "ERR-IMP Error Codes"
type: "error-list"
slug: "errors-imp"
summary: "Reference catalogue of ERR-IMP error codes raised during Ledgerline data import validation, status checks, and posting operations."
audience: "staff"
status: "current"
sources: ["04_service_definitions/admin/imp_post.yaml", "04_service_definitions/admin/imp_status.yaml", "04_service_definitions/admin/imp_validate.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

The ERR-IMP error codes are raised across Ledgerline administration data import services including import status verification, validation, and posting operations [^r1][^r3][^r4]. These codes signal missing import records or invalid batch status conditions during import lifecycle processing [^r1][^r2]. Users encountering these codes typically address them through [[screen-sys-imp-13|SYS-IMP-13 Data Import Upload]] or underlying [[services-adm-imp|ADM imp services]] [^r1][^r3][^r4].

### ERR-IMP-0001

* **Message**: DATA IMPORT NOT FOUND [^r1][^r3][^r4]
* **Cause**: The requested data import record cannot be located [^r1][^r3][^r4].
* **Remedy**: Verify the import identifier and ensure the import batch exists before retrying [^r1][^r3][^r4].
* **Raised by**: `imp_post`, `imp_status`, `imp_validate` [^r1][^r3][^r4]

### ERR-IMP-0007

* **Message**: DATA IMPORT NOT IN DRAFT (<status>) [^r2]
* **Cause**: An attempt was made to post a data import batch that is not currently in DRAFT status [^r2].
* **Remedy**: Check the current status of the import batch and ensure it is in DRAFT status prior to posting [^r2].
* **Raised by**: `imp_post` [^r2]

## See also

* [[screen-sys-imp-13|SYS-IMP-13 Data Import Upload]]
* [[services-adm-imp|ADM imp services]]

## References

[^r1]: 04_service_definitions/admin/imp_post.yaml, errors
[^r3]: 04_service_definitions/admin/imp_status.yaml, errors
[^r4]: 04_service_definitions/admin/imp_validate.yaml, errors
[^r2]: 04_service_definitions/admin/imp_post.yaml, errors
