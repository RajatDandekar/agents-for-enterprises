---
title: "PUR-PR-01 Purchase Request Entry"
type: "screen"
slug: "screen-pur-pr-01"
summary: "Ledgerline screen for creating and submitting purchase requests, capturing items, quantities, need-by dates, and cost centres with automated defaults."
audience: "staff"
status: "mixed"
sources: ["02_procedures/SOP-PUR-002 PR to PO v1.3 (FINAL).pdf", "02_procedures/SOP-PUR-002 PR to PO v1.4.pdf", "03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/purchase/pr_fetch.yaml", "04_service_definitions/purchase/pr_save.yaml", "04_service_definitions/purchase/pr_submit.yaml", "11_training/QRC-01 Raising a purchase request.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | PUR-PR-01 |
| name | Purchase Request Entry |
| module | Purchase |
| menu | Purchase > Request entry |
| roles | PUR-EXEC, PUR-SR, SYS-ADMIN |
| services | pr_fetch, pr_save, pr_submit |
| status | current |

PUR-PR-01 Purchase Request Entry is the Ledgerline screen used to raise and submit internal purchase requests for materials and services [^r9]. It is accessed under Menu Purchase > Request entry by roles PUR-EXEC, PUR-SR, and SYS-ADMIN [^r9]. Entering an item code and fetching defaults automatically calculates estimated gross values based on previous orders, creating drafts in status DR or routing requests for approval [^r1][^r6][^r7][^r9].

| Field | Value |
|---|---|
| Screen code | PUR-PR-01 [^r9] |
| Name | Purchase Request Entry [^r9] |
| Menu path | Purchase > Request entry [^r9] |
| Roles | PUR-EXEC, PUR-SR, SYS-ADMIN [^r9] |
| Read service | pr_fetch [^r14] |
| Write services | pr_save, pr_submit [^r16][^r18] |

## Fields

PUR-PR-01 separates request data into mandatory inputs, optional specifications, and system-calculated display fields [^r4][^r12].

* **PR TYPE**: Mandatory request type [^r12].
* **ITEM CD**: Mandatory item code (`itm_cd`) used to retrieve defaults [^r4][^r12][^r14][^r16]. Users must avoid manually overwriting the item description if a lookup fails, as this causes errors during downstream purchase order generation [^r22].
* **QTY**: Mandatory quantity requested (`qty`) [^r4][^r12][^r16].
* **NEED DT**: Mandatory need-by date (`need_dt`) [^r4][^r12][^r16]. Setting this date in the past causes save operations to fail [^r8][^r13].
* **CC CD**: Mandatory cost centre code (`cc_cd`) [^r4][^r12][^r16]. The screen populates a default cost centre on fetch [^r1][^r5][^r10].
* **WHS CD**: Mandatory warehouse destination, which defaults to WH-MAN-STR if not specified [^r4][^r12].
* **EST RATE**: Optional estimated unit rate (`est_rate`) [^r4][^r12]. Populated on fetch using the rate from the last released purchase order rather than the active rate contract [^r1][^r5][^r10][^r15].
* **REMARKS**: Optional free-text notes [^r4][^r12].
* **PR NO**: Read-only purchase request number assigned upon saving [^r6][^r11][^r12].
* **UOM**: Read-only unit of measure populated from the item record [^r1][^r5][^r10][^r12].
* **EST VALUE (GROSS)**: Read-only estimated gross value calculated by Ledgerline as quantity multiplied by estimated rate multiplied by 1.20, assuming 20% VAT [^r6][^r12][^r17].
* **STATUS**: Read-only request status, set initially to DR (Draft) upon saving [^r3][^r6][^r11][^r12][^r20].

## Keys and services

PUR-PR-01 operates using function key triggers mapped to backend [[services-pur-pr|purchase request services]] [^r10][^r11][^r14][^r16][^r18]:

* **F3 (Fetch / `pr_fetch`)**: Executes read service `pr_fetch` using the entered item code (`itm_cd`) [^r10][^r14][^r19]. It auto-populates UOM, warehouse, default cost centre, and the estimated rate derived from the last released purchase order rather than current rate contracts [^r1][^r5][^r10][^r15].
* **F8 (Save / `pr_save`)**: Invokes write service `pr_save` via endpoint `POST /ll72/svc/pr_save` [^r11][^r16]. It assigns a new PR number in draft status DR and computes the gross estimated value [^r3][^r6][^r11][^r17][^r20]. Saving does not validate whether the assigned cost centre has been closed by Finance, and Ledgerline provides no warning at this stage [^r2][^r11].
* **F9 (Submit / `pr_submit`)**: Calls write service `pr_submit` at `POST /ll72/svc/pr_submit` to progress the request, displaying confirmation in the status prompt at the foot of the screen [^r18][^r21]. PUR-PR-01 prevents submission if the assigned cost centre is marked as closed [^r23]. If the value falls within the user's authorization limit, the request is immediately approved in status AP; otherwise, it is assigned status PA (pending approval) and routed upward with an email notification [^r7].

## Messages

* **ERR-PR-0105**: Generated when attempting to save a request with a Need-by date set in the past [^r8][^r13].

## Versions and conflicts

* **SOP-PUR-002 versioning**: Under current [[sop-pur-002|SOP-PUR-002]] v1.4 (effective 2025-02-01), pressing F3 fetches the unit, warehouse, default cost centre, and estimated rate from the last released order, F8 saves in draft status DR, and F9 submits for approval [^r1][^r3]. This supersedes SOP-PUR-002 v1.3 (effective 2023-05-01), which specified the same core function key procedures and fetch sources [^r24][^r25].

## See also

* [[sop-pur-002|SOP-PUR-002 Purchase Request to Purchase Order]]
* [[man-pur-72|MAN-PUR-72 Ledgerline ERP 7.2 User Manual, Purchasing]]
* [[services-pur-pr|PUR pr services]]
* [[screen-pur-pr-04|PUR-PR-04 Purchase Request Approval]]
* [[screen-pur-po-01|PUR-PO-01 Purchase Order Entry]]
* [[screen-fin-cc-01|FIN-CC-01 Cost Centre Entry]]

## References

[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 29, PUR-PR-01 PURCHASE REQUEST ENTRY
[^r1]: 02_procedures/SOP-PUR-002 PR to PO v1.4.pdf, p. 3, §5. Procedure
[^r6]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 6, §9.4 Saving a request
[^r7]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 6, §9.5 Submitting a request
[^r14]: 04_service_definitions/purchase/pr_fetch.yaml, screen
[^r16]: 04_service_definitions/purchase/pr_save.yaml, service: pr_save
[^r18]: 04_service_definitions/purchase/pr_submit.yaml, service: pr_submit
[^r4]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 6, §9.2 Fields
[^r12]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 29, PUR-PR-01 PURCHASE REQUEST ENTRY
[^r22]: 11_training/QRC-01 Raising a purchase request.pdf, p. 1, Fetching item details
[^r8]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 6, §9.6 Need-by date
[^r13]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 29, PUR-PR-01 PURCHASE REQUEST ENTRY
[^r5]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 6, §9.3 Fetch
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 29, PUR-PR-01 PURCHASE REQUEST ENTRY
[^r15]: 04_service_definitions/purchase/pr_fetch.yaml, notes
[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 29, PUR-PR-01 PURCHASE REQUEST ENTRY
[^r17]: 04_service_definitions/purchase/pr_save.yaml, notes
[^r3]: 02_procedures/SOP-PUR-002 PR to PO v1.4.pdf, p. 3, §5. Procedure
[^r20]: 11_training/QRC-01 Raising a purchase request.pdf, p. 1, Saving and submission
[^r19]: 11_training/QRC-01 Raising a purchase request.pdf, p. 1, Steps
[^r2]: 02_procedures/SOP-PUR-002 PR to PO v1.4.pdf, p. 3, §5. Procedure
[^r21]: 11_training/QRC-01 Raising a purchase request.pdf, p. 1, Saving and submission
[^r23]: 11_training/QRC-01 Raising a purchase request.pdf, p. 1, Cost centre checks
[^r24]: 02_procedures/SOP-PUR-002 PR to PO v1.3 (FINAL).pdf, p. 3, §5. Procedure
[^r25]: 02_procedures/SOP-PUR-002 PR to PO v1.3 (FINAL).pdf, p. 3, §5. Procedure
