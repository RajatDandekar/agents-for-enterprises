---
title: "ERR-CSG-* Error Messages"
type: "error-list"
slug: "errors-csg"
summary: "Reference list of ERR-CSG-* error codes raised during consignment stock transactions and service calls in Ledgerline Inventory."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "04_service_definitions/inventory/csg_get.yaml", "04_service_definitions/inventory/csg_save.yaml", "04_service_definitions/inventory/csg_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-CSG-* |
| Module | Inventory (INV) |
| Domain | Consignment Stock |
| Source Manual | MAN-INV-72 |

This page catalogues the `ERR-CSG-*` error codes raised by Ledgerline ERP consignment stock operations and backend services. These messages occur primarily during consignment lookups, searches, and record maintenance in the inventory module. Detailed root causes and operational remedies are covered on individual error pages where narrative sources provide them.

### ERR-CSG-0001
* **Message**: `CONSIGNMENT STOCK NOT FOUND` [^r1][^r3]
* **Cause**: Raised by service `csg_get` when the specified consignment reference (`csg_no`) cannot be located in the system [^r3].
* **Remedy**: Verify the entered consignment stock identifier and confirm that the record exists prior to retrieval.
* **Raised by**: `csg_get` in [[services-inv-csg|INV csg services]] [^r3], documented in [[man-inv-72|MAN-INV-72]] [^r1].
* **Detail page**: [[err-csg-0001|ERR-CSG-0001 CONSIGNMENT STOCK NOT FOUND]]

### ERR-CSG-0201
* **Message**: `QTY MUST BE > 0` [^r2][^r4][^r5]
* **Cause**: Raised when saving consignment stock with a quantity less than or equal to zero, or encountered during consignment stock operations such as `csg_search` [^r4][^r5].
* **Remedy**: Enter a valid positive quantity greater than zero before saving or executing the operation.
* **Raised by**: `csg_save` and `csg_search` in [[services-inv-csg|INV csg services]] [^r4][^r5], documented in [[man-inv-72|MAN-INV-72]] [^r2].
* **Detail page**: [[err-csg-0201|ERR-CSG-0201 QTY MUST BE > 0 / Invalid Consignment Status]]

## See also
* [[services-inv-csg|INV csg services]]
* [[screen-inv-csg-17|INV-CSG-17 Consignment Stock Entry]]
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]
* [[errors-inv|Errors INV (ERR-INV-*)]]
* [[err-csg-0001|ERR-CSG-0001 CONSIGNMENT STOCK NOT FOUND]]
* [[err-csg-0201|ERR-CSG-0201 QTY MUST BE > 0 / Invalid Consignment Status]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 68, §20. Messages
[^r3]: 04_service_definitions/inventory/csg_get.yaml, errors
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 68, §20. Messages
[^r4]: 04_service_definitions/inventory/csg_save.yaml, errors
[^r5]: 04_service_definitions/inventory/csg_search.yaml, errors
