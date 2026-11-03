---
title: "ERR-PCS petty cash error codes"
type: "error-list"
slug: "errors-pcs"
summary: "Reference list of ERR-PCS petty cash error codes raised by Ledgerline accounts payable petty cash services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/accounts_payable/pcs_get.yaml", "04_service_definitions/accounts_payable/pcs_post.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-PCS |
| Module | Accounts Payable |
| Subsystem | Petty Cash |
| Services | pcs_get, pcs_post |

This page catalogues the `ERR-PCS` petty cash error codes returned by Ledgerline accounts payable services [^r1][^r2][^r3]. These codes are triggered during petty cash retrieval and posting operations when records cannot be located or fail status validation [^r1][^r2][^r3].

### [[err-pcs-0001|ERR-PCS-0001]]
* **Message**: `PETTY CASH NOT FOUND` [^r1][^r2]
* **Cause**: The petty cash record cannot be found in the system [^r1][^r2].
* **Remedy**: Verify the petty cash identifier and confirm the record exists before retrying [^r1][^r2].
* **Raised by**: `pcs_get` and `pcs_post` [^r1][^r2].

### [[err-pcs-0007|ERR-PCS-0007]]
* **Message**: `PETTY CASH NOT IN DRAFT (<status>)` [^r3]
* **Cause**: The petty cash transaction is not in draft status at the time of posting [^r3].
* **Remedy**: Check the current record status and ensure the petty cash voucher is in draft before posting [^r3].
* **Raised by**: `pcs_post` [^r3].

## See also
* [[err-pcs-0001]]
* [[err-pcs-0007]]
* [[screen-ap-pcs-15|AP-PCS-15 Petty Cash Entry]]
* [[services-ap-pcs|AP pcs services]]
* [[user-jfletcher|Joanna Fletcher (JFLETCHER)]]

## References

[^r1]: 04_service_definitions/accounts_payable/pcs_get.yaml, errors
[^r2]: 04_service_definitions/accounts_payable/pcs_post.yaml, errors
[^r3]: 04_service_definitions/accounts_payable/pcs_post.yaml, errors
