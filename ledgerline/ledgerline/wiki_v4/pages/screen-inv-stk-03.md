---
title: "INV-STK-03 Stock Val"
type: "screen"
slug: "screen-inv-stk-03"
summary: "INV-STK-03 Stock Val provides centralized valuation, movement, aging, ABC analysis, and snapshot processing across Manchester and Leeds inventory."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/stk_abc_run.yaml", "04_service_definitions/inventory/stk_age_query.yaml", "04_service_definitions/inventory/stk_move_query.yaml", "04_service_definitions/inventory/stk_snapshot.yaml", "04_service_definitions/inventory/stk_val_query.yaml", "04_service_definitions/inventory/stk_val_run.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | INV-STK-03 |
| Title | Stock Val |
| Menu path | Inventory > Stock val |
| Authorized roles | STORES, STORES-MGR, PUR-EXEC, SYS-ADMIN |
| Primary services | stk_val_query, stk_val_run, stk_age_query, stk_abc_run, stk_move_query, stk_snapshot |

Screen INV-STK-03 (Stock Val) provides centralized visibility and processing routines for physical inventory, valuation balances, stock movements, and categorisation across Manchester and Leeds[^r2]. It is accessed by inventory, purchasing, and system administration roles to inspect stock values and run valuation recalibrations[^r6]. The screen also supports creating frozen inventory balance snapshots stamped with explanatory comments without altering general ledger accounts[^r1][^r5].

## Fields

* **ITM CD** (`itm_cd`): Mandatory item code[^r1][^r6]. Leaving this field blank and pressing **Val Query** (`stk_val_query`) retrieves a consolidated valuation view across all current parts[^r3].
* **COMMENT** (`comment`): Optional text field used to annotate snapshot records[^r1][^r5][^r6].

## Keys and services

INV-STK-03 exposes six operational buttons mapped to underlying [[services-inv-stk|INV stk services]][^r7][^r8]:

* **Val Query** (`stk_val_query`): Read service to inspect item or plant-wide valuation details[^r3][^r7][^r8][^r13].
* **Val Run** (`stk_val_run`): Write service (`POST /ll72/svc/stk_val_run`) executing stored procedure `sp_stk_val_run` to recalculate costs, update unit values from posted purchase variances, and refresh general ledger summary balances[^r4][^r7][^r8][^r14].
* **Age Query** (`stk_age_query`): Read service executing stock aging enquiries[^r7][^r8][^r10].
* **Abc Run** (`stk_abc_run`): Write service to execute inventory ABC analysis categorisations[^r7][^r8][^r9].
* **Move Query** (`stk_move_query`): Read service to retrieve historical stock movements[^r7][^r8][^r11].
* **Snapshot** (`stk_snapshot`): Read service that freezes current stock balances and copies quantities and valuations to snapshot storage tables stamped with `comment` without altering general ledger balances[^r5][^r7][^r8][^r12].

## Messages

The screen raises the following validation and processing errors:

* [[err-stk-0001|ERR-STK-0001]]: Raised during stock valuation and run processing errors[^r7].
* [[err-itm-0011|ERR-ITM-0011]]: Raised when an entered item code is not found or inactive[^r7].

See also the reference catalogues [[errors-stk|ERR-STK Error Codes]] and [[errors-itm|ERR-ITM error codes]].

## Versions and conflicts

* **Valuation run and snapshot behaviour**: Under current manual `MAN-INV-72` v7.2.3 (effective 2025-01-15), executing `stk_val_run` recalculates costs, integrates posted purchase variances, and updates general ledger summary balances, while `stk_snapshot` writes to snapshot storage tables without affecting GL balances[^r4][^r5]. In superseded manual `MAN-INV-72` v7.2.2 (2024-06-10), `stk_val_run` posted valuation totals to GL holding accounts and `stk_snapshot` wrote to archive tables for stocktake audit files[^r16][^r17] (`superseded`).

## See also

* [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]]
* [[screen-inv-cnt-06|INV-CNT-06 Stock Count Entry]]
* [[screen-inv-adj-05|INV-ADJ-05 Stock Adjustment Entry]]
* [[screen-inv-trf-04|INV-TRF-04 Stock Transfer Entry]]
* [[services-inv-stk|INV stk services]]
* [[err-stk-0001|ERR-STK-0001]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]

## References

[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 45, Purpose
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 20, INV-STK-03 STOCK VAL
[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 45, §14. Stock (INV-STK-03)
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 47, Step by step
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 46, Step by step
[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 20, INV-STK-03 STOCK VAL
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 19, stk_val_query STOCK VAL QUERY
[^r13]: 04_service_definitions/inventory/stk_val_query.yaml, whole file
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 46, Step by step
[^r14]: 04_service_definitions/inventory/stk_val_run.yaml, screen
[^r10]: 04_service_definitions/inventory/stk_age_query.yaml, screen
[^r9]: 04_service_definitions/inventory/stk_abc_run.yaml, service: stk_abc_run
[^r11]: 04_service_definitions/inventory/stk_move_query.yaml, service: stk_move_query
[^r12]: 04_service_definitions/inventory/stk_snapshot.yaml, service: stk_snapshot
[^r16]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 20, Step by step
[^r17]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 20, Step by step
