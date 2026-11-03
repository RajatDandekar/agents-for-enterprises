---
title: "INV-STK-02 Stock Status Enquiry"
type: "screen"
slug: "screen-inv-stk-02"
summary: "Ledgerline screen for querying item stock balances across warehouses, displaying on-hand, allocated, and on-order quantities, reorder levels, and cover days."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/purchase/stk_query.yaml", "11_training/QRC-08 Stock enquiry and days of cover.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | INV-STK-02 |
| Module | Inventory |
| Menu path | Inventory > Stock status |
| Access | ALL roles |
| Service | stk_query |
| Status | current |

Screen INV-STK-02 (Stock Status Enquiry) is a read-only enquiry screen in Ledgerline ERP used to look up inventory levels, allocations, open orders, and calculated cover days for an item[^r1][^r3][^r5]. Accessible to all roles at `Inventory > Stock status`, it allows queries for a specific warehouse or across both the Manchester and Leeds sites[^r4][^r8]. Stock on order is excluded from on-hand balances until goods clear incoming inspection, and stock allocations remain held against unposted picking lists or overdue assembly orders[^r9][^r10].

| Field / Attribute | Value |
|---|---|
| Screen code | INV-STK-02[^r4] |
| Title | Stock Status Enquiry[^r4] |
| Navigation | Inventory > Stock status[^r4] |
| Permitted roles | ALL[^r4] |
| Query service | `stk_query` (`POST /ll72/svc/stk_query`)[^r5][^r6] |
| Mode | Read-only[^r3][^r5] |

## Fields

The screen accepts selection parameters and displays stock ledger balances[^r1][^r4][^r5]:

* **Item code (`itm_cd`)**: Mandatory string input; supports F2 lookup via `itm_search`[^r1][^r4][^r6].
* **Warehouse (`whs_cd`)**: String input; supports F2 lookup via `whs_list`[^r4]. When specified, balances reflect that location; leaving it blank returns combined stock across both the Manchester and Leeds sites[^r1][^r6][^r8].
* **On hand (`on_hand`)**: Read-only integer showing physically held stock[^r1][^r5]. Goods on order do not reflect in this figure until purchase receipts clear incoming inspection[^r9].
* **Allocated (`allocated`)**: Read-only integer showing reserved inventory[^r1][^r5]. Unposted picking lists and overdue assembly orders retain allocations against this balance[^r10].
* **On order (`on_order`)**: Read-only integer showing outstanding purchase orders[^r1][^r5].
* **Average daily issue (`avg_daily_issue`)**: Read-only integer representing consumption rate[^r5].
* **Reorder level (`reorder_lvl`)**: Read-only integer target threshold[^r5].
* **Days of cover (`cover_days`)**: Read-only integer computed as `(on_hand - allocated) / avg_daily_issue`, rounded down[^r5][^r7].

The underlying stock ledger is read-only from this screen, and any stock corrections require a separate stock adjustment approved by the stores manager[^r3].

## Keys and services

* **Query button**: Executes read service `stk_query` via endpoint `POST /ll72/svc/stk_query` using mandatory field `itm_cd` and optional field `whs_cd`[^r5][^r6].
* **Close button**: Exits the enquiry screen[^r5].
* **F2**: Invokes search helpers `itm_search` on `itm_cd` and `whs_list` on `whs_cd`[^r4].

## Messages

* **[[err-stk-0001|ERR-STK-0001]]**: Raised if no stock row exists for the requested item and warehouse combination[^r5].

## Versions and conflicts

* **Days of cover calculation**: Service definition `stk_query.yaml` defines cover days as `(on_hand - allocated) / avg_daily_issue`, rounded down[^r7]. [[man-pur-72|MAN-PUR-72]] (§4.3) describes it as on-hand quantity divided by average daily issue, rounded down, omitting the deduction of allocated stock[^r2]. Kind: `contradiction`.
* **Warehouse field requirement**: Service definition `stk_query.yaml` and quick reference card QRC-08 document `whs_cd` as optional, permitting queries across both Manchester and Leeds when omitted[^r6][^r8]. [[man-pur-72|MAN-PUR-72]] (§4.2) also lists warehouse as optional[^r1]. Screen manual MAN-SCR-72 (p. 19) incorrectly lists `whs_cd` as a mandatory input field[^r4]. Kind: `contradiction`.

## See also

* [[err-stk-0001|ERR-STK-0001]]
* [[man-pur-72|MAN-PUR-72 Ledgerline ERP 7.2 User Manual, Purchasing]]
* [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]]
* [[screen-inv-itm-03|INV-ITM-03 Item Enquiry]]
* [[screen-qa-ins-01|QA-INS-01 Incoming Inspection Entry]]
* [[services-pur-stk|PUR stk services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 4, §4.2 Fields
[^r3]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 4, §4.4 The stock ledger
[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 20, INV-STK-02 STOCK STATUS ENQUIRY
[^r4]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 19, INV-STK-02 STOCK STATUS ENQUIRY
[^r8]: 11_training/QRC-08 Stock enquiry and days of cover.pdf, p. 1, Steps
[^r9]: 11_training/QRC-08 Stock enquiry and days of cover.pdf, p. 1, Tips / Calculating free stock
[^r10]: 11_training/QRC-08 Stock enquiry and days of cover.pdf, p. 1, Tips / Stock allocated to production
[^r6]: 04_service_definitions/purchase/stk_query.yaml, service: stk_query
[^r7]: 04_service_definitions/purchase/stk_query.yaml, notes
[^r2]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 4, §4.3 Reading the result
