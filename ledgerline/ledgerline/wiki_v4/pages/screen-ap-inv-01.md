---
title: "AP-INV-01 Supplier Invoice Entry"
type: "screen"
slug: "screen-ap-inv-01"
summary: "Screen AP-INV-01 (Supplier Invoice Entry) records supplier invoices against purchase orders and runs three-way matching in Ledgerline Accounts Payable."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-AP-001 Three-Way Invoice Matching v2.1.pdf", "03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/accounts_payable/inv_cancel.yaml", "04_service_definitions/accounts_payable/inv_get.yaml", "04_service_definitions/accounts_payable/inv_hold.yaml", "04_service_definitions/accounts_payable/inv_post.yaml", "04_service_definitions/accounts_payable/inv_release.yaml", "04_service_definitions/accounts_payable/inv_save.yaml", "04_service_definitions/accounts_payable/inv_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | AP-INV-01 |
| Module | Accounts payable |
| Menu path | Accounts payable > Supplier invoice |
| Roles | AP-CLERK, AP-MGR, FIN-CTRL, SYS-ADMIN |
| Read services | inv_get, inv_search |
| Write services | inv_save, inv_post, inv_hold, inv_release, inv_cancel |
| Status | current |

Screen AP-INV-01 (Supplier invoice) is the Ledgerline screen used to enter supplier invoices against purchase orders and execute the three-way matching comparison [^r1][^r4]. It is located under Accounts payable > Supplier invoice and is accessible to roles AP-CLERK, AP-MGR, FIN-CTRL, and SYS-ADMIN [^r4][^r16]. Invoices entered on this screen are validated against purchase orders, matched against receipt balances, posted to the ledgers, or placed on hold [^r1][^r2][^r7][^r8][^r9].

| Field | Value |
|---|---|
| Screen code | AP-INV-01 |
| Screen title | Supplier Invoice Entry |
| Menu path | Accounts payable > Supplier invoice |
| Roles | AP-CLERK, AP-MGR, FIN-CTRL, SYS-ADMIN |
| Read services | [[services-ap-inv|inv_get]], inv_search |
| Write services | inv_save, inv_post, inv_hold, inv_release, inv_cancel |
| Status | current |

## Fields

Screen AP-INV-01 contains invoice header details, a line details grid, a matching pane showing receipt balances, a unit rate comparison, and a hold status pane [^r2]. The hold status pane flags matched lines with HOLD-PRC or HOLD-QTY during match processing or refresh [^r3].

Mandatory fields on the screen are:
* `SUP CD` (`sup_cd`): Supplier code [^r5][^r17].
* `SUP INV NO` (`sup_inv_no`): Supplier invoice number [^r5][^r17].
* `INV DT` (`inv_dt`): Invoice date [^r5][^r17].
* `BASIC` (`basic`): Basic invoice amount [^r5][^r17].
* `TAX CD` (`tax_cd`): Tax code [^r5][^r17].
* `GROSS` (`gross`): Gross invoice amount [^r5][^r17].
* `AP DOC` (`ap_doc`): System-allocated accounts payable document reference [^r5][^r7][^r17].
* `REASON` (`reason`): Mandatory narrative required when cancelling an invoice voucher or placing it on query hold [^r5][^r6][^r17][^r21].

Optional fields on the screen are:
* `PO NO` (`po_no`): Purchase order reference [^r2][^r5][^r17].
* `TAX` / `TAX AMT` (`tax`): Calculated tax amount [^r5][^r17].
* `STATUS` (`status`): Processing status of the voucher [^r5][^r17].
* `COMMENT` (`comment`): Additional voucher notes [^r5][^r17][^r25].

## Keys and services

Screen AP-INV-01 executes seven backend services through dedicated function keys and buttons [^r4][^r18][^r20]:

* **Save** (F8): Invokes write service `inv_save` via endpoint POST `/ll72/svc/inv_save` [^r4][^r18][^r27]. This validates entries against the purchase order, ensures uniqueness of `SUP CD` and `SUP INV NO`, allocates the internal reference `AP DOC`, and marks `STATUS` as draft [^r7].
* **Get** (F3): Invokes read service `inv_get` via endpoint POST `/ll72/svc/inv_get` using `ap_doc` to retrieve an existing invoice record [^r4][^r18][^r22].
* **Search** (F2 / Enter): Invokes read service `inv_search` to query supplier invoices using optional filters `sup_cd`, `sup_inv_no`, `inv_dt`, and `status` [^r4][^r18][^r29].
* **Post** (F9): Invokes write service `inv_post` via endpoint POST `/ll72/svc/inv_post` requiring `ap_doc` (with optional `comment`) [^r4][^r18][^r24][^r25]. It commits the voucher to the purchase ledger and general ledger, marks purchase order lines as invoiced, and updates `STATUS` to posted [^r8].
* **Hold**: Invokes write service `inv_hold` with mandatory `ap_doc` and optional `reason` [^r4][^r18][^r23]. This sets `STATUS` to held to prevent voucher selection in payment runs [^r9].
* **Release** (F9): Invokes write service `inv_release` via endpoint POST `/ll72/svc/inv_release` using `ap_doc` to clear the hold flag [^r4][^r18][^r26][^r9].
* **Cancel** (Shift+F8): Invokes write service `inv_cancel` via endpoint POST `/ll72/svc/inv_cancel` requiring `ap_doc` and `reason` [^r4][^r18][^r21]. This marks `STATUS` as cancelled on unposted vouchers and releases matched quantities back to the purchase order [^r10]. Invoking cancellation on an already posted invoice raises ERR-INV-0801, requiring a credit note instead [^r15].

