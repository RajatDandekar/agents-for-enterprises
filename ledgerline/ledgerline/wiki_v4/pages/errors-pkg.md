---
title: "ERR-PKG Error Codes"
type: "error-list"
slug: "errors-pkg"
summary: "Error codes for Ledgerline returnable packaging operations raised by inventory packaging services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/inventory/pkg_get.yaml", "04_service_definitions/inventory/pkg_post.yaml", "04_service_definitions/inventory/pkg_save.yaml", "04_service_definitions/inventory/pkg_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-PKG |
| Module | Inventory |
| Domain | Returnable packaging |
| Status | current |
| Updated | 2026-10-26 |

Catalogue of returnable packaging error codes with the `ERR-PKG` prefix raised by Ledgerline inventory services. These codes prevent processing when packaging records are missing, in an invalid status, or contain invalid quantities. They are raised primarily across operations in [[services-inv-pkg|INV pkg services]].

### ERR-PKG-0001
* **Message:** RETURNABLE PACKAGING NOT FOUND [^r1][^r2]
* **Cause:** A requested returnable packaging record cannot be located [^r1].
* **Remedy:** Verify the packaging identifier and ensure the record exists before querying or posting.
* **Raised by:** Service `pkg_get` [^r1] and service `pkg_post` [^r2].
* **Detailed page:** [[err-pkg-0001|ERR-PKG-0001 Packaging information missing or unrecognised]]

### ERR-PKG-0007
* **Message:** RETURNABLE PACKAGING NOT IN DRAFT (<status>) [^r3]
* **Cause:** The returnable packaging record is not in draft status [^r3].
* **Remedy:** Ensure the packaging record is in draft status before attempting to post.
* **Raised by:** Service `pkg_post` [^r3].
* **Detailed page:** [[err-pkg-0007|ERR-PKG-0007 Invalid or duplicate packaging number]]

### ERR-PKG-0201
* **Message:** QTY MUST BE > 0 [^r4][^r5]
* **Cause:** A returnable packaging transaction was submitted with a quantity that is not greater than zero [^r4][^r5].
* **Remedy:** Specify a positive quantity greater than zero.
* **Raised by:** Service `pkg_save` [^r4] and service `pkg_search` [^r5].
* **Detailed page:** [[err-pkg-0201|ERR-PKG-0201 Packaging posting failure]]

## See also
* [[services-inv-pkg|INV pkg services]]
* [[screen-inv-pkg-15|INV-PKG-15 Returnable Packaging Entry]]
* [[err-pkg-0001|ERR-PKG-0001 Packaging information missing or unrecognised]]
* [[err-pkg-0007|ERR-PKG-0007 Invalid or duplicate packaging number]]
* [[err-pkg-0201|ERR-PKG-0201 Packaging posting failure]]

## References

[^r1]: 04_service_definitions/inventory/pkg_get.yaml, errors
[^r2]: 04_service_definitions/inventory/pkg_post.yaml, errors
[^r3]: 04_service_definitions/inventory/pkg_post.yaml, errors
[^r4]: 04_service_definitions/inventory/pkg_save.yaml, errors
[^r5]: 04_service_definitions/inventory/pkg_search.yaml, errors
