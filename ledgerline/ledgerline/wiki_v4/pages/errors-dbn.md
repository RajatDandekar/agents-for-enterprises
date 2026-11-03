---
title: "ERR-DBN Debit Note Error Codes"
type: "error-list"
slug: "errors-dbn"
summary: "Ledgerline accounts payable error codes with the ERR-DBN prefix raised by debit note backend services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/accounts_payable/dbn_cancel.yaml", "04_service_definitions/accounts_payable/dbn_get.yaml", "04_service_definitions/accounts_payable/dbn_post.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-DBN |
| Module | Accounts Payable |
| Subsystem | Debit Notes |
| Raised by | [[services-ap-dbn|AP dbn services]] |
| Status | Current |

This page catalogues system error codes bearing the `ERR-DBN` prefix in Ledgerline Accounts Payable. These errors are raised during debit note inquiry, posting, and cancellation workflows when records are missing or in an incompatible status [^r1][^r2][^r3][^r4][^r5]. Operational issues surfacing these codes typically originate from [[services-ap-dbn|AP dbn services]] interfacing with screens such as [[screen-ap-dbn-04|AP-DBN-04 Debit Note Entry]].

| Code | Message | Raised by | Detailed Page |
|---|---|---|---|
| ERR-DBN-0001 | DEBIT NOTE NOT FOUND | dbn_cancel, dbn_get, dbn_post | [[err-dbn-0001]] |
| ERR-DBN-0007 | DEBIT NOTE NOT IN DRAFT (&lt;status&gt;) | dbn_post | [[err-dbn-0007]] |
| ERR-DBN-0801 | DEBIT NOTE CLOSED (&lt;status&gt;) | dbn_cancel | [[err-dbn-0801]] |

### [[err-dbn-0001|ERR-DBN-0001]]

* **Message**: `DEBIT NOTE NOT FOUND` [^r1][^r3][^r4]
* **Cause**: The requested debit note identifier does not match an existing record in the database [^r1][^r3][^r4].
* **Remedy**: Verify the debit note number before re-invoking the operation.
* **Raised by**: `dbn_cancel` [^r1], `dbn_get` [^r3], and `dbn_post` [^r4].

### [[err-dbn-0007|ERR-DBN-0007]]

* **Message**: `DEBIT NOTE NOT IN DRAFT (<status>)` [^r5]
* **Cause**: Attempting to post a debit note that is not currently in `DRAFT` status [^r5].
* **Remedy**: Inspect the debit note status and ensure posting actions are executed only on draft documents.
* **Raised by**: `dbn_post` [^r5].

### [[err-dbn-0801|ERR-DBN-0801]]

* **Message**: `DEBIT NOTE CLOSED (<status>)` [^r2]
* **Cause**: Attempting to cancel a debit note that has already been closed [^r2].
* **Remedy**: Check the current status of the debit note; closed notes cannot be cancelled.
* **Raised by**: `dbn_cancel` [^r2].

## See also

* [[services-ap-dbn|AP dbn services]]
* [[screen-ap-dbn-04|AP-DBN-04 Debit Note Entry]]
* [[err-dbn-0001|ERR-DBN-0001]]
* [[err-dbn-0007|ERR-DBN-0007]]
* [[err-dbn-0801|ERR-DBN-0801]]

## References

[^r1]: 04_service_definitions/accounts_payable/dbn_cancel.yaml, errors
[^r2]: 04_service_definitions/accounts_payable/dbn_cancel.yaml, errors
[^r3]: 04_service_definitions/accounts_payable/dbn_get.yaml, errors
[^r4]: 04_service_definitions/accounts_payable/dbn_post.yaml, errors
[^r5]: 04_service_definitions/accounts_payable/dbn_post.yaml, errors
