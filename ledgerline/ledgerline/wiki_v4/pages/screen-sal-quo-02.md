---
title: "SAL-QUO-02 Quotation Entry"
type: "screen"
slug: "screen-sal-quo-02"
summary: "Ledgerline screen used by sales administration staff to record price quotations and convert them directly into live sales orders."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/sales/quo_cancel.yaml", "04_service_definitions/sales/quo_convert.yaml", "04_service_definitions/sales/quo_get.yaml", "04_service_definitions/sales/quo_save.yaml", "04_service_definitions/sales/quo_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | SAL-QUO-02 |
| Screen title | Quotation Entry |
| Module | Sales |
| Navigation | Sales > Quotation |
| Authorised roles | SAL-EXEC, SAL-MGR, SYS-ADMIN |
| Primary services | quo_save, quo_get, quo_search, quo_convert, quo_cancel |
| Status | Current |

Screen SAL-QUO-02 allows sales administration staff at Manchester and Leeds to record formal price quotations and convert them directly into live sales orders without re-keying line details [^r3]. Accessed via the menu path Sales > Quotation, the screen manages the end-to-end quotation lifecycle through backend quotation services [^r1][^r9][^r11]. Authorized roles for the screen comprise SAL-EXEC, SAL-MGR, and SYS-ADMIN [^r9].

## Fields

| Field label | Technical name | Mandatory / Optional | Notes |
|---|---|---|---|
| CUST CD | `cust_cd` | Mandatory | Customer code; required to raise a quotation and used as an optional search filter [^r2][^r4][^r9][^r15][^r17]. |
| ITEM CD | `itm_cd` | Mandatory | Item code; required to raise a quotation and used as an optional search filter [^r2][^r4][^r9][^r15][^r17]. |
| QTY | `qty` | Mandatory | Order quantity; required to raise a quotation and used as an optional search filter [^r2][^r4][^r9][^r15][^r17]. |
| PRICE | `price` | Mandatory | Unit quotation price [^r2][^r4][^r9][^r15]. |
| VALID TO | `valid_to` | Mandatory | Quotation expiry date [^r2][^r4][^r9][^r15]. |
| QUO NO | `quo_no` | Mandatory | Quotation reference number generated upon saving, or entered to retrieve or cancel [^r2][^r4][^r5][^r9][^r12][^r14]. |
| REASON | `reason` | Mandatory | Mandatory justification code supplied when executing a cancellation [^r2][^r9][^r12]. |
| STATUS | `status` | Optional | Quotation status; can be used as an optional search filter [^r2][^r9][^r17]. Updates to closed by conversion upon order conversion [^r6][^r7]. |
| COMMENT | `comment` | Optional | Free-text commentary entered during quotation creation [^r2][^r4][^r8][^r9]. Internal confidential remarks should not be entered here as comments may appear on customer-facing print templates [^r8]. |

To raise a new quotation, the user enters CUST CD, ITEM CD, QTY, PRICE, VALID TO, and optional COMMENT, then executes the save action to generate a QUO NO [^r4]. Existing records can be retrieved by providing QUO NO or searched by entering CUST CD to open a lookup window [^r5]. Pressing convert creates a sales order and updates the quotation STATUS to closed by conversion, provided the VALID TO date has not passed [^r6]. Once converted, quotation STATUS updates to closed and all fields become locked against further changes [^r7].

## Keys and services

Screen SAL-QUO-02 interfaces with the following key bindings and backend services grouped under [[services-sal-quo]]:

* **Save (F8)**: Invokes write service `quo_save` to persist quotation records with mandatory fields `cust_cd`, `itm_cd`, `qty`, `price`, and `valid_to` via stored procedure `sp_quo_save` [^r10][^r15].
* **Get (F3)**: Invokes read service `quo_get` (POST `/ll72/svc/quo_get`) with input parameter `quo_no` to retrieve quotation records [^r10][^r14].
* **Search (F2/Enter)**: Invokes read service `quo_search` (QUOTATION LIST) to query quotation records using optional filters `cust_cd`, `itm_cd`, `qty`, and `status` [^r10][^r16][^r17].
* **Convert**: Invokes backend service `quo_convert` to perform QUOTATION CONVERT operations directly into sales orders [^r6][^r10][^r13].
* **Cancel (Shift+F8)**: Invokes service `quo_cancel` to cancel quotations using mandatory parameters `quo_no` and `reason` [^r10][^r12].

## Messages

The screen displays the following validation and processing messages, catalogued in [[errors-quo]]:

* `ERR-QUO-0201`: "QTY MUST BE > 0" — triggered during search or entry operations when an invalid quantity is supplied [^r10][^r18].
* [[err-itm-0011|ERR-ITM-0011]]: "ITEM NOT FOUND OR INACTIVE" — triggered during quotation operations when an invalid or inactive item code is entered [^r10][^r18].
* `ERR-QUO-0001`: Quotation processing error code raised by the screen [^r10].
* `ERR-QUO-0801`: Quotation processing error code raised by the screen [^r10].

## See also

* [[services-sal-quo|SAL quo services]]
* [[errors-quo|ERR-QUO quotation error codes]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[screen-sal-so-01|SAL-SO-01 Sales Order]]
* [[screen-sal-cus-01|SAL-CUS-01 Customer Master Entry]]
* [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]]

## References

[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 11, Purpose
[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 11, §5. Quotation (SAL-QUO-02)
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 38, SAL-QUO-02 QUOTATION ENTRY
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 41, quo_save QUOTATION SAVE
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 11, §5. Quotation (SAL-QUO-02)
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 12, Raising a new quotation
[^r15]: 04_service_definitions/sales/quo_save.yaml, service: quo_save
[^r17]: 04_service_definitions/sales/quo_search.yaml, request
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 12, Retrieving an existing quotation
[^r12]: 04_service_definitions/sales/quo_cancel.yaml, screen
[^r14]: 04_service_definitions/sales/quo_get.yaml, whole file
[^r6]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 13, Converting a quotation to a firm order
[^r7]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 15, Questions users ask
[^r8]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 14, Tips
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 38, SAL-QUO-02 QUOTATION ENTRY
[^r16]: 04_service_definitions/sales/quo_search.yaml, screen: SAL-QUO-02
[^r13]: 04_service_definitions/sales/quo_convert.yaml, screen
[^r18]: 04_service_definitions/sales/quo_search.yaml, errors
