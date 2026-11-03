---
title: "ERR-SCP Production Scrap Error Codes"
type: "error-list"
slug: "errors-scp"
summary: "Reference list of ERR-SCP error codes raised by Ledgerline production scrap services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/production/scp_get.yaml", "04_service_definitions/production/scp_post.yaml", "04_service_definitions/production/scp_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-SCP |
| Domain | Production Scrap |
| Module | PRD |
| Authority | Ledgerline Service Definitions |
| Status | Current |

The ERR-SCP series of error codes is raised by Ledgerline backend services handling production scrap transactions. As of 26 October 2026, these codes enforce record existence, status validation, and quantity checks during scrap processing across [[services-prd-scp|PRD scp services]]. Specific message definitions are declared across the service definitions for scrap retrieval, updating, and posting.

### ERR-SCP-0001
* **Message**: PRODUCTION SCRAP NOT FOUND [^r1][^r2].
* **Cause**: Attempting to access or post a production scrap record that does not exist in the system [^r2].
* **Remedy**: Verify the scrap identifier before retrieving or posting the record [^r1][^r2].
* **Raised by**: `scp_get` [^r1], `scp_post` [^r2].
* **Detail page**: [[err-scp-0001|ERR-SCP-0001]].

### ERR-SCP-0007
* **Message**: PRODUCTION SCRAP NOT IN DRAFT (<status>) [^r3].
* **Cause**: Attempting to post a production scrap entry that is not in draft status [^r3].
* **Remedy**: Ensure the production scrap record is in draft status prior to posting [^r3].
* **Raised by**: `scp_post` [^r3].

### ERR-SCP-0201
* **Message**: QTY MUST BE > 0 [^r4].
* **Cause**: A production scrap line is submitted with a quantity that is not greater than zero [^r4].
* **Remedy**: Enter a valid quantity greater than zero on the scrap entry before saving [^r4].
* **Raised by**: `scp_save` [^r4].

## See also
* [[services-prd-scp|PRD scp services]]
* [[screen-prd-scp-12|PRD-SCP-12 Production Scrap Entry]]
* [[err-scp-0001|ERR-SCP-0001 Mandatory scrap header or line details missing]]
* [[errors-itm|ERR-ITM error codes]]

## References

[^r1]: 04_service_definitions/production/scp_get.yaml, errors
[^r2]: 04_service_definitions/production/scp_post.yaml, errors
[^r3]: 04_service_definitions/production/scp_post.yaml, errors
[^r4]: 04_service_definitions/production/scp_save.yaml, errors
