---
title: "ERR-COM Error Codes"
type: "error-list"
slug: "errors-com"
summary: "Catalogue of ERR-COM error codes for sales commission processing and retrieval in Ledgerline ERP Sales."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "04_service_definitions/sales/com_get.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-COM |
| Module | Sales (SAL) |
| Entity | Sales Commission |
| Source Manual | MAN-SAL-72 |
| Status | current |

The `ERR-COM` series covers error messages returned by Ledgerline ERP during sales commission calculation, inquiry, and retrieval operations. These codes are surfaced on commission screens such as [[screen-sal-com-15|SAL-COM-15]] and are returned by underlying commission services in the [[services-sal-com|SAL com services]] group. Resolving these errors ensures commission batches and individual salesperson statements reconcile accurately against open calendar periods.

### ERR-COM-0001

* **Message:** SALES COMMISSION NOT FOUND [^r2]
* **Cause:** The system cannot complete commission calculation or retrieval because the `PERIOD` parameter is blank, has an invalid format, does not exist in the financial calendar, or is locked against processing [^r1].
* **Remedy:** Verify that the target financial period exists, conforms to the standard format, is open for processing, and that commission records exist for the specified query criteria [^r1]. For full operational troubleshooting, see [[err-com-0001|ERR-COM-0001]].
* **Raised by:** Service `com_get` in [[services-sal-com|SAL com services]] [^r2]; encountered on screen [[screen-sal-com-15|SAL-COM-15]] [^r1].

## See also

* [[err-com-0001|ERR-COM-0001 Period Not Open or Already Posted]]
* [[screen-sal-com-15|SAL-COM-15 Sales Commission]]
* [[services-sal-com|SAL com services]]
* [[man-sal-72|MAN-SAL-72 Ledgerline ERP 7.2 User Manual: Sales]]
* [[sop-sal-001|SOP-SAL-001 Sales Order to Despatch]]

## References

[^r2]: 04_service_definitions/sales/com_get.yaml, errors
[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 61, Messages
