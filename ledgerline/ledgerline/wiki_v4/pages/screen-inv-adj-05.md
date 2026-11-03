---
title: "INV-ADJ-05 Stock Adjustment Entry"
type: "screen"
slug: "screen-inv-adj-05"
summary: "INV-ADJ-05 records, approves, posts, and cancels manual inventory adjustments, updating perpetual stock balances and financial ledgers."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/adj_approve.yaml", "04_service_definitions/inventory/adj_cancel.yaml", "04_service_definitions/inventory/adj_get.yaml", "04_service_definitions/inventory/adj_post.yaml", "04_service_definitions/inventory/adj_save.yaml", "04_service_definitions/inventory/adj_search.yaml", "04_service_definitions/service_index.csv"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen | INV-ADJ-05 |
| Title | Stock Adjustment Entry |
| Module | Inventory |
| Menu path | Inventory > Stock adjustment |
| Services | adj_save, adj_get, adj_search, adj_approve, adj_post, adj_cancel |

Screen INV-ADJ-05 (Stock Adjustment Entry) is the Ledgerline screen used to enter, approve, post, and cancel stock adjustments [^r1]. It is accessed via the menu path Inventory > Stock adjustment and handles inventory adjustments through six underlying services [^r1][^r13]. Once an adjustment is posted via this screen, the transaction is locked and inventory balances and nominal ledgers are permanently updated [^r8][^r10].

## Fields

Screen INV-ADJ-05 contains the following header and line fields [^r3]:

* **ADJ NO (`adj_no`)**: Mandatory field identifying the stock adjustment record [^r3][^r11]. When creating a new stock adjustment record, the ADJ NO field is left blank and is automatically assigned upon saving [^r4].
* **STATUS (`status`)**: Adjustment lifecycle state [^r3]. New records are written with an initial unapproved status upon saving [^r6].
* **COMMENT (`comment`)**: Optional field [^r3][^r15].
* **REASON (`reason`)**: Mandatory cancellation reason field required when voiding an adjustment [^r3][^r11][^r16].
* **ITEM CD (`itm_cd`)**: Mandatory item code [^r2][^r11][^r20].
* **WHS CD (`whs_cd`)**: Mandatory warehouse code [^r2][^r11][^r20].
* **QTY (+/-) (`qty`)**: Mandatory signed quantity; entering a signed quantity with a minus sign reduces recorded stock, while a plain quantity increases stock [^r2][^r5][^r20].
* **REASON CD (`reason_cd`)**: Mandatory adjustment reason code [^r2][^r11][^r20].
* **REMARKS (`remarks`)**: Optional descriptive remarks [^r2][^r3][^r20].

## Keys and services

INV-ADJ-05 interfaces directly with the [[services-inv-adj|INV adj services]] group [^r1][^r13]:

* **`adj_save`**: Executes the write service STOCK ADJUSTMENT SAVE at endpoint POST `/ll72/svc/adj_save` using mandatory fields `itm_cd`, `whs_cd`, `qty`, and `reason_cd` (with optional `remarks`) to write an unapproved record [^r6][^r19][^r20].
* **`adj_get`**: Executes the read service to retrieve existing stock adjustment records by `adj_no` [^r1][^r17].
* **`adj_search`**: Executes the read service at endpoint POST `/ll72/svc/adj_search` to list stock adjustment records [^r21].
* **`adj_approve`**: Invokes the write service STOCK ADJUSTMENT APPROVE at endpoint POST `/ll72/svc/adj_approve` (defined in `inventory/adj_approve.yaml` since version 7.0), passing `adj_no` and an optional comment to validate operator threshold limits and mark the adjustment as authorised [^r7][^r14][^r15][^r22].
* **`adj_post`**: Executes the write service STOCK ADJUSTMENT POST to lock the document, update perpetual inventory balances at `whs_cd`, write stock movement ledger records, and post financial journal entries [^r8][^r18]. Once posted, the adjustment is locked and cannot be edited or altered; corrections require entering a new adjustment with opposite sign [^r10].
* **`adj_cancel`**: Invokes the write service STOCK ADJUSTMENT CANCEL (defined in `inventory/adj_cancel.yaml` since version 7.0) to set the document to void using `adj_no` and `reason` without altering inventory quantities or nominal accounts [^r9][^r16][^r23].

## Messages

Screen INV-ADJ-05 can display the following error messages:

* `ERR-ADJ-0201` (Qty Must Be > 0) [^r12]
* [[err-itm-0011|ERR-ITM-0011]] (Item Not Found Or Inactive) [^r12]
* `ERR-ADJ-0001` (Stock Adjustment Not Found) [^r12]
* `ERR-ADJ-0007` (Stock Adjustment Not In Draft (<Status>)) [^r12]
* [[err-apr-0003|ERR-APR-0003]] (Self Approval Not Allowed) [^r12]
* [[err-apr-0004|ERR-APR-0004]] (Value Above Your Limit) [^r12]
* `ERR-ADJ-0420` (Adjustment Above Stores Limit, Needs Plant Head), raised when an adjustment exceeds the stores limit and requires plant head approval during `adj_approve` [^r12][^r15]
* `ERR-ADJ-0801` (Stock Adjustment Closed (<Status>)) [^r12]

## Versions and conflicts

* **ADJ NO field mandatory status**: In v7.2.3, when creating a new adjustment on INV-ADJ-05, the ADJ NO field is left blank and is automatically assigned upon saving [^r4]. In superseded manual v7.2.2, `adj_no` was listed among mandatory input fields without distinguishing record creation [^r25] (`superseded`).

## See also

* [[services-inv-adj]]
* [[errors-adj]]
* [[err-itm-0011]]
* [[err-apr-0003]]
* [[err-apr-0004]]
* [[screen-inv-itm-01]]
* [[screen-inv-whs-01]]
* [[screen-inv-cnt-06]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 6, §4. Stock Adjustment (INV-ADJ-05)
[^r13]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 10, §3. Inventory services
[^r8]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 9, Posting an Adjustment to the Ledger
[^r10]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 10, Questions users ask
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 7, Screen Layout and Fields
[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 11, INV-ADJ-05 STOCK ADJUSTMENT ENTRY
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 8, Creating a New Stock Adjustment Record
[^r6]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 8, Creating a New Stock Adjustment Record
[^r15]: 04_service_definitions/inventory/adj_approve.yaml, errors
[^r16]: 04_service_definitions/inventory/adj_cancel.yaml, service: adj_cancel
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 6, §4. Stock Adjustment (INV-ADJ-05)
[^r20]: 04_service_definitions/inventory/adj_save.yaml, request.fields
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 7, Screen Layout and Fields
[^r19]: 04_service_definitions/inventory/adj_save.yaml, whole file
[^r17]: 04_service_definitions/inventory/adj_get.yaml, whole file
[^r21]: 04_service_definitions/inventory/adj_search.yaml, service: adj_search
[^r7]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 8, Approving an Adjustment
[^r14]: 04_service_definitions/inventory/adj_approve.yaml, service
[^r22]: 04_service_definitions/service_index.csv, sheet csv, row adj_approve, SHEET csv
[^r18]: 04_service_definitions/inventory/adj_post.yaml, service: adj_post
[^r9]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 9, Cancelling an Adjustment
[^r23]: 04_service_definitions/service_index.csv, sheet csv, row adj_cancel, SHEET csv
[^r12]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 12, INV-ADJ-05 STOCK ADJUSTMENT ENTRY
[^r25]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 4, §4. Stock Adjustment (INV-ADJ-05)
