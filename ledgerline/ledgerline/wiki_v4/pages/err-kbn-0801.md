---
title: "ERR-KBN-0801 Kanban Card Status Transition or Warehouse Validation Error"
type: "error"
slug: "err-kbn-0801"
summary: "Ledgerline error code raised on invalid Kanban card transitions or unauthorized warehouse-item assignments."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-KBN-0801 |
| module | Inventory (INV) |
| type | Error |
| status | current |
| source | MAN-INV-72 |

Error ERR-KBN-0801 is a Ledgerline ERP inventory validation error associated with Kanban card processing on screen [[screen-inv-kbn-13|INV-KBN-13]]. It prevents illegal lifecycle state changes on Kanban cards as well as unauthorized item assignments to warehouse locations [^r1][^r2]. Resolving the error requires checking the active card status, clearing open stores movements, or verifying warehouse authorization in the master data [^r1][^r2].

| Field | Value |
|---|---|
| Error code | ERR-KBN-0801 |
| Module | Inventory (INV) |
| Manual | [[man-inv-72|MAN-INV-72]] |
| Status | Current |

## Meaning

The error indicates an invalid operation on a Kanban card, triggered either by an illegal card status transition or by an incompatible warehouse location mapping [^r1][^r2].

## Cause

The error occurs under three specific conditions:
* Triggering `kbn_signal` on a card that is already in a signalling state [^r1].
* Executing `kbn_close` on a card while stores transactions remain pending [^r1].
* Executing `kbn_save` when the designated warehouse code (`WHS CD`) is not authorized to hold the specified item code (`ITEM CD`) [^r2].

## How to fix

* Verify the current status of the card on [[screen-inv-kbn-13|INV-KBN-13]] before issuing a signal transaction [^r1].
* Complete or reverse all pending stores transactions associated with the card before attempting to close it [^r1].
* Confirm on [[screen-inv-whs-01|INV-WHS-01]] or [[screen-inv-itm-01|INV-ITM-01]] that the target warehouse is authorized to store the component item [^r2].

## Raised by

The error is raised by the following backend services in [[services-inv-kbn|INV kbn services]]:
* `kbn_signal` [^r1]
* `kbn_close` [^r1]
* `kbn_save` [^r2]

## See also

* [[screen-inv-kbn-13|INV-KBN-13 Kanban Card Entry]]
* [[services-inv-kbn|INV kbn services]]
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]
* [[errors-inv|Errors INV (ERR-INV-*)]]
* [[screen-inv-whs-01|INV-WHS-01 Warehouse Master]]
* [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 52, Messages
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 53, Questions users ask
