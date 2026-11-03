---
title: "INV kbn services"
type: "service-group"
slug: "services-inv-kbn"
summary: "Ledgerline inventory services managing shop-floor Kanban card replenishment loops, signals, card retrievals, listings, and closures."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/kbn_close.yaml", "04_service_definitions/inventory/kbn_get.yaml", "04_service_definitions/inventory/kbn_save.yaml", "04_service_definitions/inventory/kbn_search.yaml", "04_service_definitions/inventory/kbn_signal.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | INV |
| Object | kbn (Kanban Card) |
| Screen | INV-KBN-13 |
| Services | kbn_save, kbn_get, kbn_search, kbn_signal, kbn_close |
| Introduced | 7.2.0 |
| Status | Current |

The `kbn` service group in the Ledgerline INV module provides backend services to create, read, list, signal, and close shop-floor bin replenishment cards on screen [[screen-inv-kbn-13|INV-KBN-13]][^r1]. Available since Ledgerline ERP version 7.2.0, these services coordinate production-line inventory requests and track bin turnarounds with stores[^r1][^r11][^r18][^r23][^r28][^r33]. All calls require authentication via a session token passed in header `X-LL-Session` and role authorisation for the service[^r12][^r19][^r24][^r29][^r34].

## Services

### kbn_save

The `kbn_save` service (KANBAN CARD SAVE) is an INV write service tied to screen [[screen-inv-kbn-13|INV-KBN-13]] that executes stored procedure `sp_kbn_save` to store new loop parameters or commit modifications to an existing card record[^r2][^r6][^r23]. It was introduced in version 7.2.0 and is invoked at endpoint `POST /ll72/svc/kbn_save`[^r23][^r24]. Calls require an active session token in header `X-LL-Session` and an authorised user role[^r24].

* **Required fields:** `itm_cd` (string, ITEM CD), `whs_cd` (string, WHS CD), and `bin_qty` (integer, BIN QTY)[^r6][^r25].
* **Optional fields:** `cards` (integer, NO OF CARDS)[^r6][^r25].
* **Response:** Returns envelope fields `rc` (`S | W | E`), `err_cd` (on error), short uppercase `msg`, and `data`[^r26].
* **Errors:** Specific error [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE), as well as common errors ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (`<FIELD> MANDATORY`), ERR-SYS-0422 (`UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>`), and ERR-SYS-0503 (`SERVER BUSY, TRY LATER`)[^r27].
* **Source file:** `04_service_definitions/inventory/kbn_save.yaml`[^r23].

### kbn_get

The `kbn_get` service (KANBAN CARD GET) is an INV read service introduced in version 7.2.0 to retrieve an existing card record using known key data on screen [[screen-inv-kbn-13|INV-KBN-13]][^r3][^r7][^r18]. It is called via endpoint `POST /ll72/svc/kbn_get` using session authentication header `X-LL-Session` with appropriate role permissions[^r18][^r19].

* **Required fields:** `kbn_no` (string, KBN NO)[^r7][^r20].
* **Optional fields:** None[^r20].
* **Response:** Returns envelope fields `rc` (`S | W | E`), `err_cd` (error code when `rc` is `E`), short uppercase `msg`, and `data` (result)[^r21].
* **Errors:** Specific error [[err-kbn-0001|ERR-KBN-0001]] (KANBAN CARD NOT FOUND), along with common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503[^r7][^r22].
* **Source file:** `04_service_definitions/inventory/kbn_get.yaml`[^r18].

### kbn_search

The `kbn_search` service (KANBAN CARD LIST) is an INV read service available since version 7.2.0 that provides search and filtering on screen [[screen-inv-kbn-13|INV-KBN-13]] to display a selection window[^r3][^r8][^r28]. It is invoked at endpoint `POST /ll72/svc/kbn_search` with header `X-LL-Session` and role authorisation[^r28][^r29].

* **Required fields:** None[^r30].
* **Optional fields:** `itm_cd` (string, ITEM CD), `whs_cd` (string, WHS CD), `bin_qty` (integer, BIN QTY), and `status` (string, STATUS)[^r8][^r30].
* **Response:** Returns envelope fields `rc` (`S | W | E`), `err_cd`, short uppercase `msg`, and `data`[^r31].
* **Errors:** Specific error [[err-itm-0011|ERR-ITM-0011]] (ITEM NOT FOUND OR INACTIVE), plus common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503[^r8][^r32].
* **Source file:** `04_service_definitions/inventory/kbn_search.yaml`[^r28].

### kbn_signal

The `kbn_signal` service (KANBAN CARD SIGNAL) is an INV write service available since version 7.2.0 that executes stored procedure `sp_kbn_signal` from screen [[screen-inv-kbn-13|INV-KBN-13]][^r4][^r9][^r33][^r37]. It notifies stores that a container has been emptied and requires replenishment, logging an internal timestamp[^r4]. Requests are posted to `/ll72/svc/kbn_signal` with header `X-LL-Session` under an authorised role[^r33][^r34].

* **Required fields:** `kbn_no` (string, KBN NO)[^r9][^r35].
* **Optional fields:** `comment` (string, COMMENT)[^r9][^r35].
* **Response:** Returns envelope fields `rc` (`S | W | E`), `err_cd` when `rc` is `E`, short uppercase `msg`, and `data`[^r36].
* **Errors:** Specific error [[err-kbn-0001|ERR-KBN-0001]] (KANBAN CARD NOT FOUND), as well as common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503[^r9][^r37].
* **Source file:** `04_service_definitions/inventory/kbn_signal.yaml`[^r33].

