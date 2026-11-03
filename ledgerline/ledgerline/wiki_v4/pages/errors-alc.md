---
title: "Errors ALC (ERR-ALC-*)"
type: "error-list"
slug: "errors-alc"
summary: "Reference list of ALC allocation error codes ERR-ALC-0001 and ERR-ALC-0801 across Ledgerline Sales screens and backend allocation services."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "04_service_definitions/sales/alc_cancel.yaml", "04_service_definitions/sales/alc_get.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-ALC |
| Module | Sales (Allocation) |
| Manual | MAN-SAL-72 |
| Status | current |

This page documents the `ERR-ALC-*` error codes raised within Northbridge Cycles' Ledgerline ERP system during stock allocation and cancellation. These errors originate both from UI interactions on allocation screens and from underlying sales allocation backend services. Understanding their specific causes helps users and support staff resolve order allocation blocks and cancellation failures.

### ERR-ALC-0001

* **Message:** ALLOCATION NOT FOUND [^r3][^r5]
* **Cause:** In backend allocation services such as `alc_get` and `alc_cancel`, the requested allocation record cannot be identified or found [^r3][^r5]. In user manual screen messages, it indicates that the sales order entered in SO NO cannot be found or is in an invalid status for allocation, such as being in draft state or under finance credit hold [^r1].
* **Remedy:** Verify that the allocation identifier or order number exists and is correct [^r1][^r3][^r5]. If operating on an order, ensure the sales order is confirmed and not held under a finance credit hold [^r1].
* **Raised by:** Backend services `alc_get` and `alc_cancel`, and allocation UI operations [^r1][^r3][^r5].

### ERR-ALC-0801

* **Message:** ALLOCATION CLOSED (<status>) [^r4]
* **Cause:** When raised by the `alc_cancel` service, the system was requested to cancel an allocation that has already been closed [^r4]. In the user manual screen documentation, it indicates that an allocation run failed due to insufficient free pickable stock, items being held in quarantine locations, or inventory records being locked by concurrent transactions [^r2].
* **Remedy:** For cancellation attempts, check the existing status of the allocation before retrying [^r4]. For failed allocation runs, verify stock availability in pickable bins, release items from quarantine where appropriate, and retry the allocation once concurrent inventory transactions have completed [^r2].
* **Raised by:** Backend service `alc_cancel` and allocation processing screens [^r2][^r4].

## Versions and conflicts

* **ERR-ALC-0001 meaning:** Service definitions specify the error message as 'ALLOCATION NOT FOUND' when an allocation cannot be identified during `alc_get` or `alc_cancel` services [^r3][^r5]. In contrast, [[man-sal-72|MAN-SAL-72]] describes ERR-ALC-0001 as indicating that the sales order entered in SO NO cannot be found or is in an invalid status such as draft state or finance credit hold [^r1]. (Kind: contradiction).
* **ERR-ALC-0801 meaning:** The service definition for `alc_cancel` specifies the error message as 'ALLOCATION CLOSED (<status>)' when attempting to cancel an already closed allocation [^r4]. In contrast, [[man-sal-72|MAN-SAL-72]] documents ERR-ALC-0801 as an allocation run failure caused by insufficient free pickable stock, items held in quarantine locations, or inventory records locked by concurrent transactions [^r2]. (Kind: contradiction).

## See also

* [[screen-sal-alc-03|SAL-ALC-03 Allocation]]
* [[services-sal-alc|SAL alc services]]
* [[sop-sal-001|SOP-SAL-001 Sales Order to Despatch]]
* [[man-sal-72|MAN-SAL-72 Ledgerline ERP 7.2 User Manual: Sales]]
* [[errors-so|Errors SO (Sales Order)]]

## References

[^r3]: 04_service_definitions/sales/alc_cancel.yaml, errors
[^r5]: 04_service_definitions/sales/alc_get.yaml, errors
[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 16, Messages
[^r4]: 04_service_definitions/sales/alc_cancel.yaml, errors
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 16, Messages
