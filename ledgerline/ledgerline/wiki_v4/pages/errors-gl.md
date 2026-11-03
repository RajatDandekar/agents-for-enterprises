---
title: "GL Error Codes"
type: "error-list"
slug: "errors-gl"
summary: "Reference list of general ledger ERR-GL error codes raised by Ledgerline AP GL services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/accounts_payable/gl_post.yaml", "04_service_definitions/accounts_payable/gl_query.yaml", "04_service_definitions/accounts_payable/gl_reverse.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-GL |
| Domain | General Ledger / Accounts Payable |
| Source type | Service definitions |
| Status | current |

This page catalogues the `ERR-GL-*` error codes defined across Ledgerline general ledger services in Accounts Payable as of 26 October 2026. These errors are returned when querying, posting, or reversing general ledger transactions such as journal vouchers. Detailed handling and context for individual codes are documented on their dedicated error pages where available.

### ERR-GL-0001
* **Message**: `GL POSTING NOT FOUND` [^r1]
* **Cause**: The requested GL posting record cannot be located in Ledgerline [^r1].
* **Remedy**: Verify the GL posting reference or identifier before querying, posting, or reversing the entry [^r1][^r3][^r4]. Refer to [[err-gl-0001|ERR-GL-0001]] for specific troubleshooting guidance.
* **Raised by**: `gl_post` [^r1], `gl_query` [^r3], and `gl_reverse` [^r4].

### ERR-GL-0007
* **Message**: `GL POSTING NOT IN DRAFT (<status>)` [^r2]
* **Cause**: An attempt was made to post a journal voucher that is not currently in draft status [^r2].
* **Remedy**: Confirm that the journal voucher is in draft status before triggering posting operations [^r2]. Refer to [[err-gl-0007|ERR-GL-0007]] for detailed status resolution steps.
* **Raised by**: `gl_post` [^r2].

## See also
* [[err-gl-0001|ERR-GL-0001 Missing or Invalid Header Information]]
* [[err-gl-0007|ERR-GL-0007 Ledger Integrity Failure]]
* [[screen-ap-gl-14|AP-GL-14 Gl Posting]]
* [[services-ap-gl|AP gl services]]

## References

[^r1]: 04_service_definitions/accounts_payable/gl_post.yaml, errors
[^r3]: 04_service_definitions/accounts_payable/gl_query.yaml, errors
[^r4]: 04_service_definitions/accounts_payable/gl_reverse.yaml, errors
[^r2]: 04_service_definitions/accounts_payable/gl_post.yaml, errors
