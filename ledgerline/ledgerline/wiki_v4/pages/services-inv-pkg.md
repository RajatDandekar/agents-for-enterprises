---
title: "INV pkg services"
type: "service-group"
slug: "services-inv-pkg"
summary: "Ledgerline INV services pkg_save, pkg_post, pkg_get, and pkg_search for managing returnable packaging entries and balance updates on screen INV-PKG-15."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/pkg_get.yaml", "04_service_definitions/inventory/pkg_post.yaml", "04_service_definitions/inventory/pkg_save.yaml", "04_service_definitions/inventory/pkg_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | INV |
| Target screen | INV-PKG-15 |
| Services | pkg_save, pkg_post, pkg_get, pkg_search |
| Transport | POST /ll72/svc/pkg_* |
| Authentication | Header X-LL-Session |
| Availability | Ledgerline 7.0 or higher |
| Backend procedures | sp_pkg_save, sp_pkg_post |

The `pkg` service group provides backend functions for managing returnable packaging records within the Inventory (INV) module on screen [[screen-inv-pkg-15|INV-PKG-15]]. Available since Ledgerline version 7.0, these services handle creating, searching, fetching, and posting returnable container entries to track balance adjustments against suppliers [^r13][^r17][^r22][^r28]. All calls operate via HTTP POST under `/ll72/svc/`, requiring session token authentication in the `X-LL-Session` header and appropriate user role authorization [^r14][^r18][^r23][^r29].

## Services

### pkg_save

The `pkg_save` service is a write operation that validates input against master tables and establishes an intact, unposted returnable packaging transaction using backend stored procedure `sp_pkg_save` [^r1][^r9][^r22][^r25]. It retains draft returnable packaging records and validates that the supplier and crate reference combination is not already open [^r5].

* **Endpoint:** `POST /ll72/svc/pkg_save` [^r23]
* **Required fields:** `sup_cd` (string, supplier code), `pkg_type` (string, package type), and `qty` (integer, quantity) [^r9][^r24].
* **Optional fields:** None [^r24].
* **Errors:** Specific error codes [[err-pkg-0201|ERR-PKG-0201]] ('QTY MUST BE > 0'), [[err-sup-0030|ERR-SUP-0030]] ('SUPPLIER NOT FOUND'), and [[err-pkg-0007|ERR-PKG-0007]] on duplicate open entries; common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r5][^r9][^r26][^r27].
* **Source files:** `04_service_definitions/inventory/pkg_save.yaml`, `MAN-SVC-72 v7.2.3`, `MAN-INV-72 v7.2.3` [^r1][^r5][^r9][^r22][^r23][^r24][^r25][^r26][^r27].

### pkg_post

The `pkg_post` service is a write operation that commits a saved packaging record to inventory balance files, adjusting the packaging register and locking values permanently using backend procedure `sp_pkg_post` [^r2][^r17][^r21]. It updates record status to confirmed [^r6].

* **Endpoint:** `POST /ll72/svc/pkg_post` [^r17]
* **Required fields:** `pkg_no` (string, PKG NO) [^r12][^r19].
* **Optional fields:** `comment` (string, COMMENT) [^r12][^r19].
* **Errors:** [[err-pkg-0001|ERR-PKG-0001]], [[err-pkg-0007|ERR-PKG-0007]], and [[err-pkg-0201|ERR-PKG-0201]] (raised if another station holds a lock on the packaging control register) [^r6][^r12].
* **Source files:** `04_service_definitions/inventory/pkg_post.yaml`, `MAN-SVC-72 v7.2.3`, `MAN-INV-72 v7.2.3` [^r2][^r6][^r12][^r17][^r18][^r19][^r20][^r21].

### pkg_get

The `pkg_get` service is a read operation titled RETURNABLE PACKAGING GET that retrieves an individual container record and loads full line entries into the active session from a selected packaging header [^r3][^r8][^r10][^r13].

* **Endpoint:** `POST /ll72/svc/pkg_get` [^r14]
* **Required fields:** `pkg_no` (string, PKG NO) [^r10][^r15].
* **Optional fields:** None [^r15].
* **Errors:** [[err-pkg-0001|ERR-PKG-0001]] (RETURNABLE PACKAGING NOT FOUND), ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r10][^r16].
* **Source files:** `04_service_definitions/inventory/pkg_get.yaml`, `MAN-SVC-72 v7.2.3`, `MAN-INV-72 v7.2.3` [^r3][^r8][^r10][^r13][^r14][^r15][^r16].

