---
title: "INV-PKG-15 Returnable Packaging Entry"
type: "screen"
slug: "screen-inv-pkg-15"
summary: "Ledgerline screen for managing and posting returnable packaging entries, containers, and balances under Inventory."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/pkg_get.yaml", "04_service_definitions/inventory/pkg_post.yaml", "04_service_definitions/inventory/pkg_save.yaml", "04_service_definitions/inventory/pkg_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | INV-PKG-15 |
| Module | Inventory |
| Path | Inventory > Returnable packaging |
| Primary services | pkg_save, pkg_get, pkg_search, pkg_post |
| Status | current |

Screen INV-PKG-15 is the Ledgerline interface used to record, search, retrieve, and post returnable packaging entries under the Inventory module [^r1]. It tracks reusable containers associated with vendor shipments by managing packaging numbers and quantities before posting movements to inventory ledger balances [^r2][^r5]. The screen operates against the returnable packaging service group and enforces supplier validation and unique container tracking [^r1][^r7][^r9].

| Field | Description |
|---|---|
| Screen code | INV-PKG-15 [^r1] |
| Module | Inventory [^r1] |
| Navigation | Inventory > Returnable packaging [^r1] |
| Primary services | pkg_save, pkg_get, pkg_search, pkg_post [^r1] |
| Status | Current [^r1] |

## Fields

Screen INV-PKG-15 contains both mandatory and optional entry fields [^r2][^r14]:
* **SUP CD** (`sup_cd`): Mandatory supplier code [^r2][^r14][^r20].
* **PKG TYPE** (`pkg_type`): Mandatory returnable packaging container type [^r2][^r14][^r20].
* **QTY** (`qty`): Mandatory packaging quantity [^r2][^r14][^r20]. Leaving this field blank halts processing [^r10].
* **PKG NO** (`pkg_no`): Mandatory packaging identification number [^r2][^r14].
* **STATUS** (`status`): Optional status field [^r2][^r14]. Updated to confirmed upon successful posting [^r12].
* **COMMENT** (`comment`): Optional narrative comment [^r2][^r14].

## Keys and services

INV-PKG-15 interfaces with four returnable packaging services [^r1][^r15][^r16]:
* **`pkg_save` (F8)**: Invokes write service `POST /ll72/svc/pkg_save` to record returnable packaging entries with required fields `sup_cd`, `pkg_type`, and `qty` [^r15][^r19][^r20].
* **`pkg_get` (F3)**: Calls the read service to retrieve an exact returnable packaging record using `pkg_no` and `sup_cd` [^r4][^r15][^r17].
* **`pkg_search` (F2/Enter)**: Executes the read service `POST /ll72/svc/pkg_search` (RETURNABLE PACKAGING LIST) to populate matching container lines using `sup_cd` and optional criteria such as `pkg_type`, `qty`, and `status` [^r3][^r15][^r21][^r22]. Unposted packaging sheets can be queried by supplying `sup_cd`, leaving `pkg_no` blank, pressing `pkg_search`, and loading selected rows via `pkg_get` [^r13].
* **`pkg_post` (F9)**: Calls the write service RETURNABLE PACKAGING POST to commit validated saved records directly to site inventory ledger balances and update the entry `status` to confirmed [^r5][^r12][^r15][^r18].

## Messages

The screen raises the following validation and processing messages [^r15]:
* [[err-pkg-0001]]: Triggered when `pkg_type` is blank or invalid, or if `qty` is zero, blank, or outside acceptable entry rules [^r6][^r10].
* [[err-pkg-0007]]: Triggered when `pkg_no` violates the expected pattern for that packaging type, or when saving an entry where the combination of crate reference and supplier code is already open or exists as an active on-site duplicate [^r7][^r11].
* [[err-pkg-0201]]: Raised during `pkg_post` if posting fails because the entry was not saved first, carries an invalid status, is locked, or if a database lock on the packaging control register cannot be secured [^r8][^r12].
* [[err-sup-0030]]: Raised when the entered `sup_cd` does not exist in the master file or corresponds to a supplier account that is closed, suspended, or prohibited from inventory transactions [^r9].

## Versions and conflicts

* **Error definitions for ERR-PKG-0001 and ERR-PKG-0007**: Under current documentation (MAN-INV-72 v7.2.3), [[err-pkg-0001]] indicates a missing or invalid packaging type or zero/invalid quantity, while [[err-pkg-0007]] flags active duplicate package numbers or pattern mismatches [^r6][^r7]. In superseded manual MAN-INV-72 v7.2.2 (effective 2024-06-10), ERR-PKG-0001 indicated that the reference did not exist and ERR-PKG-0007 meant the quantity was invalid or exceeded receipt [^r25]. Kind: `superseded`.
* **Posting status lifecycle and ERR-PKG-0201**: Under v7.2.3, successful posting via `pkg_post` marks the record as confirmed, and [[err-pkg-0201]] occurs when an entry is not saved, is locked, or has an invalid status [^r8][^r12]. Under superseded v7.2.2, `pkg_save` set status to open, `pkg_post` set status to posted, and ERR-PKG-0201 indicated an attempt to update an already posted movement [^r24][^r25]. Kind: `superseded`.

## See also

* [[services-inv-pkg|INV pkg services]]
* [[err-pkg-0001|ERR-PKG-0001 Packaging information missing or unrecognised]]
* [[err-pkg-0007|ERR-PKG-0007 Invalid or duplicate packaging number]]
* [[err-pkg-0201|ERR-PKG-0201 Packaging posting failure]]
* [[err-sup-0030|ERR-SUP-0030]]
* [[screen-inv-scr-16|INV-SCR-16 Scrap Note Entry]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 56, §17. Returnable Packaging (INV-PKG-15)
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 56, §17. Returnable Packaging (INV-PKG-15)
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 58, Step by step
[^r7]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 59, Messages
[^r9]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 59, Messages
[^r14]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 17, INV-PKG-15 RETURNABLE PACKAGING ENTRY
[^r20]: 04_service_definitions/inventory/pkg_save.yaml, request.fields
[^r10]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 60, §18. Scrap Note (INV-SCR-16)
[^r12]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 60, §18. Scrap Note (INV-SCR-16)
[^r15]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 17, INV-PKG-15 RETURNABLE PACKAGING ENTRY
[^r16]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 23, pkg_post RETURNABLE PACKAGING POST
[^r19]: 04_service_definitions/inventory/pkg_save.yaml, screen
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 58, Step by step
[^r17]: 04_service_definitions/inventory/pkg_get.yaml, whole file
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 58, Step by step
[^r21]: 04_service_definitions/inventory/pkg_search.yaml, service: pkg_search
[^r22]: 04_service_definitions/inventory/pkg_search.yaml, request.fields
[^r13]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 60, Questions users ask
[^r18]: 04_service_definitions/inventory/pkg_post.yaml, screen
[^r6]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 58, Messages
[^r11]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 60, §18. Scrap Note (INV-SCR-16)
[^r8]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 59, Messages
[^r25]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 25, Messages
[^r24]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 25, Step by step
