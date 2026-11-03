---
title: "FIN-CC-01 Cost Centre Entry"
type: "screen"
slug: "screen-fin-cc-01"
summary: "Ledgerline screen to maintain cost centre records, check budget commitments, and manage opening and closing across production programmes."
audience: "staff"
status: "mixed"
sources: ["01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf", "01_policies/old/Purchase Policy v4.0.docx", "02_procedures/SOP-FIN-001 Cost Centre Open and Close v1.1.pdf", "02_procedures/SOP-PUR-002 PR to PO v1.3 (FINAL).pdf", "02_procedures/SOP-PUR-002 PR to PO v1.4.pdf", "03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/admin/cc_close.yaml", "04_service_definitions/admin/cc_reopen.yaml", "04_service_definitions/admin/cc_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | FIN-CC-01 |
| Title | Cost Centre Entry |
| Menu path | System > Cost centre |
| Accessible roles | IT-ADMIN, SYS-ADMIN |
| Read/write services | cc_save, cc_close, cc_reopen |

Screen FIN-CC-01 (Cost Centre Entry) is the Ledgerline screen used to maintain, inspect, open, and close cost centres across Northbridge Cycles' production programmes [^r1][^r2]. Finance personnel use it to manage cost centre lifecycles and verify that zero balances remain before closure, while purchasing staff reference it to verify active status prior to creating purchase requests and orders [^r1][^r2][^r4][^r6]. The screen displays budget commitments and blocks closures when unposted journals or open operational documents remain attached [^r3][^r4][^r5].

## Fields

FIN-CC-01 displays the cost centre's code, name, description, owner, status (OPEN or CLOSED), and closure date [^r3][^r7]. It also presents the programme description, the quarterly budget, and the committed amount [^r3][^r7]. Two dedicated tabs show open balances and commitments [^r3].

Each user is configured by IT with a default cost centre that populates upon Fetch, but these default values are not updated automatically when Finance closes a cost centre [^r9]. When a purchase document is charged to a closed cost centre, Ledgerline saves it as Draft and issues warning W-CC-114 rather than refusing it [^r8]. Approving a purchase order commits its gross value against the cost centre's available quarterly budget, failing with ERR-BUD-0207 if the gross value exceeds the available budget [^r10].

## Keys and services

FIN-CC-01 belongs to the menu path System > Cost centre and is accessible to roles IT-ADMIN and SYS-ADMIN [^r11].

The screen interacts with the following backend services under [[services-adm-cc]]:
* `cc_save`: invoked via endpoint `POST /ll72/svc/cc_save` to save cost centre records [^r15].
* `cc_close`: write service invoked to execute cost centre closure [^r13].
* `cc_reopen`: write service invoked to reopen closed cost centres [^r14].

Before saving a closure on FIN-CC-01, all ledger balances on the open balance and commitments tabs must stand at zero, with no unposted journals, sales orders, work orders, or subcontract manifests linked to the code [^r4].

## Messages

FIN-CC-01 raises and displays the following message and error codes [^r5][^r12]:
* [[err-cc-0009]]: Cost Centre Not Found [^r12].
* `ERR-CC-0001`: Cost Centre Not Found [^r12].
* [[err-cc-0310]]: Open Documents On Cost Centre, raised in the error message panel when attempting to save a closure while open documents or commitments remain attached [^r5][^r12].
* `ERR-CC-0801`: Cost Centre Closed (<Status>) [^r12].

Purchasing workflows checking FIN-CC-01 also interact with warning W-CC-114 when resolving orders against closed cost centres, as well as budget check error ERR-BUD-0207 upon purchase order approval [^r6][^r8][^r10].

## Versions and conflicts

* **Cost centre verification before ordering**: Under [[pol-pur-001]] v4.1 (effective 2026-04-01), staff must check cost centre open or closed status in Ledgerline using screen FIN-CC-01 prior to creating purchase orders [^r1]. In superseded v4.0, users could either check FIN-CC-01 or verify status directly with Finance [^r16]. (Kind: `superseded`) [^r1][^r16].
* **Purchase request default cost centre checks**: Under [[sop-pur-002]] v1.4, FIN-CC-01 is used to check whether a cost centre remains active and has not been closed by Finance before saving purchase requests or when resolving warning W-CC-114 [^r6]. Superseded SOP-PUR-002 v1.3 specified checking FIN-CC-01 prior to saving a request specifically to verify that the user's default cost centre had not been closed [^r17]. (Kind: `superseded`) [^r6][^r17].

## See also

* [[pol-pur-001|POL-PUR-001 Purchase Policy]]
* [[sop-fin-001|SOP-FIN-001 Cost Centre Open and Close]]
* [[sop-pur-002|SOP-PUR-002 Purchase Request to Purchase Order]]
* [[man-pur-72|MAN-PUR-72 Ledgerline ERP 7.2 User Manual, Purchasing]]
* [[services-adm-cc|ADM cc services]]
* [[errors-cc|Cost Centre Error Codes (ERR-CC-*)]]
* [[err-cc-0009|ERR-CC-0009]]
* [[err-cc-0310|ERR-CC-0310 Cost centre has open documents]]
* [[screen-pur-pr-01|PUR-PR-01 Purchase Request Entry]]
* [[screen-pur-po-01|PUR-PO-01 Purchase Order Entry]]

## References

[^r1]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 1, §4. Cost centres and budgets
[^r2]: 02_procedures/SOP-FIN-001 Cost Centre Open and Close v1.1.pdf, p. 3, §5. Procedure
[^r4]: 02_procedures/SOP-FIN-001 Cost Centre Open and Close v1.1.pdf, p. 4, What to check on the screen
[^r6]: 02_procedures/SOP-PUR-002 PR to PO v1.4.pdf, p. 3, §5. Procedure
[^r3]: 02_procedures/SOP-FIN-001 Cost Centre Open and Close v1.1.pdf, p. 4, What to check on the screen
[^r5]: 02_procedures/SOP-FIN-001 Cost Centre Open and Close v1.1.pdf, p. 4, What to check on the screen
[^r7]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 6, §8.1 Purpose
[^r9]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 6, §8.3 Your default cost centre
[^r8]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 6, §8.2 Status
[^r10]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 6, §8.4 Budget check
[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 11, FIN-CC-01 COST CENTRE ENTRY
[^r15]: 04_service_definitions/admin/cc_save.yaml, service: cc_save
[^r13]: 04_service_definitions/admin/cc_close.yaml, service: cc_close
[^r14]: 04_service_definitions/admin/cc_reopen.yaml, service: cc_reopen
[^r12]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 11, FIN-CC-01 COST CENTRE ENTRY
[^r16]: 01_policies/old/Purchase Policy v4.0.docx, §4. Cost centres and budgets
[^r17]: 02_procedures/SOP-PUR-002 PR to PO v1.3 (FINAL).pdf, p. 3, §5. Procedure