### kbn_close

The `kbn_close` service (KANBAN CARD CLOSE) is an INV write service available since version 7.2.0 that executes stored procedure `sp_kbn_close` from screen [[screen-inv-kbn-13|INV-KBN-13]][^r5][^r10][^r11][^r15]. It deactivates a loop or clears an open replenishment request when a full bin arrives back at the line[^r5]. Requests are submitted to endpoint `POST /ll72/svc/kbn_close` with header `X-LL-Session` and role authorisation[^r11][^r12].

* **Required fields:** `kbn_no` (string, KBN NO)[^r10][^r13].
* **Optional fields:** `comment` (string, COMMENT)[^r10][^r13].
* **Response:** Returns envelope fields `rc` (`S | W | E`), `err_cd` when `rc` is `E`, short uppercase `msg`, and `data`[^r14].
* **Errors:** Specific errors [[err-kbn-0001|ERR-KBN-0001]] (KANBAN CARD NOT FOUND) and [[err-kbn-0801|ERR-KBN-0801]] (`KANBAN CARD CLOSED (<status>)`), along with common errors ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (`<FIELD> MANDATORY`), ERR-SYS-0422 (`UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>`), and ERR-SYS-0503 (`SERVER BUSY, TRY LATER`)[^r10][^r16][^r17].
* **Source file:** `04_service_definitions/inventory/kbn_close.yaml`[^r11].

## Versions and conflicts

In the current [[man-inv-72|MAN-INV-72]] v7.2.3 manual, `kbn_save` stores loop parameters or commits card record modifications, and `kbn_search` operates as a standard card listing filter[^r2][^r3]. The superseded manual [[man-inv-72|MAN-INV-72]] v7.2.2 (dated 10 June 2024) described `kbn_save` specifically for generating initial card references and highlighted `kbn_search` for cross-facility lookups when physical card labels were torn or missing references[^r38][^r39] (`superseded`).

## See also

* [[screen-inv-kbn-13|INV-KBN-13 Kanban Card Entry]]
* [[err-kbn-0001|ERR-KBN-0001 Kanban Card Not Found or Duplicate Signal]]
* [[err-kbn-0801|ERR-KBN-0801 Kanban Card Status Transition or Warehouse Validation Error]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]
* [[services-inv-bin|INV bin services]]
* [[services-inv-whs|INV whs services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 49, §15. Kanban Card (INV-KBN-13)
[^r11]: 04_service_definitions/inventory/kbn_close.yaml, service
[^r18]: 04_service_definitions/inventory/kbn_get.yaml, service: kbn_get
[^r23]: 04_service_definitions/inventory/kbn_save.yaml, service: kbn_save
[^r28]: 04_service_definitions/inventory/kbn_search.yaml, service: kbn_search
[^r33]: 04_service_definitions/inventory/kbn_signal.yaml, service: kbn_signal
[^r12]: 04_service_definitions/inventory/kbn_close.yaml, auth
[^r19]: 04_service_definitions/inventory/kbn_get.yaml, auth
[^r24]: 04_service_definitions/inventory/kbn_save.yaml, service: kbn_save
[^r29]: 04_service_definitions/inventory/kbn_search.yaml, auth
[^r34]: 04_service_definitions/inventory/kbn_signal.yaml, auth
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 50, Screen layout and fields
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 21, kbn_save KANBAN CARD SAVE
[^r25]: 04_service_definitions/inventory/kbn_save.yaml, request.fields
[^r26]: 04_service_definitions/inventory/kbn_save.yaml, response.envelope
[^r27]: 04_service_definitions/inventory/kbn_save.yaml, errors
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 50, Screen layout and fields
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 21, kbn_get KANBAN CARD GET
[^r20]: 04_service_definitions/inventory/kbn_get.yaml, request.fields
[^r21]: 04_service_definitions/inventory/kbn_get.yaml, response.envelope
[^r22]: 04_service_definitions/inventory/kbn_get.yaml, errors
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 21, kbn_search KANBAN CARD LIST
[^r30]: 04_service_definitions/inventory/kbn_search.yaml, request.fields
[^r31]: 04_service_definitions/inventory/kbn_search.yaml, response.envelope
[^r32]: 04_service_definitions/inventory/kbn_search.yaml, errors
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 52, Worked example
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 21, kbn_signal KANBAN CARD SIGNAL
[^r37]: 04_service_definitions/inventory/kbn_signal.yaml, errors
[^r35]: 04_service_definitions/inventory/kbn_signal.yaml, request.fields
[^r36]: 04_service_definitions/inventory/kbn_signal.yaml, response.envelope
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 50, Screen layout and fields
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 21, kbn_close KANBAN CARD CLOSE
[^r15]: 04_service_definitions/inventory/kbn_close.yaml, procedures
[^r13]: 04_service_definitions/inventory/kbn_close.yaml, request.fields
[^r14]: 04_service_definitions/inventory/kbn_close.yaml, response.envelope
[^r16]: 04_service_definitions/inventory/kbn_close.yaml, errors
[^r17]: 04_service_definitions/inventory/kbn_close.yaml, common_errors
[^r38]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 22, Step by step
[^r39]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 22, Step by step
