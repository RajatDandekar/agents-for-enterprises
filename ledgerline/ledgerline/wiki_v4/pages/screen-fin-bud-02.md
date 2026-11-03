---
title: "FIN-BUD-02 Budget Entry"
type: "screen"
slug: "screen-fin-bud-02"
summary: "Ledgerline screen for entering, querying, and transferring cost centre budgets using bud_query, bud_save, and bud_transfer services."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/admin/bud_query.yaml", "04_service_definitions/admin/bud_save.yaml", "04_service_definitions/admin/bud_transfer.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen Code | FIN-BUD-02 |
| Screen Title | Budget Entry |
| Module | FIN / ADM |
| Write Service | bud_save |
| Read Service | bud_query |
| Transfer Service | bud_transfer |
| Status | current |

FIN-BUD-02 (Budget Entry) is the Ledgerline screen used to maintain, query, and transfer cost centre budget allocations [^r1][^r3][^r5]. It requires mandatory entry of the cost centre code, budget period, and allocation amount [^r1]. The screen executes backend updates via stored procedures to persist budget lines and process budget transfers [^r4][^r5].

## Fields

| Field | Parameter | Mandatory | Description |
|---|---|---|---|
| CC CD | `cc_cd` | Yes | Cost centre code [^r1]. |
| PERIOD | `period` | Yes | Budget accounting period [^r1]. |
| AMOUNT | `amount` | Yes | Budget allocation amount [^r1]. |

## Keys and services

* Read operations invoke the backend query service `bud_query` to retrieve budget details [^r3].
* Record saves invoke the `bud_save` write service via `POST /ll72/svc/bud_save`, executing stored procedure `sp_bud_save` [^r4].
* Budget reallocations execute the `bud_transfer` service against stored procedure `sp_bud_transfer` [^r5].
* Detailed service definitions and schemas are maintained under [[services-adm-bud|ADM bud services]] [^r3][^r4][^r5].

## Messages

* [[err-cc-0009|ERR-CC-0009]]: Cost Centre Not Found [^r2].
* `ERR-BUD-0001`: Budget Not Found [^r2].
* `ERR-BUD-0207`: Budget Exceeded For <Cc_Cd> [^r2].

## See also

* [[err-cc-0009|ERR-CC-0009]]
* [[screen-fin-cc-01|FIN-CC-01 Cost Centre Entry]]
* [[services-adm-bud|ADM bud services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 11, FIN-BUD-02 BUDGET ENTRY
[^r3]: 04_service_definitions/admin/bud_query.yaml, screen
[^r5]: 04_service_definitions/admin/bud_transfer.yaml, whole file
[^r4]: 04_service_definitions/admin/bud_save.yaml, screen: FIN-BUD-02
[^r2]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 11, FIN-BUD-02 BUDGET ENTRY
