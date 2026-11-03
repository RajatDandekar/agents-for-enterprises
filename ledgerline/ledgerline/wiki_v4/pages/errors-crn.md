---
title: "ERR-CRN error code reference"
type: "error-list"
slug: "errors-crn"
summary: "Reference list of ERR-CRN error codes raised by Ledgerline accounts payable supplier credit note services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/accounts_payable/crn_get.yaml", "04_service_definitions/accounts_payable/crn_post.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-CRN |
| Module | Accounts Payable |
| Subsystem | Supplier Credit Notes |
| Status | current |

Reference catalogue of ERR-CRN error codes returned by Ledgerline accounts payable credit note services. These codes are raised during supplier credit note retrieval and posting actions, notably in [[services-ap-crn|AP crn services]]. Operations encountering these errors typically originate in interfaces such as [[screen-ap-crn-05|AP-CRN-05 Supplier Credit Note Entry]].

### ERR-CRN-0001
* **Message**: SUPPLIER CREDIT NOTE NOT FOUND [^r1][^r2]
* **Cause**: The requested supplier credit note identifier cannot be located when attempting an operation or fetching record details [^r1][^r2].
* **Remedy**: Verify the credit note reference number and confirm the record exists before re-attempting the query or action.
* **Raised by**: `crn_get` [^r1], `crn_post` [^r2]

### ERR-CRN-0007
* **Message**: SUPPLIER CREDIT NOTE NOT IN DRAFT (<status>) [^r3]
* **Cause**: An attempt was made to post a supplier credit note that is not currently in draft status [^r3].
* **Remedy**: Check the current record status; only credit notes in draft status can be submitted for posting.
* **Raised by**: `crn_post` [^r3]

## See also
* [[screen-ap-crn-05|AP-CRN-05 Supplier Credit Note Entry]]
* [[services-ap-crn|AP crn services]]

## References

[^r1]: 04_service_definitions/accounts_payable/crn_get.yaml, errors
[^r2]: 04_service_definitions/accounts_payable/crn_post.yaml, errors
[^r3]: 04_service_definitions/accounts_payable/crn_post.yaml, errors