## Messages

The screen checks entry and posting conditions and displays the following message codes [^r11][^r19]:

* `ERR-INV-0001` [^r11][^r19]
* `ERR-INV-0007`: Raised when the supplier invoice number in `SUP INV NO` has already been entered and posted for the vendor in `SUP CD` [^r11][^r13][^r19].
* [[err-inv-0118|ERR-INV-0118]]: Duplicate Supplier Invoice No [^r19][^r28], or incomplete lines/missing required fields such as `PO NO` or monetary fields upon selecting post [^r14].
* `ERR-INV-0801`: Supplier Invoice Closed (`<Status>`), raised when attempting to cancel an already posted invoice voucher [^r11][^r15][^r19].
* `ERR-MAT-0410` [^r11][^r19]
* `ERR-MAT-0411` [^r11][^r19]
* `ERR-PER-0003`: Ap Period Closed (`<Period>`) [^r11][^r19].
* `ERR-PO-0001`: Po Not Found [^r11][^r19][^r28].
* [[err-sup-0030|ERR-SUP-0030]]: SUPPLIER NOT FOUND [^r11][^r28].
* `ERR-TAX-0101`: Invalid Tax Code [^r11][^r19][^r28].

## Versions and conflicts

* Saving via `inv_save` sets the voucher `STATUS` to draft according to the service workflow description [^r7]. In contrast, the user guidance section describes the resulting status after save as unposted [^r12] (contradiction between MAN-AP-72 v7.2.3 p. 5 and p. 7).
* In the service definition and screen reference, `ERR-INV-0118` is defined as Duplicate Supplier Invoice No [^r19][^r28]. However, the user manual questions section states that duplicate entries raise `ERR-INV-0007` upon save, whereas `ERR-INV-0118` is returned when attempting to post with incomplete lines or blank mandatory fields [^r13][^r14] (contradiction between MAN-AP-72 v7.2.3 and MAN-SCR-72 / inv_save.yaml).

## See also

* [[services-ap-inv|AP inv services]]
* [[errors-inv|Errors INV (ERR-INV-*)]]
* [[screen-ap-mat-02|AP-MAT-02 Three-Way Match]]
* [[screen-ap-pay-03|AP-PAY-03 Payment Run]]
* [[screen-ap-crn-05|AP-CRN-05 Supplier Credit Note Entry]]
* [[screen-ap-per-11|AP-PER-11 Ap Period]]
* [[screen-ap-tax-17|AP-TAX-17 Tax Code Master]]
* [[screen-ap-spy-16|AP-SPY-16 Supplier Payment Hold Hold]]
* [[services-pur-po|PUR po services]]

## References

[^r1]: 02_procedures/SOP-AP-001 Three-Way Invoice Matching v2.1.pdf, p. 3, §5. Procedure
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 3, §3. Supplier Invoice (AP-INV-01)
[^r16]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 7, AP-INV-01 SUPPLIER INVOICE ENTRY
[^r2]: 02_procedures/SOP-AP-001 Three-Way Invoice Matching v2.1.pdf, p. 4, What to check on screen AP-INV-01
[^r7]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 5, Step by step
[^r8]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 5, Step by step
[^r9]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 5, Step by step
[^r3]: 02_procedures/SOP-AP-001 Three-Way Invoice Matching v2.1.pdf, p. 4, What to check on screen AP-INV-01
[^r5]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 3, §3. Supplier Invoice (AP-INV-01)
[^r17]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 7, AP-INV-01 SUPPLIER INVOICE ENTRY
[^r6]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 4, Layout and fields
[^r21]: 04_service_definitions/accounts_payable/inv_cancel.yaml, service: inv_cancel
[^r25]: 04_service_definitions/accounts_payable/inv_post.yaml, request.fields
[^r18]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 7, AP-INV-01 SUPPLIER INVOICE ENTRY
[^r20]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 25, inv_save SUPPLIER INVOICE SAVE
[^r27]: 04_service_definitions/accounts_payable/inv_save.yaml, service
[^r22]: 04_service_definitions/accounts_payable/inv_get.yaml, screen
[^r29]: 04_service_definitions/accounts_payable/inv_search.yaml, screen
[^r24]: 04_service_definitions/accounts_payable/inv_post.yaml, service
[^r23]: 04_service_definitions/accounts_payable/inv_hold.yaml, whole file
[^r26]: 04_service_definitions/accounts_payable/inv_release.yaml, service: inv_release
[^r10]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 5, Step by step
[^r15]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 7, Questions users ask
[^r11]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 5, Messages
[^r19]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 7, AP-INV-01 SUPPLIER INVOICE ENTRY
[^r13]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 7, Questions users ask
[^r28]: 04_service_definitions/accounts_payable/inv_save.yaml, errors
[^r14]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 7, Questions users ask
[^r12]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 7, Questions users ask
