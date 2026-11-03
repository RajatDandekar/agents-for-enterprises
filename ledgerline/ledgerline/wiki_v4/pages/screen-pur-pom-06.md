---
title: "PUR-POM-06 Purchase Order Amendment"
type: "screen"
slug: "screen-pur-pom-06"
summary: "Ledgerline screen PUR-POM-06 for amending purchase order quantities, need dates, and cost centres, or cancelling purchase orders."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-PUR-003 PO Amendment and Cancellation v1.2.pdf", "03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/purchase/po_amend.yaml", "04_service_definitions/purchase/po_cancel.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | PUR-POM-06 |
| name | Purchase Order Amendment |
| menu | Purchase > Order amendment |
| roles | PUR-EXEC, PUR-SR, SYS-ADMIN |
| services | po_amend, po_cancel |

Screen PUR-POM-06 (Purchase Order Amendment) is the Ledgerline screen used to update the quantity, need-by date, or cost centre on existing purchase orders, or to cancel an order entirely [^r1][^r4][^r9]. It is available under Menu Purchase > Order amendment to users with roles PUR-EXEC, PUR-SR, and SYS-ADMIN [^r9]. Changes that exceed existing approval limits return the order to approval, while cancellations set the order status to CN and release committed budget without alerting the vendor [^r8][^r10][^r16].

| Property | Value |
|---|---|
| Screen code | PUR-POM-06 [^r9] |
| Screen title | Purchase Order Amendment [^r9] |
| Navigation path | Purchase > Order amendment [^r9] |
| Authorized roles | PUR-EXEC, PUR-SR, SYS-ADMIN [^r9] |
| Underlying services | po_amend, po_cancel [^r13] |

## Fields

Users retrieve purchase orders into the screen using the Fetch function [^r1]. Screen PUR-POM-06 restricts updates strictly to line quantity, need-by date, and cost centre [^r1][^r4][^r10]:

* **PO Number** (`po_no`): Mandatory purchase order identifier used to retrieve and target the record [^r15][^r17].
* **Quantity** (`qty`): Order line quantity permitted for amendment [^r1][^r10][^r15].
* **Need-By Date** (`need_dt`): Target delivery requirement date permitted for amendment [^r1][^r10][^r15].
* **Cost Centre** (`cc_cd`): Assigned department cost centre code permitted for amendment [^r1][^r10][^r15].
* **Cancellation Reason** (`reason`): Mandatory narrative text field required when invoking order cancellation [^r2][^r8][^r17].

## Keys and services

Screen PUR-POM-06 executes background transactional write services provided by [[services-pur-po]]:

* **Fetch**: Retrieves existing order records into the screen interface [^r1].
* **Save (F8)**: Invokes the `po_amend` write service at endpoint `POST /ll72/svc/po_amend` with mandatory parameter `po_no` and optional line updates `qty`, `need_dt`, and `cc_cd` [^r14][^r15]. Saving recalculates the gross order value, releases earlier budget commitments, validates the assigned cost centre, and re-commits the required budget [^r5]. If amendments cause order values to exceed existing approval thresholds, a released order reverts to Pending Approval (`PA`) and is routed back into the approval workflow handled by [[screen-pur-poa-04|PUR-POA-04 Purchase Order Approval]] [^r10][^r16]. Moving an order out of a closed cost centre onto an active one transitions it to `AP` or `PA`, allowing it to proceed onward to [[screen-pur-por-05|PUR-POR-05 Purchase Order Release]] [^r7].
* **Cancel Button**: Executes the `po_cancel` write service at endpoint `POST /ll72/svc/po_cancel`, passing mandatory parameters `po_no` and `reason` [^r13][^r17]. The operation assigns the order status to Cancelled (`CN`) and uncommits budget allocations [^r8]. It does not trigger an automated notification or dispatch a cancellation notice to the external vendor [^r2][^r8][r18].

## Messages

* **[[err-po-0801|ERR-PO-0801]]**: Raised when an operator attempts to amend or commit changes against purchase orders that are already in closed (`CL`), rejected (`RJ`), or cancelled (`CN`) states [^r3][^r12].
* **W-CC-114**: Warning issued when an amended order is assigned to a closed cost centre, retaining or reverting the order to Draft (`DR`) status [^r6][^r11][^r16].

## See also

* [[err-po-0801|ERR-PO-0801 Order in CN, RJ or CL status cannot be amended]]
* [[screen-fin-cc-01|FIN-CC-01 Cost Centre Entry]]
* [[screen-pur-po-01|PUR-PO-01 Purchase Order Entry]]
* [[screen-pur-poa-04|PUR-POA-04 Purchase Order Approval]]
* [[screen-pur-por-05|PUR-POR-05 Purchase Order Release]]
* [[services-pur-po|PUR po services]]

## References

[^r1]: 02_procedures/SOP-PUR-003 PO Amendment and Cancellation v1.2.pdf, p. 3, §5. Procedure
[^r4]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 9, §14.1 Purpose
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 28, PUR-POM-06 PURCHASE ORDER AMENDMENT
[^r8]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 9, §14.5 Cancelling
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 28, PUR-POM-06 PURCHASE ORDER AMENDMENT
[^r16]: 04_service_definitions/purchase/po_amend.yaml, notes
[^r13]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 7, po_amend PO AMEND
[^r15]: 04_service_definitions/purchase/po_amend.yaml, request
[^r17]: 04_service_definitions/purchase/po_cancel.yaml, service: po_cancel
[^r2]: 02_procedures/SOP-PUR-003 PO Amendment and Cancellation v1.2.pdf, p. 3, §5. Procedure
[^r14]: 04_service_definitions/purchase/po_amend.yaml, whole file
[^r5]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 9, §14.2 Amending
[^r7]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 9, §14.4 Moving a Draft off a closed cost centre
[^r3]: 02_procedures/SOP-PUR-003 PO Amendment and Cancellation v1.2.pdf, p. 4, §5. Procedure: notes and common mistakes
[^r12]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 28, PUR-POM-06 PURCHASE ORDER AMENDMENT
[^r6]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 9, §14.2 Amending
[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 28, PUR-POM-06 PURCHASE ORDER AMENDMENT
