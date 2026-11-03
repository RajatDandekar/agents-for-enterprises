---
title: "ERR-DSC Discount Error Codes"
type: "error-list"
slug: "errors-dsc"
summary: "Reference catalogue of ERR-DSC discount error codes raised by sales discount services in Ledgerline."
audience: "staff"
status: "current"
sources: ["04_service_definitions/sales/dsc_get.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-DSC |
| Domain | Sales / Discounts |
| Module | SAL |
| Related service group | services-sal-dsc |
| Status | Current |

Catalogue of error codes with prefix ERR-DSC raised by discount services in Ledgerline. These codes indicate failures encountered during discount lookup and processing in sales operations as of 26 October 2026.

### ERR-DSC-0001
* **Message:** DISCOUNT NOT FOUND [^r1]
* **Cause:** The requested discount record could not be located in the system [^r1].
* **Remedy:** Verify that the discount code exists and is correctly specified in the query parameters [^r1].
* **Raised by:** Service `dsc_get` (documented under [[services-sal-dsc|SAL dsc services]]) [^r1].
* **Detailed page:** [[err-dsc-0001|ERR-DSC-0001]]

## See also
* [[err-dsc-0001|ERR-DSC-0001]]
* [[screen-sal-dsc-10|SAL-DSC-10 Discount]]
* [[services-sal-dsc|SAL dsc services]]
* [[user-jfletcher|Joanna Fletcher (JFLETCHER)]]

## References

[^r1]: 04_service_definitions/sales/dsc_get.yaml, errors
