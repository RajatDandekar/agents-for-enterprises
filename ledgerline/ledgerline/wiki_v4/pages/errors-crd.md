---
title: "ERR-CRD Error Codes Reference"
type: "error-list"
slug: "errors-crd"
summary: "Reference catalogue of ERR-CRD credit control error codes raised by sales module services in Ledgerline."
audience: "staff"
status: "current"
sources: ["04_service_definitions/sales/crd_check.yaml", "04_service_definitions/sales/crd_hold_list.yaml", "04_service_definitions/sales/crd_release.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-CRD |
| Module | Sales (Credit Control) |
| Type | System error codes |
| Owner | Finance / Sales Administration |
| Status | Current |

System error code reference for the ERR-CRD series raised by Ledgerline credit control services in the sales module. These errors handle missing credit control records and invalid status transitions during credit evaluation and release workflows. As of 26 October 2026, the catalogue defines error codes returned across credit check, hold listing, and release operations.

### ERR-CRD-0001

* **Message**: `CREDIT CONTROL NOT FOUND` [^r1][^r2][^r3]
* **Cause**: The targeted credit control record cannot be located by the service [^r1][^r2][^r3].
* **Remedy**: Verify the credit control identifier or customer reference and re-run the transaction.
* **Raised by**: `crd_check` [^r1], `crd_hold_list` [^r2], and `crd_release` [^r3].
* **Detailed page**: [[err-crd-0001|ERR-CRD-0001]]

### ERR-CRD-0007

* **Message**: `CREDIT CONTROL NOT IN DRAFT (<status>)` [^r4]
* **Cause**: The credit control entry is not in the required draft status when invoking the action [^r4].
* **Remedy**: Check the current record status and ensure the workflow sequence allows release from that state.
* **Raised by**: `crd_release` [^r4].

## See also

* [[err-crd-0001|ERR-CRD-0001 Missing mandatory remarks for credit release]]
* [[screen-sal-crd-11|SAL-CRD-11 Credit Control Check]]
* [[services-sal-crd|SAL crd services]]
* [[user-jfletcher|Joanna Fletcher (JFLETCHER)]]

## References

[^r1]: 04_service_definitions/sales/crd_check.yaml, errors
[^r2]: 04_service_definitions/sales/crd_hold_list.yaml, errors
[^r3]: 04_service_definitions/sales/crd_release.yaml, errors
[^r4]: 04_service_definitions/sales/crd_release.yaml, errors