### pkg_search

The `pkg_search` service is a read operation titled RETURNABLE PACKAGING LIST that returns a grid of open container records and sessions matching filters [^r4][^r7][^r11][^r28].

* **Endpoint:** `POST /ll72/svc/pkg_search` [^r29]
* **Required fields:** None [^r30].
* **Optional fields:** `sup_cd` (str), `pkg_type` (str), `qty` (int), and `status` (str) [^r11][^r30].
* **Errors:** [[err-pkg-0201|ERR-PKG-0201]] ('QTY MUST BE > 0'), ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r11][^r31].
* **Source files:** `04_service_definitions/inventory/pkg_search.yaml`, `MAN-SVC-72 v7.2.3`, `MAN-INV-72 v7.2.3` [^r4][^r7][^r11][^r28][^r29][^r30][^r31].

## Versions and conflicts

* **Record status values on save and post:** Today under [[man-inv-72|MAN-INV-72 v7.2.3]] (2025-01-15), `pkg_save` establishes an unposted draft transaction and `pkg_post` commits packaging balances to site inventory while updating status to confirmed [^r1][^r5][^r6]. In superseded manual MAN-INV-72 v7.2.2 (2024-06-10), `pkg_save` assigned status open and `pkg_post` updated status to posted (`superseded`) [^r32].

## See also

* [[screen-inv-pkg-15|INV-PKG-15 Returnable Packaging Entry]]
* [[errors-pkg|ERR-PKG Error Codes]]
* [[err-pkg-0001|ERR-PKG-0001 Packaging information missing or unrecognised]]
* [[err-pkg-0007|ERR-PKG-0007 Invalid or duplicate packaging number]]
* [[err-pkg-0201|ERR-PKG-0201 Packaging posting failure]]
* [[err-sup-0030|ERR-SUP-0030]]
* [[screen-inv-scr-16|INV-SCR-16 Scrap Note Entry]]
* [[services-inv-scr|INV scr services]]

## References

[^r13]: 04_service_definitions/inventory/pkg_get.yaml, whole file
[^r17]: 04_service_definitions/inventory/pkg_post.yaml, service: pkg_post
[^r22]: 04_service_definitions/inventory/pkg_save.yaml, service: pkg_save
[^r28]: 04_service_definitions/inventory/pkg_search.yaml, service: pkg_search
[^r14]: 04_service_definitions/inventory/pkg_get.yaml, whole file
[^r18]: 04_service_definitions/inventory/pkg_post.yaml, auth
[^r23]: 04_service_definitions/inventory/pkg_save.yaml, endpoint
[^r29]: 04_service_definitions/inventory/pkg_search.yaml, endpoint
[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 58, Step by step
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 22, pkg_save RETURNABLE PACKAGING SAVE
[^r25]: 04_service_definitions/inventory/pkg_save.yaml, response
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 60, §18. Scrap Note (INV-SCR-16)
[^r24]: 04_service_definitions/inventory/pkg_save.yaml, request.fields
[^r26]: 04_service_definitions/inventory/pkg_save.yaml, errors
[^r27]: 04_service_definitions/inventory/pkg_save.yaml, common_errors
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 58, Step by step
[^r21]: 04_service_definitions/inventory/pkg_post.yaml, procedures
[^r6]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 60, §18. Scrap Note (INV-SCR-16)
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 23, pkg_post RETURNABLE PACKAGING POST
[^r19]: 04_service_definitions/inventory/pkg_post.yaml, request.fields
[^r20]: 04_service_definitions/inventory/pkg_post.yaml, response.envelope
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 58, Step by step
[^r8]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 60, Questions users ask
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 22, pkg_get RETURNABLE PACKAGING GET
[^r15]: 04_service_definitions/inventory/pkg_get.yaml, request.fields
[^r16]: 04_service_definitions/inventory/pkg_get.yaml, errors
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 58, Step by step
[^r7]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 60, Questions users ask
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 22, pkg_search RETURNABLE PACKAGING LIST
[^r30]: 04_service_definitions/inventory/pkg_search.yaml, request.fields
[^r31]: 04_service_definitions/inventory/pkg_search.yaml, errors
[^r32]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 25, Step by step
