---
title: "INV-KBN-13 Kanban Card Entry"
type: "screen"
slug: "screen-inv-kbn-13"
summary: "Ledgerline screen INV-KBN-13 configures, searches, signals replenishment for, and closes shop-floor Kanban card loops across Manchester and Leeds assembly operations."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/kbn_close.yaml", "04_service_definitions/inventory/kbn_get.yaml", "04_service_definitions/inventory/kbn_save.yaml", "04_service_definitions/inventory/kbn_search.yaml", "04_service_definitions/inventory/kbn_signal.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | INV-KBN-13 |
| Screen title | Kanban Card Entry |
| Module | Inventory (INV) |
| Introduced | Ledgerline 7.2.0 |
| Status | Current |

Screen INV-KBN-13 establishes, tracks, and signals shop-floor replenishable loops for assembly operations across Manchester and Leeds [^r2]. Introduced in Ledgerline 7.2.0, it allows users to set up cards, query existing loops, broadcast replenishment requests to warehouse pickers, and close out retired or fulfilled cycles [^r2][^r4][^r5][^r8].

| Key | Value |
|---|---|
| Screen Code | INV-KBN-13 [^r1] |
| Screen Title | KANBAN CARD ENTRY [^r7] |
| Module | Inventory [^r1] |
| Introduced | Ledgerline 7.2.0 [^r8] |
| Status | Current [^r1] |

## Fields

The screen contains the following fields for defining and managing Kanban cards:

* **ITEM CD (`itm_cd`)**: Item code; mandatory [^r1][^r7]. Also functions as a filter for card search [^r13].
* **WHS CD (`whs_cd`)**: Warehouse code; mandatory [^r1][^r7]. Supported as a search filter [^r13].
* **BIN QTY (`bin_qty`)**: Bin quantity; mandatory [^r1][^r7]. Supported as a search filter [^r13].
* **KBN NO (`kbn_no`)**: Kanban card number; mandatory on the form [^r1][^r7], but optional during initial loop entry before card generation [^r3].
* **NO OF CARDS (`cards`)**: Number of cards; optional [^r1][^r3][^r7].
* **STATUS (`status`)**: Status indicator; optional on entry, updated during card lifecycle transitions; functions as a search filter [^r1][^r4][^r5][^r7][^r13].
* **COMMENT (`comment`)**: Narrative remarks; optional [^r1][^r3][^r7][^r9][^r14].

## Keys and services

INV-KBN-13 interacts with the backend through five dedicated services grouped under [[services-inv-kbn]]:

* **F8 (`kbn_save`)**: Executes write service `kbn_save` via endpoint `POST /ll72/svc/kbn_save` to persist or update Kanban card records [^r3][^r8][^r11][^r15].
* **`kbn_get`**: Executes read service `kbn_get` using card key `kbn_no` to retrieve record details [^r4][^r8][^r10][^r15].
* **F2 / Enter (`kbn_search`)**: Executes read service `kbn_search` via endpoint `POST /ll72/svc/kbn_search` to query and list cards using filters `itm_cd`, `whs_cd`, `bin_qty`, and `status` [^r8][^r12][^r13][^r15].
* **`kbn_signal`**: Executes write service `kbn_signal` passing `kbn_no` and an optional `comment` to flag `status` for replenishment and notify warehouse pickers [^r4][^r8][^r14][^r15].
* **`kbn_close`**: Executes write service `kbn_close` via endpoint `POST /ll72/svc/kbn_close` passing mandatory `kbn_no` and optional `comment` [^r8][^r9][^r15]. This marks `status` as closed or retired to disable triggers when an assembly run completes or a container is decommissioned [^r5], or clears the open replenishment request once a replenished bin arrives at the line so the card can return to circulation [^r6].

## Messages

The screen can return the following validation and processing errors:

* [[err-itm-0011]]: Raised if the specified item code is missing or inactive [^r15].
* [[err-kbn-0001]]: Raised if the card identifier cannot be found or if a duplicate replenishment signal is triggered [^r15].
* [[err-kbn-0801]]: Raised on invalid card status transitions or warehouse validation failures [^r15].

## Versions and conflicts

* **Card closing workflow**: Under current manual MAN-INV-72 v7.2.3 (effective 2025-01-15), calling `kbn_close` retires a card loop and disables replenishment triggers when an assembly run finishes or a container is retired, or clears the open request when a replenished bin reaches the assembly line [^r5][^r6]. Superseded manual MAN-INV-72 v7.2.2 (dated 2024-06-10) previously defined `kbn_close` strictly as clearing the request once stock was returned to the bin [^r17] (`superseded`).

## See also

* [[services-inv-kbn]]
* [[err-itm-0011]]
* [[err-kbn-0001]]
* [[err-kbn-0801]]
* [[screen-inv-itm-01]]
* [[screen-inv-whs-01]]
* [[screen-inv-bin-09]]

## References

[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 49, Section INV-KBN-13: Kanban Card
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 51, Step by step: Signalling replenishment
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 51, Step by step: Closing a card loop
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 21, kbn_save KANBAN CARD SAVE
[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 49, §15. Kanban Card (INV-KBN-13)
[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 15, INV-KBN-13 KANBAN CARD ENTRY
[^r13]: 04_service_definitions/inventory/kbn_search.yaml, request.fields
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 50, Step by step: Setting up a new card
[^r9]: 04_service_definitions/inventory/kbn_close.yaml, service
[^r14]: 04_service_definitions/inventory/kbn_signal.yaml, service: kbn_signal
[^r11]: 04_service_definitions/inventory/kbn_save.yaml, service: kbn_save
[^r15]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 15, INV-KBN-13 KANBAN CARD ENTRY
[^r10]: 04_service_definitions/inventory/kbn_get.yaml, screen: INV-KBN-13
[^r12]: 04_service_definitions/inventory/kbn_search.yaml, service: kbn_search
[^r6]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 52, Worked example
[^r17]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 22, Step by step
