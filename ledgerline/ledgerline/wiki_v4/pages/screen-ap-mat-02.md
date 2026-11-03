---
title: "AP-MAT-02 Three-Way Match"
type: "screen"
slug: "screen-ap-mat-02"
summary: "AP-MAT-02 Three-Way Match screen compares supplier invoices against purchase order lines and goods receipt notes, supporting runs, overrides, and tolerance checks."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/accounts_payable/mat_get.yaml", "04_service_definitions/accounts_payable/mat_override.yaml", "04_service_definitions/accounts_payable/mat_run.yaml", "04_service_definitions/accounts_payable/mat_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | AP-MAT-02 |
| Module | Accounts payable |
| Menu path | Accounts payable > Three-Way match |
| Roles | AP-CLERK, AP-MGR, FIN-CTRL, SYS-ADMIN |
| Read services | mat_get, mat_search |
| Write services | mat_run, mat_override |

Screen AP-MAT-02 runs the automated three-way matching process in Ledgerline, comparing supplier invoice details with linked purchase order lines and warehouse receipt lines [^r1][^r3]. It is accessed at menu path Accounts payable > Three-Way match by users assigned to roles AP-CLERK, AP-MGR, FIN-CTRL, and SYS-ADMIN [^r1][^r6]. The screen allows senior accounts staff to review match discrepancies and execute management overrides with an explanatory comment [^r4].

| Attribute | Details |
|---|---|
| Screen code | AP-MAT-02 |
| Menu path | Accounts payable > Three-Way match |
| Module | Accounts payable |
| Accessible roles | AP-CLERK, AP-MGR, FIN-CTRL, SYS-ADMIN |
| Underlying services | `mat_run`, `mat_get`, `mat_override`, `mat_search` |

## Fields

| Field label | Parameter | Type | Required | Description |
|---|---|---|---|---|
| AP DOC | `ap_doc` | str | Yes | Accounts payable document identifier [^r2][^r7]. |
| COMMENT | `comment` | str | No | Explanation recorded in the audit log when overriding match holds; mandatory when running overrides [^r2][^r4][^r5][^r7]. |
| TOL % | `tol_pct` | float | No | Tolerance percentage, populated by default from system settings assigned to the supplier or line type [^r2][^r3][^r7]. |
| STATUS | `status` | str | No | Processing status, updated to cleared by management upon an override [^r2][^r4][^r7]. |

Ledgerline automatically populates invoice details, linked purchase order lines, warehouse receipt lines, and the standard system tolerance in TOL % [^r3].

## Keys and services

| Action / Key | Service | Type | Endpoint / Implementation | Description |
|---|---|---|---|---|
| Run | `mat_run` | Write | POST `/ll72/svc/mat_run` | Executes the three-way match run [^r1][^r8][^r10][^r13]. |
| Get / F3 | `mat_get` | Read | POST `/ll72/svc/mat_get` | Retrieves matching records using mandatory parameter `ap_doc` [^r1][^r8][^r10][^r11]. |
| Override | `mat_override` | Write | `sp_mat_override` | Bypasses match holds, sets STATUS to cleared by management, and logs the audit comment [^r1][^r4][^r8][^r12]. |
| Search / F2 / Enter | `mat_search` | Read | POST `/ll72/svc/mat_search` | Searches match records using optional criteria `ap_doc`, `tol_pct`, and `status` [^r1][^r8][^r14]. |

Senior accounts staff bypass matching holds by entering an explanation into COMMENT and selecting Override (`mat_override`), which records the comment in the audit log and marks STATUS cleared by management [^r4].

## Messages

The screen references error definitions documented under [[errors-mat]]:

* `ERR-MAT-0001`: Three-Way Match Not Found; also displayed when executing `mat_override` with a blank COMMENT field [^r5][^r9].
* `ERR-MAT-0410`: Match Failed: Price Outside Tolerance [^r9].
* `ERR-MAT-0411`: Match Failed: Qty Invoiced > Qty Received [^r9].
* `ERR-MAT-0412`: No Grn For Po Line [^r9].
* `ERR-MAT-0420`: Override Needs Ap-Mgr Role (see [[err-mat-0420]]) [^r9].

## See also

* [[services-ap-mat|AP mat services]]
* [[errors-mat|ERR-MAT message and error codes]]
* [[err-mat-0420|ERR-MAT-0420 Match override permission denied]]
* [[screen-ap-inv-01|AP-INV-01 Supplier Invoice Entry]]
* [[screen-inv-grn-03|INV-GRN-03 Goods Receipt Note (Grn)]]
* [[services-pur-po|PUR po services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 7, §4. Three-Way Match (AP-MAT-02)
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 8, Step by step
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 8, AP-MAT-02 THREE-WAY MATCH
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 8, Step by step
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 7, §4. Three-Way Match (AP-MAT-02)
[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 8, AP-MAT-02 THREE-WAY MATCH
[^r5]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 10, Worked example
[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 8, AP-MAT-02 THREE-WAY MATCH
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 26, mat_run THREE-WAY MATCH RUN
[^r13]: 04_service_definitions/accounts_payable/mat_run.yaml, screen
[^r11]: 04_service_definitions/accounts_payable/mat_get.yaml, service: mat_get
[^r12]: 04_service_definitions/accounts_payable/mat_override.yaml, whole file
[^r14]: 04_service_definitions/accounts_payable/mat_search.yaml, whole file
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 8, AP-MAT-02 THREE-WAY MATCH
