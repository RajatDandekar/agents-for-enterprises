---
title: "PUR-PO-01 Purchase Order Entry"
type: "screen"
slug: "screen-pur-po-01"
summary: "Ledgerline screen for raising standard or direct single-line purchase orders, requiring F3 Fetch before saving to avoid ERR-SCR-0221."
audience: "staff"
status: "mixed"
sources: ["02_procedures/SOP-PUR-002 PR to PO v1.3 (FINAL).pdf", "02_procedures/SOP-PUR-002 PR to PO v1.4.pdf", "03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/purchase/po_fetch.yaml", "04_service_definitions/purchase/po_save.yaml", "08_release_notes/RN-7.0 Ledgerline Release Notes.pdf", "08_release_notes/RN-7.0.1 Ledgerline Release Notes.pdf", "08_release_notes/RN-7.2.3 Ledgerline Release Notes.pdf", "08_release_notes/RN-7.2.3-P4 Ledgerline Patch Notes.pdf", "08_release_notes/RN-7.3 PREVIEW (planned March 2027).pdf", "11_training/QRC-02 Raising a purchase order - Fetch first.pdf", "11_training/intranet_export_2016/how_to_raise_an_order.html"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | PUR-PO-01 |
| Module | Purchase |
| Menu path | Purchase > Order entry |
| Allowed roles | PUR-EXEC, PUR-SR, SYS-ADMIN |
| Header services | po_fetch, po_save |
| Document types | STD, DIR |

PUR-PO-01 is the Ledgerline purchasing screen used to create, edit, and park single-line purchase orders [^r9][^r11][^r22]. It supports standard orders referencing an approved purchase request and direct orders without a request, but does not allow direct supplier dispatch or immediate authorisation from the entry form [^r1][^r6][^r22]. Users must run the Fetch function (`F3`) after populating or changing the supplier and item fields, or the subsequent save will be rejected [^r2][^r7][^r28][^r35].

| Field | Detail |
|---|---|
| Screen code | PUR-PO-01 |
| Title | Purchase Order Entry |
| Menu path | Menu Purchase > Order entry [^r11] |
| Permitted roles | PUR-EXEC, PUR-SR, SYS-ADMIN [^r11] |
| Primary services | `po_fetch`, `po_save` [^r12][^r18][^r20] |
| Order types | `STD` (Standard), `DIR` (Direct) [^r1][^r6] |

## Fields

Each purchase order raised on PUR-PO-01 accommodates exactly one line item in the grid [^r9].

* **PO NO (`po_no`)**: Purchase order document identifier; read-only [^r13].
* **PO TYPE (`po_type`)**: Mandatory order classification [^r13]. Supported values are `STD` for orders referencing an approved purchase request and `DIR` for direct low-value orders raised without a request [^r1][^r6]. `DIR` orders referencing a purchase request trigger error ERR-PO-0611, while `DIR` orders exceeding £50,000 gross value trigger [[err-po-0610|ERR-PO-0610]] [^r10][^r16].
* **SOURCE PR (`pr_no`)**: Optional request reference; populated with the approved request number when raising `STD` orders [^r1][^r18][^r33].
* **SUP CD (`sup_cd`)**: Mandatory supplier code [^r13][^r18].
* **ITEM CD (`itm_cd`)**: Mandatory item number [^r13][^r18]. The component lookup may experience query latency across large item families unless restricted by initial character input [^r27].
* **QTY (`qty`)**: Mandatory order quantity; populated by `po_fetch` when linked to a request [^r12][^r13].
* **RATE (`rate`)**: Mandatory unit price; populated by `po_fetch` from contracted rates [^r12][^r13]. Pressing `F2` in this field opens a historical rate look-up window displaying previous agreed purchase rates, references, and statuses for the selected supplier and item, transferring the selected value directly into the line [^r25][^r26].
* **PAY TERM (`pt_cd`)**: Payment terms; retrieved via `po_fetch`; read-only [^r12][^r13].
* **TAX CD (`tax_cd`)**: Mandatory tax classification [^r13]. Populated by `po_fetch` with default `VAT20-UK` representing plant location [^r3][^r15][^r19]. For non-UK suppliers, users must manually change this field to `VAT20-RC` to avoid validation failure on save [^r3][^r8][^r15][^r19][^r36].
* **CC CD (`cc_cd`)**: Mandatory cost centre code; populated by `po_fetch` [^r12][^r13].
* **NEED DT (`need_dt`)**: Mandatory required delivery date; populated by `po_fetch` [^r12][^r13].
* **STATUS (`status`)**: Header purchase order status; read-only [^r13]. Possible values include Draft (`DR`), Pending Approval (`PA`), or Approved (`AP`) [^r4][^r17].
* **DELIVERY REMARKS**: Text field for special transit or carriage instructions to alert receiving personnel to pallet drops or oversized deliveries [^r40].

## Keys and services

* **F2 (Rate History)**: Accessible within the Rate field; invokes the previous rate enquiry pop-up for the active supplier and item [^r25]. Cancelling returns to the field without updating values [^r26].
* **F3 (Fetch / `po_fetch`)**: Executes read service `po_fetch` under [[services-pur-po|PUR po services]] using mandatory inputs `sup_cd` and `itm_cd`, and optional input `pr_no` [^r12][^r18]. It retrieves the contract rate, lead periods, descriptions, payment terms, cost centre, need date, quantity, and defaults `tax_cd` to `VAT20-UK` [^r12][^r18][^r19][^r34].
* **F8 (Save / `po_save`)**: Invokes backend service `po_save` to record order details [^r20]. Upon write completion, the bottom status bar displays `SAVED` regardless of whether the document remains uncommitted or stuck in status `DR`, `PA`, or `AP` [^r4][^r37].
* **Order submission**: Submitting an order transfers it to [[screen-pur-poa-04|PUR-POA-04]] for approval [^r23]. Any subsequent line modification returns the order to an unapproved state [^r23]. If rejected during approval, the order returns to PUR-PO-01 with notification for the creator [^r24].

## Messages

* **[[err-scr-0221|ERR-SCR-0221]] (`FETCH NOT DONE`)**: Raised on save when the user has not performed an explicit `F3` Fetch action for the current supplier and item combination, or if either field was modified after fetching [^r2][^r7][^r14][^r28][^r35].
* **[[err-po-0412|ERR-PO-0412]] (`TAX CODE DOES NOT MATCH SUPPLIER COUNTRY`)**: Raised on save when an order for an overseas supplier retains the default UK tax code `VAT20-UK` instead of `VAT20-RC` [^r3][^r8][^r15][^r19].
* **[[err-po-0610|ERR-PO-0610]]**: Raised on save if a direct purchase order (`DIR`) exceeds the gross monetary limit of £50,000 [^r10][^r16].
* **ERR-PO-0611**: Raised on save if a direct purchase order (`DIR`) references a purchase request [^r10].
* **[[w-cc-114|W-CC-114]]**: Amber warning banner displayed when saving an order allocated to a closed cost centre [^r17][^r21][^r29]. The order is stored in Draft status (`DR`) with editable lines, commitment is blocked, and the status bar displays `SAVED` [^r5][^r17][^r21][^r29].
* **W-SUP-0207 (`UN38.3 CERTIFICATE MISSING OR EXPIRED`)**: Advisory status bar warning generated when system parameter `PUR.CERT_CHK` is set to `Y` and an order is saved for an item flagged as a lithium cell whose supplier lacks a valid UN 38.3 certificate on the order date [^r30][^r31]. The warning is non-fatal and allows the order to save [^r31][^r32].

## Versions and conflicts

* **Fetch requirement before save**: Today, `F3` Fetch must be executed for the identical supplier and item combination prior to saving, otherwise save is halted with [[err-scr-0221|ERR-SCR-0221]] (`MAN-PUR-72 v7.2.3`, `RN-7.2.3`, `QRC-02 v2026.1`) [^r7][^r28][^r35]. In obsolete 2016 intranet guidance (`11_training/intranet_export_2016/how_to_raise_an_order.html`), Fetch was described as optional with rates entered manually (`superseded`) [^r39].
* **Single-line versus multi-line orders**: Today, PUR-PO-01 permits only one item line per purchase order document (`MAN-PUR-72 v7.2.3`) [^r9]. From March 2027 under Ledgerline ERP 7.3 preview, PUR-PO-01 will support multi-line purchase orders on a single document header (`RN-7.3-PREVIEW`) (`future_dated`) [^r41].
* **UN 38.3 validation severity**: Today, when `PUR.CERT_CHK=Y`, missing or expired UN 38.3 certificates issue an advisory status warning `W-SUP-0207` while permitting the order save to complete (`RN-7.2.3-P4`) [^r31][^r32]. From March 2027 under Ledgerline ERP 7.3 preview, a non-compliant or expired certificate on any cell line will hard-block the entire order with [[err-sup-0207|ERR-SUP-0207]] (`RN-7.3-PREVIEW`) (`future_dated`) [^r42].

## See also

* [[sop-pur-002|SOP-PUR-002 Purchase Request to Purchase Order]]
* [[man-pur-72|MAN-PUR-72 Ledgerline ERP 7.2 User Manual, Purchasing]]
* [[services-pur-po|PUR po services]]
* [[screen-pur-pr-01|PUR-PR-01 Purchase Request Entry]]
* [[screen-pur-poa-04|PUR-POA-04 Purchase Order Approval]]
* [[screen-pur-por-05|PUR-POR-05 Purchase Order Release]]
* [[screen-pur-pom-06|PUR-POM-06 Purchase Order Amendment]]
* [[screen-pur-poh-02|PUR-POH-02 Order History By Item]]
* [[screen-fin-cc-01|FIN-CC-01 Cost Centre Entry]]
* [[err-scr-0221|ERR-SCR-0221 FETCH NOT DONE]]
* [[err-po-0412|ERR-PO-0412 TAX CODE DOES NOT MATCH SUPPLIER COUNTRY]]
* [[err-po-0610|ERR-PO-0610 Direct order exceeds maximum allowed value]]
* [[w-cc-114|W-CC-114]]
* [[data-tax-codes|Tax codes]]

## References

[^r9]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 7, §11.6 Line fields
[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 27, PUR-PO-01 PURCHASE ORDER ENTRY
[^r22]: 08_release_notes/RN-7.0 Ledgerline Release Notes.pdf, p. 2, §3. Details
[^r1]: 02_procedures/SOP-PUR-002 PR to PO v1.4.pdf, p. 3, §5. Procedure
[^r6]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 7, §11.2 Order types
[^r2]: 02_procedures/SOP-PUR-002 PR to PO v1.4.pdf, p. 3, §5. Procedure
[^r7]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 7, §11.3 Fetch before Save
[^r28]: 08_release_notes/RN-7.2.3 Ledgerline Release Notes.pdf, p. 2, Save on PUR-PO-01 needs Fetch for the current supplier and item: ERR-SCR-0221 FETCH NOT DONE.
[^r35]: 11_training/QRC-02 Raising a purchase order - Fetch first.pdf, p. 1, Steps
[^r12]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 27, PUR-PO-01 PURCHASE ORDER ENTRY
[^r18]: 04_service_definitions/purchase/po_fetch.yaml, service: po_fetch
[^r20]: 04_service_definitions/purchase/po_save.yaml, screen: PUR-PO-01
[^r13]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 27, PUR-PO-01 PURCHASE ORDER ENTRY
[^r10]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 7, §11.7 Direct orders
[^r16]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 27, PUR-PO-01 PURCHASE ORDER ENTRY
[^r33]: 11_training/QRC-02 Raising a purchase order - Fetch first.pdf, p. 1, Steps
[^r27]: 08_release_notes/RN-7.0.1 Ledgerline Release Notes.pdf, p. 3, §4. Known issues
[^r25]: 08_release_notes/RN-7.0.1 Ledgerline Release Notes.pdf, p. 2, Purchasing: Rate history on F2 in the Rate field of PUR-PO-01
[^r26]: 08_release_notes/RN-7.0.1 Ledgerline Release Notes.pdf, p. 2, Purchasing: Rate history on F2 in the Rate field of PUR-PO-01
[^r3]: 02_procedures/SOP-PUR-002 PR to PO v1.4.pdf, p. 3, §5. Procedure
[^r15]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 27, PUR-PO-01 PURCHASE ORDER ENTRY
[^r19]: 04_service_definitions/purchase/po_fetch.yaml, notes
[^r8]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 7, §11.4 The tax code
[^r36]: 11_training/QRC-02 Raising a purchase order - Fetch first.pdf, p. 1, Tips - Tax codes for overseas orders
[^r4]: 02_procedures/SOP-PUR-002 PR to PO v1.4.pdf, p. 3, §5. Procedure
[^r17]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 27, PUR-PO-01 PURCHASE ORDER ENTRY
[^r40]: 11_training/intranet_export_2016/how_to_raise_an_order.html, How to raise an order
[^r34]: 11_training/QRC-02 Raising a purchase order - Fetch first.pdf, p. 1, Tips - Fetching records
[^r37]: 11_training/QRC-02 Raising a purchase order - Fetch first.pdf, p. 1, Tips - Checking order status
[^r23]: 08_release_notes/RN-7.0 Ledgerline Release Notes.pdf, p. 2, §3. Details
[^r24]: 08_release_notes/RN-7.0 Ledgerline Release Notes.pdf, p. 2, §3. Details
[^r14]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 27, PUR-PO-01 PURCHASE ORDER ENTRY
[^r21]: 04_service_definitions/purchase/po_save.yaml, notes
[^r29]: 08_release_notes/RN-7.2.3 Ledgerline Release Notes.pdf, p. 3, Orders saved against a closed cost centre are kept as Draft with warning W-CC-114 instead of being refused.
[^r5]: 02_procedures/SOP-PUR-002 PR to PO v1.4.pdf, p. 3, §5. Procedure
[^r30]: 08_release_notes/RN-7.2.3-P4 Ledgerline Patch Notes.pdf, p. 2, §3. Details
[^r31]: 08_release_notes/RN-7.2.3-P4 Ledgerline Patch Notes.pdf, p. 2, §3. Details
[^r32]: 08_release_notes/RN-7.2.3-P4 Ledgerline Patch Notes.pdf, p. 2, §3. Details
[^r39]: 11_training/intranet_export_2016/how_to_raise_an_order.html, How to raise an order
[^r41]: 08_release_notes/RN-7.3 PREVIEW (planned March 2027).pdf, p. 1, Multi-line purchase orders on PUR-PO-01
[^r42]: 08_release_notes/RN-7.3 PREVIEW (planned March 2027).pdf, p. 2, Common misunderstandings
