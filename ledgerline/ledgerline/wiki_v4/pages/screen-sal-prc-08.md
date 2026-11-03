---
title: "SAL-PRC-08 Price List"
type: "screen"
slug: "screen-sal-prc-08"
summary: "Ledgerline screen SAL-PRC-08 for maintaining sales price lists, supporting search, fetch, save, and copy operations across item prices."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/sales/prc_copy.yaml", "04_service_definitions/sales/prc_get.yaml", "04_service_definitions/sales/prc_save.yaml", "04_service_definitions/sales/prc_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | SAL-PRC-08 |
| Module | Sales > Price list |
| Authorized roles | SAL-EXEC, SAL-MGR, SYS-ADMIN |
| Read services | prc_search, prc_get |
| Write services | prc_save, prc_copy |

Screen SAL-PRC-08 (Price List) is the Ledgerline interface used under Sales > Price list to manage item pricing entries and base sales rates[^r5]. It allows authorized roles to search, view, save, and duplicate price list records across active products[^r2][^r4][^r5]. Unit values entered on this screen represent prices in pounds excluding value added tax and delivery surcharges[^r3].

| Field | Code | Required | Details |
|---|---|---|---|
| Screen Code | SAL-PRC-08 | — | Ledgerline price list screen[^r1][^r5]. |
| Menu Path | Sales > Price list | — | Navigation path in Ledgerline[^r5]. |
| Allowed Roles | SAL-EXEC, SAL-MGR, SYS-ADMIN | — | Roles authorized to access the screen[^r5]. |

## Fields

Screen SAL-PRC-08 contains five fields used for configuring and maintaining price list lines[^r1]:

* **PRICE LIST (`price_list`)**: Mandatory identifier for the price list group[^r1][^r5][^r10].
* **ITEM CD (`itm_cd`)**: Mandatory item code for the listed product[^r1][^r5][^r10].
* **PRICE (`price`)**: Mandatory unit value entered in pounds, excluding value added tax and delivery surcharges[^r1][^r3][^r5][^r10].
* **VALID FROM (`valid_from`)**: Mandatory effective start date for the pricing entry[^r1][^r5][^r10].
* **STATUS (`status`)**: Optional status field indicating line state[^r1][^r5].

## Keys and services

SAL-PRC-08 maps keyboard shortcuts and four interface buttons directly to [[services-sal-prc|SAL prc services]][^r2][^r6]:

* **Search (F2 / Enter)**: Invokes `prc_search` (PRICE LIST LIST) to search price list entries by `price_list`, `itm_cd`, `price`, and `status`[^r2][^r6][^r11].
* **Get (F3)**: Invokes read service `prc_get` (PRICE LIST GET) via POST `/ll72/svc/prc_get` using required parameter `price_list`[^r2][^r6][^r8].
* **Save (F8)**: Invokes write service `prc_save` (PRICE LIST SAVE) via POST `/ll72/svc/prc_save` submitting mandatory fields `price_list`, `itm_cd`, `price`, and `valid_from`[^r2][^r6][^r9][^r10].
* **Copy**: Invokes `prc_copy` (PRICE LIST COPY) to execute stored procedure `sp_prc_copy`[^r2][^r6][^r7]. The button opens a dialogue prompting for target `PRICE LIST` and new `VALID FROM` parameters, duplicating all lines under active `STATUS`[^r4].

## Messages

The screen handles two specific error conditions during validation and data retrieval[^r6]:

* [[err-prc-0001]]: Triggered when mandatory parameters are absent or pricing conflicts occur[^r6].
* [[err-itm-0011]]: Triggered when an entered item code is not found or is inactive[^r6].

## See also

* [[services-sal-prc|SAL prc services]]
* [[screen-sal-so-01|SAL-SO-01 Sales Order]]
* [[screen-sal-quo-02|SAL-QUO-02 Quotation Entry]]
* [[screen-sal-dsc-10|SAL-DSC-10 Discount]]
* [[err-prc-0001|ERR-PRC-0001 Mandatory parameters absent or pricing conflict]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]

## References

[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 37, SAL-PRC-08 PRICE LIST
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 34, Screen layout
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 35, Step by step: Copying a price list
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 34, Screen layout
[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 33, §11. Price List (SAL-PRC-08)
[^r10]: 04_service_definitions/sales/prc_save.yaml, request.fields
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 37, SAL-PRC-08 PRICE LIST
[^r11]: 04_service_definitions/sales/prc_search.yaml, whole file
[^r8]: 04_service_definitions/sales/prc_get.yaml, screen
[^r9]: 04_service_definitions/sales/prc_save.yaml, service: prc_save
[^r7]: 04_service_definitions/sales/prc_copy.yaml, whole file
