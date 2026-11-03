---
title: "INV-BIN-09 Bin Master Entry"
type: "screen"
slug: "screen-inv-bin-09"
summary: "Ledgerline screen to create, manage, search, and block warehouse storage bins across Manchester and Leeds sites."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/bin_block.yaml", "04_service_definitions/inventory/bin_get.yaml", "04_service_definitions/inventory/bin_save.yaml", "04_service_definitions/inventory/bin_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | INV-BIN-09 |
| Screen title | Bin Master Entry |
| Menu path | Inventory > Bin master |
| Status | current |
| Services | bin_save, bin_get, bin_search, bin_block |

INV-BIN-09 is the Ledgerline screen located at Inventory > Bin master used to establish and manage storage bin locations across the Manchester and Leeds sites [^r1][^r3]. An active parent warehouse record must exist before a bin can be created on this screen [^r3]. The screen is serviced by [[services-inv-bin|INV bin services]] including `bin_save`, `bin_get`, `bin_search`, and `bin_block` [^r1][^r12].

| Attribute | Value |
|---|---|
| Screen code | INV-BIN-09 [^r1] |
| Screen title | Bin Master Entry [^r10] |
| Menu path | Inventory > Bin master [^r1] |
| Status | current [^r1] |
| Services | bin_save, bin_get, bin_search, bin_block [^r1][^r12] |

## Fields

* **WHS CD**: Mandatory parent warehouse code [^r2][^r16].
* **BIN CD**: Mandatory bin identifier [^r2][^r16].
* **BIN TYPE**: Non-mandatory classification designating bulk storage, picking, incoming inspection, quarantine, or assembly line replenishment [^r2][^r4][^r16].
* **MAX QTY**: Non-mandatory capacity limit for the location [^r2][^r4][^r16].
* **STATUS**: Non-mandatory status field, defaulting to active or set to pending if awaiting rack safety inspection [^r2][^r6].
* **REASON**: Non-mandatory operational justification entered when blocking or updating the bin record [^r2][^r7][^r8].

When creating a new record, `WHS CD`, `BIN CD`, `BIN TYPE`, `MAX QTY`, and `STATUS` are entered and committed using `bin_save` [^r6]. To return a suspended location to normal operation, the record is retrieved, `REASON` is cleared or updated, `STATUS` is set back to active, and changes are committed via `bin_save` [^r8].

## Keys and services

* **Search (F2 / Enter)**: Invokes the read service `bin_search` (BIN MASTER LIST, endpoint `POST /ll72/svc/bin_search`) using `whs_cd` and leading characters of `bin_cd`, or optional parameters `bin_type` and `status`, to locate bins [^r5][^r10][^r17].
* **Get (F3)**: Calls the read service `bin_get` (endpoint `POST /ll72/svc/bin_get`) using mandatory parameter `bin_cd` to populate the form [^r5][^r10][^r14].
* **Save (F8)**: Invokes the write service `bin_save` via stored procedure `sp_bin_save` requiring `WHS CD` and `BIN CD`, with optional fields `BIN TYPE` and `MAX QTY`, to create or update the record [^r6][^r10][^r15][^r16].
* **Block**: Calls write service `bin_block` (endpoint `POST /ll72/svc/bin_block`) using mandatory field `bin_cd` and optional field `reason` to halt putaway or restrict the location [^r7][^r10][^r13].

## Messages

* [[err-bin-0001|ERR-BIN-0001]] (Bin Master Not Found): Raised when mandatory fields are omitted, the location reference contains invalid formatting, or the combination of `WHS CD` and `BIN CD` does not exist or conflicts [^r9][^r11].

## Versions and conflicts

* **Superseded user instructions (2025-01-15 vs 2024-06-10)**: Current manual MAN-INV-72 v7.2.3 establishes bin management across Manchester and Leeds sites using `bin_save`, `bin_get`, `bin_search`, and `bin_block` at menu location Inventory > Bin master [^r1][^r3]. The superseded manual MAN-INV-72 v7.2.2 described stores supervisors and inventory clerks using the screen to register and maintain physical racking, floor bays, and assembly staging areas across Manchester and Leeds sites [^r18][^r19][^r20]. Kind: `superseded` [^r1][^r3][^r18][^r19][^r20].

## See also

* [[err-bin-0001|ERR-BIN-0001 Location not found or invalid format]]
* [[services-inv-bin|INV bin services]]
* [[screen-inv-whs-01|INV-WHS-01 Warehouse Master]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 22, §8. Bin Master (INV-BIN-09)
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 22, Before you start
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 15, bin_save BIN MASTER SAVE
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 12, INV-BIN-09 BIN MASTER ENTRY
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 22, §8. Bin Master (INV-BIN-09)
[^r16]: 04_service_definitions/inventory/bin_save.yaml, request.fields
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 22, Screen overview
[^r6]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 23, Creating a new bin record
[^r7]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 24, Restricting or blocking a location
[^r8]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 25, Questions users ask
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 23, Searching for an existing bin
[^r17]: 04_service_definitions/inventory/bin_search.yaml, screen
[^r14]: 04_service_definitions/inventory/bin_get.yaml, whole file
[^r15]: 04_service_definitions/inventory/bin_save.yaml, whole file
[^r13]: 04_service_definitions/inventory/bin_block.yaml, whole file
[^r9]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 24, Messages
[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 12, INV-BIN-09 BIN MASTER ENTRY
[^r18]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 11, Bin Master (INV-BIN-09)
[^r19]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 10, §8. Bin Master (INV-BIN-09)
[^r20]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 11, Step by step
